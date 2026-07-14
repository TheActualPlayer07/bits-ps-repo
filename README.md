# Hero Page Generator

Feed it a company URL. It researches the company, works out its actual
positioning, writes Ogilvy-grade copy, and hands back a complete, responsive,
**rendered** landing page — not a text dump.

Built for the Caarya WO-16 brief.

## How it works

```
URL  ─▶  Research  ─▶  Positioning  ─▶  Copywriting  ─▶  Rendered page
         (site +        (a point of      (draft +
         outside          view, not       self-critique
         context)         a fact list)    pass)
```

| Stage | File | What it leaves behind |
|---|---|---|
| Research | `lib/pipeline/research.ts` | A `ResearchData` record — grounded facts only, no invention |
| Positioning | `lib/pipeline/positioning.ts` | A `PositioningBrief` — a defensible point of view |
| Copywriting | `lib/pipeline/copywriting.ts` | A `PageContent` object, drafted then self-critiqued against house style |
| Page generation | `components/GeneratedPage.tsx` | The actual rendered page — hero, value props, features, social proof, CTA |
| Orchestration | `app/api/generate/route.ts` | Wires the three stages together behind one API call |

The self-critique pass (an optional move in the brief) is folded into the
default pipeline: every draft gets a second Gemini pass that hunts down and
rewrites anything that reads like generic filler, before the page ever
renders.

There's no database. A generated page's full content is packed into the
`/preview?data=...` URL itself (base64), so every generated page is a real,
shareable, self-contained link with zero backend storage to manage.

## Setup

Requires Node.js 18.18+ and a Gemini API key.

```bash
git clone <this-repo>
cd hero-page-generator
npm install
cp .env.example .env.local
```


```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=your_model_name
USE_SEARCH_GROUNDING=true
```

Then run it:

```bash
npm run dev
```

Open http://localhost:3000, paste a company URL, and generate a page.

### Environment variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | — | From Google AI Studio, free tier |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Swap to a stronger model if you have access and want higher copy quality |
| `USE_SEARCH_GROUNDING` | No | `true` | Set `false` if you hit free-tier quota limits — research falls back to the company's own site only |

## Sample input → output

**Input:** `https://stripe.com`

**Output:** a rendered page with a themed hero section, 3–4 value
propositions, a features grid, a grounded social-proof line, and a final
call to action — plus a "Behind this page" panel showing the research and
positioning that produced it. Try it yourself and drop a screenshot/GIF of
your own generated page here before submitting.

## Deploying

This is a stock Next.js app, so it deploys to **Vercel** with no extra
config:

1. Push this repo to GitHub.
2. Import it at https://vercel.com/new.
3. Add `GEMINI_API_KEY` (and optionally `GEMINI_MODEL`, `USE_SEARCH_GROUNDING`) as environment variables in the Vercel project settings.
4. Deploy. Vercel gives you a public URL — that's your demo link.

## Project structure

```
app/
  page.tsx              home page — URL input + pipeline ticker
  preview/page.tsx       renders a generated page (from session or a shared link)
  api/generate/route.ts  orchestrates the pipeline
components/
  GeneratedPage.tsx      the actual landing page template
  PipelineTicker.tsx     progress UI while generating
  BehindThePage.tsx      research/positioning transparency panel
lib/
  types.ts               zod schemas + matching JSON schemas for Gemini
  gemini.ts              Gemini client + structured-output helper
  theme.ts               the six accent palettes a page can render in
  share.ts               encode/decode page content into a shareable URL
  pipeline/
    research.ts
    positioning.ts
    copywriting.ts
```

