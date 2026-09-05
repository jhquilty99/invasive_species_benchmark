"""On-disk JSONL persistence for sweep results.

Belt-and-suspenders alongside Langfuse (`harness/langfuse_client.py`'s score-attach helpers), not a
workaround for broken infra — Langfuse's own trace/span ingestion is fine (see `DECISION-LOG.md`'s
2026-09-04 "Corrected misdiagnosis" entry). A local artifact is simpler to build downstream
SME-validation tooling from — a stratified sample selection and an SME-review xlsx export, neither
built yet, see `SCRATCHPAD.md` — keeps a sweep resumable without a live Langfuse dependency, and this
file's output directory doubles as PRD §12's `results/` release artifact.

One JSONL line per (card, model, arm) result, appended as each pair finishes rather than batched at
the end — an interrupted sweep loses at most the one in-flight pair, not everything before it.
Pydantic v2 natively wraps the stdlib dataclasses this module nests (`Q1Result`, `TurnMetrics`,
`LeakageReport`, `QualityResults`), so `SweepResult.model_dump_json()`/`model_validate_json()` round-
trip them without any manual conversion — confirmed 2026-09-04 against the installed pydantic
version, not assumed.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from harness.judges.quality import QualityResults
from harness.leakage_check import LeakageReport
from harness.models import GateResult, NativeStatus, QuestionType, RunMetadata
from harness.scoring import Q1Result, TurnMetrics


class SweepResult(BaseModel):
    """One finished (card, model, arm) run: everything needed to score it, review it, and export it
    to the SME xlsx without going back through Langfuse or re-running the sweep."""

    card_id: str
    model_id: str
    arm: str
    question_type: QuestionType
    native_status: NativeStatus
    trajectory: list[dict[str, Any]]
    gate_results: list[GateResult]
    quality_results: QualityResults
    q1_result: Q1Result
    turn_metrics: TurnMetrics
    referral_correct: bool | None
    leakage_report: LeakageReport
    trace_id: str | None
    run_metadata: RunMetadata

    def key(self) -> tuple[str, str, str]:
        """`(card_id, model_id, arm)` — the identity a resumable sweep checks before re-running a
        pair, and the identity a future stratified-sample selection (not yet built) would reference
        its picks by."""
        return (self.card_id, self.model_id, self.arm)


def append_result(path: Path, result: SweepResult) -> None:
    """Append one result as a single JSONL line, creating parent directories if needed.

    Opens and closes the file per call rather than holding a long-lived handle — sweep runs are
    infrequent and low-volume enough (dozens to low hundreds of lines) that the per-call open/close
    cost is irrelevant, and it means a crash mid-sweep can't leave a buffered-but-unflushed line
    behind."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(result.model_dump_json())
        f.write("\n")


def load_sweep_results(path: Path) -> list[SweepResult]:
    """Load every result from a JSONL file written by `append_result`. Returns `[]` if `path`
    doesn't exist yet — a sweep that hasn't started writing results yet is a normal, not an
    exceptional, state for a resumability check to see."""
    if not path.exists():
        return []
    results = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            results.append(SweepResult.model_validate_json(line))
    return results


def existing_keys(path: Path) -> set[tuple[str, str, str]]:
    """`(card_id, model_id, arm)` keys already present in `path` — what `harness.sweep.run_sweep`
    checks before dispatching a pair, so re-running a sweep against a partially-complete results
    file skips work already done instead of re-spending API budget on it."""
    return {result.key() for result in load_sweep_results(path)}
