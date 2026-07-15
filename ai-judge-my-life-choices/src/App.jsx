import { useState, useRef, useEffect } from 'react';
import { runTrial } from './agents/trial.js';
import { getQuotaInfo } from './lib/groq.js';
import { transcriptToMarkdown } from './agents/transcript.js';
import IntroSketch from './components/IntroSketch.jsx';
import HistoryPanel from './components/HistoryPanel.jsx';
import { getCaseHistory, saveCase, clearCaseHistory } from './lib/caseHistory.js';

const PHASE = {
  DECISION: 'decision',   // waiting for the decision text
  CONTEXT: 'context',     // decision captured, asking for optional context
  READY: 'ready',         // context captured (or skipped), can simulate
  RUNNING: 'running',
  DONE: 'done',
  ERROR: 'error',
};

const METRIC_GROUPS = [
  {
    title: 'Decision Facts',
    subtitle: 'True about this choice regardless of how well anyone argued it',
    metrics: [
      {
        key: 'risk_level',
        label: 'Risk Level',
        description:
          'How severe are the real risks here - not whether anyone noticed them?\nHigh score = risks are small and manageable.\nLow score = risks are large and likely.',
      },
      {
        key: 'reversibility',
        label: 'Reversibility',
        description:
          "If you actually went through with this choice and it turned out to be a mistake, how easily could you undo the consequences?\n(About undoing the choice itself, not doing the opposite of the verdict.)\nHigh score = easy to reverse.\nLow score = a one-way door.",
      },
    ],
  },
  {
    title: 'Courtroom Findings',
    subtitle: 'Only knowable by actually testing the case in the trial',
    metrics: [
      {
        key: 'resilience_under_scrutiny',
        label: 'Resilience Under Scrutiny',
        description:
          'Does the specific claimed benefit actually hold up when challenged?\nHigh score = the case for it survives scrutiny.\nLow score = it collapses under pressure.',
      },
      {
        key: 'alignment',
        label: 'Alignment with Goals',
        description:
          "How well does this fit your own stated context and goals?\nHigh score = genuinely tailored to your situation.\nLow score = poor fit, or not enough context was given.",
      },
    ],
  },
];

let idCounter = 0;
const nextId = () => ++idCounter;

// Matches things like "rerun", "re-run the trial", "re run this", "run it
// again", "redo this case" - typed instead of retyping the whole decision,
// so a case that came out ambiguous can just be re-argued as-is.
function isRerunCommand(text) {
  const normalized = text
    .trim()
    .toLowerCase()
    .replace(/[.!]+$/, '')
    .replace(/-/g, ' ')
    .replace(/\s+/g, ' ');

  return (
    /^(re ?run|redo)( the| this)?( trial| case| it)?$/.test(normalized) ||
    /^run( it| this| the trial)? again$/.test(normalized)
  );
}

const GREETING = "State the decision you want on trial. I'll bring in a prosecutor and defence to argue it out.";
const ASK_CONTEXT =
  'Any context I should know — timeline, alternatives, constraints? Add it, or hit "Simulate courtroom" to go straight to trial.';
const CONTEXT_NOTED = 'Noted. Hit "Simulate courtroom" whenever you\'re ready.';

// Shared by both a live trial run and a history reload, so reopening a past
// (or the just-finished current) case shows the full argued trial - every
// turn - not just the final verdict summary.
function turnsToMessages(turns) {
  return turns.map((turn) => ({
    id: nextId(),
    role: 'assistant',
    side: turn.speaker === 'Prosecutor' ? 'prosecutor' : 'defence',
    tag: `${turn.isWitness ? 'Witness · ' : ''}${turn.speaker} · ${turn.role}`,
    text: turn.content,
  }));
}

