from dotenv import load_dotenv

load_dotenv()

from hive.schema import CompanyProfile
from hive.stages.intake import intake
from hive.stages.discovery import discovery
from hive.stages.enrichment import enrichment
from hive.stages.relevance_contact import relevance_and_contact
from hive.stages.completeness import completeness_check


STAGES = [
    ("Discovery", discovery),
    ("Enrichment", enrichment),
    ("Relevance+Contact", relevance_and_contact),
]


def run_pipeline(company_name: str) -> CompanyProfile:
    profile = CompanyProfile(input_name=company_name)
    profile = intake(profile)  # fail-fast: bad input should stop everything immediately

    stage_failures = []
    for stage_label, stage_fn in STAGES:
        try:
            profile = stage_fn(profile)
        except Exception as e:
            stage_failures.append(f"{stage_label} failed: {e}")

    profile = completeness_check(profile)

    if stage_failures:
        failure_note = "Pipeline errors — " + "; ".join(stage_failures)
        profile.completeness.notes = (
            f"{profile.completeness.notes} {failure_note}"
            if profile.completeness.notes
            else failure_note
        )
        profile.completeness.is_complete = False

    return profile


if __name__ == "__main__":
    import sys

    name = sys.argv[1] if len(sys.argv) > 1 else "Acme"
    result = run_pipeline(name)
    print(result.model_dump_json(indent=2))
