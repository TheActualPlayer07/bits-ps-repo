import { z } from "zod";

/**
 * Stage 1 output — what the research step learns about the company.
 * This is intentionally a flat, factual record: no opinions yet.
 */
export const ResearchDataSchema = z.object({
  companyName: z.string(),
  url: z.string(),
  oneLineSummary: z.string(),
  whatTheyDo: z.string(),
  targetAudience: z.string(),
  productsOrServices: z.array(z.string()),
  keyClaims: z.array(z.string()),
  notableDetails: z.array(z.string()),
  toneOfVoice: z.string(),
});
export type ResearchData = z.infer<typeof ResearchDataSchema>;

/** JSON Schema mirror of ResearchDataSchema, handed to the Gemini API. */
export const researchJsonSchema = {
  type: "object",
  properties: {
    companyName: { type: "string" },
    url: { type: "string" },
    oneLineSummary: {
      type: "string",
      description: "One plain sentence describing what the company does.",
    },
    whatTheyDo: {
      type: "string",
      description: "2-4 sentences on the product/service and how it works.",
    },
    targetAudience: {
      type: "string",
      description: "Who the company actually sells to, as specifically as the research allows.",
    },
    productsOrServices: {
      type: "array",
      items: { type: "string" },
      description: "Concrete named products, features, or service lines.",
    },
    keyClaims: {
      type: "array",
      items: { type: "string" },
      description: "Specific claims the company makes about itself (numbers, guarantees, differentiators).",
    },
    notableDetails: {
      type: "array",
      items: { type: "string" },
      description: "Anything specific and citable: founding story, customers, awards, unusual facts.",
    },
    toneOfVoice: {
      type: "string",
      description: "How the company currently talks about itself (formal, playful, technical, etc).",
    },
  },
  required: [
    "companyName",
    "url",
    "oneLineSummary",
    "whatTheyDo",
    "targetAudience",
    "productsOrServices",
    "keyClaims",
    "notableDetails",
    "toneOfVoice",
  ],
};

/**
 * Stage 2 output — a point of view, not a list of facts.
 */
export const PositioningBriefSchema = z.object({
  corePositioning: z.string(),
  primaryAudience: z.string(),
  mainBenefit: z.string(),
  keyDifferentiators: z.array(z.string()),
  proofPoints: z.array(z.string()),
  toneGuidance: z.string(),
});
export type PositioningBrief = z.infer<typeof PositioningBriefSchema>;

export const positioningJsonSchema = {
  type: "object",
  properties: {
    corePositioning: {
      type: "string",
      description: "One sharp sentence: what this company offers and why it matters, in plain language.",
    },
    primaryAudience: { type: "string" },
    mainBenefit: {
      type: "string",
      description: "The single outcome the audience cares most about getting.",
    },
    keyDifferentiators: {
      type: "array",
      items: { type: "string" },
      description: "What actually separates this company from alternatives — grounded in the research, not generic.",
    },
    proofPoints: {
      type: "array",
      items: { type: "string" },
      description: "Specific facts/numbers/claims from the research that back up the positioning.",
    },
    toneGuidance: {
      type: "string",
      description: "How the copy should sound to fit this company and audience.",
    },
  },
  required: [
    "corePositioning",
    "primaryAudience",
    "mainBenefit",
    "keyDifferentiators",
    "proofPoints",
    "toneGuidance",
  ],
};

/** The six curated accent themes the generated page can be rendered in. */
export const THEME_NAMES = [
  "violet",
  "emerald",
  "amber",
  "rose",
  "slate",
  "cyan",
] as const;
export const ThemeSchema = z.enum(THEME_NAMES);
export type ThemeName = z.infer<typeof ThemeSchema>;

const ValuePropSchema = z.object({
  title: z.string(),
  description: z.string(),
});

const FeatureSchema = z.object({
  title: z.string(),
  description: z.string(),
});

/**
 * Stage 3 output — the actual page copy + structure, ready to render.
 */
