"""Improvement suggestion: the seventh and final artifact.

A specific, actionable "next improvement" — per the work order's grading
bar, this needs to point at one concrete thing the student could genuinely
do next, not a generic "keep up the great work!" platitude.
"""

from ..intake import facts_for_prompt
from ._shared import generate_json

SYSTEM_ROLE = (
    "You are a constructive technical mentor. You read a student's completed activity and suggest "
    "exactly one concrete, achievable next step that would meaningfully extend or strengthen it."
)

TASK_INSTRUCTIONS = """Produce one output from the facts ledger:

improvement_suggestion: ONE specific, actionable suggestion (roughly 25-50 words) for what the
student could genuinely do next to extend or strengthen this piece of work. It must:
- Point at one concrete thing, not a vague list ("could improve testing, documentation, and...").
- Follow naturally from what's actually in the ledger (e.g. a "challenges" entry, a gap in
  "tools_and_skills", or a natural next step implied by "actions") — do not invent unrelated advice.
- Be something the student could plausibly act on, not abstract praise or generic encouragement.

Return STRICT JSON: {"improvement_suggestion": "..."}"""


def generate(facts: dict) -> dict:
    facts_block = facts_for_prompt(facts)
    result = generate_json(
        SYSTEM_ROLE,
        TASK_INSTRUCTIONS,
        facts_block,
        is_thin=facts.get("is_thin", False),
        temperature=0.5,
        max_tokens=250,
    )
    return {"improvement_suggestion": result.get("improvement_suggestion", "").strip()}
