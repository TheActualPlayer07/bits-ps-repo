"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { PipelineTicker } from "@/components/PipelineTicker";
import { DEFAULT_MODEL } from "@/lib/models";

// Roughly how long each backbone stage tends to take against gemini.
// Purely cosmetic — the real work happens in one API call — but it keeps
// the person watching honestly informed about what's happening instead of
// staring at a bare spinner.
const STAGE_TIMINGS_MS = [4000, 8000, 14000, 4000];

export default function HomePage() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL); // Matches the server's default (lib/models.ts)
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(-1);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    return () => timers.current.forEach(clearTimeout);
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;

    setStatus("loading");
    setError(null);
    setActiveIndex(0);
    timers.current.forEach(clearTimeout);
    timers.current = [];

    let elapsed = 0;
    STAGE_TIMINGS_MS.forEach((delay, i) => {
      elapsed += delay;
      timers.current.push(setTimeout(() => setActiveIndex(i + 1), elapsed));
    });

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          url, 
          model: selectedModel // ✓ Updated line
        }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.error || "Something went wrong generating this page.");
      }

      timers.current.forEach(clearTimeout);
      sessionStorage.setItem(
        "lastGeneration",
        JSON.stringify({ research: data.research, positioning: data.positioning, page: data.page })
      );
      router.push("/preview");
    } catch (err) {
      timers.current.forEach(clearTimeout);
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong. Try again.");
    }
  }

  return (
    <main className="min-h-screen px-6 py-16 md:py-24">
      <div className="mx-auto grid max-w-5xl gap-16 md:grid-cols-[minmax(0,260px)_1fr]">
        {/* LEFT: brand + pipeline */}
        <div>
          <div className="mb-10 flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-manuscript/50">
            <span className="h-1.5 w-1.5 rounded-full bg-redline" />
            Hero Page Generator
          </div>
          <p className="mb-10 max-w-[24ch] font-display text-lg italic leading-snug text-manuscript/80">
            One URL in. One page worth shipping out.
          </p>
          <PipelineTicker activeIndex={activeIndex} complete={false} />
        </div>

        {/* RIGHT: the manuscript card */}
        <div className="manuscript-card px-7 py-9 md:px-10 md:py-12">
          <h1 className="max-w-[18ch] font-display text-[32px] font-semibold leading-[1.1] tracking-tight md:text-[40px]">
            Give it a company. It hands back a landing page.
          </h1>
          <p className="mt-4 max-w-[52ch] text-[15px] leading-relaxed text-ink-700">
            Real research on the company, an actual point of view on what it offers, and copy
            that earns its place — not template filler. Drop in a URL to see it work.
          </p>

          <form onSubmit={handleSubmit} className="mt-9">
            <div className="flex flex-col gap-4 w-full">
  
              {/* 1. GRANULAR API MODEL SELECTOR (Direct pass-through control board) */}
              <div className="flex flex-col gap-1.5">
                <label htmlFor="model-select" className="text-xs font-mono uppercase tracking-wider text-ink-950/40 block">
                  Target Gemini API Model
                </label>
                <select
                  id="model-select"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  disabled={status === "loading"}
                  className="w-full rounded-sm border border-ink-950/15 bg-white px-4 py-3 text-[15px] text-ink-950 focus-visible:ring-2 focus-visible:ring-redline disabled:opacity-60 font-mono outline-none appearance-none cursor-pointer"
                >
                  <option value="gemini-3.5-flash">Gemini 3.5 Flash (Peak Copy Quality)</option>
                  <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash Lite (High Quota Safety — 500 RPD)</option>
                  <option value="gemini-3-flash">Gemini 3 Flash</option>
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash (Stable Production Baseline)</option>
                </select>
              </div>

              {/* 2. THE MAIN URL INPUT INPUT BLOCK */}
              <div className="flex flex-col gap-1.5">
                <label htmlFor="url" className="text-xs font-mono uppercase tracking-wider text-ink-950/40 block">
                  Company URL
                </label>
                <div className="flex flex-col gap-3 sm:flex-row">
                  <input
                    id="url"
                    type="text"
                    inputMode="url"
                    required
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={status === "loading"}
                    placeholder="https://acme.com"
                    className="w-full rounded-sm border border-ink-950/15 bg-white px-4 py-3 text-[15px] text-ink-950 placeholder:text-ink-950/35 focus-visible:ring-2 focus-visible:ring-redline disabled:opacity-60"
                  />
                  <button
                    type="submit"
                    disabled={status === "loading"}
                    className="shrink-0 rounded-sm bg-redline px-6 py-3 font-display text-[15px] font-semibold text-manuscript transition hover:bg-[#98301F] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {status === "loading" ? "Generating…" : "Generate page →"}
                  </button>
                </div>
              </div>

            </div>

            {status === "loading" && (
              <p className="mt-4 font-mono text-xs text-ink-700/70">
                This usually takes 20–40 seconds — real research and two copywriting passes, not a template swap.
              </p>
            )}

            {status === "error" && error && (
              <div className="mt-5 rounded-sm border border-redline/40 bg-redline/5 px-4 py-3 text-[13.5px] text-[#8A3018]">
                <b>Couldn&apos;t generate that page.</b> {error}
              </div>
            )}
          </form>
        </div>
      </div>
    </main>
  );
}