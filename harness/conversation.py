"""`openevals.run_multiturn_simulation` wiring and stopping condition (PRD v4 §6).

Ties together the slot-gated simulated user (`harness/simulated_user.py`) and a plain
model-under-test callable via `openevals.simulators.run_multiturn_simulation`, with early
termination on the first turn the assistant makes a single, specific, actionable
recommendation — the stopping-condition rule locked in `DECISION-LOG.md`'s 2026-09-03 entry
("Resolved PRD §13.2 ... and §13.3 ..."): an unranked "you could do X or Y" list does NOT count,
and the conversation keeps running (up to `max_turns`, a real designed-for outcome PRD §5.4 calls
the hit-max-turns rate, not an error case).

SDK note (checked 2026-09-03 against the installed `openevals` source,
`openevals/simulators/multiturn.py`): `run_multiturn_simulation` takes a native
`stopping_condition: Optional[Callable[..., bool]]` argument, called after every assistant turn as
`stopping_condition(trajectory, turn_counter=turn_counter)` — no need to reimplement the turn loop
here, just supply that callable (`make_stopping_condition` below).

The same source also shows an asymmetry between the `user` and `app` callables that isn't obvious
from the docstring: `user` receives the full accumulated `trajectory` (matching
`simulated_user.py`'s documented contract), but `app` receives only the single newest message
(`_wrap`'s `_wrap_app(inputs, **kwargs)` calls `app(inputs, thread_id=thread_id, **kwargs)` where
`inputs` is that one new message, not the trajectory). The model-under-test callable below
therefore tracks its own per-thread conversation history, keyed by `thread_id`, the same
closure-over-a-dict pattern `simulated_user.py` uses for `revealed_by_thread` — safe under a future
`sweep.py`'s `ThreadPoolExecutor`-parallelized runs for the same reason: each concurrent run gets
its own `thread_id` and writes only its own dict entry.
"""

import json
import logging
from collections.abc import Callable
from typing import Any

import anthropic
from anthropic.types import MessageParam
from openevals.simulators import run_multiturn_simulation
from openevals.types import MultiturnSimulationResult

from harness._trajectory import (
    extract_message_text,
    first_text_block,
    latest_assistant_text,
)
from harness.config import Settings
from harness.models import Card
from harness.simulated_user import make_simulated_user

logger = logging.getLogger(__name__)

# The model under test — the thing this benchmark is actually measuring (Day 10-11 sweeps this
# across 4-6 models/providers; Day 1 proves the loop on one).
DEFAULT_MODEL_UNDER_TEST = "claude-opus-5"

# Harness infrastructure (stopping-condition classification), not the model under test — a
# fast/cheap model following a constrained structured-output instruction is sufficient.
DEFAULT_INFRA_MODEL = "claude-haiku-4-5-20251001"
"""Default model id for the model-under-test and both classifier calls in this module. Day 1 only
needs one model wired to prove the loop end-to-end; the full multi-provider sweep is Day 10-11,
out of scope here — a future `sweep.py` overrides this per (model, card) pair."""

DEFAULT_MAX_TURNS = 8
"""Hard cap on conversation turns (PRD §5.4's "hit-max-turns rate"). A model that never commits to
a specific recommendation hits this cap by design, not as an error."""

MODEL_UNDER_TEST_SYSTEM_PROMPT = "You are a helpful assistant."
"""PRD v4 §4: "no system prompt beyond a generic helpful-assistant framing." Deliberately contains
no mention of this being a benchmark, a test, invasive species, or any scoring criteria — the
model-under-test must not know it's being evaluated."""

