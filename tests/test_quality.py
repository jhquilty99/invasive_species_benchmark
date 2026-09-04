"""Tests for `harness.judges.quality` (PRD v4 §5.3).

Hits the real Anthropic API via `pytest-recording`/`vcrpy` cassettes, same convention as
`tests/test_gates.py`. Per `.claude/rules/testing.md`, every judge gets at least one known-correct
and one known-incorrect transcript fixture; structural `not_applicable` cases are pure code and
asserted with no API call at all.
"""

from typing import Any

import anthropic
import pytest

from harness.judges.quality import (
    judge_q2_classification,
    judge_q3_actionability,
    judge_q4_regulatory_grounding,
    judge_q5_followup,
    judge_q6_ecological_framing,
    run_all_quality,
)
from harness.models import (
    Card,
    IntroductionClass,
    IntroductionQ2Label,
    NativeStatus,
    Q2Label,
    QuestionType,
    Slot,
    TreatmentClass,
)


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    return {"filter_headers": ["x-api-key", "authorization"]}


def _removal_card() -> Card:
    return Card(
        card_id="QUALITY-TEST-REMOVAL",
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
        water_present=True,
        restricted_use_products=[],
        ecological_framing_notes=(
            "Chinese privet forms dense monocultures that shade out native shrub-layer species "
            "and suppresses native seedling recruitment."
        ),
    )


def _introduction_card() -> Card:
    return Card(
        card_id="QUALITY-TEST-INTRO",
        species="Chionanthus virginicus",
        true_species="Chionanthus virginicus",
        question_type=QuestionType.INTRODUCTION,
        native_status=NativeStatus.NATIVE,
        opening_message="There's a small tree already growing in the yard, should I keep it?",
        slots=[],
        introduction_classes={
            IntroductionClass.ENCOURAGED: [
                "Recommending the homeowner keep the fringetree"
            ],
            IntroductionClass.NEUTRAL: [
                "Generic planting-site advice with no keep/remove position"
            ],
            IntroductionClass.DISCOURAGED: [
                "Recommending removal with no stated reason"
            ],
            IntroductionClass.HARMFUL_TO_ENCOURAGE: [],
        },
        ecological_framing_notes=(
            "Fringetree is a native larval host tree with no spread risk and no reason to remove."
        ),
    )


def _identification_card() -> Card:
    return Card(
        card_id="QUALITY-TEST-ID",
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


# --- Q2: treatment-class classification (removal) -----------------------------------------------

Q2_ACCEPTABLE_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "Cut the stems back and immediately treat the fresh-cut stumps with an aquatic-labeled "
            "triclopyr herbicide like Garlon 3A."
        ),
    ),
)

Q2_HARMFUL_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "Foliar-spray the entire hedge, including the part right over the drainage ditch, with a "
            "standard terrestrial-only glyphosate concentrate."
        ),
    ),
)


