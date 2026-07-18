# Proof Builder Agent

Built for Caarya work order **WO-12**. Feed in one piece of completed student
activity; get back seven ready-to-use proof artifacts: a resume bullet, a
LinkedIn post, a portfolio card, a proof summary, a skill evidence breakdown,
a recruiter-facing description, and a next-improvement suggestion — each
meant to be publishable as-is.

## Why it's built this way

The hard part of this build isn't generating seven formats — any LLM call
can do that. The hard part is keeping all seven honest to the *same*
underlying activity, with zero inflation, while each one is still genuinely
good on its own. Two design choices exist specifically to solve that:

1. **A facts ledger sits between the raw input and every generator.**
   `proof_builder/intake.py` makes one LLM call that reduces the student's
   free-text description into a small structured JSON object — what was
   done, what tools/skills were used, the context, and an outcome *only if
   one was actually stated*. Every one of the seven outputs is generated
   from this ledger, never from the raw text. An LLM asked to write a punchy
   LinkedIn post from loose prose will reach for color it can't justify; an
   LLM asked to write the same post from five pre-extracted facts has much
   less room to embellish, and all seven outputs end up reading from the
   same source of truth instead of independently inventing their own spin.

2. **Every generator prompt repeats the same non-negotiable grounding
   rules** (`proof_builder/generators/_shared.py`): no numbers, outcomes, or
   tools beyond what's in the ledger; no upgrading soft language into a
   stronger claim; if a field is null, write around the gap instead of
   filling it in. A `is_thin` flag on sparse activities tells every
   generator to stay conservative rather than padding to sound impressive.

## Project structure

```
proof-builder-agent/
├── app.py                          Streamlit UI
├── proof_builder/
│   ├── llm.py                      Groq client wrapper (retries on rate limits)
│   ├── intake.py                   raw text -> facts ledger
│   ├── pipeline.py                 orchestrates intake + all 4 generator modules
│   ├── pdf_export.py               renders the seven artifacts to a PDF
│   └── generators/
│       ├── _shared.py              shared grounding rules + JSON-call helper
│       ├── public_proof.py         resume bullet + LinkedIn post
│       ├── presentation.py         portfolio card + proof summary
│       ├── evaluator.py            skill evidence breakdown + recruiter description
│       └── improvement.py          next-improvement suggestion
├── data/sample_activities.json     3 sample activities for testing/submission
├── scripts/generate_samples.py     runs all 3 samples end to end, saves results
├── sample_outputs/                 output of generate_samples.py lands here
├── requirements.txt
└── .env.example
```

Five LLM calls per activity (1 facts extraction + 4 generator calls, each
producing two of the seven outputs together so they read as a matched
set) — comfortably inside Groq's free-tier 30 requests/minute limit.

## Setup

1. **Get a free Groq API key.** Go to `console.groq.com`, sign up (no
   credit card), and create a key under API Keys. Full walkthrough in
   `Groq_API_Guide_Caarya_Interns.docx`.

2. **Install dependencies** (Python 3.9+):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your key.** Copy `.env.example` to `.env` and fill it in:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   Opens at `http://localhost:8501`. Pick a sample activity or write your
   own, click **Generate proof**, and all seven outputs appear in tabs.

## Generating the 3 required sample runs

The work order requires at least three activities run end to end through
all seven outputs. With your `.env` set up:

```bash
python scripts/generate_samples.py
```

This runs the three activities in `data/sample_activities.json` through the
full pipeline and writes one JSON file per activity to `sample_outputs/`
(facts ledger + all seven artifacts). Edit `data/sample_activities.json` to
swap in your own activities if you'd rather submit those instead.

## Configuration

| Env var | Default | Notes |
|---|---|---|
| `GROQ_API_KEY` | — | required |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | switch to `llama-3.1-8b-instant` if you hit rate limits often — it has higher daily limits per the Groq guide |

## Deploying a hosted demo

The submission needs a working demo reachable without your help. Easiest
path with this stack:

1. Push this repo to your own GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo,
   point it at `app.py`.
3. Add `GROQ_API_KEY` under the app's *Secrets* (not in the repo — `.env` is
   gitignored on purpose; never commit a key).
4. Deploy. You'll get a public `*.streamlit.app` URL to share.

## Notes on accuracy by design

- If an activity description is too thin to extract real detail from, the
  agent flags it (`is_thin`) and the UI shows a notice — outputs are kept
  conservative instead of being padded with generic enthusiasm.
- The skill evidence breakdown only lists skills tied to a specific action
  or tool actually present in the ledger — it won't infer soft skills like
  "leadership" unless the input supports it.
- None of the seven generators ever see the raw input text directly — only
  the extracted ledger — which is what keeps them from drifting apart.

## What's not in this build

Per the work order, this covers the five required backbone moves (activity
intake, public-proof outputs, presentation outputs, evaluator-facing
outputs, improvement + packaging), plus one optional move: **PDF export** of
the full set of seven artifacts (`proof_builder/pdf_export.py`, offered as a
download button in the UI next to the Markdown export). The remaining optional
moves — a LinkedIn tone selector, a running portfolio aggregator, and an
automated consistency self-check pass — are not implemented here and would be
natural next additions.
