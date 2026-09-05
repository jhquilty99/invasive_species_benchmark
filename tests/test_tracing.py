"""Tests for `harness._tracing.observe`.

Runs entirely against a mocked Langfuse client — no live server required. What's exercised: the
no-op path when tracing is off, and that `trace_id` (added for gate/quality judge tracing — see
`harness/judges/_common.py`) is what decides whether Langfuse starts a fresh trace or attaches this
observation to an existing one.
"""

from unittest.mock import MagicMock

from harness._tracing import _NoopObservation, observe


def test_observe_is_a_noop_without_a_langfuse_client() -> None:
    with observe(None, name="x") as obs:
        assert isinstance(obs, _NoopObservation)
        obs.update(output="ignored")  # must not raise


def test_observe_starts_a_fresh_trace_when_no_trace_id_given() -> None:
    client = MagicMock()
    with observe(client, name="model-under-test", model="claude-opus-5", input="hi"):
        pass
    _, kwargs = client.start_as_current_observation.call_args
    assert kwargs["trace_context"] is None


def test_observe_attaches_to_an_existing_trace_when_trace_id_given() -> None:
    """The mechanism `run_structured_judge_call` relies on to land a judge call as an "evaluation"
    generation on the same trace as the conversation's "simulation"/"inference" generations, even
    though judges run after that conversation's own span has already exited."""
    client = MagicMock()
    with observe(
        client,
        name="judge-g1-identity-verified",
        model="claude-sonnet-5",
        trace_id="trace-abc-123",
    ):
        pass
    _, kwargs = client.start_as_current_observation.call_args
    assert kwargs["trace_context"] == {"trace_id": "trace-abc-123"}
