import {
  PositioningBrief,
  PositioningBriefSchema,
  positioningJsonSchema,
  ResearchData,
} from "../types";
import { generateStructured } from "../gemini";

export async function buildPositioning(research: ResearchData, modelName?: string): Promise<PositioningBrief> {
  const prompt = `Here is verified research on a company. Turn it into an actual point of view — not a restatement of the facts, but a judgment about what this company offers and why it should matter to the audience it's for.

=== RESEARCH ===
${JSON.stringify(research, null, 2)}

Rules:
- Ground every claim in the research above. Do not introduce new facts.
- "corePositioning" must be a single sharp sentence a stranger could repeat back correctly.
- "keyDifferentiators" should reflect what's actually distinctive here, not generic category traits every competitor could also claim.
- If the research is thin on real differentiation, say the honest, more modest version rather than inventing one.`;

  const raw = await generateStructured<PositioningBrief>({
    systemInstruction:
      "You are a senior brand strategist. You turn raw research into a clear, defensible positioning brief. You are allergic to vague statements that could describe any company in the category — you push for the specific true thing.",
    prompt,
    jsonSchema: positioningJsonSchema,
    model: modelName,
  });

  const parsed = PositioningBriefSchema.safeParse(raw);
  if (!parsed.success) {
    throw new Error(`Positioning step returned malformed data: ${parsed.error.message}`);
  }
  return parsed.data;
}