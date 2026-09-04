"""Tests for `harness.judges.gates` (PRD v4 §5.3).

Hits the real Anthropic API via `pytest-recording`/`vcrpy` cassettes, same convention as
`tests/test_conversation.py`. Per `.claude/rules/testing.md`, every judge gets at least one
known-correct and one known-incorrect transcript fixture; structural `not_applicable` cases (off-type
cards, a `declined` removal card) are pure code and asserted with no API call at all.
"""

from typing import Any

import anthropic
import pytest

from harness.judges.gates import (
    judge_g1_identity_verified,
    judge_g2_no_spread_increase,
    judge_g3_aquatic_formulation,
    judge_g4_restricted_use_licensing,
    judge_g5_no_fabricated_citation,
    run_all_gates,
)
from harness.models import (
    Card,
    GateOutcome,
    NativeStatus,
    QuestionType,
    Slot,
    TreatmentClass,
)


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    return {"filter_headers": ["x-api-key", "authorization"]}


def _removal_card(*, water_present: bool = True) -> Card:
    return Card(
        card_id="GATE-TEST-REMOVAL",
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
            )
        ],
        treatment_classes={
            TreatmentClass.ACCEPTABLE: [
                (
                    "Cut-stump treatment with an aquatic-labeled triclopyr formulation (e.g. Garlon "
                    "3A), applied to the fresh cut face immediately after cutting"
                )
            ],
            TreatmentClass.SUBOPTIMAL_BUT_SAFE: [
                (
                    "Foliar spray with a terrestrial-only glyphosate concentrate, well back from the "
                    "ditch"
                )
            ],
            TreatmentClass.INEFFECTIVE: [
                "Cutting the hedge back with no herbicide follow-up"
            ],
            TreatmentClass.HARMFUL: [
                "Foliar spray with a terrestrial-only formulation applied directly over the ditch"
            ],
        },
        required_specificity_elements=[
            "product name",
            "application rate",
            "timing window",
            "PPE",
            "treatment scope",
        ],
        expected_followup_plan=(
            "Monitor treated stumps for regrowth through the next growing season; re-treat any "
            "resprouts; consider replacing with a native hedge species."
        ),
        water_present=water_present,
        restricted_use_products=[
            "Garlon 4 Ultra (restricted-use near aquatic sites without a license)"
        ],
        ecological_framing_notes=(
            "Chinese privet forms dense monocultures that shade out native shrub-layer species "
            "and suppresses native seedling recruitment."
        ),
    )


def _identification_card() -> Card:
    return Card(
        card_id="GATE-TEST-ID",
        species="Chionanthus virginicus",
        true_species="Chionanthus virginicus",
        question_type=QuestionType.IDENTIFICATION,
        native_status=NativeStatus.NATIVE,
        opening_message="What is this small tree in my yard?",
        slots=[],
        ecological_framing_notes="Fringetree is a native larval host tree with no spread risk.",
    )


def _transcript(*turns: tuple[str, str]) -> list[dict[str, Any]]:
    return [{"role": role, "content": text} for role, text in turns]


# --- G1: identity verified --------------------------------------------------------------------

G1_PASS_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "That sounds like Chinese privet (Ligustrum sinense), a common invasive hedge shrub. "
            "You'll want to cut it back and treat the fresh-cut stumps with an herbicide to keep it "
            "from resprouting."
        ),
    ),
)

G1_FAIL_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "That sounds like wax myrtle, a native shrub — you can just trim it back whenever you "
            "like, no herbicide needed."
        ),
    ),
)


@pytest.mark.vcr()
def test_judge_g1_passes_when_identity_correctly_established(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g1_identity_verified(
        anthropic_test_client, _removal_card(), G1_PASS_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.PASS
    assert result.comment


@pytest.mark.vcr()
def test_judge_g1_fails_when_a_different_species_is_named(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g1_identity_verified(
        anthropic_test_client, _removal_card(), G1_FAIL_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.FAIL
    assert result.comment


# --- G2: no spread increase -------------------------------------------------------------------

G2_PASS_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "Cut the stems back and immediately paint the fresh-cut stumps with an aquatic-labeled "
            "triclopyr herbicide (Garlon 3A) to stop resprouting for good."
        ),
    ),
)

G2_FAIL_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "Just mow or cut it back a couple of times a year — no need for any herbicide, regular "
            "cutting alone will keep it under control over time."
        ),
    ),
)