export const PageContentSchema = z.object({
  theme: ThemeSchema,
  meta: z.object({
    companyName: z.string(),
    tagline: z.string(),
  }),
  hero: z.object({
    eyebrow: z.string(),
    headline: z.string(),
    subheadline: z.string(),
    primaryCta: z.string(),
    primaryCtaUrl: z.string(),   // ◄ Added to validate accurate primary destinations
    secondaryCta: z.string(),
    secondaryCtaUrl: z.string(), // ◄ Added to validate accurate secondary destinations
  }),
  valueProps: z.array(ValuePropSchema).min(3).max(4),
  features: z.array(FeatureSchema).min(3).max(6),
  socialProof: z.object({
    statLine: z.string(),
    supportingLine: z.string(),
  }),
  finalCta: z.object({
    headline: z.string(),
    subtext: z.string(),
    ctaLabel: z.string(),
    ctaUrl: z.string(),         // ◄ Added to validate accurate conversion destinations
  }),
});
export type PageContent = z.infer<typeof PageContentSchema>;

export const pageContentJsonSchema = {
  type: "object",
  properties: {
    theme: {
      type: "string",
      enum: THEME_NAMES as unknown as string[],
      description:
        "Pick the accent palette that best fits the company's category and tone (e.g. emerald for finance/health, violet for creative/AI tools, amber for hospitality/food, rose for consumer/lifestyle, cyan for tech/dev tools, slate for enterprise/serious B2B).",
    },
    meta: {
      type: "object",
      properties: {
        companyName: { type: "string" },
        tagline: { type: "string", description: "Under 8 words." },
      },
      required: ["companyName", "tagline"],
    },
    hero: {
      type: "object",
      properties: {
        eyebrow: { type: "string", description: "Small label above the headline, 2-4 words." },
        headline: {
          type: "string",
          description:
            "The single most important line on the page. Specific and benefit-led. Must earn the reader's attention to the next sentence. No generic superlatives like 'best-in-class' or 'revolutionary'.",
        },
        subheadline: {
          type: "string",
          description: "1-2 sentences expanding the headline with a concrete benefit or mechanism.",
        },
        primaryCta: { type: "string", description: "Button label, 2-4 words, active voice." },
        primaryCtaUrl: { 
          type: "string", 
          description: "Relative URL path or sub-page destination matching the primary button's intent based on your research data. Look for real pages from the company site context or synthesize highly logical paths (e.g., if button is 'Schedule a volume licensing call', route to '/licensing/contact' or '/solutions/licensing/sales')." 
        },
        secondaryCta: { type: "string", description: "Lower-commitment button label, 2-4 words." },
        secondaryCtaUrl: { 
          type: "string", 
          description: "Relative path or absolute URL pointing to the matching secondary intent (e.g. if button is 'Compare Laptop Models', route to '/surface/devices' or '/docs')." 
        },
      },
      required: ["eyebrow", "headline", "subheadline", "primaryCta", "primaryCtaUrl", "secondaryCta", "secondaryCtaUrl"],
    },
    valueProps: {
      type: "array",
      minItems: 3,
      maxItems: 4,
      items: {
        type: "object",
        properties: {
          title: { type: "string", description: "3-6 words, benefit not feature." },
          description: { type: "string", description: "One specific sentence, no filler." },
        },
        required: ["title", "description"],
      },
    },
    features: {
      type: "array",
      minItems: 3,
      maxItems: 6,
      items: {
        type: "object",
        properties: {
          title: { type: "string" },
          description: { type: "string" },
        },
        required: ["title", "description"],
      },
    },
    socialProof: {
      type: "object",
      properties: {
        statLine: {
          type: "string",
          description: "One credible, specific proof point grounded in the research (a number, a named detail). Never invent a statistic that wasn't in the research — phrase qualitatively if no real number exists.",
        },
        supportingLine: { type: "string" },
      },
      required: ["statLine", "supportingLine"],
    },
    finalCta: {
      type: "object",
      properties: {
        headline: { type: "string" },
        subtext: { type: "string" },
        ctaLabel: { type: "string" },
        ctaUrl: { 
          type: "string", 
          description: "Relative path or absolute conversion landing URL (e.g. '/contact' or '/signup') matching the exact intent of the ctaLabel string." 
        },
      },
      required: ["headline", "subtext", "ctaLabel", "ctaUrl"],
    },
  },
  required: ["theme", "meta", "hero", "valueProps", "features", "socialProof", "finalCta"],
};