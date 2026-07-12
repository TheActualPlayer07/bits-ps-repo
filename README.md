# HIVE — Company Research Agent

HIVE takes a **company name** and produces a structured, sourced intelligence profile:
industry, size, and location; funding history, products, and recent news; why the
company is worth a student's attention; and a real contact with a realistic way to
reach them. It's built as a five-stage pipeline, and every factual claim it makes is
grounded in a live web search result — if a fact isn't in the search results, the field
is left empty rather than guessed.

## How it works

1. **Intake** — normalizes and validates the company name.
2. **Discovery** — searches for core facts (industry, description, size, location),
   each with a source URL.
3. **Enrichment** — a deeper, more targeted search for funding history, products, and
   recent news.
4. **Relevance + Contact** — reasons over what's already been gathered to explain why
   the company matters to a student, and searches for a real, reachable contact.
5. **Completeness check** — an honest two-layer verdict, not a single self-graded LLM
   call: a deterministic pass checks every field is genuinely filled in, and a
   separate, skeptical LLM pass flags subtler problems (vague descriptions, stale news,
   a contact that isn't actually reachable). The two are merged in plain Python — the
   LLM never gets to declare its own output complete.

**The core technique, every stage that makes a factual claim:** search the web, hand
the results to the LLM, and instruct it to answer only from those results, returning
structured (schema-validated) data. The model structures what was retrieved — it never
invents a fact that isn't grounded in a real source.

## Tech stack

- **Python**
- **Google Gemini API** — structured/JSON output mode
- **Tavily** — a web search API built for AI agents
- **Pydantic** — schema definition and validation
- **Streamlit** — the UI

## Setup

1. Clone the repo and `cd` into it.
2. Create and activate a virtual environment:
   ```
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your own API keys:
   ```
   cp .env.example .env
   ```

   | Variable | Where to get it |
   |---|---|
   | `TAVILY_API_KEY` | [tavily.com](https://tavily.com) — free tier available |
   | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) — free tier available |

## Running it

**Streamlit UI** (recommended):
```
streamlit run app.py
```
Then open the URL it prints (usually `http://localhost:8501`) and enter a company name.

**Command line**, for a raw JSON profile:
```
cd src
python -m hive.pipeline "Company Name"
```

## Project structure

```
HIVE/
├── app.py                    # Streamlit UI entry point
├── requirements.txt
├── .env.example               # template listing the required API keys
└── src/hive/
    ├── schema.py              # CompanyProfile and every sub-model (Pydantic)
    ├── clients.py             # shared Tavily/Gemini client + result-formatting helpers
    ├── pipeline.py            # run_pipeline() orchestrator
    └── stages/
        ├── intake.py
        ├── discovery.py
        ├── enrichment.py
        ├── relevance_contact.py
        └── completeness.py
```

## Sample profiles

Three fully researched example profiles (real pipeline output, unedited):

- [Notion](samples/notion.json) — SaaS / productivity software
- [Zerodha](samples/zerodha.json) — Indian fintech / stock broking
- [Stripe](samples/stripe.json) — global payments infrastructure

## Error handling

A failure in any single stage (a rate limit, a network error) is caught and doesn't
crash the run — the affected fields are simply left empty, and the completeness check
honestly flags them as missing, along with a note on what failed and why. Invalid input
(an empty or clearly-not-a-company-name string) fails fast instead, since retrying the
same input wouldn't help.

## Live demo

**[hive-research-agent.streamlit.app](https://hive-research-agent.streamlit.app/)**

## Walkthrough video

**(coming soon)**
