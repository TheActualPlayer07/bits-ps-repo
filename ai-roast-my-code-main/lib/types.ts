// lib/types.ts
import type { CodeMetrics, Language } from "./metrics";
import type { PersonaId } from "./personas";

export interface ScoreDimension {
  score: number;
  rationale: string;
}

export interface Issue {
  line: number | null;
  description: string;
  severity: "low" | "medium" | "high";
}

export interface ScoringResult {
  quality: ScoreDimension;
  readability: ScoreDimension;
  maintainability: ScoreDimension;
  overall: number;
  strengths: string[];
  weaknesses: string[];
  issues: Issue[];
}

export interface ReviewRequestBody {
  code: string;
  language: Language;
}

export interface ReviewResponseBody {
  language: Language;
  metrics: CodeMetrics;
  scoring: ScoringResult;
  personas: Record<PersonaId, string>;
  cached: boolean;
}
