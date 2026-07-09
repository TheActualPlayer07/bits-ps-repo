"""
Turns result["gap_flags"] into a concrete, prioritized action plan.

Fully deterministic — no new LLM call. Two reasons:
1. The advice structure for most gap types (pattern name -> what to revisit
   and practice) is fixed enough to template reliably and consistently.
2. For the three LLM-graded categories (Projects, Explanation Clarity,
   HR/Behavioral), the grader already produced a specific `rationale` string
   for this student's actual answer — reusing that is more specific than
   anything a fresh, context-free LLM call could generate, and costs nothing.

Each action item: {"title", "why", "action", "priority", "category"}
priority is a 1-3 int (3 = fix this first) used only for sorting/display,
derived from how heavily-weighted the category is in the overall rubric.
"""
from app.scoring.config import CATEGORY_WEIGHTS

PATTERN_ADVICE = {
    "two_pointers": {
        "title": "Two Pointers",
        "practice": "Practice on: finding a pair in a sorted array that sums to a target; merging two sorted arrays in place; removing duplicates from a sorted array in one pass.",
    },
    "sliding_window": {
        "title": "Sliding Window",
        "practice": "Practice on: longest substring without repeating characters; smallest subarray with a sum at least X; maximum sum of any contiguous window of fixed size.",
    },
    "binary_search": {
        "title": "Binary Search",
        "practice": "Practice on: finding an element in a rotated sorted array; finding the first/last occurrence of a value; search-space reduction problems (e.g. minimizing a value that satisfies a condition).",
    },
    "trees": {
        "title": "Tree Traversal",
        "practice": "Practice on: max depth / balanced-tree checks; level-order traversal; validating a binary search tree.",
    },
    "graphs": {
        "title": "Graph Traversal (DFS/BFS)",
        "practice": "Practice on: counting connected components; detecting a cycle; flood-fill style grid traversal problems.",
    },
    "shortest_path": {
        "title": "Shortest Path Algorithms",
        "practice": "Practice on: Dijkstra's algorithm on a weighted graph; BFS shortest path on an unweighted grid; understanding when Bellman-Ford is needed instead (negative weights).",
    },
    "dynamic_programming": {
        "title": "Dynamic Programming",
        "practice": "Practice on: climbing stairs / Fibonacci-style problems to build intuition; 0/1 knapsack; longest common subsequence.",
    },
    "hashing": {
        "title": "Hashing / Frequency Counting",
        "practice": "Practice on: two-sum with a hash map; grouping anagrams; detecting duplicates in near-linear time.",
    },
    "heap": {
        "title": "Heaps / Priority Queues",
        "practice": "Practice on: k largest/smallest elements in a stream; merging k sorted lists; scheduling problems with a min-heap.",
    },
    "backtracking": {
        "title": "Backtracking",
        "practice": "Practice on: generating all subsets/permutations; N-Queens; Sudoku-style constraint problems.",
    },
    "prefix_sum": {"title": "Prefix Sums", "practice": "Practice on: subarray sum equals target; range-sum queries; equilibrium-index style problems."},
    "linked_list": {"title": "Linked Lists", "practice": "Practice on: reversing a linked list; detecting a cycle (Floyd's algorithm); merging two sorted linked lists."},
    "bst": {"title": "Binary Search Trees", "practice": "Practice on: validating a BST; finding the kth smallest element; inserting/deleting while maintaining BST order."},
    "topological_sort": {"title": "Topological Sort", "practice": "Practice on: course-scheduling style dependency problems; detecting cycles in a directed graph."},
    "union_find": {"title": "Union-Find (Disjoint Set)", "practice": "Practice on: counting connected components; detecting redundant connections; grouping accounts by shared attributes."},
    "greedy": {"title": "Greedy Algorithms", "practice": "Practice on: interval scheduling; jump-game style reachability; minimum coins with well-behaved denominations."},
    "stack": {"title": "Stacks", "practice": "Practice on: valid parentheses matching; next-greater-element problems; evaluating postfix expressions."},
    "queue": {"title": "Queues", "practice": "Practice on: level-order traversal; sliding-window maximum with a deque; implementing a queue with two stacks."},
    "trie": {"title": "Tries", "practice": "Practice on: autocomplete/prefix-matching; word search in a dictionary; longest common prefix problems."},
    "bit_manipulation": {"title": "Bit Manipulation", "practice": "Practice on: counting set bits; finding the single non-duplicate number in an array; basic XOR-based tricks."},
    "segment_tree": {"title": "Segment Trees", "practice": "Practice on: range-sum/range-min queries with updates; understanding when a segment tree beats a prefix-sum array."},
    "arrays": {"title": "Array Fundamentals", "practice": "Practice on: in-place rotation; merging intervals; basic partitioning problems."},
}

