/**
 * Builds a structured transcript object from a full trial run.
 * This is the "sample output" artifact required by WO-07 — a full
 * record of the exchange, not just the final verdict JSON.
 */
export function buildTranscript({ decision, context, turns, verdict, rounds }) {
  return {
    case: { decision, context: context || null },
    trial: turns, // [{ speaker, role, content }, ...] in chronological order
    rounds,
    verdict,
    generated_at: new Date().toISOString(),
  };
}

/** Renders a transcript object as readable Markdown for submission/sharing. */
export function transcriptToMarkdown(transcript) {
  const lines = [];
  lines.push('# Trial Transcript');
  lines.push('');
  lines.push(`**Decision:** ${transcript.case.decision}`);
  if (transcript.case.context) lines.push(`**Context:** ${transcript.case.context}`);
  lines.push('');

  transcript.trial.forEach((turn) => {
    lines.push(`## ${turn.speaker} — ${turn.role}`);
    lines.push(turn.content);
    lines.push('');
  });

  lines.push(`## Ruling: ${transcript.verdict.ruling}`);
  lines.push(`Category: ${transcript.verdict.verdict_category} — Score: ${transcript.verdict.score}/100`);
  lines.push("_The judge's overall read on this decision, using the full courtroom trial as its investigation method — not a standalone moral judgment._");
  if (transcript.verdict.score_breakdown) {
    const b = transcript.verdict.score_breakdown;
    lines.push('**Decision Facts** _(true regardless of how well anyone argued it)_');
    lines.push(`- Risk Level: ${b.risk_level.score}/25 — ${b.risk_level.reason}`);
    lines.push(`- Reversibility: ${b.reversibility.score}/25 — ${b.reversibility.reason}`);
    lines.push('');
    lines.push('**Courtroom Findings** _(only knowable by testing the case in the trial)_');
    lines.push(`- Resilience Under Scrutiny: ${b.resilience_under_scrutiny.score}/25 — ${b.resilience_under_scrutiny.reason}`);
    lines.push(`- Alignment with Goals: ${b.alignment.score}/25 — ${b.alignment.reason}`);
  }
  lines.push('');
  lines.push(transcript.verdict.reasoning);
  lines.push('');
  lines.push(`**Recommendation:** ${transcript.verdict.recommendation}`);
  if (transcript.verdict.sentence) {
    const s = transcript.verdict.sentence;
    lines.push('');
    lines.push('**Sentence**');
    (s.terms || []).forEach((term) => lines.push(`- ${term}`));
    lines.push(`- Probation period: ${s.probation_period}`);
    lines.push(`- Case reopens if: ${s.review_condition}`);
  }
  lines.push('');
  lines.push(`> "${transcript.verdict.closing_line}"`);

  return lines.join('\n');
}
