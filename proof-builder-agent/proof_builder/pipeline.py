"""
The Proof Builder Agent's entry point: one raw activity description in,
all seven proof artifacts out.

    facts = intake.extract_facts(raw_activity)        # 1 call - canonical ledger
    public_proof.generate(facts)                       # 1 call - resume bullet + LinkedIn post
    presentation.generate(facts)                        # 1 call - portfolio card + proof summary
    evaluator.generate(facts)                           # 1 call - skill evidence + recruiter description
    improvement.generate(facts)                         # 1 call - improvement suggestion

Five LLM calls total per run, comfortably inside Groq's free-tier 30
requests/minute limit, and every generator reads from the exact same facts
ledger so the seven outputs can't drift apart or contradict each other.
"""

from . import intake
from .generators import evaluator, improvement, presentation, public_proof

OUTPUT_KEYS = [
    "resume_bullet",
    "linkedin_post",
    "portfolio_card",
    "proof_summary",
    "skill_evidence",
    "recruiter_description",
    "improvement_suggestion",
]


def run_pipeline(raw_activity: str) -> dict:
    """Run the full seven-artifact pipeline for one activity description."""
    facts = intake.extract_facts(raw_activity)

    public = public_proof.generate(facts)
    pres = presentation.generate(facts)
    eval_out = evaluator.generate(facts)
    imp = improvement.generate(facts)

    artifacts = {
        **public,
        **pres,
        **eval_out,
        **imp,
    }

    return {
        "facts": facts,
        "artifacts": artifacts,
    }
