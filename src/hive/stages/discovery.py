from google.genai import types
from pydantic import BaseModel

from hive.clients import get_tavily_client, get_gemini_client, format_search_results
from hive.schema import CompanyProfile, SourcedField


class DiscoveryResult(BaseModel):
    industry: SourcedField
    description: SourcedField
    company_size: SourcedField
    location: SourcedField


DISCOVERY_PROMPT = """You are a research assistant building a factual company profile.
Using ONLY the search results below, extract:
- industry: what industry/sector the company operates in
- description: a short (1-2 sentence) factual description of what the company does
- company_size: employee count or size category, if mentioned
- location: the company's headquarters location

For each field, set "source" to the URL of the specific result the fact came from.
If a fact is not present anywhere in the search results, set both "value" and "source"
to null for that field. Do not use any outside knowledge — answer only from the text
below.

Search results:
{results}
"""


def discovery(profile: CompanyProfile) -> CompanyProfile:
    tavily = get_tavily_client()
    search_response = tavily.search(
        query=f"{profile.canonical_name} company overview industry size headquarters",
        max_results=5,
    )
    results_text = format_search_results(search_response)

    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=DISCOVERY_PROMPT.format(results=results_text),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DiscoveryResult,
        ),
    )
    result = DiscoveryResult.model_validate_json(response.text)

    profile.industry = result.industry
    profile.description = result.description
    profile.company_size = result.company_size
    profile.location = result.location
    return profile
