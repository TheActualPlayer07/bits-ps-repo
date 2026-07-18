# Resume to Portfolio Agent

Upload a resume (PDF or DOCX), pick a visual theme, and get back a complete, responsive portfolio website — generated from the resume's content, not just a reformatted copy of it.

**Live demo:** [resume-to-portfolio-ht4q.onrender.com](https://resume-to-portfolio-ht4q.onrender.com)

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running It](#running-it)
- [Sample Input / Output](#sample-input--output)
- [Themes](#themes)
- [Design Notes](#design-notes)

---

## Overview

Resume to Portfolio Agent takes a raw resume file and turns it into a polished, shareable personal website in under a minute. Rather than just re-skinning the resume text, it uses an LLM to structure the content and expand thin bullet points into real narrative — while staying strictly grounded in facts the resume actually contains.

## How It Works

| Step | Module | Description |
|------|--------|-------------|
| 1. Parse | `core/parser.py` | Extracts raw text from the uploaded PDF or DOCX. |
| 2. Generate | `core/generator.py` | Sends the parsed text to Gemini, which structures it into a `PortfolioProfile` (name, headline, bio, experience, projects, education, certifications, volunteer work, skills), expanding thin bullets into real narrative without inventing unstated facts. |
| 3. Render | `core/renderer.py` | Converts the structured profile into a full responsive HTML page, styled per the selected theme (`aurora`, `terminal`, `sunset`, or `studio`). |
| 4. Share | `core/storage.py` | Persists the chosen profile and theme in Postgres under a stable slug, so the generated site stays live at a permanent link (`/p/{slug}`) instead of expiring with the session. |

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Parsing:** pdfplumber, python-docx
- **AI Generation:** Google Gemini (`google-genai`), with a fallback model chain
- **Validation:** Pydantic
- **Persistence:** PostgreSQL (`psycopg2-binary`)
- **Frontend:** Server-rendered HTML/CSS (Jinja templates)

## Project Structure

```
main.py                 FastAPI app: upload page, parsing, rendering, and shareable-link routes
core/parser.py          PDF/DOCX text extraction
core/schema.py          Pydantic schema the LLM output is forced into
core/generator.py       Gemini call: raw text -> structured PortfolioProfile
core/renderer.py        Structured profile -> full HTML page (4 themes)
core/storage.py         Postgres-backed persistence for shareable portfolio links
templates/index.html    Upload page / theme picker UI
samples/                Sample resume and generated output for local testing
```

## Setup

**Requirements:** Python 3.10+, a Postgres database (a free instance from [Neon](https://neon.tech) or [Supabase](https://supabase.com) works).

```bash
git clone git@github.com:shaurya-manjkhola/resume-to-portfolio.git
cd resume-to-portfolio
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=your_postgres_connection_string_here
```

- Get a Gemini key from [Google AI Studio](https://aistudio.google.com/apikey).
- `DATABASE_URL` is the connection string from your Postgres provider, including `sslmode=require`.
- The `portfolios` table is created automatically on startup if it doesn't already exist.

## Running It

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000**, pick a theme, and upload a resume (`.pdf` or `.docx`). Preview every theme against the same parsed data, then finalize one to get a permanent shareable link at `/p/{slug}`.

## Sample Input / Output

- Sample input resume: `samples/test_resume.pdf`
- Sample generated output: `samples/sample_output.html`

## Themes

| Theme | Style |
|-------|-------|
| **Aurora** | Dark, gradient |
| **Terminal** | Dark, monospace |
| **Sunset** | Light, warm / editorial |
| **Studio** | Light, muted / serif |

## Design Notes

- If a resume has no education section, education is omitted from the generated site rather than shown empty. The same applies to certifications and volunteer work.
- Generation runs Gemini with a fallback chain (`gemini-2.5-flash` → `gemini-1.5-flash` → `gemini-1.5-pro`) in case a model is unavailable.
- Shareable links are stable across restarts and deploys — the profile and theme are stored in Postgres, not on local disk.
- If two people share a name, the slug gets a random numeric suffix on collision rather than overwriting the earlier link.