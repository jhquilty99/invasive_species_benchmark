"""Q1 + derived metrics (PRD v4 §5.3/§5.4), computed in code only — never judged (R3).

Re-derives everything from a finished conversation trajectory rather than threading extra live state
through `harness/conversation.py`/`harness/simulated_user.py`: which turn (if any) the conversation
actually stopped on (re-running `conversation.is_terminal_response`), and which slots were asked about
before that turn (re-running `simulated_user.classify_asked_slots`). Slower than capturing this live
would be, but keeps the derivation auditable in one place rather than leaking scoring internals into
the harness's live conversation loop.

Resolves `PRODUCT_REQUIREMENTS.md` §13.5's open question: Q1/slot-gating applies to `identification`
cards too, using the same "elicited before the terminal turn" mechanism as `removal` — see
`DECISION-LOG.md`'s "First-pass LLM-as-judge validation" entry.
"""

from dataclasses import dataclass
from typing import Any

import anthropic

from harness._trajectory import extract_message_text
from harness.conversation import DEFAULT_INFRA_MODEL, is_terminal_response
from harness.models import Card
from harness.simulated_user import classify_asked_slots


@dataclass
class TurnMetrics:
    turns_to_recommendation: int | None
    """1-indexed count of assistant turns up to and including the terminal one, or `None` if the
    conversation hit `max_turns` without ever producing one."""
    hit_max_turns: bool


def determine_stopping_turn(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_INFRA_MODEL,
) -> TurnMetrics:
    """Re-classify the trajectory's last assistant turn to decide whether the conversation stopped on
    its own or ran out the turn cap.

    Only the last assistant turn needs checking: `run_conversation`'s live stopping condition already
    fires on the first turn `is_terminal_response` returns true for, so if the conversation ended
    early its last assistant turn is exactly that one; if it hit `max_turns`, the classifier must have
    returned false on every turn including the last (otherwise the loop would have already stopped one
    turn sooner) — so one re-check of the final turn is sufficient, not a scan over every turn.
    """
    assistant_turns = [m for m in trajectory if m.get("role") == "assistant"]
    if not assistant_turns:
        return TurnMetrics(turns_to_recommendation=None, hit_max_turns=False)

    last_text = extract_message_text(assistant_turns[-1].get("content", ""))
    stopped = is_terminal_response(card, last_text, client=client, model=model)
    if stopped:
        return TurnMetrics(
            turns_to_recommendation=len(assistant_turns), hit_max_turns=False
        )
    return TurnMetrics(turns_to_recommendation=None, hit_max_turns=True)


@dataclass
class Q1Result:
    all_decision_relevant_elicited: bool
    elicited_decision_relevant_slots: list[str]
    missing_decision_relevant_slots: list[str]
    distractor_slots_asked: list[str]
    """Non-`decision_relevant` slots the model asked about anyway — a turn spent on a fact that
    wouldn't have changed the correct answer for this card."""


def compute_q1(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    turn_metrics: TurnMetrics,
    *,
    model: str = DEFAULT_INFRA_MODEL,
) -> Q1Result:
    """Which of `card`'s slots the model asked about before its terminal turn.

    The elicitation window is every assistant turn strictly before the terminal one when the
    conversation stopped on its own, or the whole conversation when it hit `max_turns` (there's no
    terminal turn to draw the "before prescribing" boundary at, so everything the model did ask about
    counts).
    """
    assistant_texts = [
        extract_message_text(m.get("content", ""))
        for m in trajectory
        if m.get("role") == "assistant"
    ]
    if turn_metrics.hit_max_turns:
        window = assistant_texts
    else:
        assert turn_metrics.turns_to_recommendation is not None
        window = assistant_texts[: turn_metrics.turns_to_recommendation - 1]

    asked: set[str] = set()
    for text in window:
        asked.update(classify_asked_slots(client, text, card.slots, model=model))

    decision_relevant_names = {
        slot.name for slot in card.slots if slot.decision_relevant
    }
    distractor_names = {slot.name for slot in card.slots if not slot.decision_relevant}

    missing = sorted(decision_relevant_names - asked)
    return Q1Result(
        all_decision_relevant_elicited=not missing,
        elicited_decision_relevant_slots=sorted(asked & decision_relevant_names),
        missing_decision_relevant_slots=missing,
        distractor_slots_asked=sorted(asked & distractor_names),
    )


def premature_prescription_rate(q1_results: list[Q1Result]) -> float:
    """Share of conversations where the model committed to its terminal answer without first
    eliciting every decision-relevant slot for that card. `0.0` for an empty input."""
    if not q1_results:
        return 0.0
    premature = sum(
        1 for result in q1_results if not result.all_decision_relevant_elicited
    )
    return premature / len(q1_results)


def hit_max_turns_rate(turn_metrics: list[TurnMetrics]) -> float:
    """Share of conversations that ran out `max_turns` without the model ever committing to a
    terminal answer. `0.0` for an empty input."""
    if not turn_metrics:
        return 0.0
    return sum(1 for metrics in turn_metrics if metrics.hit_max_turns) / len(
        turn_metrics
    )
