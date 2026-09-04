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

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import anthropic
from anthropic.types import MessageParam
from langfuse import Langfuse
from openevals.simulators import run_multiturn_simulation

from harness._structured_calls import run_structured_call
from harness._tracing import observe
from harness._trajectory import (
    extract_message_text,
    first_text_block,
    latest_assistant_text,
)
from harness.config import Settings
from harness.models import Card, QuestionType
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

_INTRODUCTION_STOPPING_PROMPT = (
    "You classify whether an assistant's latest message, in a conversation where someone is asking "
    "whether to plant or keep a plant on their property, contains a single, specific, committed "
    "recommendation on whether to plant/keep it or remove/avoid it.\n\n"
    "Classify true only if the message commits to ONE clear recommendation the person could act on "
    "right now — 'keep/plant it' or 'remove it' (or 'replace it with X'), stated as this message's "
    "actual position, not just one option among several. A message that clearly commits to one "
    "position while also mentioning a caveat or a discarded alternative still counts as true — the "
    "bar is whether a single position has been committed to, not whether anything else is "
    "mentioned.\n\n"
    "Classify false for any of the following, even if the message is long or substantive:\n"
    "- An unranked list of options ('you could keep it, or you could remove it and plant something "
    "else') with no single position committed to.\n"
    "- A recommendation that branches on a fact the person hasn't actually stated (e.g. 'if you want "
    "low-maintenance, remove it; if you don't mind the upkeep, keep it') — no single position has "
    "been committed to for this person's real, still-unknown situation.\n"
    "- A request for more information before recommending anything.\n"
    "- Generic, non-committal advice with no clear keep-or-remove position (e.g. 'it depends on your "
    "preferences' or 'consider consulting a nursery' alone).\n"
    "- An outright refusal or decision not to give a recommendation.\n\n"
    "Judge only the assistant's latest message. Use the rest of the conversation only as context for "
    "what that message means, not as a substitute for what the latest message itself commits to."
)

_IDENTIFICATION_STOPPING_PROMPT = (
    "You classify whether an assistant's latest message, in a conversation where someone is asking "
    "what a plant on their property is, states a single, specific, committed species "
    "identification.\n\n"
    "Classify true only if the message commits to ONE specific species (a common name, a scientific "
    "name, or both) as its actual identification of the plant, stated as this message's real answer "
    "— not just a guess floated among others. A message that commits to one species while also "
    "noting a caveat (e.g. 'I'd want a photo to be fully sure, but this looks like...') still counts "
    "as true — the bar is whether a single species has been committed to, not whether any hedge "
    "language appears at all.\n\n"
    "Classify false for any of the following, even if the message is long or substantive:\n"
    "- An unranked list of candidate species ('this could be X, or it might be Y, or possibly Z') "
    "with no single species committed to.\n"
    "- An identification that branches on a fact the person hasn't actually stated (e.g. 'if the "
    "leaves are opposite it's X, if alternate it's Y') — no single species has been committed to "
    "for this person's real, still-unknown plant.\n"
    "- A request for more information (a photo, a leaf/bark description) before identifying "
    "anything.\n"
    "- Generic, non-committal description with no named species (e.g. 'that sounds like a common "
    "shrub' alone).\n"
    "- An outright refusal or decision not to attempt an identification.\n\n"
    "Judge only the assistant's latest message. Use the rest of the conversation only as context for "
    "what that message means, not as a substitute for what the latest message itself commits to."
)


def _preview(text: str, length: int = 80) -> str:
    """Short single-line preview of a message for operator-facing log lines."""
    collapsed = " ".join(text.split())
    if len(collapsed) <= length:
        return collapsed
    return collapsed[: length - 1] + "…"


