// Talks to OUR OWN backend (api/index.py) instead of Groq directly - the
// Groq API key now lives server-side only and never ships in this bundle.
// Same callAgent(systemPrompt, userContent, opts) / getQuotaInfo() contract
// as before, so trial.js needed zero changes when this moved server-side.
//
// In dev, Vite and Flask run on different ports, so point this at your
// local Flask server via VITE_BACKEND_URL (e.g. http://localhost:5000). In
// prod on Vercel, the frontend and /api/* share an origin, so the default
// relative path just works.
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL
  ? `${import.meta.env.VITE_BACKEND_URL}/api/agent`
  : '/api/agent';

let lastQuota = null;

/** Snapshot of the most recently seen quota info, or null if none yet. */
export function getQuotaInfo() {
  return lastQuota;
}

/**
 * Calls our backend, which calls Groq. All the retry/backoff, TPM-vs-TPD
 * classification, and refusal-cascade logic now lives server-side in
 * api/index.py (a straight port of what used to be here) - this function
 * just forwards the request and surfaces whatever the backend decided.
 * @param {string} systemPrompt - persona instructions
 * @param {string} userContent - the decision/context, or prior turns in the debate
 * @param {object} opts - { jsonMode: boolean, temperature: number, maxTokens: number }
 */
export async function callAgent(systemPrompt, userContent, opts = {}) {
  const { jsonMode = false, temperature = 0.7, maxTokens = 300 } = opts;

  const res = await fetch(BACKEND_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ systemPrompt, userContent, jsonMode, temperature, maxTokens }),
  });

  const data = await res.json().catch(() => ({}));
  if (data.quota) lastQuota = data.quota;

  if (!res.ok) {
    const err = new Error(data.error || `Backend request failed (${res.status})`);
    err.status = res.status;
    if (data.rateLimitScope) err.rateLimitScope = data.rateLimitScope;
    throw err;
  }

  return data.content ?? '';
}
