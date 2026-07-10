"""
Grades "Explanation Clarity" — how clearly the student explains technical
work in writing. This is an explicit proxy for communication skill, not
a measure of live verbal delivery (a text intake can't assess that
honestly — see the submission note for this caveat).
"""
from app.llm.client import call_structured
from app.llm.schemas import EXPLANATION_CLARITY_SCHEMA
from app.scoring.config import CATEGORY_WEIGHTS

# Dimension weights as fractions of the total (must sum to 1.0)
DIMENSION_WEIGHTS = {
    "structure": 0.3,
    "complexity_mention": 0.2,
    "clarity": 0.3,
    "audience_awareness": 0.2,
}

SYSTEM_PROMPT = """You are grading a student's written technical explanation on four dimensions:

1. Structure (structure_fraction): does the answer state its approach/structure clearly before
   diving into detail, rather than jumping straight into unstructured detail?
2. Complexity/tradeoff mention (complexity_mention_fraction): does the answer mention relevant
   complexity, tradeoffs, or reasoning about why the approach was chosen (where relevant to the
   prompt)?
3. Clarity (clarity_fraction): is the explanation free of hand-waving and vague filler
   ("it just works", "basically the logic handles it") — does it actually explain the mechanism?
4. Audience awareness (audience_awareness_fraction): if the prompt asked for the same idea
   explained to two different audiences, does the answer actually adjust tone/depth appropriately?
   If the prompt didn't ask for this, score this dimension based on general awareness of who's
   reading (still clear and appropriately pitched).

Score each dimension as a fraction from 0.0 to 1.0. Be calibrated and honest — most competent
students should land in the 0.4-0.7 range; reserve 0.85+ for explanations that are genuinely
exceptional in that dimension."""


def grade_explanation(answer_text: str) -> dict:
    """
    Returns {"score": float, "max": float, "detail": {...}, "gap_flags": [...]}
    max = CATEGORY_WEIGHTS["explanation_clarity"]["total"] (currently 10)
    """
    max_total = CATEGORY_WEIGHTS["explanation_clarity"]["total"]

    if not answer_text or not answer_text.strip():
        return {
            "score": 0.0, "max": max_total,
            "detail": {"rationale": "No explanation provided."},
            "gap_flags": ["explanation_clarity:no_answer"],
        }

    user_prompt = f'Student\'s written technical explanation:\n"""{answer_text}"""'

    result = call_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        json_schema=EXPLANATION_CLARITY_SCHEMA,
        schema_name="explanation_clarity",
    )

    dims = {
        "structure": result["structure_fraction"],
        "complexity_mention": result["complexity_mention_fraction"],
        "clarity": result["clarity_fraction"],
        "audience_awareness": result["audience_awareness_fraction"],
    }
    total = sum(dims[d] * DIMENSION_WEIGHTS[d] * max_total for d in dims)

    gap_flags = [f"explanation_clarity:{d}" for d, frac in dims.items() if frac < 0.4]

    return {
        "score": round(total, 2),
        "max": max_total,
        "detail": {"dimension_fractions": dims, "rationale": result["rationale"]},
        "gap_flags": gap_flags,
    }
