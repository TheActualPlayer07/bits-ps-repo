from google.genai import types
from pydantic import BaseModel

from hive.clients import get_tavily_client, get_gemini_client, format_search_results
from hive.schema import CompanyProfile, Contact


class RelevanceContactResult(BaseModel):
    relevance_to_student: str
    contact: Contact


RELEVANCE_CONTACT_PROMPT = """You are helping a student evaluate a company as a
potential internship/career opportunity and find a way to reach out.

Here is what has already been researched about the company:
{profile_summary}

Task 1 — Relevance: In 2-3 sentences, explain why this company could be worth a
student's attention, based specifically on the facts above (industry, growth stage,
recent developments, products) rather than generic statements. This is your own
reasoned synthesis, not a fact that needs a citation.

Below are web search results about people who might be a real point of contact for
recruiting or careers at this company:
{contact_results}

Task 2 — Contact: Using ONLY the search results above, identify a real, named person
and role who could realistically be contacted about opportunities (e.g. a recruiter,
talent acquisition lead, or university relations contact), their contact method
(LinkedIn URL, email, or similar), and the source URL it came from. If no real, specific
person is found in the search results, leave name, role, contact_method, and source all
null rather than inventing one — do not use outside knowledge for this part.
"""


def _summarize_profile(profile: CompanyProfile) -> str:
    lines = [
        f"Industry: {profile.industry.value}",
        f"Description: {profile.description.value}",
        f"Company size: {profile.company_size.value}",
        f"Location: {profile.location.value}",
    ]
    if profile.funding:
        lines.append(
            "Funding: "
            + "; ".join(
                f"{f.round_type or 'a round'} of {f.amount or 'an undisclosed amount'}"
                f"{f' in {f.date}' if f.date else ''}"
                for f in profile.funding
            )
        )
    if profile.products:
        lines.append("Products: " + "; ".join(p.name for p in profile.products if p.name))
    if profile.recent_news:
        lines.append(
            "Recent news: " + "; ".join(n.headline for n in profile.recent_news if n.headline)
        )
    return "\n".join(lines)


def relevance_and_contact(profile: CompanyProfile) -> CompanyProfile:
    tavily = get_tavily_client()
    contact_results = tavily.search(
        query=f"{profile.canonical_name} recruiter talent acquisition careers linkedin",
        max_results=5,
    )

    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=RELEVANCE_CONTACT_PROMPT.format(
            profile_summary=_summarize_profile(profile),
            contact_results=format_search_results(contact_results),
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RelevanceContactResult,
        ),
    )
    result = RelevanceContactResult.model_validate_json(response.text)

    profile.relevance_to_student = result.relevance_to_student
    profile.contact = result.contact
    return profile
