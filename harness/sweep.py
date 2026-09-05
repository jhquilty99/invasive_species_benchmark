"""Sweep runner: `ThreadPoolExecutor` across (model, card) pairs (PRD v4 §6, the "Days 10-11" full
production sweep, also serving the SME-validation deliverable's smaller-scope run).

Reuses `harness/scripts/run_validation.py`'s per-card judge-calling sequence (conversation → quality
judges → declined check → gate judges → stopping-turn re-derivation → Q1 → referral correctness),
just repeated across every (model, card) pair instead of one model against every card. This module
adds two steps `run_validation.py` doesn't have: the R5 leakage check (`harness.leakage_check.
check_leakage`) and persisting each finished result to `harness/results_store.py`'s on-disk JSONL as
it completes, rather than only pushing to Langfuse.

Concurrency lives here and only here (`.claude/rules/python.md`'s "Concurrency" section) — every
function this module calls is plain synchronous code. Each `(card, model)` pair gets its own
`thread_id` (`f"{card.card_id}__{model_id}__{arm}"`), which partitions
`simulated_user.py`'s/`conversation.py`'s per-thread conversation-history state so concurrent runs
never clobber each other's turns — but `thread_id` does NOT partition the vendor API clients
themselves: `run_sweep` takes one shared `ModelClients` bundle, and every worker thread calls
methods on the same underlying `anthropic.Anthropic`/`openai.OpenAI`/`genai.Client` instances
concurrently. That's deliberate, standard practice for these SDKs' synchronous, httpx-based HTTP
clients (each call gets its own connection from the client's pool), not something this module
verified itself the way `model_clients.py`'s own docstring verifies SDK call shapes — flagging the
distinction so a future reader doesn't infer client-level isolation from the `thread_id` scheme that
isn't actually there. The one piece of state every worker thread genuinely shares and mutates is the
results-file append, which is why that step alone is guarded by an explicit lock.
"""

import logging
import threading
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from langfuse import Langfuse

from harness.conversation import DEFAULT_INFRA_MODEL, run_conversation
from harness.judges._common import DEFAULT_JUDGE_MODEL
from harness.judges.gates import run_all_gates
from harness.judges.prompts import JUDGE_PROMPT_VERSION
from harness.judges.quality import run_all_quality
from harness.langfuse_client import (
    DatasetRunHandle,
    attach_gate_scores,
    attach_q1_score,
    attach_quality_scores,
    attach_referral_correct_score,
    g1_outcome,
    link_trace_to_dataset_run,
    start_dataset_run,
)
from harness.leakage_check import check_leakage
from harness.model_clients import ModelClients
from harness.models import Card, RunMetadata
from harness.results_store import (
    SweepResult,
    append_result,
    existing_keys,
    load_sweep_results,
)
from harness.scoring import (
    compute_q1,
    determine_stopping_turn,
    is_declined,
    is_referral_correct,
)

logger = logging.getLogger(__name__)

_write_lock = threading.Lock()


def _run_one(
    card: Card,
    model_id: str,
    *,
    arm: str,
    clients: ModelClients,
    card_set_version: str,
    langfuse_client: Langfuse | None,
    dataset_run: DatasetRunHandle | None,
) -> SweepResult:
    thread_id = f"{card.card_id}__{model_id}__{arm}"
    oracle = arm == "oracle"

    conversation = run_conversation(
        card,
        client=clients.anthropic,
        model_under_test=model_id,
        langfuse_client=langfuse_client,
        oracle=oracle,
        thread_id=thread_id,
        model_clients=clients,
    )
    trajectory = conversation.trajectory
    trace_id = conversation.trace_id

    quality_results = run_all_quality(
        clients.anthropic,
        card,
        trajectory,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )
    declined = is_declined(card, quality_results.q2.label)
    gate_results = run_all_gates(
        clients.anthropic,
        card,
        trajectory,
        declined=declined,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )

    turn_metrics = determine_stopping_turn(clients.anthropic, card, trajectory)
    q1_result = compute_q1(clients.anthropic, card, trajectory, turn_metrics)
    leakage_report = check_leakage(clients.anthropic, card, trajectory, oracle=oracle)
    referral_correct = is_referral_correct(
        card, q2_label=quality_results.q2.label, g1_outcome=g1_outcome(gate_results)
    )

    if trace_id is not None and langfuse_client is not None:
        if dataset_run is not None:
            link_trace_to_dataset_run(
                langfuse_client,
                dataset_run,
                dataset_item_id=card.card_id,
                trace_id=trace_id,
            )
        attach_gate_scores(langfuse_client, trace_id, gate_results)
        attach_quality_scores(langfuse_client, trace_id, quality_results)
        attach_q1_score(langfuse_client, trace_id, q1_result)
        attach_referral_correct_score(
            langfuse_client,
            trace_id,
            card,
            q2_label=quality_results.q2.label,
            gate_results=gate_results,
        )

    return SweepResult(
        card_id=card.card_id,
        model_id=model_id,
        arm=arm,
        question_type=card.question_type,
        native_status=card.native_status,
        trajectory=trajectory,
        gate_results=gate_results,
        quality_results=quality_results,
        q1_result=q1_result,
        turn_metrics=turn_metrics,
        referral_correct=referral_correct,
        leakage_report=leakage_report,
        trace_id=trace_id,
        run_metadata=RunMetadata(
            card_set_version=card_set_version,
            judge_prompt_version=JUDGE_PROMPT_VERSION,
            model_id=model_id,
            run_timestamp=datetime.now(UTC),
        ),
    )


