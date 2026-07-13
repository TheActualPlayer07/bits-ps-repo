const STORAGE_KEY = 'aiJudge.caseHistory';
const COUNTER_KEY = 'aiJudge.caseCounter';
const MAX_HISTORY = 50;

export function getCaseHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function nextCaseId() {
  try {
    const n = Number(localStorage.getItem(COUNTER_KEY) || '0') + 1;
    localStorage.setItem(COUNTER_KEY, String(n));
    return String(n).padStart(4, '0');
  } catch {
    // localStorage unavailable (private mode, quota, etc.) - fall back to a
    // timestamp-derived id so the app still works, just without persistence.
    return String(Date.now()).slice(-4);
  }
}

export function saveCase({ decision, context, result }) {
  const entry = {
    id: nextCaseId(),
    decision,
    context,
    createdAt: new Date().toISOString(),
    result,
  };
  const history = [entry, ...getCaseHistory()].slice(0, MAX_HISTORY);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (err) {
    // History is a nice-to-have, not core functionality - fail silently
    // rather than breaking the trial flow if storage is full/unavailable.
    console.warn('Could not save case history:', err);
  }
  return entry;
}

export function clearCaseHistory() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
