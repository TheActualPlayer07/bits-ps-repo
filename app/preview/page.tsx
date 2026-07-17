"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { GeneratedPage } from "@/components/GeneratedPage";
import { BehindThePage } from "@/components/BehindThePage";
import { PageContent, PositioningBrief, ResearchData } from "@/lib/types";
import { decodePageContent, encodePageContent } from "@/lib/share";

type LoadedState = {
  page: PageContent;
  research?: ResearchData;
  positioning?: PositioningBrief;
};

function PreviewInner() {
  const searchParams = useSearchParams();
  const [state, setState] = useState<LoadedState | "loading" | "not-found" | "error">("loading");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const sharedData = searchParams.get("data");

    if (sharedData) {
      try {
        setState({ page: decodePageContent(sharedData) });
        return;
      } catch {
        setState("error");
        return;
      }
    }

    const stored = sessionStorage.getItem("lastGeneration");
    if (!stored) {
      setState("not-found");
      return;
    }
    try {
      const parsed = JSON.parse(stored);
      setState({ page: parsed.page, research: parsed.research, positioning: parsed.positioning });
    } catch {
      setState("error");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (state === "loading") {
    return <CenteredMessage>Loading…</CenteredMessage>;
  }

  if (state === "not-found") {
    return (
      <CenteredMessage>
        Nothing to show yet.{" "}
        <Link href="/" className="underline">
          Generate a page
        </Link>{" "}
        first.
      </CenteredMessage>
    );
  }

  if (state === "error") {
    return <CenteredMessage>That link&apos;s data looks corrupted.</CenteredMessage>;
  }

  function handleShare() {
    if (state === "loading" || state === "not-found" || state === "error") return;
    const encoded = encodePageContent(state.page);
    const shareUrl = `${window.location.origin}/preview?data=${encoded}`;
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div>
      <div className="flex items-center justify-between gap-4 border-b border-slate-100 bg-white px-6 py-3">
        <Link href="/" className="text-sm font-medium text-slate-600 hover:text-slate-900">
          ← New page
        </Link>
        <button
          onClick={handleShare}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
        >
          {copied ? "Link copied ✓" : "Copy shareable link"}
        </button>
      </div>

      {/* 
        FIX: Added the companyUrl prop mapping safely. 
        Extracts the source URL straight from your cached research state block.
      */}
      <GeneratedPage 
        page={state.page} 
        companyUrl={state.research?.url} 
      />

      {state.research && state.positioning && (
        <BehindThePage research={state.research} positioning={state.positioning} />
      )}
    </div>
  );
}

function CenteredMessage({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-6 text-center text-slate-600">
      <p>{children}</p>
    </div>
  );
}

export default function PreviewPage() {
  return (
    <Suspense fallback={<CenteredMessage>Loading…</CenteredMessage>}>
      <PreviewInner />
    </Suspense>
  );
}