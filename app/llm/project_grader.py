"""
Grades the qualitative half of the Projects category — novelty and
complexity, judged from the student's own project description. The
deterministic checklist half (README, tests, deployment, etc.) lives
in app.scoring.deterministic.score_projects_checklist.
"""
from app.llm.client import call_structured
from app.llm.schemas import PROJECT_QUALITY_SCHEMA
from app.scoring.config import CATEGORY_WEIGHTS

SYSTEM_PROMPT = """You are grading a student's project on two dimensions: novelty and complexity,
based only on the description they provide.

Novelty: does this go beyond a standard tutorial/clone project (e.g. yet another to-do app,
a basic CRUD blog, a copy of a well-known starter template)? Higher novelty = original problem,
unusual angle, or a real gap the student identified themselves.

Complexity: does the project involve genuine technical depth — nontrivial algorithms, meaningful
system design, integration of multiple non-trivial components, handling real edge cases — versus
a shallow wrapper around a single library or tutorial pattern?

Score each dimension as a fraction from 0.0 (weak) to 1.0 (excellent). Be honest and calibrated:
most standard student projects should land in the 0.3-0.6 range on each dimension; reserve 0.8+
for projects that would genuinely stand out. Do not inflate scores to be encouraging — an honest,
slightly lower score with specific rationale is more useful to the student than false praise.

Example of LOW novelty/complexity: "A to-do list app with add/delete/mark-complete, stored in
local state, styled with basic CSS."
Example of HIGH novelty/complexity: "A scheduling tool that models constraint satisfaction between
overlapping calendars, with a custom conflict-resolution algorithm and a deployed backend handling
concurrent edits."
"""


def grade_project(project_description: str) -> dict:
    """
    Returns {"score": float, "max": float, "detail": {...}}
    max = CATEGORY_WEIGHTS["projects"]["quality"] (currently 9, split evenly between the two dimensions)
    """
    proj_w = CATEGORY_WEIGHTS["projects"]["quality"]
    dim_max = proj_w / 2  # novelty and complexity split evenly

    if not project_description or not project_description.strip():
        return {
            "score": 0.0, "max": proj_w,
            "detail": {"rationale": "No project description provided."},
            "gap_flags": ["projects:no_description"],
        }

    user_prompt = f'Student\'s project description:\n"""{project_description}"""'

    result = call_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        json_schema=PROJECT_QUALITY_SCHEMA,
        schema_name="project_quality",
    )

    novelty_points = result["novelty_fraction"] * dim_max
    complexity_points = result["complexity_fraction"] * dim_max
    total = round(novelty_points + complexity_points, 2)

    gap_flags = []
    if result["novelty_fraction"] < 0.4:
        gap_flags.append("projects:low_novelty")
    if result["complexity_fraction"] < 0.4:
        gap_flags.append("projects:low_complexity")

    return {
        "score": total,
        "max": proj_w,
        "detail": {
            "novelty_points": round(novelty_points, 2),
            "complexity_points": round(complexity_points, 2),
            "rationale": result["rationale"],
        },
        "gap_flags": gap_flags,
    }
