"""
Deterministic scoring functions. No LLM involved anywhere in this file.
Every function takes a chunk of intake data and returns:
    {"score": float, "max": float, "detail": {...}}   plus any gap flags.

Expected intake shape for each function is documented in its docstring.
Weights are pulled from config.CATEGORY_WEIGHTS rather than hardcoded here,
so rebalancing the rubric only ever requires editing config.py.
"""
from app.scoring.config import CATEGORY_WEIGHTS

DSA_W = CATEGORY_WEIGHTS["dsa"]
CS_W = CATEGORY_WEIGHTS["cs_fundamentals"]["total"]
EXP_W = CATEGORY_WEIGHTS["experience_certifications"]["total"]

# Major DSA patterns — missing several of these drags the coverage score down harder
MAJOR_PATTERNS = {
    "arrays", "hashing", "two_pointers", "sliding_window",
    "binary_search", "trees", "graphs", "dynamic_programming",
}

ALL_PATTERNS = MAJOR_PATTERNS | {
    "prefix_sum", "linked_list", "bst", "dfs_bfs", "topological_sort",
    "shortest_path", "union_find", "greedy", "heap", "stack", "queue",
    "trie", "backtracking", "bit_manipulation", "segment_tree",
}


def score_dsa_self_report(intake: dict) -> dict:
    """
    intake = {
        "leetcode_easy": int, "leetcode_medium": int, "leetcode_hard": int,
        "patterns_known": [str, ...]   # subset of ALL_PATTERNS
    }
    Max = DSA_W["self_report"] (currently 11), split into volume + pattern coverage
    per DSA_W["self_report_volume"] / DSA_W["self_report_coverage"].
    """
    vol_max = DSA_W["self_report_volume"]
    cov_max = DSA_W["self_report_coverage"]

    easy = intake.get("leetcode_easy", 0)
    medium = intake.get("leetcode_medium", 0)
    hard = intake.get("leetcode_hard", 0)
    weighted = easy * 1 + medium * 2 + hard * 3

    # Volume/quality tiers, expressed as a fraction of vol_max so rebalancing
    # the weight table never requires touching these thresholds.
    if weighted < 60:
        vol_fraction = 1 / 6
    elif weighted < 150:
        vol_fraction = 3.5 / 9
    elif weighted < 300:
        vol_fraction = 5.5 / 9
    elif weighted < 500:
        vol_fraction = 7.5 / 9
    else:
        vol_fraction = 1.0
    volume = vol_fraction * vol_max

    # Pattern coverage
    known = set(p.lower() for p in intake.get("patterns_known", []))
    known = known & ALL_PATTERNS  # ignore junk input
    coverage_ratio = len(known) / len(ALL_PATTERNS)
    coverage_score = coverage_ratio * cov_max

    missing_major = MAJOR_PATTERNS - known
    gap_flags = [f"pattern:{p}" for p in missing_major]

    # Penalize harder if missing more than 3 major patterns
    if len(missing_major) > 3:
        coverage_score *= 0.7

    total = round(volume + coverage_score, 2)
    return {
        "score": total,
        "max": DSA_W["self_report"],
        "detail": {
            "weighted_problem_count": weighted,
            "volume_points": round(volume, 2),
            "coverage_points": round(coverage_score, 2),
            "missing_major_patterns": sorted(missing_major),
        },
        "gap_flags": gap_flags,
    }


CS_TOPICS = {
    "os": ["processes_vs_threads", "deadlock", "paging", "scheduling", "virtual_memory"],
    "dbms": ["indexing", "normalization", "transactions", "isolation", "joins"],
    "cn": ["tcp", "udp", "http", "dns", "routing"],
    "oop": ["inheritance", "polymorphism", "solid", "virtual_functions", "encapsulation"],
}


def score_cs_fundamentals(intake: dict) -> dict:
    """
    intake = {
        "os_known": [str,...], "dbms_known": [...], "cn_known": [...], "oop_known": [...]
    }
    Each list is a subset of that topic's 5 core-concept checklist.
    CS_W total split evenly across the 4 topics.
    """
    per_topic_max = CS_W / len(CS_TOPICS)

    detail = {}
    gap_flags = []
    total = 0.0
    for topic, concepts in CS_TOPICS.items():
        known = set(intake.get(f"{topic}_known", []))
        score = (len(known & set(concepts)) / len(concepts)) * per_topic_max
        total += score
        detail[topic] = round(score, 2)
        if score < per_topic_max * 0.6:
            gap_flags.append(f"cs_fundamentals:{topic}")

    return {"score": round(total, 2), "max": CS_W, "detail": detail, "gap_flags": gap_flags}