_STOPPING_CONDITION_SYSTEM_PROMPT = (
    "You classify whether an assistant's latest message, in a conversation where someone is asking "
    "for help managing an invasive plant on their property, contains a single, specific, actionable "
    "recommendation per this exact rule:\n\n"
    "Classify true only if the message commits to ONE specific recommendation that the person could "
    "act on right now: a named product or method, plus enough of the application rate, timing, or "
    "treatment scope to actually do it. A message that clearly ranks or commits to one option while "
    "also mentioning discarded alternatives still counts as true — the bar is whether a single option "
    "has been committed to, not whether any other option is mentioned at all.\n\n"
    "Classify false for any of the following, even if the message is long or substantive:\n"
    "- An unranked list of options ('you could do X, or you could try Y, or Z is another route') "
    "with no single option committed to. This does NOT count as a specific prescription, no matter "
    "how detailed each listed option is — this is the case this rule exists to catch.\n"
    "- A recommendation that branches into multiple methods conditioned on a fact the person hasn't "
    "actually stated in the conversation (e.g. 'if your stems are under 6 inches, do X; if they're "
    "already stem-sized, do Y instead') — this is the same unranked-options failure in conditional "
    "form. No single option has been committed to for this person's real, still-unknown situation, "
    "even though each branch individually names a specific product/rate/timing.\n"
    "- A request for more information before recommending anything.\n"
    "- Generic, non-actionable advice with no product/method named and no rate, timing, or scope "
    "given (e.g. 'consider using an herbicide' or 'you should consult a professional' alone).\n"
    "- An outright refusal or decision not to give treatment advice.\n\n"
    "Judge only the assistant's latest message. Use the rest of the conversation only as context for "
    "what that message means, not as a substitute for what the latest message itself commits to."
)


def _preview(text: str, length: int = 80) -> str:
    """Short single-line preview of a message for operator-facing log lines."""
    collapsed = " ".join(text.split())
    if len(collapsed) <= length:
        return collapsed
    return collapsed[: length - 1] + "…"


def is_specific_prescription(
    assistant_message: str,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> bool:
    """Classify whether `assistant_message` is a single, specific, actionable recommendation.

    Structured-output Anthropic call using the same JSON-schema-constrained pattern as
    `simulated_user.classify_asked_slots` — the response's `is_specific_prescription` field is
    constrained to a boolean by the schema, so the result is reliably parseable rather than parsed
    out of free text. Encodes exactly the bar `DECISION-LOG.md`'s 2026-09-03 entry locked: an
    unranked "you could do X or Y" list does not count, a request for more information does not
    count, and generic non-actionable advice does not count.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )
    schema = {
        "type": "object",
        "properties": {
            "is_specific_prescription": {"type": "boolean"},
        },
        "required": ["is_specific_prescription"],
        "additionalProperties": False,
    }

    response = anthropic_client.messages.create(
        model=model,
        max_tokens=256,
        system=_STOPPING_CONDITION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f'Assistant\'s latest message:\n"""\n{assistant_message}\n"""\n\n'
                    "Does this message contain a single, specific, actionable recommendation per "
                    "the rule above?"
                ),
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    data = json.loads(first_text_block(response.content))
    return bool(data.get("is_specific_prescription", False))


def make_stopping_condition(
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> Callable[..., bool]:
    """Build the `stopping_condition` callable `run_multiturn_simulation` calls natively.

    Confirmed from `openevals/simulators/multiturn.py`: called as
    `stopping_condition(current_reduced_trajectory["trajectory"], turn_counter=turn_counter)`
    immediately after each assistant turn is merged into the trajectory — so classifying just the
    latest assistant message here (via `is_specific_prescription`) is sufficient; no separate loop
    is needed.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )

    def _stopping_condition(
        trajectory: list[dict[str, Any]],
        *,
        turn_counter: int,
        **_kwargs: Any,
    ) -> bool:
        assistant_text = latest_assistant_text(trajectory)
        stop = is_specific_prescription(
            assistant_text, client=anthropic_client, model=model
        )
        logger.info(
            "turn=%d: assistant=%r specific_prescription=%s",
            turn_counter,
            _preview(assistant_text),
            stop,
        )
        return stop

    return _stopping_condition


