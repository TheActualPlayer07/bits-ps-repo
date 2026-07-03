"""
Thin wrapper around the Groq API (OpenAI-compatible) used by every generator
in this project. Centralizing it here means:
  - the API key / model name is configured in exactly one place
  - rate-limit handling (Groq free tier: 30 RPM / 1,000 RPD) is handled once
  - swapping models or providers later only touches this file
"""

import os
import time

from groq import Groq

DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


class ProofBuilderLLMError(RuntimeError):
    """Raised when the LLM call fails in a way the caller should surface to the user."""


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ProofBuilderLLMError(
                "GROQ_API_KEY is not set. Get a free key at console.groq.com "
                "(see Groq_API_Guide_Caarya_Interns.docx) and put it in a .env "
                "file or your shell environment."
            )
        _client = Groq(api_key=api_key)
    return _client


def chat(
    messages,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
    max_tokens: int = 1024,
    json_mode: bool = False,
    max_retries: int = 3,
) -> str:
    """
    Send a chat completion request to Groq and return the message text.

    Retries on rate limits with a short backoff, since the free tier (30 RPM)
    is easy to hit when generating seven outputs from one activity in a row.
    """
    client = get_client()
    kwargs = dict(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as exc:  # noqa: BLE001 - Groq SDK error hierarchy varies by version
            last_error = exc
            status_code = getattr(exc, "status_code", None)
            is_rate_limit = status_code == 429 or "rate limit" in str(exc).lower()
            if is_rate_limit and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
                continue
            if is_rate_limit:
                break
            raise ProofBuilderLLMError(f"Groq API error: {exc}") from exc

    raise ProofBuilderLLMError(
        "Hit Groq's free-tier rate limit (30 requests/min) and retries were "
        "exhausted. Wait a moment and try again, or switch GROQ_MODEL to "
        "llama-3.1-8b-instant which has higher limits."
    ) from last_error
