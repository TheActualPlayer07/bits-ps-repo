"""
Shared Groq API client wrapper. Every LLM-rubric grader in this app
(DSA free-text, Projects quality, Explanation Clarity, HR/Behavioral)
goes through call_structured() below, so retry/error-handling logic
only has to be written once.

Requires: pip install groq
Requires: GROQ_API_KEY environment variable set.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()  # ensures GROQ_API_KEY is available even when this module is
                # imported directly, without going through app.main first

DEFAULT_MODEL = "openai/gpt-oss-120b"  # strongest reasoning tier on Groq; swap if latency becomes an issue

class GroqGradingError(Exception):
    """Raised when a structured grading call fails after all retries."""
    pass


def _get_client():
    try:
        from groq import Groq
    except ImportError as e:
        raise GroqGradingError(
            "The 'groq' package is not installed. Run: pip install groq"
        ) from e
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise GroqGradingError("GROQ_API_KEY environment variable is not set.")
    return Groq(api_key=api_key)


def call_structured(system_prompt: str, user_prompt: str, json_schema: dict,
                     schema_name: str, model: str = DEFAULT_MODEL,
                     temperature: float = 0.2, max_retries: int = 2) -> dict:
    """
    Calls Groq's chat completion with a JSON schema response format and
    returns the parsed dict. Retries on malformed JSON or schema mismatch.

    json_schema: a plain JSON Schema dict (properties, required, etc.)
    schema_name: short identifier Groq uses to label the schema in the request
    """
    client = _get_client()
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema_name,
                        "strict": True,
                        "schema": json_schema,
                    },
                },
            )
            raw = response.choices[0].message.content
            parsed = json.loads(raw)
            _validate_required_fields(parsed, json_schema)
            return parsed

        except Exception as e:  # malformed JSON, schema mismatch, network error, etc.
            last_error = e
            continue

    raise GroqGradingError(
        f"Structured call '{schema_name}' failed after {max_retries + 1} attempts: {last_error}"
    )


def _validate_required_fields(parsed: dict, json_schema: dict):
    """Lightweight sanity check on top of Groq's own strict-mode enforcement."""
    required = json_schema.get("required", [])
    missing = [field for field in required if field not in parsed]
    if missing:
        raise ValueError(f"Response missing required fields: {missing}")
