"""
DSA conceptual question bank — direct technique/complexity questions.
No references to LeetCode/NeetCode or any named external problem; each
question is an original, pattern-focused prompt. Free-text answers are
graded by the LLM grader (see app/llm/) against expected_pattern /
expected_complexity / known_suboptimal_approaches below.

pattern_tag values must match the pattern names used in
app/scoring/deterministic.py (ALL_PATTERNS) so gap detection can
cross-reference quiz misses against the self-report checklist.
"""

DSA_QUESTION_BANK = [
    {
        "id": "dsa_q001",
        "category": "Arrays",
        "pattern_tag": "two_pointers",
        "difficulty": "Medium",
        "question_text": "You need to find whether a sorted array contains two elements that sum to a target value, without using extra space, in better than O(n^2) time. What technique would you use, and what's its time complexity?",
        "expected_pattern": "Two Pointers",
        "expected_complexity": "O(n)",
        "known_suboptimal_approaches": [
            "Nested loop checking every pair — O(n^2)",
            "Hash set lookup — O(n) time but uses O(n) extra space, which the question rules out",
        ],
        "model_answer": "Use two pointers starting at each end of the sorted array, moving the low pointer up or high pointer down based on whether the current sum is too small or too large. Single pass, O(n) time, O(1) space.",
    },
    {
        "id": "dsa_q002",
        "category": "Arrays",
        "pattern_tag": "sliding_window",
        "difficulty": "Medium",
        "question_text": "You need to find the length of the longest contiguous subarray whose elements sum to at most a given value, in a single pass. What technique fits, and what's the time complexity?",
        "expected_pattern": "Sliding Window",
        "expected_complexity": "O(n)",
        "known_suboptimal_approaches": [
            "Checking every subarray — O(n^2) or O(n^3) depending on how the sum is recomputed",
        ],
        "model_answer": "A sliding window with two pointers expands the window while the sum is within bounds and contracts it when it exceeds the limit, giving O(n) time since each pointer moves forward at most n times.",
    },
    {
        "id": "dsa_q003",
        "category": "Searching",
        "pattern_tag": "binary_search",
        "difficulty": "Easy",
        "question_text": "You have a sorted array of a million elements and need to find whether a target value exists. What's the optimal approach and its time complexity?",
        "expected_pattern": "Binary Search",
        "expected_complexity": "O(log n)",
        "known_suboptimal_approaches": [
            "Linear scan through the array — O(n)",
        ],
        "model_answer": "Binary search repeatedly halves the search space by comparing the target to the middle element, giving O(log n) time.",
    },
    {
        "id": "dsa_q004",
        "category": "Trees",
        "pattern_tag": "trees",
        "difficulty": "Medium",
        "question_text": "You need to find the maximum depth of a binary tree. What approach would you use, and what's the time and space complexity?",
        "expected_pattern": "DFS (recursive tree traversal)",
        "expected_complexity": "O(n) time, O(h) space where h is tree height",
        "known_suboptimal_approaches": [
            "Iterative BFS level-by-level counting is also valid at O(n) time — not suboptimal, just a different valid approach",
        ],
        "model_answer": "Recursively compute the depth of the left and right subtrees and return 1 plus the larger of the two. O(n) time since every node is visited once, O(h) space for the recursion stack.",
    },
    {
        "id": "dsa_q005",
        "category": "Graphs",
        "pattern_tag": "graphs",
        "difficulty": "Medium",
        "question_text": "Given a graph, you need to determine if it's possible to visit every node starting from a given node. Which traversal technique fits, and what's the time complexity in terms of vertices V and edges E?",
        "expected_pattern": "DFS or BFS",
        "expected_complexity": "O(V + E)",
        "known_suboptimal_approaches": [
            "Checking reachability between every pair of nodes independently — much worse than O(V+E)",
        ],
        "model_answer": "A DFS or BFS from the starting node visits every reachable node exactly once, giving O(V + E) time since each vertex and edge is processed a constant number of times.",
    },
    {
        "id": "dsa_q006",
        "category": "Graphs",
        "pattern_tag": "shortest_path",
        "difficulty": "Hard",
        "question_text": "You need to find the shortest path between two nodes in a weighted graph with no negative edge weights. What algorithm fits, and what's its time complexity with a binary heap?",
        "expected_pattern": "Dijkstra's Algorithm",
        "expected_complexity": "O((V + E) log V)",
        "known_suboptimal_approaches": [
            "Brute-force checking every possible path — exponential time",
            "Bellman-Ford — O(VE), correct but slower than necessary since there are no negative weights",
        ],
        "model_answer": "Dijkstra's algorithm with a min-heap greedily expands the closest unvisited node each time, giving O((V+E) log V) time.",
    },
    {
        "id": "dsa_q007",
        "category": "Dynamic Programming",
        "pattern_tag": "dynamic_programming",
        "difficulty": "Medium",
        "question_text": "You need to find the minimum number of coins to make a given amount, from a set of coin denominations. Naive recursion is exponential — what technique fixes this, and what's the resulting time complexity?",
        "expected_pattern": "Dynamic Programming (bottom-up tabulation or memoization)",
        "expected_complexity": "O(amount * number_of_denominations)",
        "known_suboptimal_approaches": [
            "Plain recursion without memoization — exponential time due to repeated subproblems",
            "Greedy always picking the largest coin — fast but not always correct for arbitrary denominations",
        ],
        "model_answer": "Build a DP table where each entry represents the minimum coins needed for that amount, filling it bottom-up using previously computed smaller amounts. This avoids recomputation, giving O(amount * denominations) time.",
    },
    {
        "id": "dsa_q008",
        "category": "Hashing",
        "pattern_tag": "hashing",
        "difficulty": "Easy",
        "question_text": "You need to check if two strings are anagrams of each other. What's the most efficient approach, and its time complexity?",
        "expected_pattern": "Hashing / frequency count",
        "expected_complexity": "O(n)",
        "known_suboptimal_approaches": [
            "Sorting both strings and comparing — O(n log n)",
        ],
        "model_answer": "Count character frequencies for both strings using a hash map (or fixed-size array for a known alphabet), then compare the counts. O(n) time.",
    },
    {
        "id": "dsa_q009",
        "category": "Heaps",
        "pattern_tag": "heap",
        "difficulty": "Medium",
        "question_text": "You need to continuously find the k largest elements in a stream of numbers as new numbers arrive. What data structure fits best, and what's the time complexity per insertion?",
        "expected_pattern": "Min-heap of size k",
        "expected_complexity": "O(log k) per insertion",
        "known_suboptimal_approaches": [
            "Re-sorting the entire stream after every new number — O(n log n) per insertion",
        ],
        "model_answer": "Maintain a min-heap of size k; for each new number, push it in and pop the smallest if the heap exceeds size k. Each operation is O(log k).",
    },
    {
        "id": "dsa_q010",
        "category": "Backtracking",
        "pattern_tag": "backtracking",
        "difficulty": "Hard",
        "question_text": "You need to generate all valid combinations of balanced parentheses for a given number of pairs. What technique fits, and roughly how would you describe its time complexity?",
        "expected_pattern": "Backtracking",
        "expected_complexity": "Exponential, bounded by the Catalan number for n pairs (roughly O(4^n / sqrt(n)))",
        "known_suboptimal_approaches": [
            "Generating all possible strings of parentheses and filtering the valid ones — far worse, since it doesn't prune invalid branches early",
        ],
        "model_answer": "Backtracking builds the string character by character, only adding a '(' or ')' when it keeps the sequence valid, pruning invalid paths early instead of generating everything and filtering after.",
    },
]


def get_random_sample(n: int = 4):
    """Returns n random questions (without grading metadata exposed to the client)."""
    import random
    sample = random.sample(DSA_QUESTION_BANK, k=min(n, len(DSA_QUESTION_BANK)))
    return [
        {"id": q["id"], "category": q["category"], "difficulty": q["difficulty"],
         "question_text": q["question_text"]}
        for q in sample
    ]


def get_grading_metadata(question_id: str):
    """Looks up the full grading context for one question, used by the LLM grader."""
    for q in DSA_QUESTION_BANK:
        if q["id"] == question_id:
            return q
    return None
