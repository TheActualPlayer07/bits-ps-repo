"""
Central weight table for the Placement Panic Meter scoring rubric.
Total = 100 points across 8 categories.

Method key:
  DETERMINISTIC = computed purely from rules/lookup tables, no LLM
  HYBRID        = part deterministic + part LLM-rubric graded
  LLM_RUBRIC    = fully graded by an LLM against a fixed rubric
"""

CATEGORY_WEIGHTS = {
    "dsa": {
        "total": 21,
        "self_report": 11,          # deterministic: LeetCode counts + pattern checklist
        "self_report_volume": 6,    # sub-split of self_report
        "self_report_coverage": 5,  # sub-split of self_report
        "concept_quiz": 10,         # LLM-rubric: free-text grading vs NeetCode-based questions
        "method": "HYBRID",
    },
    "cs_fundamentals": {
        "total": 17,
        "method": "DETERMINISTIC",   # per-topic self-assessment checklist
    },
    "experience_certifications": {
        "total": 12,
        "method": "DETERMINISTIC",   # internship + certification checklist
    },
    "projects": {
        "total": 15,
        "checklist": 6,          # deterministic: README, tests, deployment, etc.
        "quality": 9,            # LLM-rubric: novelty/complexity from description
        "method": "HYBRID",
    },
    "resume": {
        "total": 10,
        "method": "DETERMINISTIC",   # checklist: quantified achievements, ATS, etc.
    },
    "coding_speed": {
        "total": 10,
        "method": "DETERMINISTIC",   # behavior-anchored self-report
    },
    "explanation_clarity": {
        "total": 10,
        "method": "LLM_RUBRIC",      # graded technical-explanation prompts
    },
    "aptitude": {
        "total": 3,
        "method": "DETERMINISTIC",   # known right/wrong puzzle answers
    },
    "hr_behavioral": {
        "total": 2,
        "method": "LLM_RUBRIC",      # graded HR/behavioral answers
    },
}

assert sum(c["total"] for c in CATEGORY_WEIGHTS.values()) == 100, "Weights must sum to 100"

# Score interpretation bands (overall 0-100 -> readiness level)
SCORE_BANDS = [
    (0, 40, "Beginner", "Significant preparation needed before placement season."),
    (41, 55, "Foundation", "Can clear a few basic OAs but interview performance will likely be inconsistent."),
    (56, 70, "Placement Ready", "Competitive for many service companies and some product companies."),
    (71, 85, "Strong Candidate", "Good chance at product-company interviews with consistent preparation."),
    (86, 95, "Top Tier", "Competitive for leading product companies and many high-paying roles."),
    (96, 100, "Exceptional", "Among the strongest candidates in a typical placement cohort."),
]

# Optional company-type multiplier (opt-in only, applied on top of base score, never replaces it)
COMPANY_EMPHASIS = {
    "service_based":     {"dsa": 0.9, "cs_fundamentals": 1.1, "projects": 1.0, "explanation_clarity": 1.1},
    "product_based":     {"dsa": 1.2, "cs_fundamentals": 1.1, "projects": 1.1, "explanation_clarity": 1.0},
    "quant_hft":         {"dsa": 1.3, "cs_fundamentals": 1.1, "projects": 1.0, "explanation_clarity": 1.0},
    "ai_ml":             {"dsa": 1.1, "cs_fundamentals": 1.0, "projects": 1.3, "explanation_clarity": 1.0},
    "data_engineering":  {"dsa": 0.9, "cs_fundamentals": 1.1, "projects": 1.1, "explanation_clarity": 1.0},
}

def get_band(score: int):
    for low, high, label, meaning in SCORE_BANDS:
        if low <= score <= high:
            return {"label": label, "meaning": meaning}
    return {"label": "Unknown", "meaning": ""}


# Urgency modifier — does NOT affect the 0-100 score. It reshapes how the
# breakdown and action plan are framed (pace/tone), based on time remaining
# before placement season. A 60 with 5 months left reads differently from
# a 60 with 3 weeks left, even though the underlying readiness is identical.
URGENCY_BANDS = [
    (6, 999, "low", "You have real runway. Build steadily, prioritize the highest-weighted gaps first."),
    (3, 6, "medium", "Time is getting tighter. Focus on your 2-3 biggest gaps rather than spreading thin."),
    (1, 3, "high", "Placements are close. Triage: fix only what can realistically move the needle in time."),
    (0, 1, "critical", "Very little runway left. Focus entirely on highest-leverage, fastest wins."),
]


def get_urgency(months_remaining: float):
    for low, high, label, message in URGENCY_BANDS:
        if low <= months_remaining < high:
            return {"level": label, "message": message}
    return {"level": "unknown", "message": ""}
