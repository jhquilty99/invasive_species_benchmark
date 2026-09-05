"""Shared helpers for `harness/judges/gates.py` and `harness/judges/quality.py`.

Factors out the one thing every judge prompt needs beyond the shared `harness._structured_calls`
primitive: turning a trajectory into prompt-ready text.
"""

from typing import Any

import anthropic
from langfuse import Langfuse

from harness._structured_calls import run_structured_call
from harness._tracing import observe
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
    name: str,
    system: str,
    user_content: str,
    schema: dict[str, Any],
    model: str = DEFAULT_JUDGE_MODEL,
    max_tokens: int = 8192,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    """One judge call: JSON-schema-constrained structured output, parsed and returned as a dict.

    Every gate/quality judge function builds its own `schema` (constraining the outcome/label/score
    enum plus a required `comment` field — R1, every judged score carries its deciding evidence) and
    passes it here rather than repeating the structured-call boilerplate — see
    `harness._structured_calls.run_structured_call`, the shared primitive this delegates to.

    `max_tokens=8192`: bumped from 4096 (2026-09-04 methodology-eval hardening pass) after
    `judge_q4_regulatory_grounding` still hit an empty-text-block `JSONDecodeError` at 4096 for
    `phragmites-public-water-referral-01` × `claude-opus-5` — Q4's prompt interpolates the full
    same-species `ground_truth` yaml plus the transcript, and Phragmites' yaml plus a referral-length
    transcript apparently exhausted 4096 tokens on `claude-sonnet-5`'s extended thinking before any
    text output. Reproduced identically on retry (not a one-off transient failure), confirming this is
    a budget problem, not a fluke — see `DECISION-LOG.md`, 2026-09-04 "Bumped judge call max_tokens
    4096 -> 8192...".

    `name` identifies this judge in the Langfuse UI (e.g. `"judge-g1-identity-verified"`,
    `"judge-q3-actionability"`) — required, not defaulted, since every call site needs a distinct
    one. Wrapped in `harness._tracing.observe` the same way every other model call in this repo is
    (`harness/conversation.py`, `harness/simulated_user.py`) — this is the one choke point all
    eleven gate/quality judge calls pass through, so instrumenting it here covers every judge rather
    than needing the same `with observe(...)` boilerplate repeated at each call site. `trace_id`
    (normally the finished conversation's trace, threaded down from `harness/sweep.py`/
    `harness/scripts/run_validation.py`) attaches this "evaluation" generation to that same trace —
    see `observe`'s docstring for why that needs `trace_id` explicitly rather than ambient context.
    """
    with observe(
        langfuse_client,
        name=name,
        model=model,
        input=user_content,
        trace_id=trace_id,
    ) as obs:
        result = run_structured_call(
            client,
            system=system,
            user_content=user_content,
            schema=schema,
            model=model,
            max_tokens=max_tokens,
        )
        obs.update(output=result)
    return result
