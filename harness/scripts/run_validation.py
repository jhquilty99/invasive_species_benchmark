"""End-to-end runner for the first-pass LLM-as-judge validation.

    uv run python -m harness.scripts.run_validation

Loads every card under `cards/`, ensures the Langfuse dataset + score configs exist, runs one
per-turn-traced conversation per card against `DEFAULT_MODEL_UNDER_TEST`, runs the gate + quality
judges plus `harness/scoring.py`'s code-computed metrics against the finished transcript, attaches
every score to the conversation's trace, links the trace to a dataset run, and prints a short
pass/fail / mean-score summary.

One model-under-test, all cards currently in `cards/` — deliberately not the eventual 4-6 model sweep
(`SCRATCHPAD.md`), which needs the corpus frozen first. `CARD_SET_VERSION` is a work-in-progress tag,
not `"freeze-v1"`, which stays reserved for the eventual frozen 56-card set.

`ARM` (RQ1's oracle-contrast arm, PRD §2/§6/R6) selects `"standard"` (elicitation required, the
original behavior) or `"oracle"` (every decision-relevant slot disclosed upfront on removal cards —
a no-op on non-removal cards, since `build_oracle_opening_message` only appends
`decision_relevant` slots and non-removal cards' decision-relevant slots still exist but aren't
gated behind a treatment decision the same way). Flip the constant and re-run to exercise the other
arm — no CLI framework in this repo (`.claude/rules/python.md`), so this is a plain module constant,
not a flag. The real per-model production sweep (`harness/scripts/run_sweep.py`, not yet built) will
run both arms per model; this script validates the mechanism end-to-end on whichever one you pick.

Requires a locally reachable Langfuse instance (`cd infra/langfuse && docker compose up -d`) and a
real `ANTHROPIC_API_KEY` in the root `.env` — this script is a manual, deliberate live run, not
something the test suite executes.
"""

import logging
from pathlib import Path

import anthropic
from langfuse import Langfuse