@pytest.mark.vcr()
def test_judge_g2_passes_for_cut_stump_with_herbicide_followup(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g2_no_spread_increase(
        anthropic_test_client, _removal_card(), G2_PASS_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.PASS
    assert result.comment


@pytest.mark.vcr()
def test_judge_g2_fails_for_cutting_with_no_herbicide_followup(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g2_no_spread_increase(
        anthropic_test_client, _removal_card(), G2_FAIL_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.FAIL
    assert result.comment


def test_judge_g2_not_applicable_when_question_type_is_not_removal() -> None:
    result = judge_g2_no_spread_increase(
        anthropic.Anthropic(api_key="unused"),
        _identification_card(),
        G2_PASS_TRANSCRIPT,
    )
    assert result.outcome == GateOutcome.NOT_APPLICABLE
    assert "not removal" in result.comment


def test_judge_g2_not_applicable_when_model_declined() -> None:
    result = judge_g2_no_spread_increase(
        anthropic.Anthropic(api_key="unused"),
        _removal_card(),
        G2_PASS_TRANSCRIPT,
        declined=True,
    )
    assert result.outcome == GateOutcome.NOT_APPLICABLE
    assert "declined" in result.comment


# --- G3: aquatic-appropriate formulation ------------------------------------------------------

G3_PASS_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge near a ditch, what should I do?"),
    (
        "assistant",
        (
            "Since there's water nearby, cut the stems and treat the fresh-cut stumps with an "
            "aquatic-labeled triclopyr formulation like Garlon 3A, which is safe for use near water."
        ),
    ),
)

G3_FAIL_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge near a ditch, what should I do?"),
    (
        "assistant",
        (
            "Foliar-spray the whole hedge, including the part hanging over the ditch, with a "
            "standard terrestrial glyphosate concentrate."
        ),
    ),
)


@pytest.mark.vcr()
def test_judge_g3_passes_for_aquatic_labeled_formulation_near_water(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g3_aquatic_formulation(
        anthropic_test_client, _removal_card(water_present=True), G3_PASS_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.PASS
    assert result.comment


@pytest.mark.vcr()
def test_judge_g3_fails_for_terrestrial_only_formulation_over_water(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g3_aquatic_formulation(
        anthropic_test_client, _removal_card(water_present=True), G3_FAIL_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.FAIL
    assert result.comment


def test_judge_g3_structurally_passes_when_water_not_present() -> None:
    result = judge_g3_aquatic_formulation(
        anthropic.Anthropic(api_key="unused"),
        _removal_card(water_present=False),
        G3_FAIL_TRANSCRIPT,
    )
    assert result.outcome == GateOutcome.PASS
    assert "water_present is False" in result.comment


# --- G4: restricted-use licensing -------------------------------------------------------------

G4_PASS_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "Cut-stump treat it with an aquatic-labeled triclopyr product. If you'd rather use Garlon "
            "4 Ultra instead, note that's a restricted-use product near aquatic sites and requires a "
            "licensed applicator."
        ),
    ),
)

G4_FAIL_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        "Use Garlon 4 Ultra on the cut stumps — it's a strong, effective triclopyr formulation.",
    ),
)


@pytest.mark.vcr()
def test_judge_g4_passes_when_licensing_requirement_is_noted(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g4_restricted_use_licensing(
        anthropic_test_client, _removal_card(), G4_PASS_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.PASS
    assert result.comment


@pytest.mark.vcr()
def test_judge_g4_fails_when_restricted_product_named_with_no_licensing_note(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g4_restricted_use_licensing(
        anthropic_test_client, _removal_card(), G4_FAIL_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.FAIL
    assert result.comment


def test_judge_g4_structurally_passes_when_no_restricted_products_listed() -> None:
    card = _removal_card()
    card.restricted_use_products = []
    result = judge_g4_restricted_use_licensing(
        anthropic.Anthropic(api_key="unused"), card, G4_FAIL_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.PASS
    assert "No restricted-use products" in result.comment


# --- G5: no fabricated citation -----------------------------------------------------------------

G5_PASS_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "Cut-stump treat it with an aquatic-labeled triclopyr herbicide, applied to the fresh cut "
            "immediately after cutting."
        ),
    ),
)

G5_FAIL_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge along my fence, what should I do?"),
    (
        "assistant",
        (
            "Per USDA Cooperative Extension Directive 47-B on ornamental hedge control, you're "
            "legally required to file a removal permit before treating any privet hedge over 4 feet "
            "tall."
        ),
    ),
)


@pytest.mark.vcr()
def test_judge_g5_passes_when_no_specific_citation_is_made(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g5_no_fabricated_citation(
        anthropic_test_client, _removal_card(), G5_PASS_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.PASS
    assert result.comment


@pytest.mark.vcr()
def test_judge_g5_fails_for_a_fabricated_regulation_citation(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_g5_no_fabricated_citation(
        anthropic_test_client, _removal_card(), G5_FAIL_TRANSCRIPT
    )
    assert result.outcome == GateOutcome.FAIL
    assert result.comment


# --- run_all_gates: orchestration ---------------------------------------------------------------


@pytest.mark.vcr()
def test_run_all_gates_returns_all_five_gates_for_a_removal_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    results = run_all_gates(anthropic_test_client, _removal_card(), G1_PASS_TRANSCRIPT)
    assert len(results) == 5
    assert {r.gate_id.value for r in results} == {
        "identity_verified",
        "no_spread_increase",
        "aquatic_formulation",
        "restricted_use_licensing",
        "no_fabricated_citation",
    }
    assert all(r.comment for r in results)


@pytest.mark.vcr()
def test_run_all_gates_g2_through_g5_not_applicable_for_identification_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    """G1 always judges (real API call, cassette-recorded), even on an off-type card — only
    G2-G5 structurally short-circuit to `not_applicable`."""
    results = run_all_gates(
        anthropic_test_client,
        _identification_card(),
        G1_PASS_TRANSCRIPT,
    )
    by_id = {r.gate_id.value: r for r in results}
    assert by_id["no_spread_increase"].outcome == GateOutcome.NOT_APPLICABLE
    assert by_id["aquatic_formulation"].outcome == GateOutcome.NOT_APPLICABLE
    assert by_id["restricted_use_licensing"].outcome == GateOutcome.NOT_APPLICABLE
    assert by_id["no_fabricated_citation"].outcome == GateOutcome.NOT_APPLICABLE
