"""Public-proof outputs: resume bullet + LinkedIn post.

These are the two shortest, most shareable artifacts. The bar (per the work
order) is that they must be genuinely well-written and accurate, not
templated phrasing with the activity name dropped in.
"""

from ..intake import facts_for_prompt
from ._shared import generate_json

SYSTEM_ROLE = (
    "You are a careers writing assistant that turns a student's verified activity facts into "
    "short, sharp, publish-ready proof-of-work content. You write like a strong human writer, "
    "not a template — vary structure, avoid clichés, and never pad."
)

TASK_INSTRUCTIONS = """Produce two outputs from the facts ledger:

1. resume_bullet: ONE resume bullet point.
   - Start with a strong, accurate past-tense action verb justified by the ledger's "actions".
   - Should read like a real resume line: specific, concise (roughly 18-28 words), no period-less
     sentence fragments that sound like fluff.
   - Include outcome/scale ONLY if the ledger's "outcome" or "scale_or_duration" fields are non-null.
   - Do not start with "Responsible for".

2. linkedin_post: ONE short LinkedIn-style post (roughly 40-90 words).
   - First-person, genuine voice — like a student actually sharing real work, not a press release.
   - Open with something concrete from the activity, not "Excited to share...".
   - Can end with a short, natural line of reflection or what's next, but only if grounded in
     the ledger (e.g. "challenges" or general next steps) — do not invent a call to action that
     implies something not in the ledger.
   - No more than one emoji, and only if it fits naturally. No hashtag spam (0-3 relevant tags max).

Return STRICT JSON: {"resume_bullet": "...", "linkedin_post": "..."}"""


def generate(facts: dict) -> dict:
    facts_block = facts_for_prompt(facts)
    result = generate_json(
        SYSTEM_ROLE,
        TASK_INSTRUCTIONS,
        facts_block,
        is_thin=facts.get("is_thin", False),
        temperature=0.6,
        max_tokens=500,
    )
    return {
        "resume_bullet": result.get("resume_bullet", "").strip(),
        "linkedin_post": result.get("linkedin_post", "").strip(),
    }
