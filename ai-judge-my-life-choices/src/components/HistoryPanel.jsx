export default function HistoryPanel({ open, cases, onSelect, onClear, onClose }) {
  return (
    <>
      <div className={`rc-history-backdrop${open ? ' rc-open' : ''}`} onClick={onClose} aria-hidden="true" />
      <div className={`rc-history-panel${open ? ' rc-open' : ''}`} aria-hidden={!open}>
        <div className="rc-history-header">
          <span>Case History</span>
          <div className="rc-history-header-actions">
            {cases.length > 0 && (
              <button className="rc-history-clear" onClick={onClear}>
                Clear
              </button>
            )}
            <button className="rc-history-close" onClick={onClose} aria-label="Close case history">
              ✕
            </button>
          </div>
        </div>
        <div className="rc-history-list">
          {cases.length === 0 && (
            <p className="rc-history-empty">No cases yet — run a trial and it'll show up here.</p>
          )}
          {cases.map((c) => (
            <button key={c.id} className="rc-history-item" onClick={() => onSelect(c)}>
              <span className="rc-history-id">#{c.id}</span>
              <span className="rc-history-decision">{c.decision}</span>
              <span className="rc-history-meta">
                {c.result?.verdict?.verdict_category && (
                  <span className="rc-history-badge">{c.result.verdict.verdict_category}</span>
                )}
                <span className="rc-history-date">{formatDate(c.createdAt)}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
}
