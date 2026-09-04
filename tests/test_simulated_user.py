"""Tests for `harness.simulated_user` (PRD v4 §5.2).

Uses an inline minimal fixture `Card` — do not depend on any real authored card under `cards/`,
since none exists yet. Hits the real Anthropic API via `pytest-recording`/`vcrpy` cassettes:
record once (`--record-mode=once`, with a real `ANTHROPIC_API_KEY` set), replay forever after.
No test hits a real paid API by default (record mode defaults to "none" per `tests/conftest.py`).
"""

from typing import Any

import anthropic
import pytest

from harness.models import Card, NativeStatus, QuestionType, Slot, TreatmentClass
from harness.simulated_user import (
    build_oracle_opening_message,
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
        question_type=QuestionType.REMOVAL,
        native_status=NativeStatus.INVASIVE,
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
        ecological_framing_notes=(
            "Chinese privet forms dense monocultures that shade out native shrub-layer species."
        ),
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


# --- oracle-contrast arm (RQ1) -------------------------------------------------------------------


def test_build_oracle_opening_message_includes_every_decision_relevant_slot_value() -> (
    None
):
    card = _fixture_card()

    message = build_oracle_opening_message(card)

    assert card.opening_message in message
    assert "3 feet from the hedge" in message  # water_proximity (decision_relevant)
    assert "pencil-thick" in message  # stem_diameter (decision_relevant)
    assert "third of an acre" not in message  # yard_size (NOT decision_relevant)


def test_build_oracle_opening_message_with_no_decision_relevant_slots_is_unchanged() -> (
    None
):
    card = _fixture_card()
    for slot in card.slots:
        slot.decision_relevant = False

    assert build_oracle_opening_message(card) == card.opening_message


def test_simulated_user_oracle_mode_discloses_decision_relevant_slots_on_first_turn(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """No API call needed here either — oracle mode's turn-0 branch, like the standard branch,
    builds the opening message from the card alone."""
    card = _fixture_card()
    simulated_user = make_simulated_user(
        card, client=anthropic_test_client, oracle=True
    )

    result = simulated_user([], thread_id="test-thread-oracle-1", turn_counter=0)

    assert result["role"] == "user"
    assert "3 feet from the hedge" in result["content"]
    assert "pencil-thick" in result["content"]
    assert "third of an acre" not in result["content"]


def test_simulated_user_oracle_mode_does_not_reveal_already_disclosed_slots_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every decision-relevant slot was already disclosed at turn 0 in oracle mode — if the model
    then explicitly asks about one anyway, the response generator must not be told it's newly
    asked (it's already in `revealed` from the turn-0 pre-seed). Monkeypatches the classifier and
    response generator to make this a deterministic, API-free assertion on exactly what
    `generate_user_response` is called with, rather than inferring it from generated text.
    """
    import harness.simulated_user as simulated_user_module

    card = _fixture_card()
    monkeypatch.setattr(
        simulated_user_module,
        "classify_asked_slots",
        lambda *a, **k: ["water_proximity"],
    )
    captured: dict[str, Any] = {}

    def _fake_generate_user_response(
        client: Any, assistant_message: str, revealed_slots: list[Slot], **kwargs: Any
    ) -> str:
        captured["revealed_slots"] = revealed_slots
        return "okay"

    monkeypatch.setattr(
        simulated_user_module, "generate_user_response", _fake_generate_user_response
    )

    simulated_user = make_simulated_user(
        card, client=anthropic.Anthropic(api_key="unused"), oracle=True
    )
    simulated_user(
        [], thread_id="test-thread-oracle-2", turn_counter=0
    )  # seeds revealed state

    trajectory = [
        {"role": "user", "content": build_oracle_opening_message(card)},
        {"role": "assistant", "content": ASSISTANT_ASKS_ABOUT_WATER},
    ]
    simulated_user(trajectory, thread_id="test-thread-oracle-2", turn_counter=1)

    assert captured["revealed_slots"] == []
