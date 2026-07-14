/**
 * Single source of truth for default/fallback Gemini model names.
 *
 * This file deliberately has zero imports. `lib/gemini.ts` pulls in the
 * `@google/genai` SDK, which is server-only — if a client component (like
 * `app/page.tsx`) imported a model name from there, Next.js would try to
 * bundle server-only SDK code into the browser. Keeping these two constants
 * here means both server code (the API route, lib/gemini.ts) and client
 * code (the model picker in app/page.tsx) can import the *same* values
 * without that problem, so the "default model" can't quietly drift apart
 * between files again like it did before (route.ts/page.tsx had hardcoded
 * "gemini-3.5-flash" while lib/gemini.ts's env fallback said "gemini-2.5-flash").
 */

/** Used whenever no model is explicitly requested. Matches the model the
 * README/.env.example describe as the recommended free-tier default. */
export const DEFAULT_MODEL = "gemini-2.5-flash";

/** High-quota model the circuit breaker retries on if the requested model
 * comes back rate-limited or overloaded. This is the same model the UI's
 * dropdown already labels "High Quota Safety" — we're just wiring that
 * existing label up to an actual behavior. */
export const FALLBACK_MODEL = "gemini-3.1-flash-lite";