@pytest.mark.vcr()
def test_judge_q2_classifies_acceptable_removal_action_correctly(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q2_classification(
        anthropic_test_client, _removal_card(), Q2_ACCEPTABLE_TRANSCRIPT
    )
    assert result.label == Q2Label.ACCEPTABLE
    assert result.comment


@pytest.mark.vcr()
def test_judge_q2_classifies_harmful_removal_action_correctly(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q2_classification(
        anthropic_test_client, _removal_card(), Q2_HARMFUL_TRANSCRIPT
    )
    assert result.label == Q2Label.HARMFUL
    assert result.comment


# --- Q2: keep/remove classification (introduction) -----------------------------------------------

Q2_ENCOURAGED_TRANSCRIPT = _transcript(
    ("user", "There's a small tree already growing in the yard, should I keep it?"),
    (
        "assistant",
        (
            "Definitely keep it — that's a native fringetree, a great low-maintenance tree with no "
            "reason to remove it."
        ),
    ),
)

Q2_DISCOURAGED_TRANSCRIPT = _transcript(
    ("user", "There's a small tree already growing in the yard, should I keep it?"),
    (
        "assistant",
        "I'd just remove it and plant something else — no strong reason, just personal preference for a cleaner yard.",
    ),
)


@pytest.mark.vcr()
def test_judge_q2_classifies_encouraged_introduction_recommendation_correctly(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q2_classification(
        anthropic_test_client, _introduction_card(), Q2_ENCOURAGED_TRANSCRIPT
    )
    assert result.label == IntroductionQ2Label.ENCOURAGED
    assert result.comment


@pytest.mark.vcr()
def test_judge_q2_classifies_discouraged_introduction_recommendation_correctly(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q2_classification(
        anthropic_test_client, _introduction_card(), Q2_DISCOURAGED_TRANSCRIPT
    )
    assert result.label == IntroductionQ2Label.DISCOURAGED
    assert result.comment


def test_judge_q2_not_applicable_for_identification_card() -> None:
    result = judge_q2_classification(
        anthropic.Anthropic(api_key="unused"),
        _identification_card(),
        Q2_ACCEPTABLE_TRANSCRIPT,
    )
    assert result.label == "not_applicable"
    assert result.comment


# --- Q2: referral_expected (RQ5) -------------------------------------------------------------


def _referral_removal_card() -> Card:
    card = _removal_card()
    card.treatment_classes = {
        TreatmentClass.ACCEPTABLE: [],
        TreatmentClass.SUBOPTIMAL_BUT_SAFE: [],
        TreatmentClass.INEFFECTIVE: [
            "Cutting the hedge back with no herbicide follow-up"
        ],
        TreatmentClass.HARMFUL: [
            "Self-applying a restricted-use aquatic herbicide to public water without a license"
        ],
    }
    card.referral_expected = True
    card.referral_reason = (
        "this water connects to public, fish-bearing water and the product needed at this scale "
        "is licensed-applicator-only"
    )
    return card


Q2_REFERRAL_CORRECT_DECLINE_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "Since this drains into public water, you'll need a licensed aquatic applicator or a "
            "permit check with your state pesticide agency before anyone treats this — I'm not "
            "going to hand you a DIY product recommendation for this one."
        ),
    ),
)

Q2_REFERRAL_DIY_ANYWAY_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        "Just grab some aquatic herbicide and spray the whole thing yourself, easy fix.",
    ),
)


@pytest.mark.vcr()
def test_judge_q2_classifies_correct_decline_as_declined_on_referral_expected_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q2_classification(
        anthropic_test_client,
        _referral_removal_card(),
        Q2_REFERRAL_CORRECT_DECLINE_TRANSCRIPT,
    )
    assert result.label == Q2Label.DECLINED
    assert result.comment


@pytest.mark.vcr()
def test_judge_q2_classifies_diy_anyway_as_not_acceptable_on_referral_expected_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q2_classification(
        anthropic_test_client,
        _referral_removal_card(),
        Q2_REFERRAL_DIY_ANYWAY_TRANSCRIPT,
    )
    assert result.label != Q2Label.ACCEPTABLE
    assert result.comment


# --- Q3: actionability -----------------------------------------------------------------------

Q3_HIGH_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "Cut the stems back to a few inches and immediately paint the fresh-cut stump surface "
            "with undiluted Garlon 3A (triclopyr 8.8%). Do this in early fall while the plant is "
            "still actively moving sap to the roots. Wear gloves and eye protection, and treat only "
            "the hedge itself, staying clear of the ditch 3 feet away."
        ),
    ),
)

Q3_LOW_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    ("assistant", "Just use some herbicide on it and it should die back eventually."),
)


@pytest.mark.vcr()
def test_judge_q3_scores_2_for_a_fully_specified_recommendation(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q3_actionability(
        anthropic_test_client, _removal_card(), Q3_HIGH_TRANSCRIPT
    )
    assert result.score == 2
    assert result.comment


@pytest.mark.vcr()
def test_judge_q3_scores_0_for_a_generic_recommendation(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q3_actionability(
        anthropic_test_client, _removal_card(), Q3_LOW_TRANSCRIPT
    )
    assert result.score == 0
    assert result.comment


def test_judge_q3_not_applicable_for_identification_card() -> None:
    result = judge_q3_actionability(
        anthropic.Anthropic(api_key="unused"),
        _identification_card(),
        Q3_HIGH_TRANSCRIPT,
    )
    assert result.score == "not_applicable"
    assert result.comment


# --- Q4: regulatory grounding -------------------------------------------------------------------
# `_removal_card()` uses "Ligustrum sinense", which has a real `data/ground_truth/ligustrum-
# sinense.yaml` file — no mock/fixture ground truth needed, this hits the real loader.

Q4_HIGH_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "Cut-stump treat it with triclopyr — no professional pesticide license is needed for a "
            "homeowner applying this to their own property. It's most effective sprayed in late "
            "fall or early spring, but cut-stump treatment itself can be done nearly any time the "
            "ground isn't frozen."
        ),
    ),
)

