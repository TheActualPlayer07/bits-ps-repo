"""
Aptitude puzzle bank — deterministic, right/wrong scoring only.
3-5 are randomly sampled per intake session.
Answer format expected from the form: the option id the student picked.
"""

APTITUDE_BANK = [
    {
        "id": "apt_001",
        "type": "logical",
        "question": "A father is 3 times as old as his son. In 12 years, he will be twice as old. How old is the son now?",
        "options": [
            {"id": "a", "text": "10"},
            {"id": "b", "text": "12"},
            {"id": "c", "text": "14"},
            {"id": "d", "text": "16"},
        ],
        "correct_option_id": "b",
    },
    {
        "id": "apt_002",
        "type": "probability",
        "question": "You flip a fair coin 3 times. What's the probability of getting exactly 2 heads?",
        "options": [
            {"id": "a", "text": "1/8"},
            {"id": "b", "text": "1/4"},
            {"id": "c", "text": "3/8"},
            {"id": "d", "text": "1/2"},
        ],
        "correct_option_id": "c",
    },
    {
        "id": "apt_003",
        "type": "logical",
        "question": "If all Zips are Zaps, and some Zaps are Zops, which statement must be true?",
        "options": [
            {"id": "a", "text": "All Zips are Zops"},
            {"id": "b", "text": "Some Zips may be Zops"},
            {"id": "c", "text": "No Zips are Zops"},
            {"id": "d", "text": "All Zops are Zips"},
        ],
        "correct_option_id": "b",
    },
    {
        "id": "apt_004",
        "type": "numerical",
        "question": "A shopkeeper marks up a product by 25% then gives a 20% discount on the marked price. What's the net effect on the original price?",
        "options": [
            {"id": "a", "text": "No change"},
            {"id": "b", "text": "5% increase"},
            {"id": "c", "text": "5% decrease"},
            {"id": "d", "text": "10% decrease"},
        ],
        "correct_option_id": "a",
    },
    {
        "id": "apt_005",
        "type": "puzzle",
        "question": "You have two ropes, each takes exactly 1 hour to burn but burns unevenly. How do you measure exactly 45 minutes?",
        "options": [
            {"id": "a", "text": "Burn one rope fully, then half of the second"},
            {"id": "b", "text": "Light one rope at both ends and the other at one end simultaneously; when the first burns out, light the second rope's other end"},
            {"id": "c", "text": "Cut both ropes in half and burn one half of each"},
            {"id": "d", "text": "It's not possible with uneven-burning ropes"},
        ],
        "correct_option_id": "b",
    },
    {
        "id": "apt_006",
        "type": "logical",
        "question": "In a race, you overtake the person in 2nd place. What position are you now in?",
        "options": [
            {"id": "a", "text": "1st"},
            {"id": "b", "text": "2nd"},
            {"id": "c", "text": "3rd"},
            {"id": "d", "text": "Depends on the race"},
        ],
        "correct_option_id": "b",
    },
    {
        "id": "apt_007",
        "type": "numerical",
        "question": "A train 200m long crosses a platform 300m long in 25 seconds. What's the train's speed?",
        "options": [
            {"id": "a", "text": "18 km/h"},
            {"id": "b", "text": "54 km/h"},
            {"id": "c", "text": "72 km/h"},
            {"id": "d", "text": "90 km/h"},
        ],
        "correct_option_id": "c",
    },
    {
        "id": "apt_008",
        "type": "puzzle",
        "question": "You have 8 identical-looking balls, one is heavier. Using a balance scale, what's the minimum number of weighings to find it?",
        "options": [
            {"id": "a", "text": "1"},
            {"id": "b", "text": "2"},
            {"id": "c", "text": "3"},
            {"id": "d", "text": "4"},
        ],
        "correct_option_id": "b",
    },
]


def get_random_sample(n: int = 4):
    """Returns n random puzzles (without their correct answers exposed to the client)."""
    import random
    sample = random.sample(APTITUDE_BANK, k=min(n, len(APTITUDE_BANK)))
    return [
        {"id": q["id"], "type": q["type"], "question": q["question"], "options": q["options"]}
        for q in sample
    ]


def grade_answers(submitted: list) -> list:
    """
    submitted = [{"question_id": str, "selected_option_id": str}, ...]
    Returns [{"question_id": str, "correct": bool}, ...] for score_aptitude() to consume.
    """
    lookup = {q["id"]: q["correct_option_id"] for q in APTITUDE_BANK}
    return [
        {"question_id": s["question_id"],
         "correct": lookup.get(s["question_id"]) == s.get("selected_option_id")}
        for s in submitted if s["question_id"] in lookup
    ]
