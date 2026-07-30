# AI Roast My Code

A code-review agent with a two-stage LLM pipeline and two switchable reviewer
personas (Vex and Sage), built against the "AI Roast My Code" work order.
Paste code, pick a language, get scored on **quality**, **readability**, and
**maintainability**, plus a persona-narrated review of the same underlying
findings.

## How it works

1. **Static metrics** (`lib/metrics.ts`) — language-aware heuristic pass over
   the submission: comment ratio, function count, nesting depth, an
   approximate cyclomatic complexity, and a comment/whitespace-stripped
   version of the code. This isn't a full AST parser (that would need a
   different toolchain per language), but it serves the same purpose the
   work order asks for: give the model hard numbers instead of asking it to
   eyeball everything, and cut the tokens it has to read.
2. **Stage 1 — scoring** (`app/api/review/route.ts` → `SCORING_MODEL`) — one
   call to Claude with the code + metrics, instructed to return **strict
   JSON**: three dimension scores with rationale, an overall score,
   strengths, weaknesses, and line-referenced issues. Temperature is low
   (0.2) so identical input gets identical scores run to run.
3. **Stage 2 — persona narration** (`PERSONA_MODEL`) — the stage-1 JSON (not
   the raw code) is handed to two persona prompts in parallel. Each persona
   narrates the *same* scores and findings in its own voice; neither is
   allowed to re-score or invent problems. This is what keeps Vex and Sage
   from disagreeing on the facts while still sounding like different
   reviewers.
4. **Guards** (`lib/guards.ts`) — a content-hash cache (identical code +
   language skips both LLM calls and returns the prior verdict) and a
   per-IP token-bucket rate limiter.
5. **Retries** (`lib/anthropic.ts`) — exponential backoff with jitter on 429s
   and 5xxs from the Anthropic API, since that's the actual failure mode
   under back-to-back submissions.

## Honest caveats

- **No `temperature` is sent on any call.** Claude Sonnet 5 (and Opus 4.7+)
  reject non-default `temperature`/`top_p`/`top_k` with a 400 error — they
  use adaptive thinking instead of manual sampling control. Earlier models
  like Haiku 4.5 still accept it, but sending it at all becomes a landmine
  the moment `SCORING_MODEL` or `PERSONA_MODEL` gets pointed at a newer
  model, so the client omits it everywhere. Score consistency and persona
  voice variety are both driven entirely by the system prompts now, not by
  temperature — see `SCORING_SYSTEM_PROMPT` and each persona's prompt in
  `lib/personas.ts` if you want to tune either.

- **The cache and rate limiter are best-effort, not distributed.** They live
  in a module-level `Map`, which only persists for the life of one warm
  serverless instance. Vercel can spin up multiple instances under real
  concurrent load, each with its own `Map` — so this dedupes within a
  session and takes the edge off a single instance's burst, but it is
  **not** a hard guarantee across all traffic. For that, swap `lib/guards.ts`
  for [Vercel KV](https://vercel.com/docs/storage/vercel-kv) or
  [Upstash Redis](https://upstash.com/) — the function signatures
  (`getCached`/`setCached`/`checkRateLimit`) are designed so the call sites
  in `route.ts` don't need to change.
- **The static analysis is heuristic, not a real parser.** Nesting depth,
  function counts, and complexity are computed with regex/bracket-counting
  per language family, not a proper AST. It's accurate enough to be useful
  evidence for the scoring prompt, but a determined adversarial input
  (e.g. brackets inside a string literal) could throw individual metrics off.
- **Two API calls minimum per submission, four on a cache miss** (1 scoring +
  2 persona, run in parallel) — cost and latency scale with that, which is
  why scoring defaults to the cheaper Haiku model and only persona narration
  uses Sonnet.

## Setup

```bash
npm install
cp .env.example .env.local
# edit .env.local and set ANTHROPIC_API_KEY
npm run dev
```

Open http://localhost:3000.

### Environment variables

| Variable         | Required | Default                        |
|------------------|----------|---------------------------------|
| `ANTHROPIC_API_KEY` | Yes   | —                               |
| `SCORING_MODEL`  | No       | `claude-haiku-4-5-20251001`     |
| `PERSONA_MODEL`  | No       | `claude-sonnet-5`               |

## Deploy to Vercel

1. Push this repo to GitHub.
2. In Vercel: **New Project → Import** the repo. Framework preset
   auto-detects as Next.js — no build config changes needed.
3. In **Project Settings → Environment Variables**, add `ANTHROPIC_API_KEY`
   (and `SCORING_MODEL` / `PERSONA_MODEL` if you want non-default models).
   **Add the key in the Vercel dashboard, not in a committed file** — nothing
   in this repo should ever contain the real key.
4. Deploy. The API route runs as a Node.js serverless function
   (`export const runtime = "nodejs"` in `route.ts`), with `maxDuration = 60`
   seconds to give the two-stage pipeline room to finish.

## Sample input/output

Paste this into the editor with language set to Python:

```python
def process(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            if data[i] > 0:
                result.append(data[i] * 2)
    return result
```

Expect: a maintainability ding for the nested conditionals and manual
index loop, a readability note on `!= None` vs `is not None`, and both
personas agreeing on those exact points while sounding nothing alike.

## Project structure

```
app/
  layout.tsx          Root layout, fonts
  page.tsx             Landing page shell
  globals.css
  api/review/route.ts  The pipeline: metrics -> scoring -> personas
components/
  ReviewApp.tsx        Submission form + state machine
  ScoreTicket.tsx       Score display (the "ticket")
  PersonaPass.tsx       Persona toggle + narration display
lib/
  metrics.ts           Static analysis
  anthropic.ts         API client + retry logic
  personas.ts          Persona system prompts + scoring rubric
  guards.ts            Cache + rate limiter
  types.ts
```