CS_FUNDAMENTALS_ADVICE = {
    "os": "Revisit processes vs threads, deadlock conditions, paging, CPU scheduling, and virtual memory — these come up constantly in OS-focused interview rounds.",
    "dbms": "Revisit indexing, normalization, transactions, isolation levels, and join types — a common source of surprise questions even in coding-focused interviews.",
    "cn": "Revisit TCP vs UDP, the HTTP request lifecycle, DNS resolution, and basic routing — brief but frequent in system-design-adjacent rounds.",
    "oop": "Revisit inheritance, polymorphism, the SOLID principles, and virtual functions — often tested through short design questions rather than direct definitions.",
}

RESUME_ADVICE = {
    "quantified_achievements": "Add numbers to your bullet points — e.g. 'reduced load time by 40%' instead of 'improved performance.' Recruiters skim; numbers stop the skim.",
    "clean_formatting": "Clean up formatting inconsistencies — mismatched fonts, spacing, or bullet styles are the fastest way to get skimmed past.",
    "strong_projects_listed": "Make sure your strongest 2-3 projects are clearly listed with a one-line impact statement each, not just a tech-stack list.",
    "no_fluff": "Cut generic filler phrases ('hardworking team player') — every line should say something only you could say.",
    "one_page": "Trim to one page. A longer resume for an entry-level role usually signals padding, not depth.",
    "ats_friendly": "Avoid tables, columns, and graphics that ATS parsers choke on — stick to a single-column, plain-text-parseable layout.",
}

CODING_SPEED_ADVICE = {
    "easy_under_15min": "Time yourself on Easy-difficulty problems until you consistently finish under 15 minutes — right now that's not happening, which suggests the fundamentals need more repetition before speed will follow.",
    "medium_under_35min": "Push your Medium-problem solve time down toward 35 minutes through timed practice — untimed practice builds correctness but not speed.",
    "hard_under_60min": "Hard problems under 60 minutes usually come from pattern recognition, not raw speed — this will likely improve on its own as your pattern coverage (DSA section above) improves.",
    "debugs_independently": "Practice debugging without immediately reaching for help — deliberately introduce a bug into your own past solutions and force yourself to trace it.",
    "writes_clean_code": "Practice naming variables and structuring solutions clearly even under time pressure — interviewers read your code, not just your final answer.",
}

EXPERIENCE_ADVICE = {
    "has_internship": "Look for even a short internship or research assistantship — it's one of the highest-leverage gaps to close before placement season, more valuable than another certification.",
    "internship_relevant": "If your internship experience isn't closely related to your target role, be ready to explicitly bridge the connection in interviews rather than leaving it implicit.",
    "internship_2plus_months": "A short internship still counts, but a 2+ month one gives you enough to speak about with real depth — worth prioritizing if you have time before placements.",
    "has_certification": "A relevant certification is a fast way to signal directed effort, especially if your other categories are still developing.",
    "certification_relevant": "Make sure any certification you hold is directly relevant to your target role — an unrelated certificate rarely moves the needle with recruiters.",
}

DSA_CATEGORY_ADVICE_DEFAULT = "You didn't recognize the shape of this problem at all — worth reviewing the category broadly (not just one technique) before drilling specific patterns."


def _priority_for(category_weight_key: str, sub_weight: float = None) -> int:
    """Rough 1-3 priority derived from how heavily-weighted the category is."""
    weight = sub_weight if sub_weight is not None else CATEGORY_WEIGHTS.get(category_weight_key, {}).get("total", 0)
    if weight >= 15:
        return 3
    elif weight >= 8:
        return 2
    return 1


