"""Evaluator-facing outputs: skill evidence breakdown + recruiter description.

These are written for someone evaluating the student — what the work
actually demonstrates, in language a recruiter would take seriously. The
work order specifically calls out that these need to be "genuinely
recruiter-ready", not a vague summary.
"""

from ..intake import facts_for_prompt
from ._shared import generate_json

SYSTEM_ROLE = (
    "You are a technical recruiter-facing writing assistant. You translate a student's verified "
    "activity facts into language a recruiter or hiring manager would find credible and specific. "
    "You never inflate scope or seniority beyond what the facts support."
)

TASK_INSTRUCTIONS = """Produce two outputs from the facts ledger:

1. skill_evidence: a list of skill-evidence pairs, each grounded in a specific action or tool from
   the ledger. Format as a list of objects:
   [{"skill": "...", "evidence": "..."}, ...]
   - Only include skills that are directly supported by "tools_and_skills" or "actions" — do not
     infer soft skills (e.g. "leadership", "communication") unless "collaboration" or "actions"
     actually supports it.
   - "evidence" should cite the specific action that demonstrates the skill, not a generic claim.
   - Produce between 2 and 5 pairs depending on how much the ledger actually supports.

2. recruiter_description: a short paragraph (roughly 50-90 words) written as if briefing a
   recruiter on why this piece of work is relevant evidence of capability. Specific and credible —
   name the concrete actions and tools, frame the context, and state the outcome ONLY if "outcome"
   is non-null. Avoid generic praise ("great team player", "highly motivated") with nothing under it.

Return STRICT JSON: {"skill_evidence": [{"skill": "...", "evidence": "..."}], "recruiter_description": "..."}"""


def generate(facts: dict) -> dict:
    facts_block = facts_for_prompt(facts)
    result = generate_json(
        SYSTEM_ROLE,
        TASK_INSTRUCTIONS,
        facts_block,
        is_thin=facts.get("is_thin", False),
        temperature=0.4,
        max_tokens=650,
    )
    return {
        "skill_evidence": result.get("skill_evidence", []),
        "recruiter_description": result.get("recruiter_description", "").strip(),
    }
