import os

from google import genai
from tavily import TavilyClient


def get_tavily_client() -> TavilyClient:
    return TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def get_gemini_client() -> genai.Client:
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def format_search_results(search_response: dict) -> str:
    return "\n\n".join(
        f"URL: {result['url']}\nContent: {result['content']}"
        for result in search_response["results"]
    )
