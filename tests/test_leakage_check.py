"""Tests for `harness.leakage_check` (PRD v4 §6 R5).

Cases that need `classify_asked_slots` to know what an assistant turn actually asked about are
VCR-cassette-based, matching `tests/test_scoring.py`'s pattern. Cases that never need a real
elicitation judgment (a leak in the opening turn before any assistant turn exists; the oracle-arm
short-circuit; the short-value guard) are plain unit tests with no API call at all.
"""

from typing import Any

import anthropic
import pytest

from harness.leakage_check import LeakageReport, check_leakage
from harness.models import Card, NativeStatus, QuestionType, Slot, TreatmentClass


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    return {"filter_headers": ["x-api-key", "authorization"]}


def _card() -> Card:
    return Card(
        card_id="LEAKAGE-TEST",
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


# --- pure cases: no assistant turn precedes the check, no API call needed -----------------------


def test_check_leakage_flags_a_slot_value_leaked_in_the_opening_turn() -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, and there's a drainage ditch "
            "runs along the property line, about 3 feet from the hedge. What should I do?",
        ),
    ]

    result = check_leakage(anthropic.Anthropic(api_key="unused"), _card(), trajectory)

    assert result == LeakageReport(
        leaked=True,
        leaked_slots=["water_proximity"],
        details=[
            (
                'turn 0: slot "water_proximity" value appeared in a user turn before any '
                "assistant turn asked about it."
            )
        ],
    )


def test_check_leakage_no_leak_when_opening_turn_stays_vague() -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
    ]

    result = check_leakage(anthropic.Anthropic(api_key="unused"), _card(), trajectory)

    assert result == LeakageReport(leaked=False, leaked_slots=[], details=[])


def test_check_leakage_oracle_arm_does_not_flag_pre_disclosed_decision_relevant_slots() -> (
    None
):
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do? A drainage "
            "ditch runs along the property line, about 3 feet from the hedge.",
        ),
    ]

    result = check_leakage(
        anthropic.Anthropic(api_key="unused"), _card(), trajectory, oracle=True
    )

    assert result == LeakageReport(leaked=False, leaked_slots=[], details=[])


def test_check_leakage_short_slot_value_is_never_flagged() -> None:
    card = _card()
    card.slots.append(
        Slot(
            name="has_pets",
            value="No",
            decision_relevant=False,
            description="Whether pets have access to the treatment area.",
        )
    )
    trajectory = [
        _msg("user", "No idea what this is but it's spreading fast, help."),
    ]

    result = check_leakage(anthropic.Anthropic(api_key="unused"), card, trajectory)

    assert result == LeakageReport(leaked=False, leaked_slots=[], details=[])


# --- cases needing classify_asked_slots (VCR cassette) ------------------------------------------


@pytest.mark.vcr()
def test_check_leakage_no_leak_when_slot_properly_elicited(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
        _msg("assistant", "Is there any water nearby, like a ditch or pond?"),
        _msg("user", "Yeah, there's a drainage ditch about 3 feet away."),
    ]

    result = check_leakage(anthropic_test_client, _card(), trajectory)

    assert result == LeakageReport(leaked=False, leaked_slots=[], details=[])


@pytest.mark.vcr()
def test_check_leakage_flags_a_distractor_leaked_alongside_a_properly_elicited_slot(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    trajectory = [
        _msg(
            "user",
            "There's an overgrown hedge of shrubs along the fence, what should I do?",
        ),
        _msg("assistant", "Is there any water nearby, like a ditch or pond?"),
        _msg(
            "user",
            "Yeah, there's a drainage ditch about 3 feet away. About a third of an acre. That's "
            "the whole property if that matters.",
        ),
    ]

    result = check_leakage(anthropic_test_client, _card(), trajectory)

    assert result == LeakageReport(
        leaked=True,
        leaked_slots=["yard_size"],
        details=[
            (
                'turn 2: slot "yard_size" value appeared in a user turn before any assistant '
                "turn asked about it."
            )
        ],
    )
