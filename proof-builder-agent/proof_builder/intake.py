"""
Activity intake.

The single hardest part of this build (per the work order) is keeping seven
very different outputs honestly tied to the same underlying activity, with
zero inflation. The design choice here is: don't let any generator touch the
student's raw free-text description directly. Instead, extract one canonical
"facts ledger" from the raw input first, and have every one of the seven
generators work *only* from that ledger.

Why this works: an LLM asked to write a punchy LinkedIn post from raw,
unstructured text will reach for color it can't fully justify. An LLM asked
to write the same post from a short list of pre-extracted, already-deduped
facts has much less surface area to embellish. It also guarantees the seven
outputs agree with each other, since they're all reading the same ledger.
"""

import json
from copy import deepcopy

from . import llm

FACTS_SCHEMA_KEYS = [
    "title",
    "what_was_done",
    "actions",
    "tools_and_skills",
    "context",
    "collaboration",
    "scale_or_duration",
    "outcome",
    "challenges",
]

_FACTS_SYSTEM_PROMPT = """You are a precise fact-extraction assistant for a student proof-of-work tool.

You will be given a student's free-text description of one piece of completed work. \
Extract a clean, structured ledger of ONLY the facts that are explicitly stated or \
unambiguously implied. This ledger will be the single source of truth for everything \
generated downstream — nothing outside it will be used, so leave nothing important out, \
but never add anything that isn't actually in the text.

Rules:
- Do NOT invent numbers, outcomes, audience size, tools, durations, or names that are not stated.
- Do NOT upgrade vague language into something more impressive ("helped with" is not "led").
- If something is not mentioned, use null (or an empty list for list fields). Do not guess.
- Keep "what_was_done" factual and plain — no marketing language. The marketing happens later,
  downstream, working only from these facts.
- "actions" should be a list of concrete, specific steps/actions actually described.
- "tools_and_skills" should only list tools, technologies, or skills explicitly named or
  unmistakably implied by a described action (e.g. "wrote a Python script" implies "Python").

Return STRICT JSON with exactly these keys:
{
  "title": "short, factual title for the activity, <=8 words",
  "what_was_done": "1-3 plain factual sentences, no embellishment",
  "actions": ["concrete action 1", "concrete action 2", "..."],
  "tools_and_skills": ["..."],
  "context": "where/when/why this happened (course, internship, hackathon, club, personal project, etc.) or null",
  "collaboration": "solo / team of N / null if unstated",
  "scale_or_duration": "only if explicitly mentioned, else null",
  "outcome": "result or impact, ONLY if the student actually stated one, else null",
  "challenges": "an obstacle or constraint mentioned, else null"
}"""


def extract_facts(raw_activity: str) -> dict:
    """Turn raw student input into the canonical facts ledger."""
    raw_activity = (raw_activity or "").strip()
    if not raw_activity:
        raise ValueError("Activity description is empty — there's nothing to extract facts from.")

    messages = [
        {"role": "system", "content": _FACTS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Student's activity description:\n\n\"\"\"\n{raw_activity}\n\"\"\"\n\n"
            "Extract the facts ledger as JSON.",
        },
    ]
    content = llm.chat(messages, temperature=0.1, json_mode=True, max_tokens=700)

    try:
        facts = json.loads(content)
    except json.JSONDecodeError as exc:
        raise llm.ProofBuilderLLMError(
            f"Model did not return valid JSON for facts extraction: {exc}\nRaw output: {content}"
        ) from exc

    # Normalize so every expected key exists even if the model dropped one.
    for key in FACTS_SCHEMA_KEYS:
        facts.setdefault(key, None if key not in ("actions", "tools_and_skills") else [])

    facts["raw_input"] = raw_activity
    facts["is_thin"] = _looks_thin(facts)
    return facts


def _looks_thin(facts: dict) -> bool:
    """Flag activities with very little extractable detail, so generators can
    stay extra conservative rather than padding to sound impressive."""
    has_actions = bool(facts.get("actions"))
    has_detail = bool(facts.get("what_was_done")) and len(facts.get("what_was_done", "")) > 40
    return not (has_actions and has_detail)


def facts_for_prompt(facts: dict) -> str:
    """Serialize the ledger for embedding in a generator prompt, deliberately
    excluding raw_input/is_thin so generators can't reach past the ledger
    back into the original free text."""
    clean = deepcopy(facts)
    clean.pop("raw_input", None)
    clean.pop("is_thin", None)
    return json.dumps(clean, indent=2)
