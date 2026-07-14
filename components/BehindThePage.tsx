import { PositioningBrief, ResearchData } from "@/lib/types";

export function BehindThePage({
  research,
  positioning,
}: {
  research: ResearchData;
  positioning: PositioningBrief;
}) {
  return (
    <details className="mx-auto max-w-4xl border-t border-slate-200 px-6 py-6 text-sm text-slate-700">
      <summary className="cursor-pointer font-semibold text-slate-900">
        Behind this page — research &amp; positioning
      </summary>
      <div className="mt-5 grid gap-8 sm:grid-cols-2">
        <div>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Research</h4>
          <dl className="space-y-3">
            <Field label="What they do">{research.whatTheyDo}</Field>
            <Field label="Audience">{research.targetAudience}</Field>
            <ListField label="Key claims" items={research.keyClaims} />
            <ListField label="Notable details" items={research.notableDetails} />
          </dl>
        </div>
        <div>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Positioning</h4>
          <dl className="space-y-3">
            <Field label="Core positioning">{positioning.corePositioning}</Field>
            <Field label="Main benefit">{positioning.mainBenefit}</Field>
            <ListField label="Differentiators" items={positioning.keyDifferentiators} />
            <ListField label="Proof points" items={positioning.proofPoints} />
          </dl>
        </div>
      </div>
    </details>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs font-medium text-slate-400">{label}</dt>
      <dd className="mt-0.5 leading-relaxed">{children}</dd>
    </div>
  );
}

function ListField({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <dt className="text-xs font-medium text-slate-400">{label}</dt>
      <dd className="mt-1">
        <ul className="list-inside list-disc space-y-1">
          {items.map((item) => (
            <li key={item} className="leading-relaxed">
              {item}
            </li>
          ))}
        </ul>
      </dd>
    </div>
  );
}