from harness.cards import load_cards
from harness.config import Settings
from harness.conversation import DEFAULT_MODEL_UNDER_TEST, run_conversation
from harness.judges.gates import run_all_gates
from harness.judges.prompts import JUDGE_PROMPT_VERSION
from harness.judges.quality import QualityResults, run_all_quality
from harness.langfuse_client import (
    Q1_SCORE_NAME,
    Q2_SCORE_NAME,
    REFERRAL_CORRECT_SCORE_NAME,
    attach_score,
    ensure_score_configs,
    get_langfuse_client,
    get_or_create_dataset,
    link_trace_to_dataset_run,
    start_dataset_run,
    upsert_card_dataset_item,
)
from harness.models import (
    Card,
    GateID,
    GateOutcome,
    GateResult,
    IntroductionQ2Label,
    Q2Label,
)
from harness.scoring import (
    Q1Result,
    TurnMetrics,
    compute_q1,
    determine_stopping_turn,
    hit_max_turns_rate,
    is_declined,
    is_referral_correct,
    premature_prescription_rate,
    q2_label_value,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

CARDS_DIR = Path(__file__).resolve().parent.parent.parent / "cards"
CARD_SET_VERSION = "wip-2026-09-03"
"""Work-in-progress tag, not the eventual frozen 56-card set's `"freeze-v1"`."""
ARM = "standard"
"""Flip to `"oracle"` to run the RQ1 oracle-contrast arm instead. See module docstring."""


def _attach_gate_scores(
    langfuse_client: Langfuse, trace_id: str, gate_results: list[GateResult]
) -> None:
    for result in gate_results:
        attach_score(
            langfuse_client,
            name=result.gate_id.name,
            value=result.outcome.value,
            comment=result.comment,
            trace_id=trace_id,
            data_type="CATEGORICAL",
        )


def _attach_quality_scores(
    langfuse_client: Langfuse, trace_id: str, quality_results: QualityResults
) -> None:
    attach_score(
        langfuse_client,
        name=Q2_SCORE_NAME,
        value=q2_label_value(quality_results.q2.label),
        comment=quality_results.q2.comment,
        trace_id=trace_id,
        data_type="CATEGORICAL",
    )
    for score in (
        quality_results.q3,
        quality_results.q4,
        quality_results.q5,
        quality_results.q6,
    ):
        if score.score == "not_applicable":
            logger.info(
                "%s not_applicable; a numeric score config can't hold that value, skipping "
                "Langfuse attach for this dimension on this card.",
                score.dimension.value,
            )
            continue
        attach_score(
            langfuse_client,
            name=score.dimension.name,
            value=score.score,
            comment=score.comment,
            trace_id=trace_id,
            data_type="NUMERIC",
        )


def _attach_q1_score(
    langfuse_client: Langfuse, trace_id: str, q1_result: Q1Result
) -> None:
    attach_score(
        langfuse_client,
        name=Q1_SCORE_NAME,
        value="pass" if q1_result.all_decision_relevant_elicited else "fail",
        comment=(
            f"Elicited before terminal turn: {q1_result.elicited_decision_relevant_slots}. "
            f"Missing: {q1_result.missing_decision_relevant_slots}. "
            f"Distractor slots asked anyway: {q1_result.distractor_slots_asked}."
        ),
        trace_id=trace_id,
        data_type="CATEGORICAL",
    )


def _g1_outcome(gate_results: list[GateResult]) -> GateOutcome:
    (g1,) = (r for r in gate_results if r.gate_id == GateID.G1_IDENTITY_VERIFIED)
    return g1.outcome


def _attach_referral_correct_score(
    langfuse_client: Langfuse,
    trace_id: str,
    card: Card,
    *,
    q2_label: Q2Label | IntroductionQ2Label | str,
    gate_results: list[GateResult],
) -> None:
    """RQ5: only attached when `card.referral_expected` is `True` — `is_referral_correct` returns
    `None` otherwise, and `None` isn't a value this score's config can hold, same reasoning as the
    not_applicable-quality-score skip in `_attach_quality_scores`."""
    g1_outcome = _g1_outcome(gate_results)
    referral_correct = is_referral_correct(
        card, q2_label=q2_label, g1_outcome=g1_outcome
    )
    if referral_correct is None:
        return
    attach_score(
        langfuse_client,
        name=REFERRAL_CORRECT_SCORE_NAME,
        value="pass" if referral_correct else "fail",
        comment=f"referral_expected card; q2_label={q2_label!r}, g1_outcome={g1_outcome.value!r}.",
        trace_id=trace_id,
        data_type="CATEGORICAL",
    )


def main() -> None:
    settings = Settings()  # type: ignore[call-arg]
    anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    langfuse_client = get_langfuse_client(settings)

    cards = load_cards(CARDS_DIR)
    logger.info("Loaded %d cards from %s", len(cards), CARDS_DIR)

    ensure_score_configs(langfuse_client)
    get_or_create_dataset(langfuse_client)
    for card in cards:
        upsert_card_dataset_item(langfuse_client, card)

    run = start_dataset_run(
        DEFAULT_MODEL_UNDER_TEST,
        JUDGE_PROMPT_VERSION,
        card_set_version=CARD_SET_VERSION,
        arm=ARM,
    )

    all_turn_metrics: list[TurnMetrics] = []
    all_q1_results: list[Q1Result] = []

    for card in cards:
        logger.info(
            "=== %s (%s / %s) ===",
            card.card_id,
            card.question_type.value,
            card.native_status.value,
        )

        conversation = run_conversation(
            card,
            client=anthropic_client,
            langfuse_client=langfuse_client,
            oracle=(ARM == "oracle"),
        )
        trajectory = conversation.trajectory
        trace_id = conversation.trace_id

        quality_results = run_all_quality(anthropic_client, card, trajectory)
        declined = is_declined(card, quality_results.q2.label)
        gate_results = run_all_gates(
            anthropic_client, card, trajectory, declined=declined
        )

        turn_metrics = determine_stopping_turn(anthropic_client, card, trajectory)
        q1_result = compute_q1(anthropic_client, card, trajectory, turn_metrics)
        all_turn_metrics.append(turn_metrics)
        all_q1_results.append(q1_result)

        if trace_id is not None:
            link_trace_to_dataset_run(
                langfuse_client, run, dataset_item_id=card.card_id, trace_id=trace_id
            )
            _attach_gate_scores(langfuse_client, trace_id, gate_results)
            _attach_quality_scores(langfuse_client, trace_id, quality_results)
            _attach_q1_score(langfuse_client, trace_id, q1_result)
            _attach_referral_correct_score(
                langfuse_client,
                trace_id,
                card,
                q2_label=quality_results.q2.label,
                gate_results=gate_results,
            )
        else:
            logger.warning(
                "card=%s: no trace_id — is Langfuse reachable? Scores not attached.",
                card.card_id,
            )

        gate_summary = ", ".join(
            f"{result.gate_id.name}={result.outcome.value}" for result in gate_results
        )
        logger.info(
            "card=%s: turns_to_recommendation=%s hit_max_turns=%s q1_all_elicited=%s q2=%s "
            "gates=[%s]",
            card.card_id,
            turn_metrics.turns_to_recommendation,
            turn_metrics.hit_max_turns,
            q1_result.all_decision_relevant_elicited,
            q2_label_value(quality_results.q2.label),
            gate_summary,
        )

    logger.info(
        "=== Summary: arm=%s | %d cards | hit_max_turns_rate=%.2f | premature_prescription_rate=%.2f ===",
        ARM,
        len(cards),
        hit_max_turns_rate(all_turn_metrics),
        premature_prescription_rate(all_q1_results),
    )
    if ARM == "oracle":
        logger.info(
            "arm=oracle: premature_prescription_rate/Q1 above is not a meaningful headline number "
            "for this arm (every decision-relevant slot was already disclosed, so there was "
            "nothing to elicit) — the oracle-arm headline metric is Q2 classification-accuracy "
            "compared against the same cards' standard-arm run (PRD §5.4 metric 3)."
        )


if __name__ == "__main__":
    main()
