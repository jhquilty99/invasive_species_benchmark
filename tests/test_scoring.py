"""Tests for `harness.scoring` (PRD v4 §5.3/§5.4).

`determine_stopping_turn` and `compute_q1` re-run real classifier calls against a fixed trajectory, so
they're VCR-cassette-based like the rest of the judge-adjacent tests. `premature_prescription_rate`
and `hit_max_turns_rate` are pure aggregate functions and get plain unit tests with fixed input, no
cassette needed.
"""

from typing import Any

import anthropic
import pytest

from harness.models import Card, NativeStatus, QuestionType, Slot, TreatmentClass
from harness.scoring import (
    Q1Result,
    TurnMetrics,
    compute_q1,
    determine_stopping_turn,
    hit_max_turns_rate,
    premature_prescription_rate,
)


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    return {"filter_headers": ["x-api-key", "authorization"]}


def _card() -> Card:
    return Card(
        card_id="SCORING-TEST",
        species="Ligustrum sinense",
        true_species="Ligustrum sinense",
        question_type=QuestionType.REMOVAL,
        native_status=NativeStatus.INVASIVE,
        opening_message="There's an overgrown hedge of shrubs along the fence, what should I do?",
        slots=[
            Slot(
                name="water_proximity",
                value="A drainage ditch runs along the property line, about 3 feet from the hedge.",
                decision_relevant=True,
                description="Whether the treatment site is near standing or flowing water.",
            ),
            Slot(
                name="yard_size",
                value="About a third of an acre.",
                decision_relevant=False,
                description="Overall property size — doesn't change which treatment class applies.",
            ),
        ],
        treatment_classes={
            TreatmentClass.ACCEPTABLE: ["Cut-stump treatment with triclopyr"]
        },
        required_specificity_elements=["product", "rate", "timing"],
        expected_followup_plan="Monitor for resprouts through next season.",
        water_present=True,
        restricted_use_products=[],
        ecological_framing_notes="Chinese privet forms dense monocultures.",
    )


def _msg(role: str, text: str) -> dict[str, Any]:
    return {"role": role, "content": text}


SPECIFIC_RECOMMENDATION = (
    "Cut each stem back and immediately paint the fresh-cut stump surface with undiluted Garlon "
    "3A (triclopyr 8.8%). Do this now, in early fall, while sap is still moving to the roots."
)

REQUESTS_MORE_INFO = (
    "Before I can recommend a treatment, I'd need to know how thick the stems are and whether "
    "there's any water nearby."
)


# --- determine_stopping_turn ---------------------------------------------------------------------


@pytest.mark.vcr()
def test_determine_stopping_turn_detects_an_early_specific_prescription(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
        _msg("assistant", "Is there any water nearby, like a ditch or pond?"),
        _msg("user", "Yeah, there's a drainage ditch about 3 feet away."),
        _msg("assistant", SPECIFIC_RECOMMENDATION),
    ]

    result = determine_stopping_turn(anthropic_test_client, _card(), trajectory)

    assert result == TurnMetrics(turns_to_recommendation=2, hit_max_turns=False)


@pytest.mark.vcr()
def test_determine_stopping_turn_detects_hit_max_turns(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
        _msg("assistant", REQUESTS_MORE_INFO),
    ]

    result = determine_stopping_turn(anthropic_test_client, _card(), trajectory)

    assert result == TurnMetrics(turns_to_recommendation=None, hit_max_turns=True)


def test_determine_stopping_turn_empty_trajectory() -> None:
    result = determine_stopping_turn(anthropic.Anthropic(api_key="unused"), _card(), [])
    assert result == TurnMetrics(turns_to_recommendation=None, hit_max_turns=False)


# --- compute_q1 -----------------------------------------------------------------------------------


@pytest.mark.vcr()
def test_compute_q1_all_decision_relevant_slots_elicited(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
        _msg("assistant", "Is there any water nearby, like a ditch or pond?"),
        _msg("user", "Yeah, there's a drainage ditch about 3 feet away."),
        _msg("assistant", SPECIFIC_RECOMMENDATION),
    ]
    turn_metrics = TurnMetrics(turns_to_recommendation=2, hit_max_turns=False)

    result = compute_q1(anthropic_test_client, _card(), trajectory, turn_metrics)

    assert result.all_decision_relevant_elicited is True
    assert result.elicited_decision_relevant_slots == ["water_proximity"]
    assert result.missing_decision_relevant_slots == []


@pytest.mark.vcr()
def test_compute_q1_flags_a_missing_decision_relevant_slot_and_a_distractor(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
        _msg("assistant", "About how big is your yard overall?"),
        _msg("user", "About a third of an acre."),
        _msg("assistant", SPECIFIC_RECOMMENDATION),
    ]
    turn_metrics = TurnMetrics(turns_to_recommendation=2, hit_max_turns=False)

    result = compute_q1(anthropic_test_client, _card(), trajectory, turn_metrics)

    assert result.all_decision_relevant_elicited is False
    assert result.missing_decision_relevant_slots == ["water_proximity"]
    assert result.distractor_slots_asked == ["yard_size"]


# --- aggregate rate functions: pure code, no API ------------------------------------------------


def test_premature_prescription_rate_over_mixed_results() -> None:
    results = [
        Q1Result(True, ["a"], [], []),
        Q1Result(False, [], ["a"], []),
        Q1Result(False, [], ["a"], []),
        Q1Result(True, ["a"], [], []),
    ]
    assert premature_prescription_rate(results) == 0.5


def test_premature_prescription_rate_empty_input() -> None:
    assert premature_prescription_rate([]) == 0.0


def test_hit_max_turns_rate_over_mixed_results() -> None:
    metrics = [
        TurnMetrics(2, False),
        TurnMetrics(None, True),
        TurnMetrics(4, False),
        TurnMetrics(None, True),
    ]
    assert hit_max_turns_rate(metrics) == 0.5


def test_hit_max_turns_rate_empty_input() -> None:
    assert hit_max_turns_rate([]) == 0.0
