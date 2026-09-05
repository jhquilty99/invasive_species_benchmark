"""Stratified SME-sample selection entrypoint (`harness/sampling.py`, PRD v4 Sec 7).

    uv run python -m harness.scripts.select_sme_sample

Reads `RESULTS_PATH` (the sweep's on-disk JSONL, `harness/results_store.py`), selects `SELECTED_TOTAL`
items per `harness.sampling.select_sme_sample`, writes the selection to `SELECTION_PATH`, and prints a
per-stratum summary plus, for every selected item, a direct Langfuse console trace link
(`Langfuse.get_trace_url`) — the fastest way to open exactly that conversation's transcript/scores
without hunting through the dataset's run list by hand. No API calls, no API budget spent — this only
reads already-computed results and (for the trace-link text) builds URLs from `LANGFUSE_HOST` plus the
project slug the SDK already resolves.

Plain module constants, no CLI framework (`.claude/rules/python.md`). Model identity is real (not yet
blinded) in this script's output — blinding to Model A/B/C happens at the xlsx-export step
(`harness/scripts/build_sme_review_xlsx.py`, not yet built), which is this script's downstream
consumer, not this one.
"""

import logging
from pathlib import Path

from harness.config import Settings
from harness.langfuse_client import get_langfuse_client
from harness.results_store import load_sweep_results
from harness.sampling import select_sme_sample

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CARD_SET_VERSION = "wip-2026-09-04-sme-validation-21card"
RESULTS_PATH = _REPO_ROOT / "results" / "sweep" / CARD_SET_VERSION / "results.jsonl"
SELECTION_PATH = (
    _REPO_ROOT / "results" / "sweep" / CARD_SET_VERSION / "sample_selection.json"
)
SEED = 42


def main() -> None:
    results = load_sweep_results(RESULTS_PATH)
    logger.info("Loaded %d results from %s", len(results), RESULTS_PATH)

    selection = select_sme_sample(results, seed=SEED)

    SELECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SELECTION_PATH.write_text(selection.model_dump_json(indent=2), encoding="utf-8")

    settings = Settings()  # type: ignore[call-arg]
    langfuse_client = get_langfuse_client(settings)

    print(
        f"\n=== SME sample selection: {len(selection.items)}/{selection.target_total} items ==="
    )
    for note in selection.notes:
        print(f"NOTE: {note}")

    by_stratum: dict[str, list] = {}
    for item in selection.items:
        by_stratum.setdefault(item.question_type.value, []).append(item)

    for question_type, target in selection.stratum_targets.items():
        stratum_items = by_stratum.get(question_type.value, [])
        n_flagged = sum(1 for i in stratum_items if i.flagged)
        print(
            f"\n--- {question_type.value}: {len(stratum_items)}/{target} "
            f"({n_flagged} flagged, {len(stratum_items) - n_flagged} unflagged) ---"
        )
        for item in stratum_items:
            trace_url = (
                langfuse_client.get_trace_url(trace_id=item.trace_id)
                if item.trace_id
                else "(no trace_id — Langfuse was unreachable for this run)"
            )
            flag_tag = f"FLAGGED[{item.flag_reason}]" if item.flagged else "clean"
            print(
                f"  {item.card_id:45s} {item.model_id:25s} {flag_tag:35s} {trace_url}"
            )

    print(f"\nFull selection written to {SELECTION_PATH}")
    print(
        "\nTo browse the same items by dataset run instead of by trace link: Langfuse console -> "
        "Datasets -> case-cards -> Runs tab -> one run per model "
        "(name format '<model_id>__<judge_prompt_version>'), then filter that run's items by card_id."
    )


if __name__ == "__main__":
    main()
