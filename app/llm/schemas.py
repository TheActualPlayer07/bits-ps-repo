"""
JSON Schemas for every LLM-rubric grading call.

Design principle: every dimension the model scores comes back as a
fraction between 0 and 1 (relative quality), never an absolute point
value. The actual points-per-dimension conversion happens in our own
grader code using app.scoring.config weights — so rebalancing the
rubric later never requires touching a prompt or schema.
"""

DSA_GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "classification": {
            "type": "string",
            "enum": ["optimal", "suboptimal", "incorrect"],
        },
        "pattern_flagged": {"type": ["string", "null"]},   # set when classification == "suboptimal"
        "category_flagged": {"type": ["string", "null"]},  # set when classification == "incorrect"
        "rationale": {"type": "string"},
    },
    "required": ["classification", "pattern_flagged", "category_flagged", "rationale"],
    "additionalProperties": False,
}

PROJECT_QUALITY_SCHEMA = {
    "type": "object",
    "properties": {
        "novelty_fraction": {"type": "number"},      # 0-1
        "complexity_fraction": {"type": "number"},   # 0-1
        "rationale": {"type": "string"},
    },
    "required": ["novelty_fraction", "complexity_fraction", "rationale"],
    "additionalProperties": False,
}

EXPLANATION_CLARITY_SCHEMA = {
    "type": "object",
    "properties": {
        "structure_fraction": {"type": "number"},           # 0-1
        "complexity_mention_fraction": {"type": "number"},  # 0-1
        "clarity_fraction": {"type": "number"},              # 0-1 (free of hand-waving)
        "audience_awareness_fraction": {"type": "number"},   # 0-1
        "rationale": {"type": "string"},
    },
    "required": ["structure_fraction", "complexity_mention_fraction", "clarity_fraction",
                 "audience_awareness_fraction", "rationale"],
    "additionalProperties": False,
}

HR_BEHAVIORAL_SCHEMA = {
    "type": "object",
    "properties": {
        "specificity_fraction": {"type": "number"},     # 0-1
        "coherence_fraction": {"type": "number"},       # 0-1
        "self_awareness_fraction": {"type": "number"},  # 0-1
        "cliche_penalty_applied": {"type": "boolean"},
        "rationale": {"type": "string"},
    },
    "required": ["specificity_fraction", "coherence_fraction", "self_awareness_fraction",
                 "cliche_penalty_applied", "rationale"],
    "additionalProperties": False,
}
