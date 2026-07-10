"""
Mocked sanity check for the LLM graders — verifies the deterministic
point-conversion math is correct, WITHOUT making a real Groq API call
(this sandbox has no network access). Run this for real once a
GROQ_API_KEY is set and network is available, to confirm the live
call/parsing path also works.

Run: python -m app.llm.test_graders_mocked
"""
from unittest.mock import patch

import app.llm.dsa_grader as dsa_grader
import app.llm.project_grader as project_grader
import app.llm.explanation_grader as explanation_grader
import app.llm.hr_grader as hr_grader


def test_dsa_grader():
    print("\n=== DSA grader (mocked: 1 optimal, 1 suboptimal, 1 incorrect) ===")
    fake_responses = [
        {"classification": "optimal", "pattern_flagged": None, "category_flagged": None, "rationale": "correct"},
        {"classification": "suboptimal", "pattern_flagged": "two_pointers", "category_flagged": None, "rationale": "brute force"},
        {"classification": "incorrect", "pattern_flagged": None, "category_flagged": "Graphs", "rationale": "off target"},
    ]
    with patch("app.llm.dsa_grader.call_structured", side_effect=fake_responses):
        result = dsa_grader.score_dsa_concept_quiz(
            question_ids=["dsa_q001", "dsa_q002", "dsa_q005"],
            student_answers={"dsa_q001": "two pointers, O(n)", "dsa_q002": "nested loop", "dsa_q005": "not sure"},
        )
    print(f"Score: {result['score']} / {result['max']}")
    print(f"Gap flags: {result['gap_flags']}")
    # 1 optimal (full share) + 1 suboptimal (half share) + 1 incorrect (zero) out of 3 questions, max=10
    expected = round((1.0 + 0.5 + 0.0) * (10 / 3), 2)
    assert result["score"] == expected, f"Expected {expected}, got {result['score']}"
    assert "pattern:two_pointers" in result["gap_flags"]
    assert "dsa_category:Graphs" in result["gap_flags"]
    print("PASS")


def test_project_grader():
    print("\n=== Project grader (mocked: novelty=0.7, complexity=0.5) ===")
    fake_response = {"novelty_fraction": 0.7, "complexity_fraction": 0.5, "rationale": "solid but not groundbreaking"}
    with patch("app.llm.project_grader.call_structured", return_value=fake_response):
        result = project_grader.grade_project("A scheduling tool with constraint satisfaction.")
    print(f"Score: {result['score']} / {result['max']}")
    # dim_max = 9/2 = 4.5; novelty=0.7*4.5=3.15, complexity=0.5*4.5=2.25, total=5.4
    assert result["score"] == 5.4, f"Expected 5.4, got {result['score']}"
    print("PASS")


def test_explanation_grader():
    print("\n=== Explanation Clarity grader (mocked) ===")
    fake_response = {
        "structure_fraction": 0.8, "complexity_mention_fraction": 0.6,
        "clarity_fraction": 0.7, "audience_awareness_fraction": 0.5,
        "rationale": "clear and structured",
    }
    with patch("app.llm.explanation_grader.call_structured", return_value=fake_response):
        result = explanation_grader.grade_explanation("I used a hash map because it gives O(1) lookups...")
    print(f"Score: {result['score']} / {result['max']}")
    # 0.8*0.3*10 + 0.6*0.2*10 + 0.7*0.3*10 + 0.5*0.2*10 = 2.4+1.2+2.1+1.0 = 6.7
    assert result["score"] == 6.7, f"Expected 6.7, got {result['score']}"
    print("PASS")


def test_hr_grader():
    print("\n=== HR/Behavioral grader (mocked, 2 questions) ===")
    fake_responses = [
        {"specificity_fraction": 0.8, "coherence_fraction": 0.7, "self_awareness_fraction": 0.6,
         "cliche_penalty_applied": False, "rationale": "specific and coherent"},
        {"specificity_fraction": 0.2, "coherence_fraction": 0.3, "self_awareness_fraction": 0.2,
         "cliche_penalty_applied": True, "rationale": "generic filler"},
    ]
    with patch("app.llm.hr_grader.call_structured", side_effect=fake_responses):
        result = hr_grader.score_hr_behavioral(
            question_ids=["hr_002", "hr_005"],
            student_answers={"hr_002": "specific plan...", "hr_005": "I'm a hard worker..."},
        )
    print(f"Score: {result['score']} / {result['max']}")
    print(f"Gap flags: {result['gap_flags']}")
    assert "hr_behavioral:hr_005" in result["gap_flags"]
    print("PASS")


if __name__ == "__main__":
    test_dsa_grader()
    test_project_grader()
    test_explanation_grader()
    test_hr_grader()
    print("\nAll mocked grader tests passed.")
