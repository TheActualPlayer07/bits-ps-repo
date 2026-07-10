"""
The scoring brain. Orchestrates every deterministic scorer and every
LLM-rubric grader into one final structured result: total score, band,
urgency, per-category breakdown, and an aggregated gap-flag list ready
for the action-plan generator.

Handles LLM failures gracefully: if a Groq call fails (bad key, network,
malformed response after retries), that category falls back to a neutral
default rather than crashing the whole run — the student still gets a
complete result, with a clear note about what couldn't be graded live.
"""
from app.scoring import deterministic as det
from app.scoring.config import CATEGORY_WEIGHTS, get_band, get_urgency
from app.llm.client import GroqGradingError
from app.llm.dsa_grader import score_dsa_concept_quiz
from app.llm.project_grader import grade_project
from app.llm.explanation_grader import grade_explanation
from app.llm.hr_grader import score_hr_behavioral
import concurrent.futures

from app.data.aptitude_bank import get_random_sample as sample_aptitude, grade_answers as grade_aptitude_answers
from app.data.dsa_question_bank import get_random_sample as sample_dsa
from app.data.hr_question_pool import get_random_sample as sample_hr


def build_intake_samples() -> dict:
    """Called on GET — freshly samples the randomized question sets for one session."""
    return {
        "aptitude_questions": sample_aptitude(4),
        "dsa_questions": sample_dsa(4),
        "hr_questions": sample_hr(3),
    }


def _llm_fallback(max_points: float, category_label: str) -> dict:
    """Neutral default when a Groq call fails after retries — half credit, clearly flagged."""
    return {
        "score": round(max_points * 0.5, 2),
        "max": max_points,
        "detail": {"note": "LLM grading unavailable — default applied. Re-run once the grading service is reachable."},
        "gap_flags": [f"{category_label}:llm_unavailable"],
    }


def run_full_scoring(form_data: dict) -> dict:
    """
    form_data is the fully assembled intake payload — see app/main.py for the
    exact shape pulled from the submitted form. Returns the complete result
    dict consumed by the results template and (later) the action-plan generator.
    """
    results = {}
    all_gap_flags = []

    # ---- Deterministic categories ----
    results["dsa_self_report"] = det.score_dsa_self_report(form_data["dsa"])
    results["cs_fundamentals"] = det.score_cs_fundamentals(form_data["cs"])
    results["experience_certifications"] = det.score_experience_certifications(form_data["experience"])
    results["resume"] = det.score_resume(form_data["resume"])
    results["coding_speed"] = det.score_coding_speed(form_data["speed"])
    results["projects_checklist"] = det.score_projects_checklist(form_data["projects"])

    aptitude_graded = grade_aptitude_answers(form_data["aptitude_submitted"])
    results["aptitude"] = det.score_aptitude(aptitude_graded)

    # ---- LLM-rubric categories ----
    # All 4 are independent of each other, so they run concurrently — this is
    # the difference between a submission waiting on ~4 sequential network
    # round-trips versus ~1. Each still falls back individually if it fails,
    # so one bad category never sinks the other three or the whole request.
    llm_tasks = {
        "dsa_concept_quiz": (
            score_dsa_concept_quiz,
            (form_data["dsa_question_ids"], form_data["dsa_answers"]),
            CATEGORY_WEIGHTS["dsa"]["concept_quiz"],
        ),
        "projects_quality": (
            grade_project,
            (form_data["project_description"],),
            CATEGORY_WEIGHTS["projects"]["quality"],
        ),
        "explanation_clarity": (
            grade_explanation,
            (form_data["explanation_answer"],),
            CATEGORY_WEIGHTS["explanation_clarity"]["total"],
        ),
        "hr_behavioral": (
            score_hr_behavioral,
            (form_data["hr_question_ids"], form_data["hr_answers"]),
            CATEGORY_WEIGHTS["hr_behavioral"]["total"],
        ),
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(llm_tasks)) as executor:
        future_to_key = {
            executor.submit(func, *args): (key, max_pts)
            for key, (func, args, max_pts) in llm_tasks.items()
        }
        for future in concurrent.futures.as_completed(future_to_key):
            key, max_pts = future_to_key[future]
            try:
                results[key] = future.result()
            except Exception:
                results[key] = _llm_fallback(max_pts, key)

    # ---- Aggregate ----
    for r in results.values():
        all_gap_flags.extend(r.get("gap_flags", []))

    total_score = round(sum(r["score"] for r in results.values()), 2)
    total_max = sum(r["max"] for r in results.values())

    urgency = get_urgency(form_data.get("months_remaining", 6))
    band = get_band(round(total_score))

    return {
        "total_score": total_score,
        "total_max": total_max,
        "band": band,
        "urgency": urgency,
        "categories": results,
        "gap_flags": all_gap_flags,
    }
