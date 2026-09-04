"""One shared primitive for every JSON-schema-constrained Anthropic call in this repo.

Used by `harness/conversation.py`'s stopping-condition classifiers, `harness/simulated_user.py`'s
slot classifier, and every judge in `harness/judges/` — anywhere a single Anthropic call needs to
return schema-constrained JSON rather than free text. Factored out once here rather than living as
near-duplicate boilerplate in each caller.
"""

import json
from typing import Any

import anthropic

from harness._trajectory import first_text_block


def run_structured_call(
    client: anthropic.Anthropic,
    *,
    system: str,
    user_content: str,
    schema: dict[str, Any],
    model: str,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """One structured-output call: JSON-schema-constrained request, parsed response.

    `max_tokens=4096`: several models used here (`claude-opus-5`, `claude-sonnet-5`) use extended
    thinking by default, which can consume most of a smaller budget before any output text is
    emitted — see `DECISION-LOG.md`'s 2026-09-03 "Live validation run" entry for the truncated-JSON
    failure this default was raised to prevent.
    """
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_content}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    result: dict[str, Any] = json.loads(first_text_block(response.content))
    return result
