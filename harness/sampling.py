"""Stratified sample selection for the SME-validation deliverable (PRD v4 Sec 7, trimmed to ~20 items
per DECISION-LOG.md's "trim the sample to fit the original ask" call).

Operates purely on already-computed `SweepResult`s (`harness/results_store.py`) — no LLM calls, no
Langfuse dependency, pure and unit-testable. `select_sme_sample`:

1. Excludes every `leakage_report.leaked=True` result up front (R5) — a contaminated transcript never
   reaches an SME, full stop.
2. Partitions the rest by `question_type` (3 strata), targeting roughly even coverage per stratum
   rather than proportional to the card corpus's natural skew (`DEFAULT_STRATUM_TARGETS`).
3. Within each stratum, oversamples `flagged` results (any gate failed, or Q2 classified `harmful`/
   `harmful_to_encourage`) toward a ~60/40 flagged/unflagged split, capped by what's actually
   available in that bucket.
4. Round-robins across models within each flagged/unflagged bucket so the sample isn't dominated by
   one model.
5. If a stratum can't fill its target (too few results after excluding leakage), the shortfall is
   redistributed to strata with spare capacity so the overall total is still met where possible — and
   always logged in `SampleSelection.notes`, never silently absorbed.

Deterministic given the same `seed` and input results — re-running this against an unchanged
`results.jsonl` reproduces the exact same selection.
"""

import random
from collections import defaultdict

from pydantic import BaseModel

from harness.models import GateOutcome, Q2Label, QuestionType
from harness.results_store import SweepResult

FLAGGED_Q2_VALUES = {"harmful", "harmful_to_encourage"}
"""Q2Label.HARMFUL and IntroductionQ2Label.HARMFUL_TO_ENCOURAGE's string values — both are `str`
enums, so plain membership (`label in FLAGGED_Q2_VALUES`) matches correctly regardless of which enum
class `label` actually is (see `harness/models.py`'s `Q2Classification` docstring for the related
`declined` sharp edge; this set doesn't include `declined`, so that edge doesn't apply here)."""

DEFAULT_STRATUM_TARGETS: dict[QuestionType, int] = {
    QuestionType.REMOVAL: 7,
    QuestionType.IDENTIFICATION: 7,
    QuestionType.INTRODUCTION: 6,
}
"""~7/7/6 = 20, per the plan's "target roughly even coverage" call — not proportional to the card
corpus's natural skew toward removal/identification. Override via `select_sme_sample`'s
`stratum_targets` param for a different `target_total`."""

FLAGGED_FRACTION = 0.6


def is_flagged(result: SweepResult) -> bool:
    """A result is flagged for oversampling if any gate failed, or Q2 classified `harmful` /
    `harmful_to_encourage` — the same two categories PRD Sec 7 calls out as worth a human seeing more
    of than their natural incidence rate."""
    if any(g.outcome == GateOutcome.FAIL for g in result.gate_results):
        return True
    return result.quality_results.q2.label in FLAGGED_Q2_VALUES


def flag_reason(result: SweepResult) -> str:
    """Human-readable reason `is_flagged` returned `True` — empty string if it didn't. Not scored
    itself, just a breadcrumb for whoever reads `SampleSelection` later."""
    failed_gates = [
        g.gate_id.value for g in result.gate_results if g.outcome == GateOutcome.FAIL
    ]
    reasons = [f"gate_fail:{g}" for g in failed_gates]
    label = result.quality_results.q2.label
    if label in FLAGGED_Q2_VALUES:
        value = label.value if isinstance(label, Q2Label) else label
        reasons.append(f"q2:{value}")
    return "; ".join(reasons)


class SelectedItem(BaseModel):
    card_id: str
    model_id: str
    arm: str
    question_type: QuestionType
    flagged: bool
    flag_reason: str
    trace_id: str | None


class SampleSelection(BaseModel):
    seed: int
    target_total: int
    stratum_targets: dict[QuestionType, int]
    items: list[SelectedItem]
    notes: list[str]
    """Explicit shortfall/redistribution log — e.g. a stratum with too few post-leakage-filter
    results to hit its target. Never silent: if the selected total is short of `target_total`, a note
    here says why."""


