"""Tests for `harness.results_store` — on-disk JSONL persistence for sweep results.

`sweep.py` itself (the `ThreadPoolExecutor` orchestration) isn't separately unit-tested here: it's a
thin composition of already-tested pieces (`run_conversation`, the judges, `check_leakage`,
`is_referral_correct`), and its real integration test is the planned dry run against the actual card
corpus, not a synthetic mock-everything test that would mostly just be re-asserting the mocks were
called.
"""

from datetime import UTC, datetime
from pathlib import Path

from harness.judges.quality import QualityResults
from harness.leakage_check import LeakageReport
from harness.models import (
    GateID,
    GateOutcome,
    GateResult,
    NativeStatus,
    Q2Classification,
    Q2Label,
    QualityDimension,
    QualityScore,
    QuestionType,
    RunMetadata,
)
from harness.results_store import (
    SweepResult,
    append_result,
    existing_keys,
    load_sweep_results,
)
from harness.scoring import Q1Result, TurnMetrics


def _result(
    card_id: str = "CARD-1", model_id: str = "claude-opus-5", arm: str = "standard"
) -> SweepResult:
    return SweepResult(
        card_id=card_id,
        model_id=model_id,
        arm=arm,
        question_type=QuestionType.REMOVAL,
        native_status=NativeStatus.INVASIVE,
        trajectory=[{"role": "user", "content": "hi"}],
        gate_results=[
            GateResult(
                gate_id=GateID.G1_IDENTITY_VERIFIED,
                outcome=GateOutcome.PASS,
                comment="Identified Ligustrum sinense by name.",
            )
        ],
        quality_results=QualityResults(
            q2=Q2Classification(
                label=Q2Label.ACCEPTABLE, comment="Correct treatment class."
            ),
            q3=QualityScore(
                dimension=QualityDimension.Q3_ACTIONABILITY, score=2, comment="ok"
            ),
            q4=QualityScore(
                dimension=QualityDimension.Q4_REGULATORY_GROUNDING,
                score=1,
                comment="ok",
            ),
            q5=QualityScore(
                dimension=QualityDimension.Q5_FOLLOWUP, score=2, comment="ok"
            ),
            q6=QualityScore(
                dimension=QualityDimension.Q6_ECOLOGICAL_FRAMING, score=2, comment="ok"
            ),
        ),
        q1_result=Q1Result(True, ["water_proximity"], [], []),
        turn_metrics=TurnMetrics(turns_to_recommendation=2, hit_max_turns=False),
        referral_correct=None,
        leakage_report=LeakageReport(leaked=False, leaked_slots=[], details=[]),
        trace_id="trace-abc",
        run_metadata=RunMetadata(
            card_set_version="wip-2026-09-04",
            judge_prompt_version="v2",
            model_id=model_id,
            run_timestamp=datetime.now(UTC),
        ),
    )


def test_append_and_load_round_trips_a_single_result(tmp_path: Path) -> None:
    path = tmp_path / "results.jsonl"
    result = _result()

    append_result(path, result)
    loaded = load_sweep_results(path)

    assert len(loaded) == 1
    assert loaded[0] == result


def test_append_result_creates_parent_directories(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "dir" / "results.jsonl"
    append_result(path, _result())
    assert path.exists()


def test_load_sweep_results_returns_empty_list_for_missing_file(tmp_path: Path) -> None:
    assert load_sweep_results(tmp_path / "does-not-exist.jsonl") == []


def test_append_result_appends_rather_than_overwrites(tmp_path: Path) -> None:
    path = tmp_path / "results.jsonl"
    append_result(path, _result(card_id="CARD-1"))
    append_result(path, _result(card_id="CARD-2"))

    loaded = load_sweep_results(path)

    assert [r.card_id for r in loaded] == ["CARD-1", "CARD-2"]


def test_existing_keys_reflects_card_model_arm_tuples(tmp_path: Path) -> None:
    path = tmp_path / "results.jsonl"
    append_result(
        path, _result(card_id="CARD-1", model_id="claude-opus-5", arm="standard")
    )
    append_result(
        path, _result(card_id="CARD-1", model_id="gpt-5.6-sol", arm="standard")
    )
    append_result(
        path, _result(card_id="CARD-2", model_id="claude-opus-5", arm="oracle")
    )

    keys = existing_keys(path)

    assert keys == {
        ("CARD-1", "claude-opus-5", "standard"),
        ("CARD-1", "gpt-5.6-sol", "standard"),
        ("CARD-2", "claude-opus-5", "oracle"),
    }


def test_existing_keys_empty_for_missing_file(tmp_path: Path) -> None:
    assert existing_keys(tmp_path / "does-not-exist.jsonl") == set()
