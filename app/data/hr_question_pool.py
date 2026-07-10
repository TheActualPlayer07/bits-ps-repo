"""
HR/Behavioral question pool — well-known, generic interview questions
(standard industry phrasing, not owned by any single source).
2-3 are randomly sampled per intake session. Answers are free-text,
graded by the LLM grader (see app/llm/) against the rubric dimensions:
specificity, coherence with the student's own profile, self-awareness,
and avoidance of cliché/filler language.

`focus` documents what each question is actually probing, so the grader
prompt can weight its read of the answer accordingly.
"""

HR_QUESTION_POOL = [
    {"id": "hr_001", "category": "self_awareness", "question_text": "Tell me about yourself.",
     "focus": "Structure and relevance — does the answer connect to their actual field/goals, or ramble generically?"},
    {"id": "hr_002", "category": "motivation", "question_text": "Where do you see yourself in 5 years?",
     "focus": "Specificity and coherence with their current trajectory, not generic ambition statements."},
    {"id": "hr_003", "category": "motivation", "question_text": "Why do you want to work in this field/role?",
     "focus": "Concrete reasoning tied to their own experience, not a generic 'I'm passionate about it.'"},
    {"id": "hr_004", "category": "self_reflection", "question_text": "Describe a challenge you faced and how you handled it.",
     "focus": "Real reflection — what they learned or would do differently, not just narrating events."},
    {"id": "hr_005", "category": "self_awareness", "question_text": "What are your greatest strengths?",
     "focus": "Backed by a specific example, not just a claimed trait with no evidence."},
    {"id": "hr_006", "category": "self_awareness", "question_text": "What is your biggest weakness?",
     "focus": "Genuine self-awareness vs. a disguised humble-brag ('I work too hard')."},
    {"id": "hr_007", "category": "teamwork", "question_text": "Describe a time you worked in a team and there was a disagreement. How did you handle it?",
     "focus": "Specific conflict-resolution approach, not a vague 'we talked it out.'"},
    {"id": "hr_008", "category": "motivation", "question_text": "Why should we hire you over other candidates?",
     "focus": "Specific, evidence-backed differentiation vs. generic self-praise."},
    {"id": "hr_009", "category": "self_reflection", "question_text": "Tell me about a time you failed. What did you learn?",
     "focus": "Honesty and depth of the lesson learned, not a sanitized non-failure."},
    {"id": "hr_010", "category": "adaptability", "question_text": "Describe a situation where you had to adapt to a significant change.",
     "focus": "Concrete actions taken to adapt, not just acknowledging change happened."},
    {"id": "hr_011", "category": "leadership", "question_text": "Describe a time you took initiative or led something without being asked.",
     "focus": "A real, specific instance of ownership, not a generic leadership claim."},
    {"id": "hr_012", "category": "motivation", "question_text": "What do you know about our company/industry, and why does it interest you?",
     "focus": "Whether the answer shows real research/thought vs. filler enthusiasm."},
    {"id": "hr_013", "category": "self_reflection", "question_text": "How do you handle stress or pressure?",
     "focus": "A concrete coping strategy or example, not just 'I stay calm.'"},
    {"id": "hr_014", "category": "teamwork", "question_text": "Do you prefer working alone or in a team? Why?",
     "focus": "A reasoned, self-aware answer rather than a safe non-answer."},
    {"id": "hr_015", "category": "goal_setting", "question_text": "What are your short-term and long-term career goals?",
     "focus": "Specificity and whether the two goals actually connect logically."},
    {"id": "hr_016", "category": "self_reflection", "question_text": "Tell me about a time you received difficult feedback. How did you respond?",
     "focus": "Whether they show genuine receptiveness vs. defensiveness dressed as humility."},
    {"id": "hr_017", "category": "problem_solving", "question_text": "Describe a time you solved a problem creatively.",
     "focus": "A real example with a specific creative angle, not a generic technical fix."},
    {"id": "hr_018", "category": "motivation", "question_text": "What motivates you to do your best work?",
     "focus": "A genuine, specific driver vs. a generic 'I love learning' filler line."},
    {"id": "hr_019", "category": "leadership", "question_text": "Describe your ideal work environment or team culture.",
     "focus": "Self-aware and specific, not a checklist of buzzwords."},
    {"id": "hr_020", "category": "self_reflection", "question_text": "What's an accomplishment you're most proud of, and why?",
     "focus": "Personal specificity and clear reasoning for why it matters to them."},
    {"id": "hr_021", "category": "adaptability", "question_text": "How do you prioritize when you have multiple deadlines at once?",
     "focus": "A real, describable method, not just 'I make a to-do list.'"},
    {"id": "hr_022", "category": "goal_setting", "question_text": "What does success look like to you?",
     "focus": "Personal, specific definition vs. a generic 'being happy and successful' answer."},
]


def get_random_sample(n: int = 3):
    """Returns n random HR questions (full question shown to client — no hidden grading key needed here)."""
    import random
    sample = random.sample(HR_QUESTION_POOL, k=min(n, len(HR_QUESTION_POOL)))
    return [{"id": q["id"], "category": q["category"], "question_text": q["question_text"]} for q in sample]


def get_focus(question_id: str):
    """Looks up the grading focus note for one question, used by the LLM grader prompt."""
    for q in HR_QUESTION_POOL:
        if q["id"] == question_id:
            return q["focus"]
    return None
