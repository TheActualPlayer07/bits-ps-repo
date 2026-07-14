import { NextRequest, NextResponse } from "next/server";
import { runResearch } from "@/lib/pipeline/research";
import { buildPositioning } from "@/lib/pipeline/positioning";
import { writeCopy } from "@/lib/pipeline/copywriting";
import { DEFAULT_MODEL, FALLBACK_MODEL } from "@/lib/models";
import { PageContent, PositioningBrief, ResearchData } from "@/lib/types";

export const maxDuration = 60;

type PipelineResult = {
  research: ResearchData;
  positioning: PositioningBrief;
  page: PageContent;
};

/**
 * Runs the full three-stage pipeline (research -> positioning -> copy) for
 * a single model. Pulled out on its own so the circuit breaker below can
 * retry the *whole* pipeline against a fallback model without duplicating
 * this sequence.
 */
async function runPipeline(url: string, model: string): Promise<PipelineResult> {
  const research = await runResearch(url, model);
  const positioning = await buildPositioning(research, model);
  const page = await writeCopy(research, positioning, model);
  return { research, positioning, page };
}

/**
 * True if an error looks like a transient quota/overload condition (HTTP
 * 429 "RESOURCE_EXHAUSTED" or 503 "UNAVAILABLE") worth retrying on a
 * different model, rather than a real failure like a bad URL, a malformed
 * schema, or a missing API key — those should still surface as errors
 * instead of silently retrying.
 */
function isRetryableQuotaError(err: unknown): boolean {
  const message = err instanceof Error ? err.message : String(err);
  return (
    message.includes("429") ||
    message.includes("RESOURCE_EXHAUSTED") ||
    message.includes("503") ||
    message.includes("UNAVAILABLE")
  );
}

export async function POST(req: NextRequest) {
  let url: string | undefined;
  let chosenModel: string = DEFAULT_MODEL;

  try {
    const body = await req.json();
    url = body?.url;
    if (body?.model) {
      chosenModel = body.model;
    }
  } catch {
    return NextResponse.json({ error: "Request body must be JSON with a `url` field." }, { status: 400 });
  }

  if (!url || typeof url !== "string" || url.trim().length === 0) {
    return NextResponse.json({ error: "Provide a company URL to generate a page for." }, { status: 400 });
  }

  const trimmedUrl = url.trim();

  try {
    const result = await runPipeline(trimmedUrl, chosenModel);
    return NextResponse.json(result);
  } catch (err) {
    // Circuit breaker: if the *requested* model is rate-limited or
    // overloaded, transparently retry the whole pipeline on a high-quota
    // fallback model instead of failing the request outright. We only do
    // this once, and only if we weren't already on the fallback model.
    if (isRetryableQuotaError(err) && chosenModel !== FALLBACK_MODEL) {
      console.warn(
        `[CIRCUIT BREAKER] "${chosenModel}" hit a quota/overload error. Retrying with fallback model "${FALLBACK_MODEL}".`
      );

      try {
        const result = await runPipeline(trimmedUrl, FALLBACK_MODEL);
        return NextResponse.json({
          ...result,
          fallbackActivated: true,
          requestedModel: chosenModel,
          modelUsed: FALLBACK_MODEL,
        });
      } catch (fallbackErr) {
        const message =
          fallbackErr instanceof Error ? fallbackErr.message : "Something went wrong generating this page.";
        return NextResponse.json({ error: message }, { status: 500 });
      }
    }

    const message = err instanceof Error ? err.message : "Something went wrong generating this page.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}