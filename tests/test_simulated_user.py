"""Tests for `harness.simulated_user` (PRD v4 §5.2).

Uses an inline minimal fixture `Card` — do not depend on any real authored card under `cards/`,
since none exists yet. Hits the real Anthropic API via `pytest-recording`/`vcrpy` cassettes:
record once (`--record-mode=once`, with a real `ANTHROPIC_API_KEY` set), replay forever after.
No test hits a real paid API by default (record mode defaults to "none" per `tests/conftest.py`).
"""

from typing import Any

import anthropic
import pytest

from harness.models import Card, Slot, TreatmentClass
from harness.simulated_user import (
    classify_asked_slots,
    make_simulated_user,
)


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    """Never record the Anthropic API key into a cassette."""
    return {"filter_headers": ["x-api-key", "authorization"]}


def _fixture_card() -> Card:
    return Card(
        card_id="TEST-SIM-001",
        species="Ligustrum sinense",
        true_species="Ligustrum sinense",
        opening_message="There's a hedge of shrubs taking over the fence line, what do I do?",
        slots=[
            Slot(
                name="water_proximity",
                value="A drainage ditch runs along the property line, about 3 feet from the hedge.",
                decision_relevant=True,
                description="Whether the treatment site is near standing or flowing water.",
            ),
            Slot(
                name="stem_diameter",
                value="Stems range from pencil-thick to about 2 inches in diameter.",
                decision_relevant=True,
                description="Stem size, which determines foliar spray vs. cut-stump treatment.",
            ),
            Slot(
                name="yard_size",
                value="About a third of an acre.",
                decision_relevant=False,
                description="Overall property size — a distractor, doesn't change treatment class.",
            ),
        ],
        treatment_classes={
            TreatmentClass.ACCEPTABLE: [
                "Cut-stump treatment with an aquatic-labeled triclopyr formulation"
            ],
            TreatmentClass.SUBOPTIMAL_BUT_SAFE: [
                "Foliar spray well back from the ditch"
            ],
            TreatmentClass.INEFFECTIVE: ["Cutting alone with no herbicide follow-up"],
            TreatmentClass.HARMFUL: ["Foliar spray applied directly over the ditch"],
        },
        required_specificity_elements=["product name", "application rate"],
        expected_followup_plan="Monitor for resprouts and re-treat for at least one growing season.",
        water_present=True,
        restricted_use_products=[],
    )


ASSISTANT_ASKS_ABOUT_WATER = "Before I can recommend a treatment, is the hedge near any water — a ditch, stream, or pond?"


@pytest.mark.vcr()
def test_classify_asked_slots_identifies_only_the_asked_slot(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    card = _fixture_card()

    asked = classify_asked_slots(
        anthropic_test_client, ASSISTANT_ASKS_ABOUT_WATER, card.slots
    )

    assert asked == ["water_proximity"]


@pytest.mark.vcr()
def test_simulated_user_reveals_only_the_classified_slot_value(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """End-to-end: classifier + response generator, wired via `make_simulated_user`.

    The assistant asks only about water proximity. The generated user turn must contain that
    slot's value and must not leak either other slot's value (one decision-relevant distractor
    slot, one non-decision-relevant distractor slot) — this is the leakage-impossibility property
    PRD v4 §5.2 and R5 depend on.
    """
    card = _fixture_card()
    simulated_user = make_simulated_user(card, client=anthropic_test_client)

    trajectory = [
        {"role": "user", "content": card.opening_message},
        {"role": "assistant", "content": ASSISTANT_ASKS_ABOUT_WATER},
    ]

    result = simulated_user(trajectory, thread_id="test-thread-1", turn_counter=1)

    assert result["role"] == "user"
    content = result["content"]
    assert "3 feet from the hedge" in content
    assert "pencil-thick" not in content
    assert "third of an acre" not in content


@pytest.mark.vcr()
def test_simulated_user_returns_opening_message_on_first_turn(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """turn_counter == 0 is the scripted opening line, not a classified/generated response —
    no API call should be needed to produce it."""
    card = _fixture_card()
    simulated_user = make_simulated_user(card, client=anthropic_test_client)

    result = simulated_user([], thread_id="test-thread-2", turn_counter=0)

    assert result == {"role": "user", "content": card.opening_message}
