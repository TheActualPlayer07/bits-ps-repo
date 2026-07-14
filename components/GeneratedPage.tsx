import { PageContent } from "@/lib/types";
import { THEMES } from "@/lib/theme";

interface GeneratedPageProps {
  page: PageContent;
  companyUrl?: string; 
}

export function GeneratedPage({ page, companyUrl }: GeneratedPageProps) {
  const t = THEMES[page.theme];

  // Helper utility to format outbound URLs and safely eliminate duplicate locale paths (like /in/in/)
  const formatOutboundLink = (generatedUrl: string | undefined) => {
    if (!generatedUrl || generatedUrl.trim() === "#" || generatedUrl.trim() === "") {
      return companyUrl || "#";
    }
    
    // If Gemini already returned a fully qualified absolute URL link block, pass it straight through
    if (/^https?:\/\//i.test(generatedUrl)) {
      return generatedUrl;
    }
    
    if (companyUrl) {
      let base = companyUrl.replace(/\/$/, ""); // Clear any trailing trailing slashes safely
      let path = generatedUrl.startsWith("/") ? generatedUrl : `/${generatedUrl}`;
      
      try {
        // Parse the base URL to inspect its path tokens (e.g., handles "/in" sub-paths cleanly)
        const parsedBase = new URL(base.startsWith("http") ? base : `https://${base}`);
        const localeSubPath = parsedBase.pathname.replace(/\/$/, ""); // yields "/in"
        
        // FIX: If the path starts with the exact sub-directory of the base domain, slice it out
        if (localeSubPath && path.startsWith(localeSubPath + "/")) {
          path = path.substring(localeSubPath.length); // Removes the duplicate "/in" prefix
        }
      } catch {
        // Fall back gracefully to standard string combination if the base URL parsing errors out
      }
      
      return `${base}${path}`;
    }
    
    return generatedUrl;
  };

  return (
    // Clean, high-contrast light theme baseline matching your home page aesthetic
    <div className="min-h-screen bg-white text-slate-900 font-sans antialiased">
      
      {/* 1. EDITORIAL HEADER NAVIGATION */}
      <header className="border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          
          <a 
            href={companyUrl || "#"} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-lg font-bold tracking-tight text-slate-900 hover:opacity-75 transition-opacity"
          >
            {page.meta.companyName}
          </a>
          
          <nav className="hidden md:flex items-center gap-8 text-sm font-mono text-slate-500">
            <a href="#benefits" className="hover:text-slate-900 transition">Benefits</a>
            <a href="#features" className="hover:text-slate-900 transition">Features</a>
            <a href="#cta" className="hover:text-slate-900 transition">Get Started</a>
          </nav>

          {/* DYNAMIC IMPLEMENTATION: Deduplicated outbound link tracker */}
          <a
            href={formatOutboundLink(page.finalCta.ctaUrl)}
            target="_blank"
            rel="noopener noreferrer"
            className="hidden rounded-md bg-slate-900 px-4 py-2 text-xs font-mono font-bold text-white sm:inline-block hover:bg-slate-800 transition tracking-wider uppercase shadow-sm"
          >
            {page.finalCta.ctaLabel}
          </a>
        </div>
      </header>

      {/* 2. CRISP HERO ARENA */}
      <section className="border-b border-slate-100 bg-slate-50/60 py-20 sm:py-28 relative overflow-hidden">
        <div className="mx-auto max-w-4xl px-6 text-center relative z-10">
          <span className="inline-block rounded-full bg-slate-200/60 border border-slate-300/40 px-3 py-1 text-xs font-mono uppercase tracking-wide text-slate-600 mb-6">
            {page.hero.eyebrow}
          </span>
          
          <h1 className="text-4xl font-extrabold leading-[1.1] tracking-tight text-slate-900 sm:text-5xl md:text-6xl max-w-3xl mx-auto">
            {page.hero.headline}
          </h1>
          
          <p className="mx-auto mt-6 max-w-2xl text-base md:text-lg leading-relaxed text-slate-600">
            {page.hero.subheadline}
          </p>
          
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            {/* DYNAMIC IMPLEMENTATION: Deduplicated primary hero link */}
            <a
              href={formatOutboundLink(page.hero.primaryCtaUrl)}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full rounded-md bg-slate-900 px-7 py-3.5 text-center text-sm font-mono font-bold text-white shadow-md hover:bg-slate-800 transition sm:w-auto uppercase tracking-wider"
            >
              {page.hero.primaryCta}
            </a>
            
            {/* DYNAMIC IMPLEMENTATION: Deduplicated secondary hero link */}
            <a
              href={formatOutboundLink(page.hero.secondaryCtaUrl)}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full rounded-md border border-slate-300 bg-white px-7 py-3.5 text-center text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 sm:w-auto"
            >
              {page.hero.secondaryCta}
            </a>
          </div>
        </div>
      </section>

      {/* 3. VALUE PROPS */}
      <section id="benefits" className="mx-auto max-w-6xl px-6 py-16 sm:py-24">
        <div className={`grid gap-8 ${page.valueProps.length === 3 ? "sm:grid-cols-3" : "sm:grid-cols-2 lg:grid-cols-4"}`}>
          {page.valueProps.map((vp) => (
            <div key={vp.title} className="rounded-lg border border-slate-200/80 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-slate-300 flex flex-col justify-between">
              <div>
                <div className={`mb-4 h-1 w-10 rounded-full ${t?.accentBg || "bg-slate-900"}`} />
                <h3 className="text-lg font-bold tracking-tight text-slate-900 leading-snug">{vp.title}</h3>
                <p className="mt-3 text-[14.5px] leading-relaxed text-slate-600">{vp.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. OPERATIONAL FEATURES LOG */}
      <section id="features" className="bg-slate-50 border-t border-b border-slate-100 py-16 sm:py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="max-w-2xl text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl mb-10">
            {page.meta.tagline}
          </h2>
          
          <div className="grid gap-6 sm:grid-cols-2">
            {page.features.map((f) => (
              <div key={f.title} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
                <div className={`mb-4 flex h-7 w-7 items-center justify-center rounded-md text-xs font-bold text-white ${t?.accentBg || "bg-slate-900"}`}>
                  ✓
                </div>
                <h3 className="font-bold text-slate-900 text-base">{f.title}</h3>
                <p className="mt-2 text-[14px] leading-relaxed text-slate-600">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. METRIC & SOCIAL PROOF BANNER */}
      <section className="mx-auto max-w-4xl px-6 py-16 text-center sm:py-24">
        <p className="text-3xl font-extrabold tracking-tight sm:text-4xl text-slate-900">
          {page.socialProof.statLine}
        </p>
        <p className="mt-4 text-sm font-mono uppercase tracking-widest text-slate-500">
          {page.socialProof.supportingLine}
        </p>
      </section>

      {/* 6. FINAL ENGAGEMENT HUB */}
      <section id="cta" className="bg-slate-50 border-t border-slate-100">
        <div className="mx-auto max-w-3xl px-6 py-16 text-center sm:py-24">
          <h2 className="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">{page.finalCta.headline}</h2>
          <p className="mx-auto mt-4 max-w-lg text-[15px] leading-relaxed text-slate-600">{page.finalCta.subtext}</p>
          
          {/* DYNAMIC IMPLEMENTATION: Deduplicated final conversion link */}
          <a
            href={formatOutboundLink(page.finalCta.ctaUrl)}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-block rounded-md bg-slate-900 px-10 py-4 text-sm font-mono font-bold text-white shadow-md hover:bg-slate-800 transition uppercase tracking-wider"
          >
            {page.finalCta.ctaLabel}
          </a>
        </div>
      </section>

      {/* 7. REFINED PROFESSIONAL FOOTER */}
      <footer className="border-t border-slate-100 px-6 py-8 text-center font-mono text-xs text-slate-400">
        {page.meta.companyName} · page generated by Hero Page Generator
      </footer>

    </div>
  );
}