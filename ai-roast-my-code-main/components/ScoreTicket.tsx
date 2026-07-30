import type { ReviewResponseBody } from "@/lib/types";

const DIMENSION_LABELS = {
  quality: "Quality",
  readability: "Readability",
  maintainability: "Maintainability",
} as const;

function ScoreBar({ label, score, rationale }: { label: string; score: number; rationale: string }) {
  const pct = Math.max(0, Math.min(10, score)) * 10;
  const tone = score >= 8 ? "bg-chill" : score >= 5 ? "bg-amber" : "bg-ember";
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-sm font-medium text-ink">{label}</span>
        <span className="font-mono text-sm text-ink-dim">{score.toFixed(1)}/10</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface2">
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <p className="mt-1.5 text-xs leading-relaxed text-ink-dim">{rationale}</p>
    </div>
  );
}

const SEVERITY_STYLE: Record<string, string> = {
  high: "border-ember/40 text-ember bg-ember-dim/50",
  medium: "border-amber/40 text-amber bg-amber/10",
  low: "border-chill/40 text-chill bg-chill-dim/40",
};

export default function ScoreTicket({ result }: { result: ReviewResponseBody }) {
  const { scoring, metrics, cached } = result;

  return (
    <div className="ticket-edge overflow-hidden rounded-2xl border border-line bg-surface">
      <div className="flex items-center justify-between px-6 pt-5">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-widest text-ink-dim">Ticket</p>
          <p className="font-display text-lg text-ink">
            Overall <span className="italic text-ember">{scoring.overall.toFixed(1)}/10</span>
          </p>
        </div>
        {cached && (
          <span className="rounded-full border border-chill/40 bg-chill-dim/40 px-2.5 py-1 text-[10px] uppercase tracking-wide text-chill">
            same order, same ticket
          </span>
        )}
      </div>

      <div className="perforation my-5" />

      <div className="space-y-5 px-6">
        {(Object.keys(DIMENSION_LABELS) as (keyof typeof DIMENSION_LABELS)[]).map((k) => (
          <ScoreBar
            key={k}
            label={DIMENSION_LABELS[k]}
            score={scoring[k].score}
            rationale={scoring[k].rationale}
          />
        ))}
      </div>

      <div className="perforation my-5" />

      <div className="grid gap-6 px-6 sm:grid-cols-2">
        <div>
          <p className="mb-2 text-xs uppercase tracking-wider text-ink-dim">Strengths</p>
          <ul className="space-y-1.5 text-sm text-ink">
            {scoring.strengths.map((s, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-chill">+</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <p className="mb-2 text-xs uppercase tracking-wider text-ink-dim">Weaknesses</p>
          <ul className="space-y-1.5 text-sm text-ink">
            {scoring.weaknesses.map((w, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-ember">−</span>
                {w}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {scoring.issues.length > 0 && (
        <div className="mt-6 px-6">
          <p className="mb-2 text-xs uppercase tracking-wider text-ink-dim">Line notes</p>
          <ul className="space-y-2">
            {scoring.issues.map((issue, i) => (
              <li
                key={i}
                className={`flex items-start gap-3 rounded-lg border px-3 py-2 text-xs ${SEVERITY_STYLE[issue.severity]}`}
              >
                <span className="font-mono opacity-80">{issue.line ? `L${issue.line}` : "—"}</span>
                <span className="text-ink">{issue.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="perforation my-5" />

      <div className="flex flex-wrap gap-x-5 gap-y-1 px-6 pb-5 font-mono text-[11px] text-ink-dim">
        <span>{metrics.codeLines} code lines</span>
        <span>{Math.round(metrics.commentRatio * 100)}% comments</span>
        <span>{metrics.functionCount} functions</span>
        <span>depth {metrics.maxNestingDepth}</span>
        <span>cyclomatic ~{metrics.approxCyclomaticComplexity}</span>
        {metrics.tokenReductionPct > 0 && <span>−{metrics.tokenReductionPct}% before review</span>}
      </div>
    </div>
  );
}