def _advice_for_flag(flag: str, result: dict):
    prefix, _, detail = flag.partition(":")

    if prefix == "pattern":
        info = PATTERN_ADVICE.get(detail, {"title": detail.replace("_", " ").title(), "practice": "Review this technique and attempt a few problems that specifically require it."})
        return {
            "category": "DSA", "priority": 3,
            "title": f"Revisit the {info['title']} technique",
            "why": "You either flagged this as unfamiliar, or answered a related question with a brute-force/suboptimal approach instead of the optimal one.",
            "action": info["practice"],
        }

    if prefix == "dsa_category":
        return {
            "category": "DSA", "priority": 3,
            "title": f"Review {detail} fundamentals",
            "why": DSA_CATEGORY_ADVICE_DEFAULT,
            "action": f"Before drilling specific techniques, spend time understanding what kinds of problems fall under {detail} and what makes them recognizable.",
        }

    if prefix == "cs_fundamentals":
        return {
            "category": "CS Fundamentals", "priority": _priority_for("cs_fundamentals"),
            "title": f"Strengthen {detail.upper()} fundamentals",
            "why": "This topic scored below a comfortable threshold in your self-assessment.",
            "action": CS_FUNDAMENTALS_ADVICE.get(detail, f"Revisit core {detail.upper()} concepts."),
        }

    if prefix == "resume":
        return {
            "category": "Resume", "priority": _priority_for("resume"),
            "title": f"Fix: {detail.replace('_', ' ')}",
            "why": "This is a checklist item recruiters commonly screen for.",
            "action": RESUME_ADVICE.get(detail, f"Address: {detail.replace('_', ' ')}."),
        }

    if prefix == "coding_speed":
        return {
            "category": "Coding Speed", "priority": _priority_for("coding_speed"),
            "title": f"Work on: {detail.replace('_', ' ')}",
            "why": "Flagged as a 'no' on your behavior-anchored self-report.",
            "action": CODING_SPEED_ADVICE.get(detail, "Practice this specific behavior under timed conditions."),
        }

    if prefix == "experience":
        return {
            "category": "Experience & Certifications", "priority": _priority_for("experience_certifications"),
            "title": f"Gap: {detail.replace('_', ' ')}",
            "why": "Missing from your Experience & Certifications intake.",
            "action": EXPERIENCE_ADVICE.get(detail, f"Address: {detail.replace('_', ' ')}."),
        }

    if prefix == "aptitude":
        return {
            "category": "Aptitude", "priority": _priority_for("aptitude"),
            "title": "Brush up on reasoning/logic puzzles",
            "why": "You missed one or more sampled aptitude questions.",
            "action": "Spend 15-20 minutes a few times a week on logic/probability puzzles — this category responds quickly to light, regular practice.",
        }

    if prefix == "projects":
        if detail in ("low_novelty", "low_complexity"):
            rationale = result["categories"].get("projects_quality", {}).get("detail", {}).get("rationale", "")
            return {
                "category": "Projects", "priority": _priority_for("projects", CATEGORY_WEIGHTS["projects"]["quality"]),
                "title": f"Strengthen project {detail.replace('low_', '')}",
                "why": rationale or "Your project description read as lower novelty/complexity than average.",
                "action": "Consider extending this project with a genuinely nontrivial piece — a custom algorithm, a real constraint to solve, or a component you haven't built before — rather than starting a new one from scratch.",
            }
        return {
            "category": "Projects", "priority": _priority_for("projects", CATEGORY_WEIGHTS["projects"]["checklist"]),
            "title": f"Add: {detail.replace('_', ' ')}",
            "why": "Missing from your project checklist.",
            "action": f"Add {detail.replace('_', ' ')} to your strongest project before placement season.",
        }

    if prefix == "explanation_clarity":
        rationale = result["categories"].get("explanation_clarity", {}).get("detail", {}).get("rationale", "")
        dim_labels = {
            "structure": "leading with structure before detail",
            "complexity_mention": "mentioning complexity/tradeoffs",
            "clarity": "cutting hand-waving/filler language",
            "audience_awareness": "adjusting explanation depth to the audience",
        }
        return {
            "category": "Explanation Clarity", "priority": _priority_for("explanation_clarity"),
            "title": f"Improve: {dim_labels.get(detail, detail)}",
            "why": rationale or "This dimension scored low in your written technical explanation.",
            "action": "Rewrite your explanation focusing specifically on this dimension, then read it aloud — awkward or vague spots are usually obvious out loud.",
        }

    if prefix == "hr_behavioral":
        per_q = result["categories"].get("hr_behavioral", {}).get("detail", {}).get("per_question", [])
        rationale = next((q["rationale"] for q in per_q if q.get("question_id") == detail), "")
        return {
            "category": "HR/Behavioral", "priority": _priority_for("hr_behavioral"),
            "title": "Sharpen a behavioral answer",
            "why": rationale or "This answer read as generic or under-specific.",
            "action": "Rewrite this answer with one concrete, specific detail (a real project, a real number, a real moment) instead of a general statement.",
        }

    if detail == "llm_unavailable":
        return {
            "category": prefix, "priority": 1,
            "title": f"{prefix.replace('_', ' ').title()} couldn't be graded",
            "why": "The grading service was unreachable when you submitted.",
            "action": "Re-run your assessment once the grading service is available for a complete score in this category.",
        }

    return None  # unrecognized flag — skip rather than show a broken item


def generate_action_plan(result: dict) -> dict:
    """
    result: the full dict returned by aggregator.run_full_scoring()
    Returns {"urgency_level", "urgency_message", "top_priority": [...], "full_plan": [...]}
    """
    items = []
    seen = set()
    for flag in result["gap_flags"]:
        if flag in seen:
            continue
        seen.add(flag)
        item = _advice_for_flag(flag, result)
        if item:
            items.append(item)

    items.sort(key=lambda i: i["priority"], reverse=True)

    return {
        "urgency_level": result["urgency"]["level"],
        "urgency_message": result["urgency"]["message"],
        "top_priority": items[:3],
        "full_plan": items,
    }