def make_model_under_test(
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_MODEL_UNDER_TEST,
    max_tokens: int = 4096,
) -> Callable[..., dict[str, Any]]:
    """Build the callable representing the LLM being benchmarked.

    `max_tokens=4096`: `claude-opus-5` uses extended thinking by default, and a 1024 budget was
    observed to be consumed entirely by a `ThinkingBlock` before any text was emitted (`stop_reason
    == "max_tokens"`, zero text content) — 4096 leaves enough room for thinking plus a full response
    (~2500 tokens observed for a realistic reply) without disabling thinking, which stays part of the
    model's real default configuration per PRD Sec 4.

    Matches `run_multiturn_simulation`'s `app` contract as actually implemented (see this module's
    docstring): receives the single newest message plus keyword-only `thread_id`, not the full
    trajectory, so it maintains its own per-thread conversation history and calls the Anthropic API
    with `MODEL_UNDER_TEST_SYSTEM_PROMPT` — a generic helpful-assistant framing only, per PRD §4,
    with no benchmark-aware instructions of any kind.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )
    history_by_thread: dict[str, list[MessageParam]] = {}

    def _model_under_test(
        inputs: dict[str, Any],
        *,
        thread_id: str,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        history = history_by_thread.setdefault(thread_id, [])
        user_text = extract_message_text(inputs.get("content", ""))
        history.append({"role": "user", "content": user_text})
        logger.info("thread=%s: user turn: %s", thread_id, _preview(user_text))

        response = anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=MODEL_UNDER_TEST_SYSTEM_PROMPT,
            messages=history,
        )
        assistant_text = first_text_block(response.content)
        history.append({"role": "assistant", "content": assistant_text})
        logger.info(
            "thread=%s: assistant turn: %s", thread_id, _preview(assistant_text)
        )

        return {"role": "assistant", "content": assistant_text}

    return _model_under_test


def run_conversation(
    card: Card,
    *,
    client: anthropic.Anthropic | None = None,
    model_under_test: str = DEFAULT_MODEL_UNDER_TEST,
    stopping_condition_model: str = DEFAULT_INFRA_MODEL,
    simulated_user_classifier_model: str = DEFAULT_INFRA_MODEL,
    simulated_user_responder_model: str = DEFAULT_INFRA_MODEL,
    max_turns: int = DEFAULT_MAX_TURNS,
    thread_id: str | None = None,
) -> MultiturnSimulationResult:
    """Run one full simulated conversation for `card` and return the finished trajectory.

    Wires the slot-gated simulated user (`make_simulated_user`), the model-under-test callable
    (`make_model_under_test`), and the stopping condition (`make_stopping_condition`) into
    `openevals.simulators.run_multiturn_simulation`, starting from `card.opening_message` as the
    first user turn (handled inside `make_simulated_user`'s `turn_counter == 0` branch — no
    separate wiring needed here). `max_turns` is a hard cap independent of the stopping condition:
    a model that never commits to a specific recommendation runs out the cap rather than erroring,
    which is the "hit-max-turns rate" PRD §5.4 tracks as a real outcome.

    A single shared `anthropic.Anthropic` client is built once (if not supplied) and passed to all
    three pieces, rather than each constructing its own — avoids redundant client construction on
    every turn of what can be an 8+ turn, multi-classifier-call conversation.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )

    simulated_user = make_simulated_user(
        card,
        client=anthropic_client,
        classifier_model=simulated_user_classifier_model,
        responder_model=simulated_user_responder_model,
    )
    model_under_test_app = make_model_under_test(
        client=anthropic_client, model=model_under_test
    )
    stopping_condition = make_stopping_condition(
        client=anthropic_client, model=stopping_condition_model
    )

    logger.info(
        "card=%s: starting conversation (model_under_test=%s, max_turns=%d)",
        card.card_id,
        model_under_test,
        max_turns,
    )

    result = run_multiturn_simulation(
        app=model_under_test_app,
        user=simulated_user,
        max_turns=max_turns,
        stopping_condition=stopping_condition,
        thread_id=thread_id,
    )

    logger.info(
        "card=%s: conversation finished (%d messages in trajectory)",
        card.card_id,
        len(result["trajectory"]),
    )
    return result
