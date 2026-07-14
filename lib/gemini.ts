import { GoogleGenAI } from "@google/genai";
import { DEFAULT_MODEL } from "./models";

let client: GoogleGenAI | null = null;

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
  const response = await ai.models.generateContent({
    model: params.model || getModelName(), // ◄ Dynamically uses override string if present
    contents: params.prompt,
    config: {
      systemInstruction: params.systemInstruction,
      responseMimeType: "application/json",
      responseSchema: params.jsonSchema,
    },
  });

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
  const response = await ai.models.generateContent({
    model: modelName || getModelName(), // ◄ Dynamically uses override string if present
    contents: prompt,
    config: {
      tools: [{ googleSearch: {} }],
    },
  });
  return response.text ?? "";
}