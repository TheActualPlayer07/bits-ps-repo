"""
Quick manual sanity check — not a full test suite, just enough to confirm
the deterministic scorers behave sensibly on a strong / weak / mixed profile
before we wire them into the intake flow.
Run: python -m app.scoring.test_deterministic
"""
from app.scoring.deterministic import (
    score_dsa_self_report, score_cs_fundamentals, score_resume,
    score_coding_speed, score_projects_checklist, score_aptitude,
    score_experience_certifications,
)
from app.scoring.config import get_urgency

STRONG_PROFILE = {
    "dsa": {"leetcode_easy": 150, "leetcode_medium": 250, "leetcode_hard": 80,
            "patterns_known": ["arrays", "hashing", "two_pointers", "sliding_window",
                                "binary_search", "trees", "graphs", "dynamic_programming",
                                "dfs_bfs", "heap"]},
    "cs": {"os_known": ["processes_vs_threads", "deadlock", "paging", "scheduling", "virtual_memory"],
           "dbms_known": ["indexing", "normalization", "transactions", "isolation", "joins"],
           "cn_known": ["tcp", "udp", "http", "dns"],
           "oop_known": ["inheritance", "polymorphism", "solid", "virtual_functions", "encapsulation"]},
    "experience": {"has_internship": True, "internship_relevant": True,
                   "internship_2plus_months": True, "has_certification": True,
                   "certification_relevant": False},
    "resume": {"resume_checklist": ["quantified_achievements", "clean_formatting",
                                     "strong_projects_listed", "one_page", "ats_friendly"]},
    "speed": {"easy_under_15min": True, "medium_under_35min": True, "hard_under_60min": False,
              "debugs_independently": True, "writes_clean_code": True},
    "projects": {"project_checklist": ["clean_readme", "public_github", "has_tests", "deployed"]},
    "aptitude": [{"question_id": "a1", "correct": True}, {"question_id": "a2", "correct": True},
                 {"question_id": "a3", "correct": False}],
    "months_remaining": 2,
}

WEAK_PROFILE = {
    "dsa": {"leetcode_easy": 20, "leetcode_medium": 5, "leetcode_hard": 0,
            "patterns_known": ["arrays"]},
    "cs": {"os_known": [], "dbms_known": ["joins"], "cn_known": [], "oop_known": ["inheritance"]},
    "experience": {"has_internship": False, "internship_relevant": False,
                   "internship_2plus_months": False, "has_certification": False,
                   "certification_relevant": False},
    "resume": {"resume_checklist": ["one_page"]},
    "speed": {"easy_under_15min": False, "medium_under_35min": False, "hard_under_60min": False,
              "debugs_independently": False, "writes_clean_code": False},
    "projects": {"project_checklist": []},
    "aptitude": [{"question_id": "a1", "correct": False}, {"question_id": "a2", "correct": False}],
    "months_remaining": 7,
}


def run_profile(name, p):
    print(f"\n=== {name} ===")
    r_dsa = score_dsa_self_report(p["dsa"])
    r_cs = score_cs_fundamentals(p["cs"])
    r_exp = score_experience_certifications(p["experience"])
    r_resume = score_resume(p["resume"])
    r_speed = score_coding_speed(p["speed"])
    r_proj = score_projects_checklist(p["projects"])
    r_apt = score_aptitude(p["aptitude"])

    for label, r in [("DSA self-report", r_dsa), ("CS Fundamentals", r_cs),
                      ("Experience & Certs", r_exp), ("Resume", r_resume),
                      ("Coding Speed", r_speed), ("Projects checklist", r_proj),
                      ("Aptitude", r_apt)]:
        print(f"{label:22s} {r['score']:>5} / {r['max']}   gaps={r.get('gap_flags')}")

    parts = [r_dsa, r_cs, r_exp, r_resume, r_speed, r_proj, r_apt]
    subtotal = sum(r["score"] for r in parts)
    max_subtotal = sum(r["max"] for r in parts)
    print(f"{'Deterministic subtotal':22s} {subtotal:>5.2f} / {max_subtotal}"
          f"  (out of 100 once LLM-graded DSA-quiz(10)+Projects-quality(9)+"
          f"Explanation(10)+HR(2) are added)")

    urgency = get_urgency(p["months_remaining"])
    print(f"Urgency ({p['months_remaining']} months left): {urgency['level']} — {urgency['message']}")


if __name__ == "__main__":
    run_profile("STRONG profile", STRONG_PROFILE)
    run_profile("WEAK profile", WEAK_PROFILE)
