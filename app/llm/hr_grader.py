"""
Grades HR/Behavioral answers against specificity, coherence, and
self-awareness, with a cliche penalty. Low weight (2 pts total) relative
to the engineering behind it — see the submission note re: whether this
is worth the build effort at this weight.
"""
import concurrent.futures

from app.llm.client import call_structured
from app.llm.schemas import HR_BEHAVIORAL_SCHEMA
from app.data.hr_question_pool import get_focus
from app.scoring.config import CATEGORY_WEIGHTS

DIMENSION_WEIGHTS = {
    "specificity": 0.4,
    "coherence": 0.4,
    "self_awareness": 0.2,
}
CLICHE_PENALTY_MULTIPLIER = 0.8  # applied to the total if the model flags heavy cliche/filler use

SYSTEM_PROMPT = """You are grading a student's answer to an HR/behavioral interview question.

Score three dimensions as fractions from 0.0 to 1.0:
1. specificity_fraction: does the answer name concrete details (skills, situations, plans),
   or is it generic filler ("I want to grow and learn", "I'm a hard worker")?
2. coherence_fraction: does the answer connect plausibly to what a real person in this situation
   would say, showing a consistent, believable narrative rather than a disconnected template answer?
3. self_awareness_fraction: for reflective questions, does the answer show genuine reflection
   (what they learned, what they'd do differently) rather than just narrating events?

Also set cliche_penalty_applied to true if the answer leans heavily on stock phrases with no
backing evidence (e.g. "I'm passionate about making an impact", "I always give 110%").

Be calibrated: most reasonable answers land in the 0.4-0.7 range per dimension. Reserve 0.85+
for genuinely specific, well-reasoned answers."""


def grade_hr_answer(question_id: str, student_answer: str) -> dict:
    focus = get_focus(question_id) or "General behavioral fit."

    if not student_answer or not student_answer.strip():
        return {"fraction_total": 0.0, "cliche_penalty_applied": False, "rationale": "No answer provided."}

    user_prompt = f"""What this question is probing for: {focus}

Student's answer:
\"\"\"{student_answer}\"\"\"
"""

    result = call_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        json_schema=HR_BEHAVIORAL_SCHEMA,
        schema_name="hr_behavioral",
    )

    weighted_fraction = (
        result["specificity_fraction"] * DIMENSION_WEIGHTS["specificity"]
        + result["coherence_fraction"] * DIMENSION_WEIGHTS["coherence"]
        + result["self_awareness_fraction"] * DIMENSION_WEIGHTS["self_awareness"]
    )
    if result["cliche_penalty_applied"]:
        weighted_fraction *= CLICHE_PENALTY_MULTIPLIER

    return {
        "fraction_total": weighted_fraction,
        "cliche_penalty_applied": result["cliche_penalty_applied"],
        "rationale": result["rationale"],
    }


def score_hr_behavioral(question_ids: list, student_answers: dict) -> dict:
    """
    question_ids: sampled HR question ids shown to the student (2-3)
    student_answers: {question_id: answer_text}
    Splits CATEGORY_WEIGHTS["hr_behavioral"]["total"] (currently 2) evenly across questions asked.
    Grades all questions concurrently rather than one after another.
    """
    hr_max = CATEGORY_WEIGHTS["hr_behavioral"]["total"]
    per_question_max = hr_max / len(question_ids)

    graded_by_id = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(question_ids)) as executor:
        future_to_qid = {
            executor.submit(grade_hr_answer, qid, student_answers.get(qid, "")): qid
            for qid in question_ids
        }
        for future in concurrent.futures.as_completed(future_to_qid):
            qid = future_to_qid[future]
            graded_by_id[qid] = future.result()

    total = 0.0
    per_question_results = []
    gap_flags = []

    for qid in question_ids:  # original order, regardless of completion order
        graded = graded_by_id[qid]
        points = graded["fraction_total"] * per_question_max
        total += points
        per_question_results.append({"question_id": qid, "points": round(points, 2), **graded})
        if graded["fraction_total"] < 0.4:
            gap_flags.append(f"hr_behavioral:{qid}")

    return {
        "score": round(total, 2),
        "max": hr_max,
        "detail": {"per_question": per_question_results},
        "gap_flags": gap_flags,
    }
