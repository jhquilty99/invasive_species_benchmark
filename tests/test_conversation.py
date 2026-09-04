"""Tests for `harness.conversation` (PRD v4 §6).

Hits the real Anthropic API via `pytest-recording`/`vcrpy` cassettes, same convention as
`tests/test_simulated_user.py`: record once (`--record-mode=once`, with a real `ANTHROPIC_API_KEY`
set), replay forever after. No test hits a real paid API by default (record mode defaults to "none"
per `tests/conftest.py`). No cassettes have been recorded yet in this environment (no root `.env`),
so every VCR-marked test below is expected to fail on a missing-cassette error until someone with a
real API key records them — this mirrors `test_simulated_user.py`'s current state exactly.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import anthropic
import pytest

from harness.cards import load_card
from harness.conversation import (
    is_species_identified,
    is_specific_introduction_recommendation,
    is_specific_prescription,
    is_terminal_response,
    run_conversation,
)
from harness.models import Card, NativeStatus, QuestionType, Slot

CARDS_DIR = Path(__file__).parent.parent / "cards"


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    """Never record the Anthropic API key into a cassette."""
    return {"filter_headers": ["x-api-key", "authorization"]}


# --- is_specific_prescription: the DECISION-LOG stopping-condition rule, directly tested --------

SPECIFIC_SINGLE_RECOMMENDATION = (
    "Cut each resprout cluster back close to the stump and immediately paint or spray the "
    "fresh-cut stem surface with undiluted Garlon 3A (triclopyr 8.8%). Do this now, in early "
    "September — you're still within the mid-summer-to-early-fall window herbicide needs to "
    "translocate to the roots. Keep the herbicide confined to the cut stems only, well clear of "
    "your vegetable garden and grapevines 15 feet away, and stay out of the treated area for 48 "
    "hours afterward per the label's re-entry interval."
)

HEDGED_UNRANKED_OPTIONS = (
    "There are a few routes you could take here: you could cut the stumps and treat the fresh cuts "
    "with a triclopyr herbicide, or you could foliar-spray the new resprout growth instead, or you "
    "could just keep mowing it back if you'd rather avoid herbicide altogether. Each has trade-offs "
    "depending on how much time and effort you want to put in."
)

REQUESTS_MORE_INFO = (
    "Before I can recommend a treatment, I need a bit more detail — how thick are the resprouts "
    "that are coming up now, and is there any standing water or a garden near where you'd be "
    "treating?"
)


@pytest.mark.vcr()
def test_is_specific_prescription_true_for_a_single_actionable_recommendation(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """A named product, rate/dilution, timing window, scope, and REI — the exact bar the
    DECISION-LOG rule sets for a specific prescription."""
    result = is_specific_prescription(
        SPECIFIC_SINGLE_RECOMMENDATION, client=anthropic_test_client
    )

    assert result is True


@pytest.mark.vcr()
def test_is_specific_prescription_false_for_an_unranked_options_list(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """Directly tests the DECISION-LOG.md 2026-09-03 rule: an unranked "you could do X or Y" list
    does NOT count as a specific prescription, no matter how detailed each option is."""
    result = is_specific_prescription(
        HEDGED_UNRANKED_OPTIONS, client=anthropic_test_client
    )

    assert result is False


@pytest.mark.vcr()
def test_is_specific_prescription_false_for_a_request_for_more_information(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = is_specific_prescription(REQUESTS_MORE_INFO, client=anthropic_test_client)

    assert result is False


# --- is_specific_introduction_recommendation: the `introduction`-card stopping classifier -------

SPECIFIC_KEEP_RECOMMENDATION = (
    "Keep it — that's a native fringetree, not an invasive species, and it's a great low-maintenance "
    "small tree that supports local pollinators. No need to remove or replace it."
)

HEDGED_KEEP_OR_REMOVE_OPTIONS = (
    "You could keep it if you like the look, or you could remove it and plant something else if "
    "you'd rather have more sun in that corner — really depends on what you want out of that spot."
)


@pytest.mark.vcr()
def test_is_specific_introduction_recommendation_true_for_a_committed_keep_recommendation(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = is_specific_introduction_recommendation(
        SPECIFIC_KEEP_RECOMMENDATION, client=anthropic_test_client
    )

    assert result is True


@pytest.mark.vcr()
def test_is_specific_introduction_recommendation_false_for_hedged_keep_or_remove_options(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = is_specific_introduction_recommendation(
        HEDGED_KEEP_OR_REMOVE_OPTIONS, client=anthropic_test_client
    )

    assert result is False


# --- is_species_identified: the `identification`-card stopping classifier -----------------------

COMMITTED_IDENTIFICATION = (
    "Based on the opposite leaves, four-petaled white flowers, and fringe-like bloom shape, this is "
    "fringetree (Chionanthus virginicus) — a native small tree, not an invasive species."
)

HEDGED_CANDIDATE_LIST = (
    "This could be a few different things — it might be fringetree, or possibly a privet if the "
    "leaves are opposite and glossy, or even a young ash if the leaflets are compound. Hard to say "
    "without a closer look."
)


@pytest.mark.vcr()
def test_is_species_identified_true_for_a_committed_identification(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = is_species_identified(
        COMMITTED_IDENTIFICATION, client=anthropic_test_client
    )

    assert result is True


@pytest.mark.vcr()
def test_is_species_identified_false_for_a_hedged_candidate_list(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = is_species_identified(HEDGED_CANDIDATE_LIST, client=anthropic_test_client)

    assert result is False


# --- is_terminal_response: question_type dispatch, no API calls needed to test the routing ------


def _minimal_card(question_type: QuestionType) -> Card:
    slots = [
        Slot(
            name="leaf_arrangement",
            value="Opposite leaves.",
            decision_relevant=True,
            description="Whether leaves are opposite or alternate.",
        )
    ]
    ecological_framing_notes = "Fringetree is a native larval host with no spread risk."

    if question_type == QuestionType.REMOVAL:
        return Card(
            card_id="TEST-DISPATCH",
            species="Chionanthus virginicus",
            true_species="Chionanthus virginicus",
            native_status=NativeStatus.NATIVE,
            opening_message="What is this plant?",
            slots=slots,
            ecological_framing_notes=ecological_framing_notes,
            question_type=QuestionType.REMOVAL,
            treatment_classes={},
            required_specificity_elements=["product"],
            expected_followup_plan="Monitor.",
            water_present=False,
            restricted_use_products=[],
        )
    if question_type == QuestionType.INTRODUCTION:
        return Card(
            card_id="TEST-DISPATCH",
            species="Chionanthus virginicus",
            true_species="Chionanthus virginicus",
            native_status=NativeStatus.NATIVE,
            opening_message="What is this plant?",
            slots=slots,
            ecological_framing_notes=ecological_framing_notes,
            question_type=QuestionType.INTRODUCTION,
            introduction_classes={},
        )
    return Card(
        card_id="TEST-DISPATCH",
        species="Chionanthus virginicus",
        true_species="Chionanthus virginicus",
        native_status=NativeStatus.NATIVE,
        opening_message="What is this plant?",
        slots=slots,
        ecological_framing_notes=ecological_framing_notes,
        question_type=QuestionType.IDENTIFICATION,
    )


def test_is_terminal_response_dispatches_removal_to_is_specific_prescription(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock = MagicMock(return_value=True)
    monkeypatch.setattr("harness.conversation.is_specific_prescription", mock)

    result = is_terminal_response(_minimal_card(QuestionType.REMOVAL), "some message")

    assert result is True
    mock.assert_called_once()


def test_is_terminal_response_dispatches_introduction_to_introduction_classifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock = MagicMock(return_value=True)
    monkeypatch.setattr(
        "harness.conversation.is_specific_introduction_recommendation", mock
    )

    result = is_terminal_response(
        _minimal_card(QuestionType.INTRODUCTION), "some message"
    )

    assert result is True
    mock.assert_called_once()


def test_is_terminal_response_dispatches_identification_to_is_species_identified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock = MagicMock(return_value=True)
    monkeypatch.setattr("harness.conversation.is_species_identified", mock)

    result = is_terminal_response(
        _minimal_card(QuestionType.IDENTIFICATION), "some message"
    )

    assert result is True
    mock.assert_called_once()


# --- Full loop: real card, short max_turns to keep the cassette small ---------------------------


@pytest.mark.vcr()
def test_run_conversation_completes_with_the_real_ailanthus_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """End-to-end smoke test against the real Day 1 test card, capped at a small `max_turns` to
    keep the recorded cassette short. Asserts only on shape (trajectory starts with the card's
    opening message, alternates user/assistant, stays within the turn cap) rather than on model
    content, since the model-under-test's actual replies aren't something this test should pin —
    that's the judges' job (Day 2), not this harness-wiring test's.
    """
    card = load_card(CARDS_DIR / "ailanthus-stump-resprout-01.json")

    result = run_conversation(card, client=anthropic_test_client, max_turns=3)

    trajectory = result.trajectory
    assert trajectory[0]["role"] == "user"
    assert trajectory[0]["content"] == card.opening_message
    assert len(trajectory) <= 3 * 2
    for i, message in enumerate(trajectory):
        expected_role = "user" if i % 2 == 0 else "assistant"
        assert message["role"] == expected_role
    assert result.trace_id is None  # no langfuse_client passed


@pytest.mark.vcr()
def test_run_conversation_completes_with_the_real_identification_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """Same shape-only smoke test as the removal card above, but for an `identification`-type card —
    exercises the new `is_species_identified` stopping-condition path end to end, not just the
    `removal` classifier the harness originally shipped with."""
    card = load_card(CARDS_DIR / "chionanthus-virginicus-lookalike-01.json")

    result = run_conversation(card, client=anthropic_test_client, max_turns=3)

    trajectory = result.trajectory
    assert trajectory[0]["role"] == "user"
    assert trajectory[0]["content"] == card.opening_message
    assert len(trajectory) <= 3 * 2
    for i, message in enumerate(trajectory):
        expected_role = "user" if i % 2 == 0 else "assistant"
        assert message["role"] == expected_role
