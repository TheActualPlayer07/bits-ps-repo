import { PERSONAS, type PersonaId } from "@/lib/personas";

interface Props {
  personas: Record<PersonaId, string>;
  active: PersonaId;
  onChange: (id: PersonaId) => void;
}

export default function PersonaPass({ personas, active, onChange }: Props) {
  const ids = Object.keys(personas) as PersonaId[];

  return (
    <div>
      <div className="mb-3 flex gap-2">
        {ids.map((id) => {
          const persona = PERSONAS[id];
          const isActive = id === active;
          const isEmber = persona.color === "ember";
          const activeClasses = isEmber
            ? "border-ember/50 bg-ember-dim/40"
            : "border-chill/50 bg-chill-dim/40";
          const nameClasses = isActive ? (isEmber ? "text-ember" : "text-chill") : "text-ink";
          return (
            <button
              key={id}
              onClick={() => onChange(id)}
              className={`flex-1 rounded-xl border px-4 py-3 text-left transition ${
                isActive ? activeClasses : "border-line bg-surface hover:bg-surface2"
              }`}
            >
              <p className={`font-display text-base ${nameClasses}`}>{persona.name}</p>
              <p className="mt-0.5 text-xs text-ink-dim">{persona.tagline}</p>
            </button>
          );
        })}
      </div>

      <div className="rounded-2xl border border-line bg-surface px-6 py-6">
        <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-ink">
          {personas[active]}
        </p>
      </div>
    </div>
  );
}
