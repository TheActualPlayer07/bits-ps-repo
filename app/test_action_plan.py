"""
Focused test of action_plan.generate_action_plan() — checks priority
sorting, advice mapping for each gap-flag prefix, and that rationale
text from the LLM graders gets correctly pulled through for the three
qualitative categories.

Run: python -m app.test_action_plan
"""
from app.action_plan import generate_action_plan

FAKE_RESULT = {
    "urgency": {"level": "high", "message": "Placements are close. Triage: fix only what can realistically move the needle in time."},
    "gap_flags": [
        "pattern:two_pointers",           # DSA — should be priority 3
        "dsa_category:Graphs",            # DSA — should be priority 3
        "resume:one_page",                # Resume — mid priority
        "coding_speed:easy_under_15min",  # low-mid priority
        "aptitude:reasoning_gap",         # low priority
        "projects:low_novelty",           # should pull rationale from categories
        "explanation_clarity:clarity",    # should pull rationale from categories
        "hr_behavioral:hr_005",           # should pull per-question rationale
        "dsa_concept_quiz:llm_unavailable",  # fallback-flagged category
        "not_a_real_prefix:whatever",     # unrecognized — should be silently skipped
    ],
    "categories": {
        "projects_quality": {"detail": {"rationale": "The to-do app is a standard CRUD pattern without a distinguishing technical angle."}},
        "explanation_clarity": {"detail": {"rationale": "The explanation jumped into implementation details without stating the overall approach first."}},
        "hr_behavioral": {"detail": {"per_question": [
            {"question_id": "hr_005", "rationale": "Claimed 'hard worker' with no supporting example."},
        ]}},
    },
}


def run():
    plan = generate_action_plan(FAKE_RESULT)

    print(f"Urgency: {plan['urgency_level']} — {plan['urgency_message']}")
    print(f"\nTotal items: {len(plan['full_plan'])} (9 recognized + 1 skipped unrecognized flag)")
    assert len(plan["full_plan"]) == 9, f"Expected 9 items, got {len(plan['full_plan'])}"

    print("\n--- Top priority (should be the two priority-3 DSA items first) ---")
    for item in plan["top_priority"]:
        print(f"[{item['priority']}] {item['title']} — {item['category']}")
    assert plan["top_priority"][0]["priority"] == 3
    assert plan["top_priority"][1]["priority"] == 3

    print("\n--- Checking rationale pass-through for LLM-graded categories ---")
    full = {item["title"]: item for item in plan["full_plan"]}

    proj_item = next(i for i in plan["full_plan"] if i["category"] == "Projects")
    assert "CRUD" in proj_item["why"], "Expected the project grader's actual rationale to appear"
    print(f"Projects why: {proj_item['why']}")

    exp_item = next(i for i in plan["full_plan"] if i["category"] == "Explanation Clarity")
    assert "implementation details" in exp_item["why"]
    print(f"Explanation Clarity why: {exp_item['why']}")

    hr_item = next(i for i in plan["full_plan"] if i["category"] == "HR/Behavioral")
    assert "hard worker" in hr_item["why"]
    print(f"HR/Behavioral why: {hr_item['why']}")

    llm_unavail_item = next(i for i in plan["full_plan"] if "llm unavailable" in i["title"].lower() or "couldn" in i["title"].lower())
    print(f"LLM-unavailable item: {llm_unavail_item['title']}")

    print("\nAll action-plan checks PASSED.")


if __name__ == "__main__":
    run()
