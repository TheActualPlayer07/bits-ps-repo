import { callAgent, getQuotaInfo } from '../lib/groq.js';
import {
  COMPLEXITY_PROMPT,
  PROSECUTOR_OPENING_STATEMENT_PROMPT,
  DEFENCE_OPENING_STATEMENT_PROMPT,
  PROSECUTOR_PROMPT,
  DEFENCE_PROMPT,
  JUDGE_FINAL_PROMPT,
  WITNESS_PROMPT,
} from './prompts.js';
import { buildTranscript } from './transcript.js';

function safeParseJSON(raw, fallback) {
  try {
    return JSON.parse(raw);
  } catch (err) {
    return { ...fallback };
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// gpt-oss-120b occasionally misfires its own guardrails on a completely
// benign courtroom-roleplay prompt ("I'm sorry, but I can't help with
// that.") - most often on the two opening statements. Unlike a genuine
// empty/truncated response, a refusal comes back as normal non-empty text,
// so callAgentWithRetry's blank-check alone lets it through as if it were
// a real turn. These are short, generic, and never how an opening
// statement or round actually reads, so they're detectable and worth a
// dedicated retry rather than being displayed as the prosecutor's or
// defence's actual argument.
const REFUSAL_PATTERNS = [
  /i'?m sorry,? but i (can'?t|cannot|won'?t)/i,
  /i (can'?t|cannot|won'?t) (help|assist|comply) with (that|this)/i,
  /as an ai( language model)?,? i/i,
  /i'?m (not able|unable) to (help|assist)/i,
];

function looksLikeRefusal(text) {
  if (!text) return false;
  const trimmed = text.trim();
  // A real opening statement or round is several sentences - refusals are
  // short, so length alone rules out false-positiving on legitimate
  // content that happens to mention e.g. "I can't" as part of an argument.
  if (trimmed.length > 200) return false;
  return REFUSAL_PATTERNS.some((re) => re.test(trimmed));
}

// Thrown from inside the trial loop the moment ANY turn - not just the
// opening statement - comes back as a refusal after callAgentWithRetry has
// already exhausted its own retries. Caught once, centrally, in runTrial's
// catch block below. A refusal partway through (round 2, a witness, etc.)
// is exactly as disqualifying as a refusal on turn one - the case doesn't
// get to keep going just because it got further before tripping the
// guardrail.
class TrialDeclinedError extends Error {}

// Every free-text turn gets passed through this before it's pushed into
// `turns` or the transcript. If it's a refusal, the trial stops right
// there - nothing generated after this point, nothing appended.
function assertUsable(text) {
  if (looksLikeRefusal(text)) {
    throw new TrialDeclinedError();
  }
  return text;
}

/**
 * Wraps callAgent for free-text (non-JSON) turns, where a token-starved
 * call doesn't throw - it just comes back as an empty string, because
 * reasoning models spend part of max_tokens on hidden reasoning before the
 * visible answer even starts, and that reasoning length varies call to
 * call (same root cause as the verdict-truncation issue, just smaller
 * budgets make rapid rounds far more likely to hit it).
 *
 * NOTE: callAgent (groq.js) already handles guardrail refusals internally
 * - strengthened prompt, then a fallback model, before giving up - so a
 * refusal reaching this function means callAgent has already exhausted
 * its own retries. What's left to handle here is the genuine blank/
 * token-starved case: retry once against the same model, then fall back
 * to a visible placeholder instead of a blank turn.
 */
async function callAgentWithRetry(systemPrompt, userContent, opts, label) {
  const first = await callAgent(systemPrompt, userContent, opts);
  if (first && first.trim() && !looksLikeRefusal(first)) return first;

  await sleep(400);
  const retry = await callAgent(systemPrompt, userContent, opts);
  if (retry && retry.trim() && !looksLikeRefusal(retry)) return retry;

  return `(No response from ${label} after retrying - likely ran out of tokens on hidden reasoning, or the model's guardrails misfired on a benign courtroom-roleplay prompt. Try running the trial again.)`;
}

async function assessRounds(caseSummary) {
  const raw = await callAgent(COMPLEXITY_PROMPT, caseSummary, {
    jsonMode: true,
    temperature: 0.3,
    maxTokens: 150, // small JSON, but reasoning tokens count against this too
  });
  const parsed = safeParseJSON(raw, { rounds: 3 });
  const rounds = Number.isInteger(parsed.rounds) ? parsed.rounds : 3;
  return Math.min(5, Math.max(3, rounds)); // always 3-5, never fewer - capped at 5 to stay well within free-tier TPM
}

/**
 * Asks one side's counsel whether THIS case calls for a witness - a real
 * decision, not a formality. Given the opening statements, the agent either
 * declines (most cases) or invents one plausible, relevant person and
 * writes their testimony, all in a single call.
 */
async function maybeCallWitness(side, caseSummary, transcriptSoFar) {
  const input = `${transcriptSoFar}\n\nDecide whether the ${side === 'prosecutor' ? 'prosecution' : 'defence'} should call a witness in this case.`;

  const raw = await callAgent(WITNESS_PROMPT(side), input, {
    jsonMode: true,
    temperature: 0.7,
    maxTokens: 300,
  });

  const parsed = safeParseJSON(raw, { call_witness: false, witness_role: null, testimony: null });
  if (!parsed.call_witness || typeof parsed.testimony !== 'string' || !parsed.testimony.trim()) {
    return null;
  }

  return {
    speaker: side === 'prosecutor' ? 'Prosecutor' : 'Defence',
    role: `Witness — ${typeof parsed.witness_role === 'string' && parsed.witness_role.trim() ? parsed.witness_role : 'Witness'}`,
    content: parsed.testimony,
    isWitness: true,
  };
}

/**
 * Runs a fair multi-round trial like a real courtroom:
 * 1. Opening statements (4-5 sentences each) from prosecutor then defence -
 *    scene-setting, framing the whole case, read once before the rapid
 *    exchanges begin.
 * 2. Each side independently decides whether this specific case calls for
 *    a witness - most don't, and it's their call, not the user's.
 * 3. Judge decides how many rapid rounds the decision deserves (min 3, max 5).
 * 4. Prosecutor and defence alternate short (2-3 sentence) rounds, each
 *    directly responding to the previous turn.
 * 5. Judge delivers a verdict only after everything above is done - and if
 *    the ruling is a guilty verdict, attaches a structured sentence.
 *
 * Token-usage safeguards (openai/gpt-oss-120b free tier caps at 30 RPM,
 * 1K RPD, 8000 TPM, and - the one that actually bites on a multi-round
 * trial - 200,000 TPD):
 * - max_tokens capped per call so a model ignoring word-count instructions
 *   can't blow the budget.
 * - Only the last ~2 rounds are sent as context per rapid-round call, not
 *   the full growing transcript, so per-call cost stays roughly flat.
 * - A small pacing delay between calls spreads requests across a wider
 *   wall-clock window so usage doesn't all land in the same 60s TPM bucket.
 * - callAgent still retries with backoff for TPM/RPM 429s, but fails fast
 *   on a TPD 429 (no point burning 4 slow retries against a limit that
 *   only resets at day-rollover) so the partial-verdict path below kicks
 *   in immediately instead of after ~30s of pointless waiting.
 */
export async function runTrial({ decision, context }) {
  const caseSummary = `Decision: ${decision}\n\nContext: ${context || 'No additional context provided.'}`;
  const turns = [];

  try {
    const rounds = await assessRounds(caseSummary);
    let transcriptSoFar = caseSummary;

    // --- Opening statements: longer, scene-setting, read once ---
    const prosecutorOpening = assertUsable(
      await callAgentWithRetry(PROSECUTOR_OPENING_STATEMENT_PROMPT, caseSummary, { maxTokens: 400 }, 'the prosecutor')
    );
    turns.push({ speaker: 'Prosecutor', role: 'Opening Statement', content: prosecutorOpening });
    transcriptSoFar += `\n\n--- PROSECUTOR OPENING STATEMENT ---\n${prosecutorOpening}`;
    await sleep(500);

    const defenceOpeningInput = `${transcriptSoFar}\n\nDeliver your opening statement, setting out your side of the case.`;
    const defenceOpening = assertUsable(
      await callAgentWithRetry(DEFENCE_OPENING_STATEMENT_PROMPT, defenceOpeningInput, { maxTokens: 400 }, 'the defence')
    );
    turns.push({ speaker: 'Defence', role: 'Opening Statement', content: defenceOpening });
    transcriptSoFar += `\n\n--- DEFENCE OPENING STATEMENT ---\n${defenceOpening}`;
    await sleep(500);

    // --- Witnesses: each side decides for itself, based on the opening
    // statements, whether a real witness would add anything - not called
    // by default. Prosecution is asked first, then defence, matching the
    // order the rest of the trial follows. ---
    const prosecutorWitness = await maybeCallWitness('prosecutor', caseSummary, transcriptSoFar);
    if (prosecutorWitness) {
      assertUsable(prosecutorWitness.content);
      turns.push(prosecutorWitness);
      transcriptSoFar += `\n\n--- PROSECUTOR WITNESS (${prosecutorWitness.role}) ---\n${prosecutorWitness.content}`;
      await sleep(400);
    }

    const defenceWitness = await maybeCallWitness('defence', caseSummary, transcriptSoFar);
    if (defenceWitness) {
      assertUsable(defenceWitness.content);
      turns.push(defenceWitness);
      transcriptSoFar += `\n\n--- DEFENCE WITNESS (${defenceWitness.role}) ---\n${defenceWitness.content}`;
      await sleep(400);
    }

    // --- Rapid rounds: short, direct rebuttals ---
    function recentContext() {
      const parts = transcriptSoFar.split(/\n\n(?=--- )/);
      const header = parts[0];
      const recentTurns = parts.slice(-4); // last ~2 rounds worth of turns
      return [header, ...recentTurns].join('\n\n');
    }

    for (let i = 1; i <= rounds; i++) {
      const prosecutorInput = `${recentContext()}\n\n[Round ${i} of ${rounds}] Deliver your prosecutor turn.`;
      const prosecutorTurn = assertUsable(
        await callAgentWithRetry(PROSECUTOR_PROMPT, prosecutorInput, { maxTokens: 350 }, 'the prosecutor')
      );
      turns.push({ speaker: 'Prosecutor', role: `Round ${i}`, content: prosecutorTurn });
      transcriptSoFar += `\n\n--- PROSECUTOR (Round ${i}) ---\n${prosecutorTurn}`;
      await sleep(500);

      const defenceInput = `${recentContext()}\n\n[Round ${i} of ${rounds}] Deliver your defence turn.`;
      const defenceTurn = assertUsable(
        await callAgentWithRetry(DEFENCE_PROMPT, defenceInput, { maxTokens: 350 }, 'the defence')
      );
      turns.push({ speaker: 'Defence', role: `Round ${i}`, content: defenceTurn });
      transcriptSoFar += `\n\n--- DEFENCE (Round ${i}) ---\n${defenceTurn}`;
      await sleep(500);
    }

    const verdictRaw = await callAgent(JUDGE_FINAL_PROMPT, transcriptSoFar, {
      jsonMode: true,
      temperature: 0.4,
      maxTokens: 1800, // reasoning models spend part of this budget on hidden reasoning tokens
                        // before the visible JSON even starts - too low a budget doesn't error
                        // out, it just silently truncates the tail fields (score, reasoning,
                        // recommendation, closing_line) since Groq's JSON mode grammar-closes
                        // whatever was generated into syntactically valid JSON regardless.
    });

    const verdict = repairVerdict(
      safeParseJSON(verdictRaw, {
        ruling: 'Unable to reach a clean ruling - try running the trial again.',
        verdict_category: 'Unable to reach a clean verdict',
        score_breakdown: null,
        score: null,
        reasoning: "The judge's response could not be parsed as structured output.",
        recommendation: 'Try running the trial again.',
        sentence: null,
        closing_line: '',
      })
    );

    const transcript = buildTranscript({ decision, context, turns, verdict, rounds });

    return { turns, verdict, transcript, rounds, quota: getQuotaInfo() };
  } catch (err) {
    if (err instanceof TrialDeclinedError) {
      // Whatever turns got pushed before the refusal are real and stay -
      // only what would've come after is skipped. If the refusal hit on
      // the very first turn, `turns` is just empty, which is fine.
      const declinedVerdict = {
        ruling: "This case can't be argued here.",
        verdict_category: 'Declined',
        score_breakdown: null,
        score: null,
        reasoning:
          "This one stops here. Some cases aren't something this courtroom will debate, whatever framing they're wrapped in - that's a line, not a glitch, and it doesn't move for a fictional courtroom setting.",
        recommendation: 'Bring a different case to trial.',
        sentence: null,
        closing_line: '',
        declined: true,
      };
      const transcript = buildTranscript({ decision, context, turns, verdict: declinedVerdict, rounds: null });
      return { turns, verdict: declinedVerdict, transcript, rounds: null, declined: true, quota: getQuotaInfo() };
    }

    // callAgent already retries with backoff internally for TPM/RPM 429s,
    // and fails fast (no retries) on a TPD 429 - by the time an error
    // reaches here, either kind is genuinely unrecoverable within this
    // trial. Rather than losing whatever prosecutor/defence turns and
    // witnesses did complete, return them alongside a clearly-marked
    // partial verdict so the UI still has something real to show instead
    // of a hard crash.
    const isRateLimit = err?.status === 429 || err?.message?.includes('rate_limit');
    const isDailyCap = err?.rateLimitScope === 'day';
    const partialVerdict = {
      ruling: isRateLimit
        ? 'Trial cut short - API rate limit reached before the judge could rule.'
        : 'Trial cut short due to an unexpected error before the judge could rule.',
      verdict_category: 'Unable to reach a clean verdict',
      score_breakdown: null,
      score: null,
      reasoning: isRateLimit
        ? 'The courtroom got partway through before hitting the API rate/token limit. The turns above are real and complete - only the final verdict is missing.'
        : `The trial stopped early due to an error: ${err?.message || 'unknown error'}.`,
      recommendation: isDailyCap
        ? "You've hit today's Groq token cap - it resets at day rollover (UTC), not within minutes. Come back later or run fewer trials today."
        : isRateLimit
        ? 'Wait for your API quota to reset, then run the trial again.'
        : 'Try running the trial again.',
      sentence: null,
      closing_line: '',
      partial: true,
    };
    const transcript2 = buildTranscript({ decision, context, turns, verdict: partialVerdict, rounds: null });
    return { turns, verdict: partialVerdict, transcript: transcript2, rounds: null, partial: true, quota: getQuotaInfo() };
  }
}

/**
 * Groq's JSON mode grammar-closes output into syntactically valid JSON even
 * when max_tokens cuts generation short mid-response - so a truncated call
 * doesn't throw in safeParseJSON, it just silently leaves later fields in
 * the schema (score, reasoning, recommendation, closing_line) empty or null
 * while earlier fields (score_breakdown) are fully populated. This patches
 * those gaps so the UI never renders a blank total score or an empty
 * recommendation line.
 */
function repairVerdict(verdict) {
  const repaired = { ...verdict };

  if (typeof repaired.score !== 'number' && repaired.score_breakdown) {
    const b = repaired.score_breakdown;
    const keys = ['risk_level', 'resilience_under_scrutiny', 'alignment', 'reversibility'];
    if (keys.every((k) => b[k] && typeof b[k].score === 'number')) {
      repaired.score = keys.reduce((sum, k) => sum + b[k].score, 0);
    }
  }

  // Belt-and-braces on top of the VERDICT CATEGORY RULE in the prompt: the
  // category is a function of the score, never an independent judgment
  // call, so pin it here even if the model's own output drifted (e.g. a
  // 20/100 case labelled "Reconsider" instead of "Guilty of Self-Sabotage").
  // This also guarantees sentencing actually fires whenever it should,
  // since sentencing is gated purely on this label.
  const CATEGORY_ORDER = ['Guilty of Self-Sabotage', 'Reconsider', 'Proceed With Caution', 'Sound Decision'];
  const worseCategory = (a, b) => {
    if (!a) return b;
    if (!b) return a;
    return CATEGORY_ORDER.indexOf(a) <= CATEGORY_ORDER.indexOf(b) ? a : b;
  };

  if (typeof repaired.score === 'number') {
    if (repaired.score >= 75) repaired.verdict_category = 'Sound Decision';
    else if (repaired.score >= 50) repaired.verdict_category = 'Proceed With Caution';
    else if (repaired.score >= 25) repaired.verdict_category = 'Reconsider';
    else repaired.verdict_category = 'Guilty of Self-Sabotage';
  }

  // CRITICAL-METRIC OVERRIDE: the total is just an additive sum of 4
  // independent metrics, so it has no inherent meaning on its own - a severe
  // risk_level or reversibility problem can get diluted into a comfortable
  // total if alignment/resilience score well, and sentencing should never
  // be skipped because of that dilution. risk_level and reversibility are
  // the two axes that describe actual harm, so they get a veto: a severe
  // score on either one forces (or caps) the category independent of the
  // sum, same as the prompt-level rule, enforced here as a hard guarantee.
  const b = repaired.score_breakdown;
  if (b && b.risk_level && b.reversibility
      && typeof b.risk_level.score === 'number'
      && typeof b.reversibility.score === 'number') {
    const worstCriticalScore = Math.min(b.risk_level.score, b.reversibility.score);
    let floorCategory = null;
    if (worstCriticalScore <= 4) floorCategory = 'Guilty of Self-Sabotage';
    else if (worstCriticalScore <= 10) floorCategory = 'Reconsider';

    if (floorCategory) {
      repaired.verdict_category = worseCategory(repaired.verdict_category, floorCategory);
    }
  }

  if (!repaired.reasoning || !repaired.reasoning.trim()) {
    repaired.reasoning = 'The judge\'s response was cut short before the write-up - the scores above still stand, but try running the trial again for the full reasoning.';
  }

  if (!repaired.recommendation || !repaired.recommendation.trim()) {
    repaired.recommendation = 'Response was cut short - run the trial again for a concrete recommendation.';
  }

  if (!repaired.closing_line || !repaired.closing_line.trim()) {
    repaired.closing_line = '';
  }

  // If the category correction above just turned this into a guilty verdict
  // but the model - working from its own (wrong) category - never generated
  // sentence terms, fall back to a minimal sentence built from what we do
  // have rather than showing a guilty label with an empty sentence block.
  const hasUsableSentence = repaired.sentence
    && Array.isArray(repaired.sentence.terms)
    && repaired.sentence.terms.length > 0
    && repaired.sentence.probation_period
    && repaired.sentence.review_condition;

  if (repaired.verdict_category === 'Guilty of Self-Sabotage' && !hasUsableSentence) {
    repaired.sentence = {
      terms: [repaired.recommendation].filter(Boolean),
      probation_period: '30 days',
      review_condition: 'Re-run the trial once the terms above are met, to confirm the ruling still holds.',
    };
  } else if (repaired.verdict_category !== 'Guilty of Self-Sabotage') {
    repaired.sentence = null;
  }

  return repaired;
}
