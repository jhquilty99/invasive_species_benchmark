"""Tests for `harness.ground_truth` (Q4's ground-truth loader, PRD v4 §5.3).

Reads the real `data/ground_truth/*.yaml` files rather than a fixture copy — that's the actual
ground truth Q4 scores against, and it's small/stable enough to depend on directly, same convention
implicitly relied on by `tests/test_quality.py`'s Q4 tests.
"""

from pathlib import Path

import pytest

from harness.ground_truth import (
    GroundTruth,
    load_ground_truth,
    load_ground_truth_for_card,
)
from harness.models import Card, NativeStatus, QuestionType, TreatmentClass


def _removal_card(true_species: str) -> Card:
    return Card(
        card_id="GT-TEST",
        species=true_species,
        true_species=true_species,
        question_type=QuestionType.REMOVAL,
        native_status=NativeStatus.INVASIVE,
        opening_message="There's an overgrown hedge along the fence, what should I do?",
        slots=[],
        treatment_classes={TreatmentClass.ACCEPTABLE: ["Cut-stump treatment"]},
        required_specificity_elements=["product", "rate", "timing"],
        expected_followup_plan="Monitor for resprouts.",
        water_present=False,
        restricted_use_products=[],
        ecological_framing_notes="Forms dense monocultures.",
    )


def test_load_ground_truth_returns_populated_cells() -> None:
    ground_truth = load_ground_truth("ligustrum-sinense")
    assert isinstance(ground_truth, GroundTruth)
    assert ground_truth.species == "Ligustrum sinense"
    assert ground_truth.cells
    assert all(cell.citation.source for cell in ground_truth.cells)


def test_load_ground_truth_raises_for_a_nonexistent_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_ground_truth("not-a-real-species")


def test_load_ground_truth_for_card_resolves_every_removal_species() -> None:
    for true_species in (
        "Ailanthus altissima",
        "Ligustrum sinense",
        "Microstegium vimineum",
        "Wisteria sinensis",
        "Pyrus calleryana",
        "Phragmites australis ssp. australis",
    ):
        ground_truth = load_ground_truth_for_card(_removal_card(true_species))
        assert ground_truth.species.lower().startswith(true_species.split()[0].lower())


def test_load_ground_truth_for_card_raises_key_error_for_unmapped_species() -> None:
    with pytest.raises(KeyError):
        load_ground_truth_for_card(_removal_card("Some Unmapped Species"))


def test_ground_truth_yaml_directory_matches_expected_path() -> None:
    from harness.ground_truth import GROUND_TRUTH_DIR

    assert (
        GROUND_TRUTH_DIR
        == Path(__file__).resolve().parent.parent / "data" / "ground_truth"
    )
    assert GROUND_TRUTH_DIR.is_dir()
