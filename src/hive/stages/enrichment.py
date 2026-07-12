from google.genai import types
from pydantic import BaseModel

from hive.clients import get_tavily_client, get_gemini_client, format_search_results
from hive.schema import CompanyProfile, FundingRound, Product, NewsItem


class EnrichmentResult(BaseModel):
    funding: list[FundingRound] = []
    products: list[Product] = []
    recent_news: list[NewsItem] = []


ENRICHMENT_PROMPT = """You are a research assistant enriching a company profile with
funding history, product offerings, and recent news. The search results below are
grouped into three labeled sections. Using ONLY the results in each section, extract:
- funding: every funding round mentioned (round type, amount, date), each with a source
- products: the company's products or services, each with a source
- recent_news: recent news items (headline, date, brief summary), each with a source

For each item, set "source" to the URL of the specific result it came from. If a
section has no relevant information, return an empty list for that field — do not
invent entries. Do not use outside knowledge; answer only from the text below.

{results}
"""


def enrichment(profile: CompanyProfile) -> CompanyProfile:
    tavily = get_tavily_client()

    funding_results = tavily.search(
        query=f"{profile.canonical_name} funding round investment raised",
        max_results=5,
    )
    product_results = tavily.search(
        query=f"{profile.canonical_name} products features services",
        max_results=5,
    )
    news_results = tavily.search(
        query=f"{profile.canonical_name} recent news",
        max_results=5,
        topic="news",
        time_range="year",
    )

    combined_results = (
        f"=== Funding search results ===\n{format_search_results(funding_results)}\n\n"
        f"=== Product search results ===\n{format_search_results(product_results)}\n\n"
        f"=== Recent news search results ===\n{format_search_results(news_results)}"
    )

    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=ENRICHMENT_PROMPT.format(results=combined_results),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EnrichmentResult,
        ),
    )
    result = EnrichmentResult.model_validate_json(response.text)

    profile.funding = result.funding
    profile.products = result.products
    profile.recent_news = result.recent_news
    return profile
