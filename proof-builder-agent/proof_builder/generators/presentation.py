"""Presentation outputs: portfolio card + proof summary.

These are the two presentation-facing artifacts — they need to show the
work itself, not just summarize it in a single line like the resume bullet
or LinkedIn post do.
"""

from ..intake import facts_for_prompt
from ._shared import generate_json

SYSTEM_ROLE = (
    "You are a portfolio-writing assistant that turns a student's verified activity facts into "
    "presentation-ready material for a personal portfolio site. You favor concrete description "
    "over hype, and you let the work speak for itself."
)

TASK_INSTRUCTIONS = """Produce two outputs from the facts ledger:

1. portfolio_card: a structured card for a portfolio grid, as an object:
   {"headline": "...", "description": "...", "tags": ["...", "..."]}
   - headline: short title for the card, <=10 words, descriptive not clickbait.
   - description: 2-3 sentences covering what was built/done and how (drawing on "actions" and
     "tools_and_skills"), written for someone skimming a portfolio.
   - tags: 3-6 short tags drawn from "tools_and_skills" and "context" — no invented skills.

2. proof_summary: a fuller paragraph (roughly 60-110 words) that walks through the activity in
   more depth than the portfolio card — what the situation was ("context"), what was actually
   done ("actions", "what_was_done"), and the result ONLY if "outcome" is non-null. This is the
   artifact someone reads when they want the real story, not just the headline.

Return STRICT JSON: {"portfolio_card": {"headline": "...", "description": "...", "tags": [...]}, "proof_summary": "..."}"""


def generate(facts: dict) -> dict:
    facts_block = facts_for_prompt(facts)
    result = generate_json(
        SYSTEM_ROLE,
        TASK_INSTRUCTIONS,
        facts_block,
        is_thin=facts.get("is_thin", False),
        temperature=0.5,
        max_tokens=650,
    )
    card = result.get("portfolio_card") or {}
    return {
        "portfolio_card": {
            "headline": card.get("headline", "").strip(),
            "description": card.get("description", "").strip(),
            "tags": card.get("tags", []),
        },
        "proof_summary": result.get("proof_summary", "").strip(),
    }
