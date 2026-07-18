"""Shared prompt scaffolding so the grounding/accuracy rules are defined once
and identical across all four generator modules — that's what keeps all
seven outputs honest to the same facts ledger."""

import json

from .. import llm

GROUNDING_RULES = """Ground EVERY statement in the facts ledger below. These rules are non-negotiable:
- Do not state any number, outcome, tool, audience, or detail that is not present in the ledger.
- Do not upgrade soft language into a stronger claim (e.g. "contributed to" is not "led").
- If a field in the ledger is null, do not imply a value for it — write around the gap, don't invent one.
- Being specific using only what's in the ledger beats generic filler. Prefer concrete, plain language
  over hype words like "revolutionary", "cutting-edge", or "passionate" unless the ledger supports them.
"""

THIN_NOTE = (
    "Note: this activity description was fairly thin/sparse going in. Stay extra conservative — "
    "do not pad with generic enthusiasm or invented specifics to compensate for the lack of detail."
)


def build_messages(system_role: str, task_instructions: str, facts_block: str, is_thin: bool = False):
    system = f"{system_role}\n\n{GROUNDING_RULES}"
    note = f"\n\n{THIN_NOTE}" if is_thin else ""
    user = (
        f"Facts ledger (the ONLY source of truth — do not use any outside knowledge or assumptions):\n"
        f"{facts_block}{note}\n\n"
        f"Task:\n{task_instructions}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def generate_json(system_role: str, task_instructions: str, facts_block: str, is_thin: bool, **chat_kwargs) -> dict:
    """Run one grounded generation call and parse the JSON result."""
    messages = build_messages(system_role, task_instructions, facts_block, is_thin)
    content = llm.chat(messages, json_mode=True, **chat_kwargs)
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise llm.ProofBuilderLLMError(
            f"Generator did not return valid JSON: {exc}\nRaw output: {content}"
        ) from exc