def run_sweep(
    cards: Iterable[Card],
    model_ids: list[str],
    *,
    arm: str = "standard",
    clients: ModelClients,
    card_set_version: str,
    results_path: Path,
    langfuse_client: Langfuse | None = None,
    max_workers: int = 4,
) -> list[SweepResult]:
    """Run every (card, model) pair for `arm`, skipping any already present in `results_path` (by
    `(card_id, model_id, arm)`), appending each finished result as it completes.

    Builds one Langfuse dataset run per `model_id` internally (`start_dataset_run`, matching PRD §6's
    data model — "one dataset run per (model_id, prompt_version)", not one run shared across several
    models mixed together), when `langfuse_client` is given.

    `max_workers=4`: conservative default against 3 vendors' rate limits — a sweep across a few
    dozen cards × 2-3 models finishes in reasonable wall time well under most providers' default
    concurrent-request limits at this width; raise it only after confirming the vendor(s) in use can
    sustain more.

    Returns every result now in `results_path` for this `arm` (both freshly run and already-present),
    not just the newly-run ones — callers doing a resumed sweep want the full set to hand off
    downstream (`harness.sampling.select_sme_sample`), not just this call's delta.
    """
    cards = list(cards)
    dataset_runs: dict[str, DatasetRunHandle] = {
        model_id: start_dataset_run(
            model_id,
            JUDGE_PROMPT_VERSION,
            card_set_version=card_set_version,
            arm=arm,
            simulated_user_classifier_model=DEFAULT_INFRA_MODEL,
            simulated_user_responder_model=DEFAULT_INFRA_MODEL,
            stopping_condition_model=DEFAULT_INFRA_MODEL,
            judge_model=DEFAULT_JUDGE_MODEL,
        )
        for model_id in model_ids
    }
    already_done = {key for key in existing_keys(results_path) if key[2] == arm}
    pairs = [
        (card, model_id)
        for card in cards
        for model_id in model_ids
        if (card.card_id, model_id, arm) not in already_done
    ]
    logger.info(
        "run_sweep: %d cards x %d models, arm=%s — %d pairs already done, %d to run.",
        len(cards),
        len(model_ids),
        arm,
        len(already_done),
        len(pairs),
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_one,
                card,
                model_id,
                arm=arm,
                clients=clients,
                card_set_version=card_set_version,
                langfuse_client=langfuse_client,
                dataset_run=dataset_runs[model_id],
            ): (card.card_id, model_id)
            for card, model_id in pairs
        }
        for future in as_completed(futures):
            card_id, model_id = futures[future]
            try:
                result = future.result()
            except Exception:
                logger.exception(
                    "run_sweep: card=%s model=%s failed.", card_id, model_id
                )
                continue
            with _write_lock:
                append_result(results_path, result)
            logger.info(
                "run_sweep: card=%s model=%s arm=%s done (leaked=%s).",
                card_id,
                model_id,
                arm,
                result.leakage_report.leaked,
            )

    return [r for r in load_sweep_results(results_path) if r.arm == arm]