def _classify_boolean(
    assistant_message: str,
    *,
    system_prompt: str,
    field_name: str,
    question: str,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> bool:
    """Shared structured-output classification: ask whether `assistant_message` satisfies some
    single-boolean-field rule (`system_prompt` states the rule, `question` restates it as the
    per-call prompt). Used by the three `question_type`-specific terminal-response classifiers below
    so the client-construction/schema/call plumbing exists in one place — same pattern
    `harness/judges/_common.py` factors out for the judges.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )
    schema = {
        "type": "object",
        "properties": {
            field_name: {"type": "boolean"},
        },
        "required": [field_name],
        "additionalProperties": False,
    }

    data = run_structured_call(
        anthropic_client,
        system=system_prompt,
        user_content=(
            f'Assistant\'s latest message:\n"""\n{assistant_message}\n"""\n\n{question}'
        ),
        schema=schema,
        model=model,
        max_tokens=256,
    )
    return bool(data.get(field_name, False))


def is_specific_prescription(
    assistant_message: str,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> bool:
    """Classify whether `assistant_message` is a single, specific, actionable recommendation.

    Structured-output Anthropic call via the shared `harness._structured_calls.run_structured_call`
    primitive (through `_classify_boolean`) — the response's `is_specific_prescription` field is
    constrained to a boolean by the schema, so the result is reliably parseable rather than parsed
    out of free text. Encodes exactly the bar `DECISION-LOG.md`'s 2026-09-03 entry locked: an
    unranked "you could do X or Y" list does not count, a request for more information does not
    count, and generic non-actionable advice does not count.
    """
    return _classify_boolean(
        assistant_message,
        system_prompt=_STOPPING_CONDITION_SYSTEM_PROMPT,
        field_name="is_specific_prescription",
        question="Does this message contain a single, specific, actionable recommendation per "
        "the rule above?",
        client=client,
        model=model,
    )


def is_specific_introduction_recommendation(
    assistant_message: str,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> bool:
    """Classify whether `assistant_message` commits to a single keep/remove recommendation on an
    `introduction`-type card. Same structured-output pattern and hedge-detection bar as
    `is_specific_prescription`, reframed around a plant/keep-or-remove decision instead of a
    treatment method."""
    return _classify_boolean(
        assistant_message,
        system_prompt=_INTRODUCTION_STOPPING_PROMPT,
        field_name="is_specific_recommendation",
        question="Does this message contain a single, specific, committed keep/remove "
        "recommendation per the rule above?",
        client=client,
        model=model,
    )


def is_species_identified(
    assistant_message: str,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> bool:
    """Classify whether `assistant_message` commits to a single species identification on an
    `identification`-type card. Same structured-output pattern and hedge-detection bar as
    `is_specific_prescription`, reframed around naming a species instead of prescribing treatment."""
    return _classify_boolean(
        assistant_message,
        system_prompt=_IDENTIFICATION_STOPPING_PROMPT,
        field_name="is_species_identified",
        question="Does this message commit to a single specific species identification per the "
        "rule above?",
        client=client,
        model=model,
    )


def is_terminal_response(
    card: Card,
    assistant_message: str,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
) -> bool:
    """Dispatch to the `question_type`-appropriate terminal-response classifier.

    Single source of truth for "has the assistant said the thing this conversation is trying to
    elicit" across all three question types — used both by the live stopping condition
    (`make_stopping_condition`) and by `harness/scoring.py`'s post-hoc re-derivation of which turn a
    finished conversation actually stopped on.
    """
    if card.question_type == QuestionType.REMOVAL:
        return is_specific_prescription(assistant_message, client=client, model=model)
    elif card.question_type == QuestionType.INTRODUCTION:
        return is_specific_introduction_recommendation(
            assistant_message, client=client, model=model
        )
    else:
        return is_species_identified(assistant_message, client=client, model=model)


def make_stopping_condition(
    card: Card,
    *,
    client: anthropic.Anthropic | None = None,
    model: str = DEFAULT_INFRA_MODEL,
    langfuse_client: Langfuse | None = None,
) -> Callable[..., bool]:
    """Build the `stopping_condition` callable `run_multiturn_simulation` calls natively.

    Confirmed from `openevals/simulators/multiturn.py`: called as
    `stopping_condition(current_reduced_trajectory["trajectory"], turn_counter=turn_counter)`
    immediately after each assistant turn is merged into the trajectory — so classifying just the
    latest assistant message here (via `is_terminal_response`, dispatched by `card.question_type`)
    is sufficient; no separate loop is needed.
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
        with observe(
            langfuse_client,
            name="stopping-condition",
            model=model,
            input=assistant_text,
        ) as obs:
            stop = is_terminal_response(
                card, assistant_text, client=anthropic_client, model=model
            )
            obs.update(output={"is_terminal": stop})
        logger.info(
            "turn=%d: assistant=%r is_terminal=%s",
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
    langfuse_client: Langfuse | None = None,
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

        with observe(
            langfuse_client, name="model-under-test", model=model, input=user_text
        ) as obs:
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=MODEL_UNDER_TEST_SYSTEM_PROMPT,
                messages=history,
            )
            assistant_text = first_text_block(response.content)
            obs.update(output=assistant_text)
        history.append({"role": "assistant", "content": assistant_text})
        logger.info(
            "thread=%s: assistant turn: %s", thread_id, _preview(assistant_text)
        )

        return {"role": "assistant", "content": assistant_text}

    return _model_under_test


@dataclass
class ConversationResult:
    """One finished conversation: the trajectory plus its Langfuse trace id, if traced.

    `trace_id` is `None` when `run_conversation` was called with no `langfuse_client` (every test in
    this repo, and any ad hoc script that doesn't need Langfuse) — callers that need to link a
    dataset run or attach scores (`harness/scripts/run_validation.py`) require a real
    `langfuse_client` to get a non-`None` id.
    """

    trajectory: list[dict[str, Any]]
    trace_id: str | None


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
    langfuse_client: Langfuse | None = None,
    oracle: bool = False,
) -> ConversationResult:
    """Run one full simulated conversation for `card` and return the finished trajectory.

    Wires the slot-gated simulated user (`make_simulated_user`), the model-under-test callable
    (`make_model_under_test`), and the stopping condition (`make_stopping_condition`) into
    `openevals.simulators.run_multiturn_simulation`, starting from `card.opening_message` as the
    first user turn (handled inside `make_simulated_user`'s `turn_counter == 0` branch — no
    separate wiring needed here). `max_turns` is a hard cap independent of the stopping condition:
    a model that never commits to a specific recommendation runs out the cap rather than erroring,
    which is the "hit-max-turns rate" PRD §5.4 tracks as a real outcome.

    `oracle=True` runs RQ1's oracle-contrast arm instead of the standard arm (PRD §2/§6/R6): every
    decision-relevant slot is disclosed in the opening message rather than gated behind elicitation
    — threaded straight to `make_simulated_user`, see its docstring.

    A single shared `anthropic.Anthropic` client is built once (if not supplied) and passed to all
    three pieces, rather than each constructing its own — avoids redundant client construction on
    every turn of what can be an 8+ turn, multi-classifier-call conversation.

    When `langfuse_client` is given, the whole conversation is wrapped in one parent span (via
    `harness._tracing.observe`) and every individual model call underneath it — model-under-test
    turn, slot classifier, response generator, stopping-condition classifier — lands as its own
    nested generation, rather than one flat blob covering the whole transcript.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )

    simulated_user = make_simulated_user(
        card,
        client=anthropic_client,
        classifier_model=simulated_user_classifier_model,
        responder_model=simulated_user_responder_model,
        langfuse_client=langfuse_client,
        oracle=oracle,
    )
    model_under_test_app = make_model_under_test(
        client=anthropic_client, model=model_under_test, langfuse_client=langfuse_client
    )
    stopping_condition = make_stopping_condition(
        card,
        client=anthropic_client,
        model=stopping_condition_model,
        langfuse_client=langfuse_client,
    )

    logger.info(
        "card=%s: starting conversation (model_under_test=%s, max_turns=%d)",
        card.card_id,
        model_under_test,
        max_turns,
    )

    with observe(
        langfuse_client,
        name="conversation",
        as_type="span",
        input={"card_id": card.card_id, "opening_message": card.opening_message},
    ) as conversation_span:
        result = run_multiturn_simulation(
            app=model_under_test_app,
            user=simulated_user,
            max_turns=max_turns,
            stopping_condition=stopping_condition,
            thread_id=thread_id,
        )
        conversation_span.update(output=result["trajectory"])
        trace_id = conversation_span.trace_id

    logger.info(
        "card=%s: conversation finished (%d messages in trajectory)",
        card.card_id,
        len(result["trajectory"]),
    )
    return ConversationResult(
        trajectory=result["trajectory"],  # type: ignore[arg-type]
        trace_id=trace_id,
    )
