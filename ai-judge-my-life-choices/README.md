# AI Judge My Life Choices

An AI courtroom for your decisions: a prosecutor and a defence agent argue a real choice you're weighing, witnesses get called when the case actually calls for one, and a judge delivers a structured verdict — score, reasoning, and (if you're guilty of self-sabotage) a sentence.

Built for Caarya's AI Track (WO-07).

**Live demo:** https://ai-judge-my-life-choices-git-main-krishiv-mangal-s-projects.vercel.app

## Stack

- **Frontend:** React + Vite, chat-style UI (bottom-pinned input, quick-action chips)
- **Backend:** Flask (Python), deployed as a Vercel serverless function — proxies every LLM call so the Groq API key never reaches the browser
- **LLM:** Groq (`openai/gpt-oss-120b` primary, `openai/gpt-oss-20b` fallback on refusal)

## How it works

1. **Decision intake** — you state a decision, optionally add context (timeline, alternatives, constraints).
2. **Fair multi-round trial** — no rushing to verdict:
   - A quick complexity check sets the round count upfront: 3–5 full rounds depending on how high-stakes the decision is.
   - Prosecutor and defence each open with a scene-setting statement, then alternate short (2–3 sentence) rounds, each directly responding to the previous turn.
   - Either side can independently decide the case calls for a witness — most don't; it's their call, not yours.
3. **Verdict** — the judge rules only after every round is in, weighing the full debate, and returns a specific `ruling` (the actual directive for this decision) as the headline, plus the scored breakdown and sentence described below.
4. **Transcript** — the full multi-round exchange, verdict, and round count, downloadable as Markdown. This is the sample-output artifact (see below).
5. **Resilience** — handles Groq's per-minute/per-day rate limits gracefully (live cooldown countdown, partial-verdict fallback instead of a hard crash), retries token-starved or guardrail-refused turns, and repairs truncated verdict JSON so the UI never shows a blank score.

## Scoring & sentencing

Implemented in `JUDGE_FINAL_PROMPT` (`src/agents/prompts.js`) and enforced again in `repairVerdict()` (`src/agents/trial.js`); the same logic is mirrored in `scripts/trial-node.js` for stress-test tooling.

**Four metrics** (each 0–25, scored after the full trial):

| Metric | What it measures |
|---|---|
| `risk_level` | How severe and likely the potential harm is |
| `reversibility` | How hard the decision is to undo once made |
| `resilience_under_scrutiny` | How well the decision held up under cross-examination |
| `alignment` | How well the decision fits the person's stated goals |

`risk_level` and `reversibility` describe **actual harm**. `resilience_under_scrutiny` and `alignment` describe **fit and rhetorical durability** — a decision can score well on those while still being genuinely dangerous.

**Total score:** `risk_level + reversibility + resilience_under_scrutiny + alignment` (0–100). A plain additive sum — on its own it has no guaranteed meaning, since a severe problem on one axis can get diluted into a comfortable total if the other three score well.

**Sum-based bands (first pass):**

| Score | Category |
|---|---|
| 75–100 | Sound Decision |
| 50–74 | Proceed With Caution |
| 25–49 | Reconsider |
| 0–24 | Guilty of Self-Sabotage |

**Critical-metric override (the actual fix):** applied after the sum-based band, using only `risk_level` and `reversibility` — the final category is whichever is *worse* for the decision:
- Either metric ≤4 (severe, likely, largely irreversible harm) → forced to **Guilty of Self-Sabotage**, regardless of total.
- Either metric ≤10 → capped at no better than **Reconsider**, regardless of total.

