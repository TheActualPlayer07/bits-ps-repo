// lib/anthropic.ts
//
// Thin wrapper around the Anthropic Messages API with exponential-backoff
// retries, used by both pipeline stages (scoring + persona narration).

const ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION = "2023-06-01";

export interface AnthropicMessage {
  role: "user" | "assistant";
  content: string;
}

interface CallOptions {
  model: string;
  system: string;
  messages: AnthropicMessage[];
  maxTokens?: number;
  maxRetries?: number;
}

export class AnthropicCallError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "AnthropicCallError";
    this.status = status;
  }
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Calls the Anthropic Messages API and returns the concatenated text content.
 * Retries with exponential backoff (+ jitter) on 429s and 5xxs, since those
 * are the transient failure modes a review agent will actually hit under
 * back-to-back submissions.
 */
export async function callClaude({
  model,
  system,
  messages,
  maxTokens = 1500,
  maxRetries = 3,
}: CallOptions): Promise<string> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new AnthropicCallError(
      "ANTHROPIC_API_KEY is not set. Add it to your environment (.env.local locally, or Project Settings > Environment Variables on Vercel)."
    );
  }

  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(ANTHROPIC_API_URL, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-api-key": apiKey,
          "anthropic-version": ANTHROPIC_VERSION,
        },
        body: JSON.stringify({
          model,
          max_tokens: maxTokens,
          system,
          messages,
        }),
      });

      if (res.status === 429 || res.status >= 500) {
        const retryAfter = Number(res.headers.get("retry-after"));
        const backoff = Number.isFinite(retryAfter) && retryAfter > 0
          ? retryAfter * 1000
          : Math.min(1000 * 2 ** attempt + Math.random() * 300, 8000);
        if (attempt < maxRetries) {
          await sleep(backoff);
          continue;
        }
        throw new AnthropicCallError(`Anthropic API error ${res.status} after ${maxRetries} retries`, res.status);
      }

      if (!res.ok) {
        const body = await res.text();
        throw new AnthropicCallError(`Anthropic API error ${res.status}: ${body}`, res.status);
      }

      const data = await res.json();
      const text = (data.content ?? [])
        .filter((block: { type: string }) => block.type === "text")
        .map((block: { text: string }) => block.text)
        .join("\n");
      return text;
    } catch (err) {
      lastError = err;
      if (err instanceof AnthropicCallError && err.status && err.status < 500 && err.status !== 429) {
        throw err; // don't retry genuine 4xx (bad key, bad request)
      }
      if (attempt === maxRetries) break;
      await sleep(Math.min(1000 * 2 ** attempt + Math.random() * 300, 8000));
    }
  }

  throw lastError instanceof Error ? lastError : new AnthropicCallError("Anthropic API call failed");
}

/**
 * Pulls the first valid JSON object out of a model response, tolerant of
 * markdown code fences or stray prose the model adds despite instructions.
 */
export function extractJson<T>(text: string): T {
  const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/i);
  const candidate = fenced ? fenced[1] : text;
  const start = candidate.indexOf("{");
  const end = candidate.lastIndexOf("}");
  if (start === -1 || end === -1) {
    throw new Error("No JSON object found in model response");
  }
  return JSON.parse(candidate.slice(start, end + 1)) as T;
}
