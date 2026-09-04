"""Repeated-sampling pilot — cheap RQ6-adjacent noise characterization; RQ6 itself stays cut.

    uv run python -m harness.scripts.run_repeat_pilot

Runs every card currently in `cards/` `REPS` times each, scores each repeat normally (gates +
quality), and reports how often each card's gate outcomes and Q2 label agree across repeats. This
doesn't resource full RQ6 (repeated sampling *and* new simulated-user "corrects/presses" behaviors —
PRD §2 RQ6, `DECISION-LOG.md`), but it puts a real number on how much of every *other* headline
metric's variance is single-draw sampling noise rather than genuine per-card signal, for near the
cost of one extra sweep pass over the (still small) card set.

Each repeat lands as its own Langfuse dataset run (`arm="repeat-pilot-{rep}"`, reusing
`harness/langfuse_client.py`'s existing `arm` extension point — no new plumbing), rather than trying
to tag a per-item repeat index onto one shared run.

Requires a locally reachable Langfuse instance and a real `ANTHROPIC_API_KEY`, same as
`run_validation.py` — this is a manual, deliberate script, not part of the test suite.
"""

import logging
from pathlib import Path

import anthropic

from harness.cards import load_cards
from harness.config import Settings
from harness.conversation import DEFAULT_MODEL_UNDER_TEST, run_conversation
from harness.judges.gates import run_all_gates
from harness.judges.prompts import JUDGE_PROMPT_VERSION
from harness.judges.quality import run_all_quality
from harness.langfuse_client import (
    get_langfuse_client,
    get_or_create_dataset,
    link_trace_to_dataset_run,
    start_dataset_run,
    upsert_card_dataset_item,
)
from harness.scoring import compute_repeat_agreement, is_declined, q2_label_value

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

CARDS_DIR = Path(__file__).resolve().parent.parent.parent / "cards"
CARD_SET_VERSION = "wip-2026-09-03"
REPS = 3
"""How many times to run each card. 3 is a deliberately cheap pilot size, not a statistically
powered sample — see this module's docstring and the methodology eval's findings."""


def main() -> None:
    settings = Settings()  # type: ignore[call-arg]
    anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    langfuse_client = get_langfuse_client(settings)

    cards = load_cards(CARDS_DIR)
    logger.info(
        "Loaded %d cards from %s; running %d reps each (%d total conversations)",
        len(cards),
        CARDS_DIR,
        REPS,
        len(cards) * REPS,
    )

    get_or_create_dataset(langfuse_client)
    for card in cards:
        upsert_card_dataset_item(langfuse_client, card)

    runs = [
        start_dataset_run(
            DEFAULT_MODEL_UNDER_TEST,
            JUDGE_PROMPT_VERSION,
            card_set_version=CARD_SET_VERSION,
            arm=f"repeat-pilot-{rep}",
        )
        for rep in range(REPS)
    ]

    gate_labels_by_card: dict[str, dict[str, list[str]]] = {}
    q2_labels_by_card: dict[str, list[str]] = {}

    for card in cards:
        for rep in range(REPS):
            thread_id = f"{card.card_id}__rep{rep}"
            logger.info(
                "=== %s rep=%d/%d (thread=%s) ===",
                card.card_id,
                rep + 1,
                REPS,
                thread_id,
            )
            conversation = run_conversation(
                card,
                client=anthropic_client,
                langfuse_client=langfuse_client,
                thread_id=thread_id,
            )
            trajectory = conversation.trajectory
            trace_id = conversation.trace_id

            quality_results = run_all_quality(anthropic_client, card, trajectory)
            declined = is_declined(card, quality_results.q2.label)
            gate_results = run_all_gates(
                anthropic_client, card, trajectory, declined=declined
            )

            for result in gate_results:
                gate_labels_by_card.setdefault(result.gate_id.name, {}).setdefault(
                    card.card_id, []
                ).append(result.outcome.value)
            q2_labels_by_card.setdefault(card.card_id, []).append(
                q2_label_value(quality_results.q2.label)
            )

            if trace_id is not None:
                link_trace_to_dataset_run(
                    langfuse_client,
                    runs[rep],
                    dataset_item_id=card.card_id,
                    trace_id=trace_id,
                )
            else:
                logger.warning(
                    "card=%s rep=%d: no trace_id — is Langfuse reachable? Not linked to a dataset "
                    "run (agreement is still computed locally below).",
                    card.card_id,
                    rep,
                )

    logger.info(
        "=== Repeat agreement (share of %d reps sharing the modal label) ===", REPS
    )
    for gate_name, labels_by_card in sorted(gate_labels_by_card.items()):
        agreement = compute_repeat_agreement(labels_by_card)
        mean_agreement = sum(agreement.values()) / len(agreement) if agreement else 0.0
        logger.info("%s: mean=%.2f per-card=%s", gate_name, mean_agreement, agreement)

    q2_agreement = compute_repeat_agreement(q2_labels_by_card)
    mean_q2_agreement = (
        sum(q2_agreement.values()) / len(q2_agreement) if q2_agreement else 0.0
    )
    logger.info(
        "Q2_TREATMENT_CLASS: mean=%.2f per-card=%s", mean_q2_agreement, q2_agreement
    )


if __name__ == "__main__":
    main()
