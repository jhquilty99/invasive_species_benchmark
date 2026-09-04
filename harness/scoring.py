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

from collections import Counter
from dataclasses import dataclass
from typing import Any

import anthropic

from harness._trajectory import extract_message_text
from harness.conversation import DEFAULT_INFRA_MODEL, is_terminal_response
from harness.models import (
    Card,
    GateOutcome,
    IntroductionQ2Label,
    Q2Label,
    QuestionType,
)
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


def q2_label_value(label: Q2Label | IntroductionQ2Label | str) -> str:
    """Unwrap a Q2 label enum (or an already-`"not_applicable"` string) to its plain string value.

    Shared by every script that needs to log or attach a Q2 label as a plain string
    (`harness/scripts/run_validation.py`, `harness/scripts/run_repeat_pilot.py`) — pulled out here
    after the same helper was duplicated verbatim in both, following the same "shared, code-computed,
    cross-script derived value" role this module already plays for `is_referral_correct` and
    `compute_repeat_agreement`.
    """
    return label.value if isinstance(label, (Q2Label, IntroductionQ2Label)) else label


def is_declined(card: Card, q2_label: Q2Label | IntroductionQ2Label | str) -> bool:
    """Whether Q2 classified this `removal` card's response as declined — the boolean gates G2-G6's
    `run_all_gates(..., declined=...)` short-circuit expects. `False` for any other `question_type`,
    since G2-G6 only ever run on `removal` cards in the first place. Shared for the same reason as
    `q2_label_value` above — was duplicated verbatim in both `run_validation.py` and
    `run_repeat_pilot.py`."""
    return card.question_type == QuestionType.REMOVAL and q2_label == Q2Label.DECLINED


def hit_max_turns_rate(turn_metrics: list[TurnMetrics]) -> float:
    """Share of conversations that ran out `max_turns` without the model ever committing to a
    terminal answer. `0.0` for an empty input."""
    if not turn_metrics:
        return 0.0
    return sum(1 for metrics in turn_metrics if metrics.hit_max_turns) / len(
        turn_metrics
    )


def is_referral_correct(
    card: Card,
    *,
    q2_label: Q2Label | IntroductionQ2Label | str | None = None,
    g1_outcome: GateOutcome | None = None,
) -> bool | None:
    """RQ5 derived metric (code-computed, R3 — never judged): did the model correctly decline on a
    `referral_expected` card?

    `None` for a card where `referral_expected` is `False` (the metric doesn't apply) or where the
    caller didn't supply the score this card's `question_type` needs — a `removal` card's caller
    passes `q2_label` (from `judge_q2_classification`'s `Q2_REMOVAL`-prompted `_q2_referral_note`
    branch, which scores a correct decline as `Q2Label.DECLINED`); an `identification` card's
    caller passes `g1_outcome` (from `judge_g1_identity_verified`'s `_g1_referral_note` branch,
    which scores a correct decline as `GateOutcome.PASS`).
    """
    if not card.referral_expected:
        return None
    if card.question_type == QuestionType.REMOVAL:
        if q2_label is None:
            return None
        return q2_label == Q2Label.DECLINED
    if card.question_type == QuestionType.IDENTIFICATION:
        if g1_outcome is None:
            return None
        return g1_outcome == GateOutcome.PASS
    return None


def compute_repeat_agreement(
    labels_by_card: dict[str, list[str]],
) -> dict[str, float]:
    """RQ6-adjacent noise-characterization pilot (`harness/scripts/run_repeat_pilot.py`): for each
    card, the share of its repeat runs sharing the single most common label for some one dimension
    (e.g. a gate outcome or a Q2 label) — 1.0 means every repeat agreed, lower means the dimension
    is sensitive to single-draw sampling noise on that card.

    Pure function, no API calls — `labels_by_card` maps `card_id` to the list of labels observed
    for that card across its repeat runs, already extracted by the caller for whichever dimension
    is being characterized (call once per dimension of interest, not once overall).
    """
    agreement: dict[str, float] = {}
    for card_id, labels in labels_by_card.items():
        if not labels:
            continue
        _, modal_count = Counter(labels).most_common(1)[0]
        agreement[card_id] = modal_count / len(labels)
    return agreement
