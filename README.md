# Placement Panic Meter

A CS-placement readiness scoring agent. A student answers a set of questions
across 8 categories, gets a 0-100 readiness score, an honest breakdown of
where they stand, and a prioritized, specific action plan — not a vague
"work harder" verdict.

## How scoring works

The rubric splits 100 points across 8 categories. Roughly 63 of those points
are computed by **plain deterministic code** (counts, checklists, known
right/wrong answers) — the same input always produces the same score.
The remaining ~37 points come from **LLM-rubric grading via the Groq API**,
used only where a real judgment call is unavoidable (project quality,
DSA free-text explanations, written communication, behavioral answers) —
and even there, the model only classifies/scores against a fixed rubric;
it never invents the point value directly, our own code does that math.

| Category | Points | Method |
|---|---|---|
| DSA & Problem Solving | 21 | Hybrid — self-report (11) + LLM-graded conceptual quiz (10) |
| CS Fundamentals | 17 | Deterministic — topic self-assessment checklist |
| Experience & Certifications | 12 | Deterministic — internship/certification checklist |
| Projects | 15 | Hybrid — checklist (6) + LLM-graded novelty/complexity (9) |
| Resume | 10 | Deterministic — checklist |
| Coding Speed | 10 | Deterministic — behavior-anchored self-report |
| Explanation Clarity | 10 | LLM-graded — written technical explanation |
| Aptitude | 3 | Deterministic — sampled puzzles, known answers |
| HR/Behavioral | 2 | LLM-graded — sampled behavioral questions |

An optional **company-type multiplier** (Service/Product/Quant/AI-ML/Data)
can re-weight the same category scores for a second, opt-in "fit" view —
it never changes the base score.

A **time-remaining / year "urgency" layer** sits alongside the score, not
inside it — the same 60/100 reads differently with 5 months left versus
3 weeks left, so urgency reshapes the framing and action-plan pacing
without pretending a student became more or less prepared.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set your Groq API key. Either export it directly:

```bash
export GROQ_API_KEY="your-key-here"          # Windows: set GROQ_API_KEY=your-key-here
export FLASK_SECRET_KEY="something-random"
```

...or copy `.env.example` to `.env` and fill in your real values — the app
loads it automatically on startup via `python-dotenv`. `.env` is already
gitignored, so it's the safer option if you're pushing this repo to GitHub:

```bash
cp .env.example .env
# then edit .env with your real GROQ_API_KEY
```

Run it:

```bash
python -m app.main
```

Then open `http://127.0.0.1:5000`.

**No Groq key set?** The app still runs — the four LLM-graded categories
fall back to a flagged neutral default (half credit, clearly marked
"LLM grading unavailable") instead of crashing, so you always get a
complete result end to end. Set the key and re-run for the real score.

## Project structure

```
app/
├── main.py                  # Flask routes: GET / (intake), POST /submit (score + results)
├── aggregator.py             # Orchestrates every scorer into one final result
├── action_plan.py            # Turns gap flags into a prioritized, specific action plan
├── scoring/
│   ├── config.py              # The single source of truth for all weights (asserts they sum to 100)
│   └── deterministic.py       # The 6 no-LLM scoring functions
├── llm/
│   ├── client.py               # Shared Groq API wrapper (structured JSON output, retries)
│   ├── schemas.py               # JSON schemas for all 4 LLM graders (fraction-based, not raw points)
│   ├── dsa_grader.py             # Grades free-text DSA conceptual answers
│   ├── project_grader.py         # Grades project novelty/complexity from a description
│   ├── explanation_grader.py     # Grades written technical explanation clarity
│   └── hr_grader.py              # Grades HR/behavioral answers
├── data/
│   ├── aptitude_bank.py        # 8 aptitude puzzles, known answers
│   ├── dsa_question_bank.py    # 10 original conceptual DSA questions, pattern-tagged
│   └── hr_question_pool.py     # 22 well-known behavioral interview questions
├── static/style.css
└── templates/
    ├── intake.html
    └── results.html
```

## Testing

No real API key needed for these — they use mocked Groq responses or
exercise the deterministic-only path:

```bash
python -m app.scoring.test_deterministic     # sanity-checks the 6 deterministic scorers
python -m app.llm.test_graders_mocked        # verifies grader point-conversion math with mocked responses
python -m app.test_action_plan               # verifies gap-flag -> advice mapping and priority sorting
python -m app.test_e2e                       # full GET/POST cycle through Flask's test client
```

Once you have a real `GROQ_API_KEY` set, it's worth manually running one
grader for real before trusting the full flow — e.g.:

```bash
python -c "from app.llm.dsa_grader import grade_dsa_answer; print(grade_dsa_answer('dsa_q001', 'two pointers, O(n)'))"
```

## Known limitations (read before treating the score as gospel)

- **"Deterministic" describes the math, not the input.** DSA problem counts,
  resume checklist items, and coding-speed answers are self-reported, not
  verified. A student can overstate them. Pulling a real LeetCode profile
  via API would close this gap for DSA specifically, if extended later.
- **CS Fundamentals is self-rated confidence**, not tested knowledge — people
  are often miscalibrated about what they actually know. Real right/wrong
  knowledge checks (like Aptitude) would be a stronger signal if built out.
- **HR/Behavioral is a thin 2-point category** relative to the LLM grading
  engineering behind it — it's included for completeness and to surface
  useful advice, but shouldn't be expected to meaningfully move a student's
  overall band on its own.
- **DSA remains the heaviest category (21 pts)**, which optimizes this tool
  for product/DSA-heavy placement tracks. Students targeting service-based
  or non-DSA-heavy roles may be undersold by the base score — the optional
  company-type multiplier partially corrects for this, but only if the
  student opts into it.
- **Explanation Clarity measures written technical explanation, not verbal
  communication.** A text-based intake can't honestly assess live interview
  delivery, tone, or confidence — this is a deliberate, named scope
  limitation, not an oversight.
- **LLM grading is calibrated but not perfectly deterministic.** The same
  answer graded twice may drift slightly (Groq does not guarantee determinism
  even with a fixed seed). The categorical/dimension-based grading design
  keeps this drift small, but it's not zero.

## Optional extensions (not built, noted for future work)

- Shareable result card
- Common-gaps pattern log across students
- Re-check flow to compare scores over time
- Year-specific factor weight tuning
