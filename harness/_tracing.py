"""Optional per-observation Langfuse tracing, shared by `harness/conversation.py` and
`harness/simulated_user.py`.

`observe(langfuse_client, ...)` wraps one unit of work — a single Anthropic call, or (via
`as_type="span"`) a whole conversation — in a Langfuse observation when a real client is supplied, and
is a complete no-op otherwise. Every factory that takes a `langfuse_client` argument defaults it to
`None`, so no existing or new test needs a live Langfuse server to pass; only
`harness/scripts/run_validation.py` constructs a real client and threads it through.
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
) -> Iterator[Any]:
    """Wrap one unit of work in a Langfuse observation, or a `_NoopObservation` when tracing is off.

    Every call site looks the same regardless of whether tracing is active:

    ```python
    with observe(langfuse_client, name="model-under-test", model=model, input=user_text) as obs:
        response = client.messages.create(...)
        obs.update(output=assistant_text)
    ```
    """
    if langfuse_client is None:
        yield _NoopObservation()
        return

    with langfuse_client.start_as_current_observation(
        name=name,
        as_type=as_type,  # type: ignore[arg-type]
        input=input,
        model=model,
    ) as obs:
        yield obs
