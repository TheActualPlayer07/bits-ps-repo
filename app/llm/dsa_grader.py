"""
Grades a student's free-text answer to one sampled DSA conceptual question.

Design: the model only classifies the answer into one of three buckets
(optimal / suboptimal / incorrect) — it does NOT output a numeric score.
Points are assigned deterministically in code from the classification,
which is far more consistent run-to-run than trusting a model-generated
number directly.
"""
import concurrent.futures

from app.llm.client import call_structured
from app.llm.schemas import DSA_GRADE_SCHEMA
from app.data.dsa_question_bank import get_grading_metadata
from app.scoring.config import CATEGORY_WEIGHTS

# Classification -> fraction of that question's point share
CLASSIFICATION_FRACTIONS = {
    "optimal": 1.0,
    "suboptimal": 0.5,
    "incorrect": 0.0,
}

SYSTEM_PROMPT = """You are grading a student's free-text answer to a data structures & algorithms
conceptual question. You are NOT grading code — you're checking whether the student identifies
the correct technique/pattern and time complexity, in their own words.

Classify the answer into exactly one bucket:
- "optimal": correctly identifies the expected pattern AND the expected complexity (phrasing can vary).
- "suboptimal": identifies a working approach that matches one of the known suboptimal/brute-force
  approaches provided, OR shows real problem-solving but misses the optimal technique/complexity.
- "incorrect": does not recognize the problem shape at all, answer is off-target, or shows
  fundamental confusion about the problem.

If "suboptimal", set pattern_flagged to the expected_pattern given to you (this triggers a
"revisit this technique" recommendation for the student).
If "incorrect", set category_flagged to the question's category (this flags the broader topic
area rather than one specific technique).
Otherwise leave the non-applicable field as null.

Be fair to varied phrasing — students may describe the same correct technique very differently.
Do not require them to use exact terminology, only the correct underlying idea."""


def grade_dsa_answer(question_id: str, student_answer: str) -> dict:
    """
    Returns {"points": float, "max": float, "classification": str,
             "pattern_flagged": str|None, "category_flagged": str|None, "rationale": str}
    """
    meta = get_grading_metadata(question_id)
    if meta is None:
        raise ValueError(f"Unknown DSA question id: {question_id}")

    user_prompt = f"""Question posed to the student:
{meta['question_text']}

Expected optimal pattern: {meta['expected_pattern']}
Expected optimal complexity: {meta['expected_complexity']}
Known suboptimal/brute-force approaches for this question:
{chr(10).join('- ' + a for a in meta['known_suboptimal_approaches'])}

Question category (used only if classification is "incorrect"): {meta['category']}
Pattern tag (used only if classification is "suboptimal"): {meta['pattern_tag']}

Student's answer:
\"\"\"{student_answer}\"\"\"
"""

    result = call_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        json_schema=DSA_GRADE_SCHEMA,
        schema_name="dsa_grade",
    )

    return {
        "classification": result["classification"],
        "pattern_flagged": result["pattern_flagged"],
        "category_flagged": result["category_flagged"],
        "rationale": result["rationale"],
        "fraction": CLASSIFICATION_FRACTIONS[result["classification"]],
    }


def score_dsa_concept_quiz(question_ids: list, student_answers: dict) -> dict:
    """
    question_ids: the sampled question ids shown to the student
    student_answers: {question_id: answer_text}
    Splits DSA_W["concept_quiz"] evenly across however many questions were asked.

    Grades all questions concurrently (each is an independent network call to
    Groq) rather than one after another — this is the difference between the
    student waiting on ~4 sequential round-trips versus ~1.
    """
    dsa_w = CATEGORY_WEIGHTS["dsa"]
    per_question_max = dsa_w["concept_quiz"] / len(question_ids)

    graded_by_id = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(question_ids)) as executor:
        future_to_qid = {
            executor.submit(grade_dsa_answer, qid, student_answers.get(qid, "")): qid
            for qid in question_ids
        }
        for future in concurrent.futures.as_completed(future_to_qid):
            qid = future_to_qid[future]
            graded_by_id[qid] = future.result()  # propagates on failure — caught by aggregator's category-level fallback

    total = 0.0
    gap_flags = []
    per_question_results = []

    # Rebuild in original question order for deterministic display, regardless
    # of which thread happened to finish first.
    for qid in question_ids:
        graded = graded_by_id[qid]
        points = graded["fraction"] * per_question_max
        total += points

        if graded["pattern_flagged"]:
            gap_flags.append(f"pattern:{graded['pattern_flagged']}")
        if graded["category_flagged"]:
            gap_flags.append(f"dsa_category:{graded['category_flagged']}")

        per_question_results.append({"question_id": qid, "points": round(points, 2), **graded})

    return {
        "score": round(total, 2),
        "max": dsa_w["concept_quiz"],
        "detail": {"per_question": per_question_results},
        "gap_flags": gap_flags,
    }