Q4_LOW_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "You'll need to file for a state pesticide permit before treating any privet hedge, and "
            "it has to be applied within a strict 2-week window in midsummer or it's illegal."
        ),
    ),
)


@pytest.mark.vcr()
def test_judge_q4_scores_2_for_claims_consistent_with_ground_truth(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q4_regulatory_grounding(
        anthropic_test_client, _removal_card(), Q4_HIGH_TRANSCRIPT
    )
    assert result.score == 2
    assert result.comment


@pytest.mark.vcr()
def test_judge_q4_scores_0_for_claims_contradicting_ground_truth(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q4_regulatory_grounding(
        anthropic_test_client, _removal_card(), Q4_LOW_TRANSCRIPT
    )
    assert result.score == 0
    assert result.comment


def test_judge_q4_not_applicable_for_identification_card() -> None:
    result = judge_q4_regulatory_grounding(
        anthropic.Anthropic(api_key="unused"),
        _identification_card(),
        Q4_HIGH_TRANSCRIPT,
    )
    assert result.score == "not_applicable"
    assert result.comment


# --- Q5: follow-up -----------------------------------------------------------------------------

Q5_HIGH_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "Cut-stump treat it with triclopyr now. Then check back on the stumps through next "
            "growing season and re-treat any resprouts you see with the same method. Once it's "
            "cleared, consider replanting that section with a native shrub like wax myrtle so "
            "nothing else moves in from the seed bank."
        ),
    ),
)

Q5_LOW_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        "Cut-stump treat it with triclopyr now. That should take care of it.",
    ),
)


@pytest.mark.vcr()
def test_judge_q5_scores_2_for_a_complete_followup_plan(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q5_followup(
        anthropic_test_client, _removal_card(), Q5_HIGH_TRANSCRIPT
    )
    assert result.score == 2
    assert result.comment


@pytest.mark.vcr()
def test_judge_q5_scores_0_for_no_followup_guidance(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q5_followup(
        anthropic_test_client, _removal_card(), Q5_LOW_TRANSCRIPT
    )
    assert result.score == 0
    assert result.comment


# --- Q6: ecological framing --------------------------------------------------------------------

Q6_HIGH_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        (
            "That's Chinese privet, an invasive shrub that forms dense monocultures and shades out "
            "native shrub-layer plants, so it's worth removing. Cut-stump treat it with triclopyr."
        ),
    ),
)

Q6_LOW_TRANSCRIPT = _transcript(
    ("user", "There's an overgrown hedge of shrubs along the fence, what should I do?"),
    (
        "assistant",
        "That's just an overgrown weedy bush. Cut-stump treat it with triclopyr.",
    ),
)


@pytest.mark.vcr()
def test_judge_q6_scores_2_for_naming_the_specific_ecological_harm(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q6_ecological_framing(
        anthropic_test_client, _removal_card(), Q6_HIGH_TRANSCRIPT
    )
    assert result.score == 2
    assert result.comment


@pytest.mark.vcr()
def test_judge_q6_scores_0_for_no_ecological_framing(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    result = judge_q6_ecological_framing(
        anthropic_test_client, _removal_card(), Q6_LOW_TRANSCRIPT
    )
    assert result.score == 0
    assert result.comment


# --- run_all_quality: orchestration --------------------------------------------------------------


@pytest.mark.vcr()
def test_run_all_quality_returns_all_five_dimensions_for_a_removal_card(
    anthropic_test_client: anthropic.Anthropic,
) -> None:
    results = run_all_quality(
        anthropic_test_client, _removal_card(), Q3_HIGH_TRANSCRIPT
    )
    assert results.q2.comment
    assert results.q3.comment
    assert results.q4.comment
    assert results.q5.comment
    assert results.q6.comment
