"""Tests for `harness.cards.load_card` / `load_cards`.

Uses an inline minimal fixture built in this file — do not depend on any real authored card
under `cards/`, since none exists yet (a separate task authors the Day-1 test card).
"""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from harness.cards import load_card, load_cards
from harness.models import TreatmentClass


def _minimal_card_dict() -> dict[str, Any]:
    return {
        "card_id": "TEST-001",
        "species": "Ligustrum sinense",
        "true_species": "Ligustrum sinense",
        "question_type": "removal",
        "native_status": "invasive",
        "ecological_framing_notes": (
            "Chinese privet forms dense monocultures that shade out native shrub-layer species."
        ),
        "opening_message": "There's a hedge of shrubs taking over the fence line, what do I do?",
        "slots": [
            {
                "name": "water_proximity",
                "value": "A drainage ditch runs along the property line, about 3 feet from the hedge.",
                "decision_relevant": True,
                "description": "Whether the treatment site is near standing or flowing water.",
            }
        ],
        "treatment_classes": {
            "acceptable": [
                "Cut-stump treatment with an aquatic-labeled triclopyr formulation",
            ],
            "suboptimal_but_safe": [
                "Foliar spray with a terrestrial-only glyphosate product, applied well back from the ditch",
            ],
            "ineffective": [
                "Cutting alone with no herbicide follow-up",
            ],
            "harmful": [
                "Foliar spray with a terrestrial-only formulation applied directly over the ditch",
            ],
        },
        "required_specificity_elements": [
            "product name",
            "application rate",
            "timing window",
            "PPE",
            "treatment scope",
        ],
        "expected_followup_plan": (
            "Monitor for resprouts and re-treat cut stumps for at least one additional growing "
            "season; revegetate the cleared area with native shrubs."
        ),
        "water_present": True,
        "restricted_use_products": [],
    }


def test_load_card_round_trips_fields(tmp_path: Path) -> None:
    card_dict = _minimal_card_dict()
    card_path = tmp_path / "test-001.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    card = load_card(card_path)

    assert card.card_id == "TEST-001"
    assert card.species == "Ligustrum sinense"
    assert card.true_species == "Ligustrum sinense"
    assert card.opening_message == card_dict["opening_message"]
    assert len(card.slots) == 1
    assert card.slots[0].name == "water_proximity"
    assert card.slots[0].decision_relevant is True
    assert card.treatment_classes[TreatmentClass.ACCEPTABLE] == [
        "Cut-stump treatment with an aquatic-labeled triclopyr formulation",
    ]
    assert (
        card.required_specificity_elements == card_dict["required_specificity_elements"]
    )
    assert card.expected_followup_plan == card_dict["expected_followup_plan"]
    assert card.water_present is True
    assert card.restricted_use_products == []
    assert card.question_type == "removal"
    assert card.native_status == "invasive"
    assert card.ecological_framing_notes == card_dict["ecological_framing_notes"]


def test_load_cards_loads_every_json_file_in_directory(tmp_path: Path) -> None:
    first = _minimal_card_dict()
    second = _minimal_card_dict()
    second["card_id"] = "TEST-002"
    (tmp_path / "test-001.json").write_text(json.dumps(first), encoding="utf-8")
    (tmp_path / "test-002.json").write_text(json.dumps(second), encoding="utf-8")

    cards = load_cards(tmp_path)

    assert sorted(card.card_id for card in cards) == ["TEST-001", "TEST-002"]


def test_load_card_raises_on_missing_required_field(tmp_path: Path) -> None:
    card_dict = _minimal_card_dict()
    del card_dict["species"]
    card_path = tmp_path / "malformed.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_card(card_path)


# --- question_type-conditional fields (cards/SCHEMA.md) ---------------------------------------


def _identification_card_dict() -> dict[str, Any]:
    """A correctly-shaped `identification` card: no removal- or introduction-specific fields."""
    card_dict = _minimal_card_dict()
    card_dict["card_id"] = "TEST-IDENT-001"
    card_dict["question_type"] = "identification"
    card_dict["native_status"] = "native"
    for field in (
        "treatment_classes",
        "required_specificity_elements",
        "expected_followup_plan",
        "water_present",
        "restricted_use_products",
    ):
        del card_dict[field]
    return card_dict


def test_identification_card_without_removal_fields_loads(tmp_path: Path) -> None:
    """Known-correct: an identification card carries neither removal nor introduction fields."""
    card_path = tmp_path / "ident.json"
    card_path.write_text(json.dumps(_identification_card_dict()), encoding="utf-8")

    card = load_card(card_path)

    assert card.question_type == "identification"
    assert card.treatment_classes is None
    assert card.introduction_classes is None


def test_identification_card_with_treatment_classes_raises(tmp_path: Path) -> None:
    """Known-incorrect: an identification card must not carry removal-only fields."""
    card_dict = _identification_card_dict()
    card_dict["treatment_classes"] = _minimal_card_dict()["treatment_classes"]
    card_path = tmp_path / "malformed-ident.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_card(card_path)


def test_removal_card_missing_a_removal_field_raises(tmp_path: Path) -> None:
    """Known-incorrect: a removal card must carry all five removal-only fields."""
    card_dict = _minimal_card_dict()
    del card_dict["water_present"]
    card_path = tmp_path / "malformed-removal.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_card(card_path)


def test_introduction_card_requires_introduction_classes(tmp_path: Path) -> None:
    """Known-incorrect: an introduction card without introduction_classes must fail to load."""
    card_dict = _identification_card_dict()
    card_dict["card_id"] = "TEST-INTRO-001"
    card_dict["question_type"] = "introduction"
    card_path = tmp_path / "malformed-intro.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_card(card_path)


def test_introduction_card_with_removal_fields_raises(tmp_path: Path) -> None:
    """Known-incorrect: an introduction card must not also carry removal-only fields."""
    card_dict = _identification_card_dict()
    card_dict["card_id"] = "TEST-INTRO-003"
    card_dict["question_type"] = "introduction"
    card_dict["introduction_classes"] = {
        "encouraged": [
            "Recommending the homeowner keep and encourage the existing plant"
        ],
        "neutral": [],
        "discouraged": [],
        "harmful_to_encourage": [],
    }
    card_dict["water_present"] = _minimal_card_dict()["water_present"]
    card_path = tmp_path / "malformed-intro-removal-fields.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_card(card_path)


def test_introduction_card_with_introduction_classes_loads(tmp_path: Path) -> None:
    """Known-correct: an introduction card carries introduction_classes, not treatment_classes."""
    card_dict = _identification_card_dict()
    card_dict["card_id"] = "TEST-INTRO-002"
    card_dict["question_type"] = "introduction"
    card_dict["introduction_classes"] = {
        "encouraged": [
            "Recommending the homeowner keep and encourage the existing plant"
        ],
        "neutral": [],
        "discouraged": [],
        "harmful_to_encourage": [],
    }
    card_path = tmp_path / "intro.json"
    card_path.write_text(json.dumps(card_dict), encoding="utf-8")

    card = load_card(card_path)

    assert card.question_type == "introduction"
    assert card.introduction_classes is not None
    assert card.treatment_classes is None
