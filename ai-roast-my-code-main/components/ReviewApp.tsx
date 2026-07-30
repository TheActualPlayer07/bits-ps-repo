"use client";

import { useState } from "react";
import type { ReviewResponseBody } from "@/lib/types";
import type { PersonaId } from "@/lib/personas";
import ScoreTicket from "./ScoreTicket";
import PersonaPass from "./PersonaPass";

const LANGUAGES: { value: string; label: string }[] = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "java", label: "Java" },
  { value: "cpp", label: "C++" },
  { value: "c", label: "C" },
  { value: "go", label: "Go" },
  { value: "rust", label: "Rust" },
  { value: "other", label: "Other / not listed" },
];

const PLACEHOLDER = `def process(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            if data[i] > 0:
                result.append(data[i] * 2)
    return result`;

type Status = "idle" | "loading" | "error" | "done";

export default function ReviewApp() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ReviewResponseBody | null>(null);
  const [activePersona, setActivePersona] = useState<PersonaId>("vex");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!code.trim() || status === "loading") return;

    setStatus("loading");
    setError(null);
    try {
      const res = await fetch("/api/review", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ code, language }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "The kitchen sent this back. Try again.");
      }
      setResult(data as ReviewResponseBody);
      setStatus("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="overflow-hidden rounded-2xl border border-line bg-surface">
          <div className="flex items-center justify-between border-b border-line px-4 py-2.5">
            <label htmlFor="language" className="text-xs uppercase tracking-wider text-ink-dim">
              Language
            </label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="rounded-md border border-line bg-surface2 px-2.5 py-1.5 font-mono text-xs text-ink outline-none focus-visible:ring-2 focus-visible:ring-ember"
            >
              {LANGUAGES.map((l) => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={PLACEHOLDER}
            spellCheck={false}
            rows={14}
            className="w-full resize-y bg-transparent px-4 py-4 font-mono text-[13px] leading-relaxed text-ink outline-none placeholder:text-ink-dim/60"
          />
        </div>

        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={!code.trim() || status === "loading"}
            className="inline-flex items-center gap-2 rounded-full bg-ember px-6 py-3 font-display text-sm font-semibold text-base transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-base focus-visible:ring-ember"
          >
            {status === "loading" ? "Firing your ticket…" : "Fire it"}
          </button>
          <span className="text-xs text-ink-dim">
            {code.trim() ? `${code.length.toLocaleString()} characters` : "Paste code to begin"}
          </span>
        </div>
      </form>

      {status === "error" && error && (
        <div className="rounded-xl border border-ember/40 bg-ember-dim/40 px-4 py-3 text-sm text-ink">
          {error}
        </div>
      )}

      {status === "loading" && (
        <div className="rise-in flex items-center gap-3 rounded-xl border border-line bg-surface px-4 py-4 text-sm text-ink-dim">
          <span className="flex h-2.5 w-2.5 animate-pulse rounded-full bg-ember" />
          Reading the ticket, checking the metrics, sending it down the line…
        </div>
      )}

      {status === "done" && result && (
        <div className="rise-in space-y-8">
          <ScoreTicket result={result} />
          <PersonaPass
            personas={result.personas}
            active={activePersona}
            onChange={setActivePersona}
          />
        </div>
      )}
    </div>
  );
}
