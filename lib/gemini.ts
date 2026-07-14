import { GoogleGenAI, ThinkingLevel } from "@google/genai";
import { DEFAULT_MODEL } from "./models";

let client: GoogleGenAI | null = null;

/**
 * Ceiling for a *single* Gemini call. The pipeline makes up to 5 sequential
 * calls (research grounding, research extraction, positioning, draft,
 * critique) inside one request that itself has to finish inside Vercel's
 * `maxDuration` (see app/api/generate/route.ts). Without a per-call ceiling,
 * one slow call can burn the entire budget and get killed by the platform
 * instead of by our own code — and a platform-level kill returns a
 * non-JSON error page, which is what `res.json()` on the client was
 * choking on. Aborting here instead always produces a normal JS Error,
 * which the route handler turns into a real JSON error response.
 */
const GEMINI_CALL_TIMEOUT_MS = 25_000;

/**
 * Gemini 3.x models (3, 3.1, 3.5, ...) think by default, and — unlike
 * gemini-2.5-flash's dynamic token *budget* — that reasoning effort is
 * controlled by a coarser `thinkingLevel` knob that defaults to "medium".
 * For a 4-stage pipeline where every stage already has a narrow, specific
 * instruction (see the pipeline decisions in the architecture doc), medium+
 * reasoning adds latency without a proportional quality gain, and is the
 * main reason a "peak quality" model can blow past the platform's request
 * timeout where a non-reasoning model wouldn't. "low" keeps responses fast
 * while Google's own docs still describe it as strong general-purpose
 * quality. gemini-2.5-flash isn't touched here — it was never the model
 * that broke, so its existing (dynamic-budget) behavior is left alone.
 */
function getThinkingConfig(model: string): { thinkingLevel: ThinkingLevel } | undefined {
  return model.startsWith("gemini-3") ? { thinkingLevel: ThinkingLevel.LOW } : undefined;
}

/**
 * Lazily-created singleton so we only construct the client once per
 * server process, and only when a request actually needs it (keeps
 * builds working even before GEMINI_API_KEY is set).
 */
export function getGeminiClient(): GoogleGenAI {
  if (!client) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error(
        "GEMINI_API_KEY is not set. Copy .env.example to .env.local and add your key from https://aistudio.google.com/apikey"
      );
    }
    client = new GoogleGenAI({ apiKey });
  }
  return client;
}

export function getModelName(): string {
  return process.env.GEMINI_MODEL || DEFAULT_MODEL;
}

export function isSearchGroundingEnabled(): boolean {
  return process.env.USE_SEARCH_GROUNDING !== "false";
}

/**
 * Calls Gemini and forces the response into the given JSON schema shape.
 * Returns the raw parsed object — callers should still validate with the
 * matching zod schema, since the model can occasionally miss a constraint
 * (e.g. array length) that JSON Schema alone doesn't catch reliably.
 */
export async function generateStructured<T>(params: {
  systemInstruction: string;
  prompt: string;
  jsonSchema: object;
  model?: string; // ◄ Added optional model override property
}): Promise<T> {
  const ai = getGeminiClient();
  const model = params.model || getModelName();

  let response;
  try {
    response = await ai.models.generateContent({
      model,
      contents: params.prompt,
      config: {
        systemInstruction: params.systemInstruction,
        responseMimeType: "application/json",
        responseSchema: params.jsonSchema,
        thinkingConfig: getThinkingConfig(model),
        abortSignal: AbortSignal.timeout(GEMINI_CALL_TIMEOUT_MS),
      },
    });
  } catch (err) {
    if (err instanceof Error && err.name === "TimeoutError") {
      throw new Error(
        `Gemini call to "${model}" timed out after ${GEMINI_CALL_TIMEOUT_MS / 1000}s. Try a faster model, like Gemini 3.1 Flash Lite.`
      );
    }
    throw err;
  }

  const text = response.text;
  if (!text) {
    throw new Error("Gemini returned an empty response.");
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(`Gemini returned non-JSON output despite responseSchema: ${text.slice(0, 300)}`);
  }
}

/**
 * Plain-text generation with Google Search grounding turned on. Used only
 * for the research step's "go find out more" call — kept separate from
 * generateStructured() because grounding tools and forced JSON schemas
 * don't reliably combine on Flash-tier models yet.
 */
export async function generateGroundedText(prompt: string, modelName?: string): Promise<string> { // ◄ Added optional modelName argument
  const ai = getGeminiClient();
  const model = modelName || getModelName();
  const response = await ai.models.generateContent({
    model,
    contents: prompt,
    config: {
      tools: [{ googleSearch: {} }],
      thinkingConfig: getThinkingConfig(model),
      abortSignal: AbortSignal.timeout(GEMINI_CALL_TIMEOUT_MS),
    },
  });
  return response.text ?? "";
}