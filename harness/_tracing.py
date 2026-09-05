"""Optional per-observation Langfuse tracing, shared by `harness/conversation.py`,
`harness/simulated_user.py`, and (via `harness/judges/_common.py`'s `run_structured_judge_call`)
every gate/quality judge in `harness/judges/`.

`observe(langfuse_client, ...)` wraps one unit of work — a single Anthropic call, or (via
`as_type="span"`) a whole conversation — in a Langfuse observation when a real client is supplied, and
is a complete no-op otherwise. Every factory that takes a `langfuse_client` argument defaults it to
`None`, so no existing or new test needs a live Langfuse server to pass; only the manual, deliberate
scripts under `harness/scripts/` (`run_validation.py`, `run_repeat_pilot.py`, `run_sweep.py`) and
`harness/sweep.py`'s callers construct a real client and thread it through.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Literal

from langfuse import Langfuse


class _NoopObservation:
    """Stand-in for a Langfuse observation when tracing is disabled (`langfuse_client is None`)."""

    trace_id: str | None = None

    def update(self, **_kwargs: Any) -> None:
        pass


@contextmanager
def observe(
    langfuse_client: Langfuse | None,
    *,
    name: str,
    as_type: Literal["span", "generation"] = "generation",
    input: Any = None,
    model: str | None = None,
    trace_id: str | None = None,
) -> Iterator[Any]:
    """Wrap one unit of work in a Langfuse observation, or a `_NoopObservation` when tracing is off.

    Every call site looks the same regardless of whether tracing is active:

    ```python
    with observe(langfuse_client, name="model-under-test", model=model, input=user_text) as obs:
        response = client.messages.create(...)
        obs.update(output=assistant_text)
    ```

    `trace_id`, when given, attaches this observation to an *existing* trace (via Langfuse's
    `trace_context`) instead of starting a fresh one off the ambient OTEL context. Needed for the
    gate/quality judges (`harness/judges/gates.py`, `harness/judges/quality.py`): they run after
    `harness.conversation.run_conversation`'s own `observe(..., as_type="span")` block has already
    exited, so there's no live parent span left to nest under — passing that conversation's
    `trace_id` here is what lands each judge call as its own "evaluation" generation on the same
    trace as the "simulation"/"inference" generations, rather than as an unrelated standalone trace.
    """
    if langfuse_client is None:
        yield _NoopObservation()
        return

    with langfuse_client.start_as_current_observation(
        name=name,
        as_type=as_type,  # type: ignore[arg-type]
        input=input,
        model=model,
        trace_context={"trace_id": trace_id} if trace_id is not None else None,
    ) as obs:
        yield obs
