import { NextRequest, NextResponse } from "next/server";
import { analyzeCode, type Language } from "@/lib/metrics";
import { callClaude, extractJson } from "@/lib/anthropic";
import { PERSONAS, SCORING_SYSTEM_PROMPT } from "@/lib/personas";
import { checkRateLimit, getCached, hashKey, setCached } from "@/lib/guards";
import type { ReviewRequestBody, ReviewResponseBody, ScoringResult } from "@/lib/types";

export const runtime = "nodejs";
export const maxDuration = 60;

const SCORING_MODEL = process.env.SCORING_MODEL || "claude-haiku-4-5-20251001";
const PERSONA_MODEL = process.env.PERSONA_MODEL || "claude-sonnet-5";
const MAX_CODE_LENGTH = 20_000; // characters

const SUPPORTED_LANGUAGES: Language[] = [
  "python",
  "javascript",
  "typescript",
  "java",
  "cpp",
  "c",
  "go",
  "rust",
  "other",
];

function clientIp(req: NextRequest): string {
  const fwd = req.headers.get("x-forwarded-for");
  return fwd?.split(",")[0]?.trim() || req.headers.get("x-real-ip") || "unknown";
}

export async function POST(req: NextRequest) {
  const ip = clientIp(req);
  const rl = checkRateLimit(ip);
  if (!rl.allowed) {
    return NextResponse.json(
      { error: "Too many submissions. Slow down and try again shortly." },
      { status: 429, headers: { "Retry-After": String(Math.ceil((rl.retryAfterMs ?? 5000) / 1000)) } }
    );
  }

  let body: ReviewRequestBody;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Malformed request body." }, { status: 400 });
  }

  const code = (body.code ?? "").toString();
  const language = SUPPORTED_LANGUAGES.includes(body.language) ? body.language : "other";

  if (!code.trim()) {
    return NextResponse.json({ error: "No code submitted." }, { status: 400 });
  }
  if (code.length > MAX_CODE_LENGTH) {
    return NextResponse.json(
      { error: `Submission too long (${code.length} chars). Limit is ${MAX_CODE_LENGTH}.` },
      { status: 413 }
    );
  }

  const cacheKey = hashKey(code, language);
  const cachedResult = getCached<ReviewResponseBody>(cacheKey);
  if (cachedResult) {
    return NextResponse.json({ ...cachedResult, cached: true });
  }

  const metrics = analyzeCode(code, language);

  let scoring: ScoringResult;
  try {
    const scoringResponse = await callClaude({
      model: SCORING_MODEL,
      system: SCORING_SYSTEM_PROMPT,
      messages: [
        {
          role: "user",
          content: [
            `Language: ${language}`,
            `Static metrics: ${JSON.stringify(metrics, (k, v) => (k === "strippedCode" ? undefined : v))}`,
            "Code (comments and blank lines already stripped for review):",
            "```",
            metrics.strippedCode || code,
            "```",
          ].join("\n"),
        },
      ],
      maxTokens: 1200,
    });
    scoring = extractJson<ScoringResult>(scoringResponse);
  } catch (err) {
    console.error("Scoring stage failed:", err);
    return NextResponse.json(
      { error: "The review brain hit a snag scoring this submission. Please try again." },
      { status: 502 }
    );
  }

  const factSheet = JSON.stringify(scoring);
  let personaEntries: [string, string][];
  try {
    personaEntries = await Promise.all(
      (Object.keys(PERSONAS) as (keyof typeof PERSONAS)[]).map(async (id) => {
        const persona = PERSONAS[id];
        const text = await callClaude({
          model: PERSONA_MODEL,
          system: persona.systemPrompt,
          messages: [
            {
              role: "user",
              content: `Here is the ticket for this submission (scores + findings, already decided — narrate these, don't re-score):\n${factSheet}`,
            },
          ],
          maxTokens: 500,
        });
        return [id, text.trim()] as [string, string];
      })
    );
  } catch (err) {
    console.error("Persona stage failed:", err);
    return NextResponse.json(
      { error: "Scoring succeeded but the personas hit a snag narrating it. Please try again." },
      { status: 502 }
    );
  }

  const personas = Object.fromEntries(personaEntries) as ReviewResponseBody["personas"];

  const result: ReviewResponseBody = {
    language,
    metrics,
    scoring,
    personas,
    cached: false,
  };

  setCached(cacheKey, result);
  return NextResponse.json(result);
}
