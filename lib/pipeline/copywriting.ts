import {
  PageContent,
  PageContentSchema,
  pageContentJsonSchema,
  PositioningBrief,
  ResearchData,
} from "../types";
import { generateStructured } from "../gemini";

/**
 * The house style this whole project is graded against. Kept as one
 * constant so every copy-generating prompt pulls from the same standard.
 */
const OGILVY_PRINCIPLES = `You write like David Ogilvy edited every line:
- Specificity beats superlatives. "revolutionary", "best-in-class", "cutting-edge", "seamless", "unlock your potential" are banned — replace every one with a concrete claim grounded in the research.
- Every headline must earn the next sentence. If a reader could skip it and lose nothing, cut it.
- Benefits before features. Say what the reader gets, not what the product technically does, unless the mechanism itself is the benefit.
- [CRITICAL CTA UNIQUE RULE]: Every Call-To-Action (CTA) button text string MUST be completely unique. Do not repeat the same phrase on the top navigation bar and the hero primary button. Make button copy contextual (e.g., Top Nav: "Get Started", Hero: "Deploy Enterprise AI", Section CTA: "Explore Copilot Features").
- [CRITICAL DEEP-LINKING INSTRUCTION]: For every single button URL field (*Url), analyze the scraped data from the research phase and assign an accurate link path or sub-page destination matching the button text intent. If the button copy says "Schedule a volume licensing call", assign a precise synthesized or extracted pathway like "/licensing/contact" or "/solutions/licensing/sales". If a secondary button reads "Compare Laptop Models", route it to "/surface/devices" or its real equivalent. Never default to simple homepage links unless no sub-path fits.
- No line is filler. If a sentence could be pasted onto a competitor's page unchanged, rewrite it until it couldn't.
- Confidence without hype. State claims plainly; let specificity do the persuading, not adjectives.`;

/** First pass: draft the full page copy from positioning + research. */
export async function draftCopy(
  research: ResearchData,
  positioning: PositioningBrief,
  modelName?: string
): Promise<PageContent> {
  const prompt = `Write the copy and distinct deep-link URLs for a landing page hero + supporting sections for this company.

=== POSITIONING ===
${JSON.stringify(positioning, null, 2)}

=== RESEARCH (Analyze this dataset for exact page text paths, domain metrics, and structural intents) ===
${JSON.stringify(research, null, 2)}

Write every structured field and URL destination path parameter now, following the house style exactly.`;

  const raw = await generateStructured<PageContent>({
    systemInstruction: `You are an Ogilvy-trained direct-response copywriter building a highly functional landing page portal. ${OGILVY_PRINCIPLES}`,
    prompt,
    jsonSchema: pageContentJsonSchema,
    model: modelName,
  });

  const parsed = PageContentSchema.safeParse(raw);
  if (!parsed.success) {
    throw new Error(`Copywriting draft returned malformed data: ${parsed.error.message}`);
  }
  return parsed.data;
}

/**
 * Second pass: have the model review its own draft against the house
 * style and rewrite anything that reads like filler. This is the
 * "self-critique pass" optional move from the work order, folded into the
 * default pipeline because it measurably raises copy quality for close to
 * zero extra cost.
 */
export async function critiqueAndRevise(
  draft: PageContent,
  research: ResearchData,
  modelName?: string
): Promise<PageContent> {
  const prompt = `Here is a landing page draft with mapped destination links. Review every line and URL path against the house style instructions. Rewrite any headline, value prop, feature description, or link path that reads like generic LLM marketing copy, that a competitor's page could use unchanged, or that isn't grounded in the research. Ensure specific buttons like licensing or enterprise requests match up cleanly with precise sub-paths found or inferred from the text source. Keep what already earns its place. Return the full, complete page content — not a diff.

=== DRAFT ===
${JSON.stringify(draft, null, 2)}

=== RESEARCH (ground rewrites in this, don't invent new claims) ===
${JSON.stringify(research, null, 2)}`;

  const raw = await generateStructured<PageContent>(
    {
    systemInstruction: `You are a ruthless copy editor doing a final pass before a landing page ships. ${OGILVY_PRINCIPLES} You are specifically hunting for filler that survived the first draft and ensuring button URLs are completely context-aware.`,
    prompt,
    jsonSchema: pageContentJsonSchema,
    model: modelName,
  });

  const parsed = PageContentSchema.safeParse(raw);
  if (!parsed.success) {
    // If the revision pass ever comes back malformed, fail soft to the
    // (already-valid) draft rather than losing the whole run.
    return draft;
  }
  return parsed.data;
}

export async function writeCopy(
  research: ResearchData,
  positioning: PositioningBrief,
  modelName?: string
): Promise<PageContent> {
  const draft = await draftCopy(research, positioning, modelName);
  return critiqueAndRevise(draft, research, modelName);
}