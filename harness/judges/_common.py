"""Shared helpers for `harness/judges/gates.py` and `harness/judges/quality.py`.

Factors out the one thing every judge prompt needs beyond the shared `harness._structured_calls`
primitive: turning a trajectory into prompt-ready text.
"""

from typing import Any

import anthropic

from harness._structured_calls import run_structured_call
from harness._trajectory import extract_message_text

DEFAULT_JUDGE_MODEL = "claude-sonnet-5"
"""Distinct from both `conversation.DEFAULT_MODEL_UNDER_TEST` (`claude-opus-5`, the thing being
graded) and `conversation.DEFAULT_INFRA_MODEL` (`claude-haiku-4-5`, cheap harness plumbing) —
deliberately not the same model as the default model-under-test, so a judge run isn't grading that
model's output with itself."""


def format_transcript(trajectory: list[dict[str, Any]]) -> str:
    """Render a finished conversation trajectory as role-labeled text for a judge prompt."""
    lines = []
    for message in trajectory:
        role = "User" if message.get("role") == "user" else "Assistant"
        text = extract_message_text(message.get("content", ""))
        lines.append(f"{role}: {text}")
    return "\n\n".join(lines)


def run_structured_judge_call(
    client: anthropic.Anthropic,
    *,
    system: str,
    user_content: str,
    schema: dict[str, Any],
    model: str = DEFAULT_JUDGE_MODEL,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """One judge call: JSON-schema-constrained structured output, parsed and returned as a dict.

    Every gate/quality judge function builds its own `schema` (constraining the outcome/label/score
    enum plus a required `comment` field — R1, every judged score carries its deciding evidence) and
    passes it here rather than repeating the structured-call boilerplate — see
    `harness._structured_calls.run_structured_call`, the shared primitive this delegates to.
    """
    return run_structured_call(
        client,
        system=system,
        user_content=user_content,
        schema=schema,
        model=model,
        max_tokens=max_tokens,
    )
