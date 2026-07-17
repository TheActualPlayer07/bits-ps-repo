"use client";

type Stage = { label: string; detail: string };

const STAGES: Stage[] = [
  { label: "Research", detail: "reading the site, checking outside sources" },
  { label: "Positioning", detail: "working out the actual point of view" },
  { label: "Copywriting", detail: "drafting, then editing out the filler" },
  { label: "Page build", detail: "structuring hero, sections, CTAs" },
  { label: "Render", detail: "handing back a page, not a document" },
];

export function PipelineTicker({
  activeIndex,
  complete,
}: {
  /** -1 = nothing started yet */
  activeIndex: number;
  complete: boolean;
}) {
  return (
    <ol className="relative ml-3 border-l border-dashed border-manuscript/25 pl-7">
      {STAGES.map((stage, i) => {
        const isDone = complete || i < activeIndex;
        const isActive = !complete && i === activeIndex;
        return (
          <li key={stage.label} className="relative pb-8 last:pb-0">
            <span
              className={`absolute -left-[38px] top-0 flex h-6 w-6 items-center justify-center rounded-full border font-display text-[13px] italic ${
                isDone
                  ? "border-redline bg-redline text-manuscript"
                  : isActive
                  ? "border-redline text-redline"
                  : "border-manuscript/30 text-manuscript/40"
              }`}
              aria-hidden="true"
            >
              {isDone ? "✓" : i + 1}
            </span>
            <p
              className={`font-display text-[15px] leading-none ${
                isDone || isActive ? "text-manuscript" : "text-manuscript/40"
              }`}
            >
              {stage.label}
              {isActive && (
                <span className="ml-2 inline-block animate-pulse text-redline">·in progress</span>
              )}
            </p>
            <p className={`mt-1.5 text-xs ${isDone || isActive ? "text-manuscript/60" : "text-manuscript/30"}`}>
              {stage.detail}
            </p>
          </li>
        );
      })}
    </ol>
  );
}