export default function App() {
  const [entered, setEntered] = useState(false);
  const [phase, setPhase] = useState(PHASE.DECISION);
  const [decision, setDecision] = useState('');
  const [context, setContext] = useState('');
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState([{ id: nextId(), role: 'assistant', text: GREETING }]);
  const [lastResult, setLastResult] = useState(null);
  const [currentCaseId, setCurrentCaseId] = useState(null);
  const [history, setHistory] = useState([]);
  const [hoverOpen, setHoverOpen] = useState(false);
  const [pinnedOpen, setPinnedOpen] = useState(false);
  const historyOpen = hoverOpen || pinnedOpen;
  // Seconds left until Groq's per-minute token window resets, or null when
  // there's no active cooldown. Only set when remaining tokens are low
  // enough that starting another trial would likely get cut short anyway -
  // the softer "space out further trials" banner (still shown elsewhere)
  // covers the "getting low but probably fine" range above this.
  const [cooldown, setCooldown] = useState(null);

  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  // A trial can use several thousand tokens across its ~10-14 calls, so
  // "critically low" is set well above zero - below this, a new trial is
  // likely to hit the per-minute cap partway through rather than complete.
  const CRITICAL_TOKEN_THRESHOLD = 1500;

  function checkCooldownFromQuota() {
    const quota = getQuotaInfo();
    if (!quota || quota.remainingTokens == null) return;
    if (quota.remainingTokens >= CRITICAL_TOKEN_THRESHOLD) return;
    if (typeof quota.resetTokensSeconds !== 'number') return;

    // checkedAt/resetTokensSeconds describe the window as of when the
    // response arrived - subtract however long ago that was so the
    // countdown is accurate even if the user is looking at this a few
    // seconds after the last call finished, not just at that instant.
    const elapsedSinceCheck = (Date.now() - (quota.checkedAt ?? Date.now())) / 1000;
    const remaining = Math.max(0, Math.ceil(quota.resetTokensSeconds - elapsedSinceCheck));
    if (remaining > 0) setCooldown(remaining);
  }

  useEffect(() => {
    if (cooldown == null) return;
    if (cooldown <= 0) {
      setCooldown(null);
      return;
    }
    const timer = setTimeout(() => setCooldown((c) => (c == null ? null : c - 1)), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  useEffect(() => {
    setHistory(getCaseHistory());
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  function pushMessage(msg) {
    setMessages((prev) => [...prev, { id: nextId(), ...msg }]);
  }

  function resetCase(greeting = 'New case. State the decision you want on trial.') {
    setDecision('');
    setContext('');
    setDraft('');
    setLastResult(null);
    setCurrentCaseId(null);
    setPhase(PHASE.DECISION);
    setMessages([{ id: nextId(), role: 'assistant', text: greeting }]);
    requestAnimationFrame(() => textareaRef.current?.focus());
  }

  async function startTrial(finalDecision, finalContext) {
    setPhase(PHASE.RUNNING);
    pushMessage({ role: 'system', text: 'Court is in session...' });
    try {
      const trialResult = await runTrial({ decision: finalDecision, context: finalContext });
      setMessages((prev) => [...prev, ...turnsToMessages(trialResult.turns)]);
      pushMessage({ role: 'verdict', result: trialResult });
      setLastResult(trialResult);
      const entry = saveCase({ decision: finalDecision, context: finalContext, result: trialResult });
      setCurrentCaseId(entry.id);
      setHistory((prev) => [entry, ...prev]);
      setPhase(PHASE.DONE);
      checkCooldownFromQuota();
    } catch (err) {
      const msg = err.message || 'Something went wrong running the trial.';
      pushMessage({ role: 'assistant', text: `The trial couldn't complete: ${msg}` });
      setPhase(PHASE.ERROR);
      checkCooldownFromQuota();
    }
  }

  function handleSend() {
    const text = draft.trim();
    if (!text || phase === PHASE.RUNNING || cooldown) return;

    if (phase === PHASE.DECISION) {
      setDecision(text);
      pushMessage({ role: 'user', text });
      pushMessage({ role: 'assistant', text: ASK_CONTEXT });
      setPhase(PHASE.CONTEXT);
      setDraft('');
      return;
    }

    if (phase === PHASE.CONTEXT || phase === PHASE.READY) {
      setContext(text);
      pushMessage({ role: 'user', text });
      pushMessage({ role: 'assistant', text: CONTEXT_NOTED });
      setPhase(PHASE.READY);
      setDraft('');
      return;
    }

    // DONE or ERROR: a rerun phrase re-argues the same decision/context
    // instead of being treated as a fresh case; anything else starts a new one
    if (phase === PHASE.DONE || phase === PHASE.ERROR) {
      if (isRerunCommand(text) && decision) {
        pushMessage({ role: 'user', text });
        pushMessage({ role: 'assistant', text: 'Re-running the same case...' });
        setDraft('');
        startTrial(decision, context);
        return;
      }

      setDecision(text);
      setContext('');
      setLastResult(null);
      setCurrentCaseId(null);
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: 'user', text },
        { id: nextId(), role: 'assistant', text: ASK_CONTEXT },
      ]);
      setPhase(PHASE.CONTEXT);
      setDraft('');
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleTextareaInput(e) {
    setDraft(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  }

  function closeHistoryPanel() {
    setHoverOpen(false);
    setPinnedOpen(false);
  }

  function handleLoadCase(entry) {
    setDecision(entry.decision);
    setContext(entry.context);
    setLastResult(entry.result);
    setCurrentCaseId(entry.id);
    setDraft('');
    setPhase(PHASE.READY);
    setMessages([
      { id: nextId(), role: 'assistant', text: `Reloaded case #${entry.id}.` },
      { id: nextId(), role: 'user', text: entry.decision },
      ...(entry.context ? [{ id: nextId(), role: 'user', text: entry.context }] : []),
      { id: nextId(), role: 'system', text: 'Court is in session...' },
      ...turnsToMessages(entry.result.turns),
      { id: nextId(), role: 'verdict', result: entry.result },
      {
        id: nextId(),
        role: 'assistant',
        text: 'Edit the decision or context above, or hit "Simulate courtroom" to re-run it as-is.',
      },
    ]);
    closeHistoryPanel();
  }

  function handleClearHistory() {
    clearCaseHistory();
    setHistory([]);
  }

  function handleChip(action) {
    if (action === 'file') {
      resetCase();
      return;
    }

    if (action === 'simulate') {
      if (phase === PHASE.RUNNING) return;
      if (!decision.trim()) {
        pushMessage({ role: 'assistant', text: "I need a decision first — tell me what you're weighing." });
        return;
      }
      startTrial(decision, context);
      return;
    }

    if (action === 'download') {
      if (!lastResult) {
        pushMessage({ role: 'assistant', text: "There's no transcript yet — run a trial first." });
        return;
      }
      const md = transcriptToMarkdown(lastResult.transcript);
      const blob = new Blob([md], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'trial-transcript.md';
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  if (!entered) {
    return <IntroSketch onEnter={() => setEntered(true)} />;
  }

  const placeholder =
    phase === PHASE.DECISION
      ? 'Present your decision...'
      : phase === PHASE.RUNNING
      ? 'Court is in session...'
      : 'Add context, or send a new decision...';

  return (
    <div className="rc-root">
      <div className="rc-chat rc-show">
        <div className="rc-topbar">
          <div className="rc-brand">
            <svg viewBox="0 0 24 24">
              <path d="M12 3v18M5 8l-3 6a4 4 0 0 0 6 0zM19 8l-3 6a4 4 0 0 0 6 0zM5 8h14M9 3h6" />
            </svg>
            <span className="rc-brand-name">AI Judge</span>
            {currentCaseId && <span className="rc-case-pill">Case #{currentCaseId}</span>}
          </div>
          <div className="rc-topbar-right">
            <div className="rc-status">
              <span className={`rc-dot${phase === PHASE.RUNNING ? ' rc-dot-busy' : ''}`}></span>
              {phase === PHASE.RUNNING ? 'In session' : 'Ready'}
            </div>
            <div
              className="rc-history-zone"
              onMouseEnter={() => setHoverOpen(true)}
              onMouseLeave={() => setHoverOpen(false)}
            >
              <button
                className="rc-history-trigger"
                onClick={() => setPinnedOpen((v) => !v)}
                aria-label="Case history"
                aria-expanded={historyOpen}
              >
                <svg viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 7v5l3.5 2" />
                </svg>
              </button>
              <HistoryPanel open={historyOpen} cases={history} onSelect={handleLoadCase} onClear={handleClearHistory} onClose={closeHistoryPanel} />
            </div>
          </div>
        </div>

        <div className="rc-messages" ref={scrollRef}>
          {messages.map((m) => {
            if (m.role === 'verdict') return <VerdictCard key={m.id} result={m.result} />;
            if (m.role === 'system') {
              return (
                <div key={m.id} className="rc-system-msg">
                  {m.text}
                </div>
              );
            }
            return (
              <div key={m.id} className={`rc-msg${m.role === 'user' ? ' rc-user' : ''}`}>
                <div className="rc-avatar">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 3v18M5 8l-3 6a4 4 0 0 0 6 0zM19 8l-3 6a4 4 0 0 0 6 0zM5 8h14M9 3h6" />
                  </svg>
                </div>
                <div className={`rc-bubble${m.side ? ` rc-${m.side}` : ''}`}>
                  {m.tag && <span className="rc-tag">{m.tag}</span>}
                  {m.text}
                </div>
              </div>
            );
          })}
        </div>

        <div className="rc-footer">
          {cooldown != null && (
            <p className="rc-cooldown">
              ⏳ Groq's per-minute limit is nearly used up — you can file the next case in {cooldown}s.
            </p>
          )}
          <div className="rc-chips">
            <button className="rc-chip" onClick={() => handleChip('file')} disabled={!!cooldown}>
              📝 File a case
            </button>
            <button className="rc-chip" onClick={() => handleChip('simulate')} disabled={phase === PHASE.RUNNING || !!cooldown}>
              ⚖️ Simulate courtroom
            </button>
            <button className="rc-chip" onClick={() => handleChip('download')} disabled={!lastResult}>
              📁 Download transcript
            </button>
          </div>
          <div className="rc-inputbar">
            <textarea
              ref={textareaRef}
              rows={1}
              value={draft}
              onChange={handleTextareaInput}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={phase === PHASE.RUNNING || !!cooldown}
            />
            <button className="rc-send" aria-label="Send" onClick={handleSend} disabled={phase === PHASE.RUNNING || !!cooldown}>
              <svg viewBox="0 0 24 24">
                <path d="M2 21l21-9L2 3v7l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function VerdictCard({ result }) {
  const { verdict } = result;
  return (
    <div className="rc-verdict">
      {typeof result.rounds === 'number' && (
        <p className="rc-trial-note">
          The judge called this a {result.rounds}-round case — {result.rounds} full exchanges before ruling.
        </p>
      )}

      {result.declined && (
        <p className="rc-partial-banner">
          ⚖️ The model declined to argue this case — see the ruling below for why.
        </p>
      )}
      {result.partial && <p className="rc-partial-banner">⚠️ This trial was cut short - the ruling below is incomplete.</p>}

      <h2 className="rc-verdict-ruling">⚖️ {verdict.ruling}</h2>
      <span className="rc-category-badge">{verdict.verdict_category}</span>
      <p className="rc-score">Score: {typeof verdict.score === 'number' ? `${verdict.score}/100` : 'N/A'}</p>
      <p className="rc-score-caption">
        The judge's overall read on this decision, using the full courtroom trial as its investigation method — not
        a standalone moral judgment.
      </p>

      {verdict.score_breakdown && (
        <div className="rc-score-breakdown">
          {METRIC_GROUPS.map((group) => {
            const groupTotal = group.metrics.reduce((sum, m) => {
              const data = verdict.score_breakdown[m.key];
              return sum + (data ? data.score : 0);
            }, 0);
            return (
              <div className="rc-metric-group" key={group.title}>
                <div className="rc-group-header">
                  <span className="rc-group-title">{group.title}</span>
                  <span className="rc-group-subtotal">{groupTotal}/50</span>
                </div>
                <p className="rc-group-subtitle">{group.subtitle}</p>
                {group.metrics.map((m) => {
                  const data = verdict.score_breakdown[m.key];
                  if (!data) return null;
                  return (
                    <div className="rc-metric" key={m.key}>
                      <div className="rc-metric-header">
                        <span className="rc-metric-label-wrap">
                          {m.label}
                          <span className="rc-info-icon" tabIndex={0}>
                            ⓘ<span className="rc-tooltip">{m.description}</span>
                          </span>
                        </span>
                        <span className="rc-metric-value">{data.score}/25</span>
                      </div>
                      <div className="rc-bar">
                        <div className="rc-fill" style={{ width: `${(data.score / 25) * 100}%` }} />
                      </div>
                      <p className="rc-metric-reason">{data.reason}</p>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}

      <p className="rc-reasoning">{verdict.reasoning}</p>
      <p className="rc-recommendation">
        <strong>Recommendation:</strong> {verdict.recommendation}
      </p>

      {verdict.sentence && (
        <div className="rc-sentence">
          <h3>🔨 Sentence</h3>
          <ul className="rc-sentence-terms">
            {verdict.sentence.terms?.map((term, i) => (
              <li key={i}>{term}</li>
            ))}
          </ul>
          <p className="rc-sentence-meta">
            <strong>Probation period:</strong> {verdict.sentence.probation_period}
          </p>
          <p className="rc-sentence-meta">
            <strong>Case reopens if:</strong> {verdict.sentence.review_condition}
          </p>
        </div>
      )}

      {verdict.closing_line && <p className="rc-closing-line">"{verdict.closing_line}"</p>}
    </div>
  );
}
