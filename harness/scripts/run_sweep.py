"""Sweep entrypoint: run `harness.sweep.run_sweep` across the current card corpus and the wired
model line-up.

    uv run python -m harness.scripts.run_sweep

Plain module constants, no CLI framework (`.claude/rules/python.md`) — flip `CARDS_DIR`/`MODEL_IDS`/
`ARM`/`CARD_SET_VERSION` and re-run for a different scope. This same entrypoint serves the
SME-validation deliverable's sweeps (today: the expanded 21-card corpus, hence a work-in-progress
`CARD_SET_VERSION`, not `"freeze-v1"`) and, eventually, the full production sweep once the corpus is
frozen and the full 4-6 model line-up is wired (`SCRATCHPAD.md` tasks 8-11) — only the constants below
change, not `harness/sweep.py` itself.

Requires a locally reachable Langfuse instance (`cd infra/langfuse && docker compose up -d` —
best-effort: `harness.sweep.run_sweep` still writes every result to `RESULTS_PATH` even if Langfuse
scoring-attachment fails for a given trace) and real `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/
`GOOGLE_API_KEY` in the root `.env`. Spends real API budget across all three vendors — a manual,
deliberate run, not something the test suite executes.
"""

import logging
from pathlib import Path

from harness.cards import load_cards
from harness.config import Settings
from harness.langfuse_client import (
    ensure_score_configs,
    get_langfuse_client,
    get_or_create_dataset,
    upsert_card_dataset_item,
)
from harness.model_clients import build_model_clients
from harness.sweep import run_sweep

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CARDS_DIR = _REPO_ROOT / "cards"
CARD_SET_VERSION = "wip-2026-09-04-sme-validation-21card"
"""Tag for the real (non-dry-run) sweep over the expanded 21-card corpus (SCRATCHPAD.md task 1) —
distinct from the completed `"wip-2026-09-04-sme-dry-run"` 15-card dry run, and not the eventual frozen
56-card set's `"freeze-v1"`."""
MODEL_IDS = ["claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview"]
"""Pinned per `harness.model_clients.MODEL_VENDOR_MAP` — see that module's docstring and
`DECISION-LOG.md`'s 2026-09-04 entry for why these specific IDs, confirmed with the user before this
script's first real run."""
ARM = "standard"
RESULTS_PATH = _REPO_ROOT / "results" / "sweep" / CARD_SET_VERSION / "results.jsonl"


def main() -> None:
    settings = Settings()  # type: ignore[call-arg]
    clients = build_model_clients(settings)
    langfuse_client = get_langfuse_client(settings)

    cards = load_cards(CARDS_DIR)
    logger.info("Loaded %d cards from %s", len(cards), CARDS_DIR)

    ensure_score_configs(langfuse_client)
    get_or_create_dataset(langfuse_client)
    for card in cards:
        upsert_card_dataset_item(langfuse_client, card)

    results = run_sweep(
        cards,
        MODEL_IDS,
        arm=ARM,
        clients=clients,
        card_set_version=CARD_SET_VERSION,
        results_path=RESULTS_PATH,
        langfuse_client=langfuse_client,
    )

    leaked = sum(1 for r in results if r.leakage_report.leaked)
    by_model: dict[str, int] = {}
    for r in results:
        by_model[r.model_id] = by_model.get(r.model_id, 0) + 1
    logger.info(
        "=== Sweep done: %d results in %s | per-model counts: %s | %d flagged for R5 leakage ===",
        len(results),
        RESULTS_PATH,
        by_model,
        leaked,
    )


if __name__ == "__main__":
    main()