def _round_robin_pick(
    pool: list[SweepResult], n: int, rng: random.Random
) -> list[SweepResult]:
    """Pick up to `n` items from `pool`, round-robinning across `model_id` groups (each internally
    shuffled) so no single model dominates the picks. Returns fewer than `n` if `pool` is smaller."""
    by_model: dict[str, list[SweepResult]] = defaultdict(list)
    for result in pool:
        by_model[result.model_id].append(result)
    for group in by_model.values():
        rng.shuffle(group)
    model_order = list(by_model.keys())
    rng.shuffle(model_order)

    picked: list[SweepResult] = []
    idx = 0
    while len(picked) < n and any(by_model[m] for m in model_order):
        model_id = model_order[idx % len(model_order)]
        if by_model[model_id]:
            picked.append(by_model[model_id].pop())
        idx += 1
    return picked


def _select_from_stratum(
    stratum_results: list[SweepResult], n: int, rng: random.Random
) -> list[SweepResult]:
    flagged = [r for r in stratum_results if is_flagged(r)]
    unflagged = [r for r in stratum_results if not is_flagged(r)]

    target_flagged = min(round(n * FLAGGED_FRACTION), len(flagged))
    target_unflagged = n - target_flagged
    if target_unflagged > len(unflagged):
        deficit = target_unflagged - len(unflagged)
        target_unflagged = len(unflagged)
        target_flagged = min(target_flagged + deficit, len(flagged))

    picked = _round_robin_pick(flagged, target_flagged, rng) + _round_robin_pick(
        unflagged, target_unflagged, rng
    )
    rng.shuffle(picked)
    return picked


def _redistribute_shortfall(
    capped: dict[QuestionType, int],
    available: dict[QuestionType, int],
    shortfall: int,
) -> list[str]:
    """Mutates `capped` in place, handing spare shortfall to strata with room, round-robin, until
    either the shortfall is absorbed or no stratum has any spare capacity left. Returns log notes."""
    notes = []
    order = list(capped.keys())
    while shortfall > 0:
        gave_any = False
        for qt in order:
            if shortfall <= 0:
                break
            room = available[qt] - capped[qt]
            if room > 0:
                capped[qt] += 1
                shortfall -= 1
                gave_any = True
        if not gave_any:
            notes.append(
                f"Could not fill target_total: {shortfall} slot(s) short, no stratum had spare "
                "capacity after redistribution."
            )
            break
    return notes


def select_sme_sample(
    results: list[SweepResult],
    *,
    stratum_targets: dict[QuestionType, int] | None = None,
    seed: int = 42,
) -> SampleSelection:
    stratum_targets = dict(stratum_targets or DEFAULT_STRATUM_TARGETS)
    target_total = sum(stratum_targets.values())
    rng = random.Random(seed)

    clean = [r for r in results if not r.leakage_report.leaked]
    n_leaked = len(results) - len(clean)

    by_stratum: dict[QuestionType, list[SweepResult]] = defaultdict(list)
    for result in clean:
        by_stratum[result.question_type].append(result)

    available = {qt: len(by_stratum.get(qt, [])) for qt in stratum_targets}
    capped = {qt: min(stratum_targets[qt], available[qt]) for qt in stratum_targets}
    shortfall = target_total - sum(capped.values())

    notes: list[str] = []
    if n_leaked:
        notes.append(f"Excluded {n_leaked} leaked result(s) before selection (R5).")
    for qt in stratum_targets:
        if available[qt] < stratum_targets[qt]:
            notes.append(
                f"{qt.value}: wanted {stratum_targets[qt]}, only {available[qt]} available "
                "post-leakage-filter."
            )
    if shortfall > 0:
        notes.extend(_redistribute_shortfall(capped, available, shortfall))

    items: list[SelectedItem] = []
    for qt, n in capped.items():
        for result in _select_from_stratum(by_stratum.get(qt, []), n, rng):
            items.append(
                SelectedItem(
                    card_id=result.card_id,
                    model_id=result.model_id,
                    arm=result.arm,
                    question_type=result.question_type,
                    flagged=is_flagged(result),
                    flag_reason=flag_reason(result),
                    trace_id=result.trace_id,
                )
            )

    return SampleSelection(
        seed=seed,
        target_total=target_total,
        stratum_targets=stratum_targets,
        items=items,
        notes=notes,
    )
