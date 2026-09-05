"""Tests for `harness.sampling` — stratified SME-sample selection.

Pure code, no LLM calls (`select_sme_sample` only reads already-computed `SweepResult`s), so no
cassette needed per `.claude/rules/testing.md` — these are ordinary unit tests over synthetic
`SweepResult`s built the same way `tests/test_results_store.py`'s `_result` factory does.
"""

from datetime import UTC, datetime
from typing import Literal

from harness.judges.quality import QualityResults
from harness.leakage_check import LeakageReport
from harness.models import (
    GateID,
    GateOutcome,
    GateResult,
    IntroductionQ2Label,
    NativeStatus,
    Q2Classification,
    Q2Label,
    QualityDimension,
    QualityScore,
    QuestionType,
    RunMetadata,
)
from harness.results_store import SweepResult
from harness.sampling import flag_reason, is_flagged, select_sme_sample
from harness.scoring import Q1Result, TurnMetrics


def _result(
    *,
    card_id: str = "CARD-1",
    model_id: str = "claude-opus-5",
    question_type: QuestionType = QuestionType.REMOVAL,
    gate_outcome: GateOutcome = GateOutcome.PASS,
    q2_label: Q2Label | IntroductionQ2Label | Literal["not_applicable"] = (
        Q2Label.ACCEPTABLE
    ),
    leaked: bool = False,
    trace_id: str | None = "trace-abc",
) -> SweepResult:
    return SweepResult(
        card_id=card_id,
        model_id=model_id,
        arm="standard",
        question_type=question_type,
        native_status=NativeStatus.INVASIVE,
        trajectory=[{"role": "user", "content": "hi"}],
        gate_results=[
            GateResult(
                gate_id=GateID.G1_IDENTITY_VERIFIED,
                outcome=gate_outcome,
                comment="x",
            )
        ],
        quality_results=QualityResults(
            q2=Q2Classification(label=q2_label, comment="x"),
            q3=QualityScore(
                dimension=QualityDimension.Q3_ACTIONABILITY,
                score="not_applicable",
                comment="x",
            ),
            q4=QualityScore(
                dimension=QualityDimension.Q4_REGULATORY_GROUNDING,
                score="not_applicable",
                comment="x",
            ),
            q5=QualityScore(
                dimension=QualityDimension.Q5_FOLLOWUP,
                score="not_applicable",
                comment="x",
            ),
            q6=QualityScore(
                dimension=QualityDimension.Q6_ECOLOGICAL_FRAMING, score=2, comment="x"
            ),
        ),
        q1_result=Q1Result(True, [], [], []),
        turn_metrics=TurnMetrics(turns_to_recommendation=1, hit_max_turns=False),
        referral_correct=None,
        leakage_report=LeakageReport(leaked=leaked, leaked_slots=[], details=[]),
        trace_id=trace_id,
        run_metadata=RunMetadata(
            card_set_version="test",
            judge_prompt_version="v1",
            model_id=model_id,
            run_timestamp=datetime.now(UTC),
        ),
    )


def test_is_flagged_true_when_a_gate_fails() -> None:
    result = _result(gate_outcome=GateOutcome.FAIL)
    assert is_flagged(result)
    assert "gate_fail:identity_verified" in flag_reason(result)


def test_is_flagged_true_when_q2_is_harmful() -> None:
    result = _result(q2_label=Q2Label.HARMFUL)
    assert is_flagged(result)
    assert "q2:harmful" in flag_reason(result)


def test_is_flagged_false_for_a_clean_result() -> None:
    result = _result(gate_outcome=GateOutcome.PASS, q2_label=Q2Label.ACCEPTABLE)
    assert not is_flagged(result)
    assert flag_reason(result) == ""


def test_select_sme_sample_excludes_leaked_results() -> None:
    results = [
        _result(card_id="LEAKED-1", leaked=True),
        _result(card_id="CLEAN-1", leaked=False),
    ]

    selection = select_sme_sample(results, stratum_targets={QuestionType.REMOVAL: 5})

    assert "LEAKED-1" not in {item.card_id for item in selection.items}
    assert any("Excluded 1 leaked" in note for note in selection.notes)


def test_select_sme_sample_caps_at_available_and_logs_a_shortfall_note() -> None:
    results = [_result(card_id=f"CARD-{i}") for i in range(2)]

    selection = select_sme_sample(results, stratum_targets={QuestionType.REMOVAL: 5})

    assert len(selection.items) == 2
    assert any("only 2 available" in note for note in selection.notes)


def test_select_sme_sample_redistributes_shortfall_to_strata_with_room() -> None:
    results = [
        *[
            _result(card_id=f"REM-{i}", question_type=QuestionType.REMOVAL)
            for i in range(10)
        ],
        *[
            _result(card_id=f"ID-{i}", question_type=QuestionType.IDENTIFICATION)
            for i in range(10)
        ],
        _result(card_id="INTRO-1", question_type=QuestionType.INTRODUCTION),
    ]

    selection = select_sme_sample(
        results,
        stratum_targets={
            QuestionType.REMOVAL: 5,
            QuestionType.IDENTIFICATION: 5,
            QuestionType.INTRODUCTION: 5,
        },
    )

    assert len(selection.items) == 15
    assert any("wanted 5, only 1 available" in note for note in selection.notes)


def test_select_sme_sample_logs_when_it_cannot_fill_target_total() -> None:
    results = [_result(card_id="ONLY-ONE", question_type=QuestionType.REMOVAL)]

    selection = select_sme_sample(results, stratum_targets={QuestionType.REMOVAL: 5})

    assert len(selection.items) == 1
    assert any("Could not fill target_total" in note for note in selection.notes)


def test_select_sme_sample_oversamples_flagged_results() -> None:
    flagged = [
        _result(card_id=f"FLAGGED-{i}", gate_outcome=GateOutcome.FAIL) for i in range(8)
    ]
    unflagged = [_result(card_id=f"CLEAN-{i}") for i in range(8)]

    selection = select_sme_sample(
        flagged + unflagged, stratum_targets={QuestionType.REMOVAL: 10}
    )

    n_flagged = sum(1 for item in selection.items if item.flagged)
    assert n_flagged == 6  # round(10 * 0.6)
    assert len(selection.items) - n_flagged == 4


def test_select_sme_sample_round_robins_across_models() -> None:
    results = [
        *[
            _result(card_id=f"A-{i}", model_id="model-a", gate_outcome=GateOutcome.FAIL)
            for i in range(4)
        ],
        *[
            _result(card_id=f"B-{i}", model_id="model-b", gate_outcome=GateOutcome.FAIL)
            for i in range(4)
        ],
    ]

    selection = select_sme_sample(results, stratum_targets={QuestionType.REMOVAL: 4})

    picked_models = {item.model_id for item in selection.items}
    assert picked_models == {"model-a", "model-b"}


def test_select_sme_sample_is_deterministic_given_same_seed() -> None:
    results = [
        _result(card_id=f"CARD-{i}", model_id="model-a" if i % 2 else "model-b")
        for i in range(20)
    ]

    first = select_sme_sample(
        results, stratum_targets={QuestionType.REMOVAL: 10}, seed=7
    )
    second = select_sme_sample(
        results, stratum_targets={QuestionType.REMOVAL: 10}, seed=7
    )

    assert first.items == second.items