def score_experience_certifications(intake: dict) -> dict:
    """
    intake = {
        "has_internship": bool, "internship_relevant": bool,
        "internship_2plus_months": bool,
        "has_certification": bool, "certification_relevant": bool
    }
    Deterministic checklist, total = EXP_W (currently 12).
    """
    weights = {
        "has_internship": 3.0,
        "internship_relevant": 3.0,
        "internship_2plus_months": 2.0,
        "has_certification": 2.0,
        "certification_relevant": 2.0,
    }
    # weights above sum to 12 by construction; scale defensively if EXP_W ever changes
    scale = EXP_W / sum(weights.values())
    total = sum(pts * scale for key, pts in weights.items() if intake.get(key))
    gap_flags = [f"experience:{key}" for key in weights if not intake.get(key)]

    return {"score": round(total, 2), "max": EXP_W, "detail": {}, "gap_flags": gap_flags}


def score_resume(intake: dict) -> dict:
    """
    intake = {"resume_checklist": [str,...]}  subset of the 6 items below.
    """
    items = {
        "quantified_achievements": 2.5,
        "clean_formatting": 1.5,
        "strong_projects_listed": 2.5,
        "no_fluff": 1.5,
        "one_page": 1.0,
        "ats_friendly": 1.0,
    }
    checked = set(intake.get("resume_checklist", []))
    total = sum(pts for item, pts in items.items() if item in checked)
    missing = [item for item in items if item not in checked]
    gap_flags = [f"resume:{item}" for item in missing]

    return {"score": round(total, 2), "max": 10, "detail": {"missing": missing}, "gap_flags": gap_flags}


def score_coding_speed(intake: dict) -> dict:
    """
    intake = {
        "easy_under_15min": bool, "medium_under_35min": bool, "hard_under_60min": bool,
        "debugs_independently": bool, "writes_clean_code": bool
    }
    Behavior-anchored self-report, not a vague 1-5 scale.
    """
    weights = {
        "easy_under_15min": 2.5,
        "medium_under_35min": 3.0,
        "hard_under_60min": 2.0,
        "debugs_independently": 1.5,
        "writes_clean_code": 1.0,
    }
    total = sum(pts for key, pts in weights.items() if intake.get(key))
    gap_flags = [f"coding_speed:{key}" for key in weights if not intake.get(key)]

    return {"score": round(total, 2), "max": 10, "detail": {}, "gap_flags": gap_flags}


def score_projects_checklist(intake: dict) -> dict:
    """
    intake = {"project_checklist": [str,...]}  subset of the 6 items below.
    This is the deterministic half (6 pts) of the Projects category.
    The remaining 9 pts (novelty/complexity) are LLM-rubric graded — see app/llm/.
    """
    items = {
        "clean_readme": 1.0,
        "public_github": 1.0,
        "has_tests": 1.0,
        "deployed": 1.5,
        "resume_bullets": 1.0,
        "architecture_diagram": 0.5,
    }
    checked = set(intake.get("project_checklist", []))
    total = sum(pts for item, pts in items.items() if item in checked)
    missing = [item for item in items if item not in checked]
    gap_flags = [f"projects:{item}" for item in missing]

    return {"score": round(total, 2), "max": 6, "detail": {"missing": missing}, "gap_flags": gap_flags}


def score_aptitude(answers: list) -> dict:
    """
    answers = [{"question_id": str, "correct": bool}, ...]  (3-5 randomly sampled puzzles)
    Out of 3, proportional to correctness.
    """
    if not answers:
        return {"score": 0.0, "max": 3, "detail": {"answered": 0}, "gap_flags": ["aptitude:no_answers"]}

    correct = sum(1 for a in answers if a.get("correct"))
    total = (correct / len(answers)) * 3.0
    gap_flags = [] if correct == len(answers) else ["aptitude:reasoning_gap"]

    return {
        "score": round(total, 2),
        "max": 3,
        "detail": {"correct": correct, "total_asked": len(answers)},
        "gap_flags": gap_flags,
    }
