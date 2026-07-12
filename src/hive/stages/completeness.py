from datetime import date

from google.genai import types
from pydantic import BaseModel

from hive.clients import get_gemini_client
from hive.schema import CompanyProfile


PLACEHOLDER_VALUES = {
    "", "unknown", "n/a", "na", "tbd", "todo", "not found", "none",
    "not available", "no information found", "not specified",
}


class CritiqueResult(BaseModel):
    concerns: list[str] = []


CRITIQUE_PROMPT = """You are a skeptical reviewer checking a company research profile
for quality problems that a simple "is this field empty?" check would miss. An
automated check has already flagged these fields as missing entirely: {missing_fields}
— don't repeat those, they're already known.

Look instead for problems in the fields that ARE filled in:
- vague or generic descriptions that could apply to almost any company
- news items that are stale (compare their dates to today, {today}) rather than
  genuinely recent
- a contact that isn't actually a specific, reachable person (e.g. a title with no real
  name, or a contact method that isn't concrete)
- a relevance statement that reads as generic filler rather than specific to this company

Company profile:
{profile_json}

Return a list of short, specific concerns — one string per issue found. If you find no
real concerns among the filled-in fields, return an empty list.
"""


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip().lower() in PLACEHOLDER_VALUES


def _rule_based_check(profile: CompanyProfile) -> list[str]:
    missing = []
    if _is_missing(profile.canonical_name):
        missing.append("canonical_name")
    if _is_missing(profile.industry.value):
        missing.append("industry")
    if _is_missing(profile.description.value):
        missing.append("description")
    if _is_missing(profile.company_size.value):
        missing.append("company_size")
    if _is_missing(profile.location.value):
        missing.append("location")
    if not profile.funding:
        missing.append("funding")
    if not profile.products:
        missing.append("products")
    if not profile.recent_news:
        missing.append("recent_news")
    if _is_missing(profile.relevance_to_student):
        missing.append("relevance_to_student")
    if _is_missing(profile.contact.name) or _is_missing(profile.contact.contact_method):
        missing.append("contact")
    return missing


def _llm_critique(profile: CompanyProfile, missing_fields: list[str]) -> list[str]:
    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=CRITIQUE_PROMPT.format(
            missing_fields=", ".join(missing_fields) if missing_fields else "none",
            today=date.today().isoformat(),
            profile_json=profile.model_dump_json(indent=2, exclude={"completeness"}),
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CritiqueResult,
        ),
    )
    return CritiqueResult.model_validate_json(response.text).concerns


def completeness_check(profile: CompanyProfile) -> CompanyProfile:
    missing_fields = _rule_based_check(profile)

    try:
        concerns = _llm_critique(profile, missing_fields)
        critique_failed_note = None
    except Exception as e:
        concerns = []
        critique_failed_note = f"Critique pass failed: {e}"

    notes = list(concerns)
    if critique_failed_note:
        notes.append(critique_failed_note)

    profile.completeness.missing_fields = missing_fields
    profile.completeness.notes = "; ".join(notes) if notes else None
    profile.completeness.is_complete = (
        not missing_fields and not concerns and critique_failed_note is None
    )
    return profile