A good `alignment` or `resilience_under_scrutiny` score can never buy back a severe `risk_level` or `reversibility` problem. This is enforced twice, independently: in the prompt (so the model self-corrects) and as a hard guarantee in `repairVerdict()` (so it holds even if the model's output drifts).

**Sentencing:** the sentence block (`terms`, `probation_period`, `review_condition`) is gated purely on `verdict_category === 'Guilty of Self-Sabotage'`. The override is also what guarantees sentencing fires for a *diluted-total* case — severe risk hidden behind a good sum — not just a plain-low-sum one.

**Known limitation:** stress-test data collected so far (4 completed trials before hitting the Groq daily token cap) never actually forced the override to fire — the model's own scoring stayed internally consistent (all four metrics low together, or all fine together) rather than producing the diluted pattern the override defends against. The override is a correctness guarantee for a failure mode that hasn't yet been observed in practice; confirming it fires needs a case designed so `alignment`/`resilience_under_scrutiny` have a legitimate reason to score high while `risk_level`/`reversibility` stay severe (e.g. a decision that matches a stated goal and has a track record, but is still objectively risky and hard to undo).

## Setup

**Prerequisites:** Node.js 18+, Python 3.10+, a [Groq API key](https://console.groq.com).

```bash
git clone https://github.com/Krishiv-Mangal/ai-judge-my-life-choices.git
cd ai-judge-my-life-choices

# Frontend
npm install

# Backend
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root:

```bash
# Backend (Flask, read server-side only — never exposed to the browser)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Frontend (local dev only — Vite and Flask run on different ports locally;
# in production on Vercel they share an origin, so leave this unset there)
VITE_BACKEND_URL=http://localhost:5000
```

## How to run (local dev)

You need both the Flask backend and the Vite frontend running:

```bash
# Terminal 1 — backend
python api/index.py
# or: flask --app api/index run --port 5000

# Terminal 2 — frontend
npm run dev
```

Open the Vite dev URL (typically `http://localhost:5173`).

## Deploying

Deployed on Vercel using `vercel.json`, which routes `/api/*` to the Flask function and everything else to the static Vite build. Set `GROQ_API_KEY` and `GROQ_MODEL` as environment variables in the Vercel project settings — `VITE_BACKEND_URL` should be left unset in production.

## Sample input/output

**Input**
- Decision: *"Should I quit my stable job to freelance full-time with no savings cushion?"*
- Context: *"I have 3 months of expenses saved, no clients lined up yet, and my current job pays well but I'm burned out."*

**Output (abridged trial transcript):**
## Ruling: Do not quit your job until you secure at least three months of guaranteed freelance income
Category: Reconsider — Score: 30/100
_The judge's overall read on this decision, using the full courtroom trial as its investigation method — not a standalone moral judgment._
**Decision Facts** _(true regardless of how well anyone argued it)_
- Risk Level: 5/25 — Three months cushion insufficient for income gap and debt risk
- Reversibility: 5/25 — Job loss creates lasting credit and career setbacks

**Courtroom Findings** _(only knowable by testing the case in the trial)_
- Resilience Under Scrutiny: 8/25 — Stress‑relief claim collapses without reliable cash flow
- Alignment with Goals: 12/25 — Burnout aligns but financial reality conflicts with goals

Evidence shows income is speculative and expenses exceed savings, making the transition financially unsafe despite burnout concerns.

**Recommendation:** Build a three‑month client pipeline with signed contracts before leaving

> "Financial safety outweighs fleeting freedom." holds, but "no clients yet" undercuts the readiness claim
> *"The court isn't against the leap — it's against jumping blind."*


The full transcript (every prosecutor/defence/witness turn, not just the verdict) is generated per-run and downloadable as Markdown from the app itself via the "Download transcript" action. 
## Project structure

```
src/
  App.jsx               # Chat UI, phases (intake -> context -> trial -> verdict)
  agents/
    trial.js            # Trial orchestration: rounds, witnesses, verdict repair
    prompts.js           # System prompts for prosecutor, defence, judge, witness
    transcript.js         # Builds + renders the downloadable transcript
  lib/
    groq.js              # Frontend API client, quota tracking
    caseHistory.js        # LocalStorage-backed case history
  components/
    IntroSketch.jsx       # Landing page
    HistoryPanel.jsx      # Past-case sidebar
api/
  index.py               # Flask backend - proxies Groq calls, keeps key server-side
```

## Status

- [x] Decision intake
- [x] Prosecutor + defence agents (multi-round, witness-capable)
- [x] Judge + orchestration
- [x] Verdict generator (score, category, sentencing)
- [x] Deployed on Vercel
- [x] Witness generation
- [x] Sentencing system
- [ ] Multiple judge personalities
- [ ] Shareable trial card

---


