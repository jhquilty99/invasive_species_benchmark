# Archive: Study A (single-turn item benchmark)

This directory holds the frozen artifacts of the original single-turn, item-based benchmark design
(PRD v3, tagged `freeze-v1` at commit `7d2f1b9`). On 2026-09-03 the project pivoted to a multi-turn
simulated-conversation methodology (PRD v4) — see `DECISION-LOG.md`, 2026-09-03 "Pivot to multi-turn
simulated-conversation methodology (PRD v4)". These files are archived, not deleted, per this repo's
"defer, don't discard" convention (`CLAUDE.md`, "Always true").

## What's here

- `data/items.jsonl` — the frozen 40-item answerable corpus.
- `data/deferred/abstention-items.jsonl` — the 20 abstention items, already deferred out of Study A before
  the pivot.
- `scoring/checklist.jsonl`, `RUBRIC.md`, `SCORER-GUIDE.md` — the per-item accuracy/harm scoring
  instrument built for the single-turn corpus.
- `scoring/checklist.xlsx`, `items-review.xlsx` and the `build_*_xlsx.py` / `sync_items_from_xlsx.py`
  scripts that generated/synced them.
- `SCHEMA.md` — a snapshot of `data/SCHEMA.md` as it stood before it was trimmed for the pivot; documents
  the `items.jsonl` and deferred-abstention-item formats these files use. (`data/SCHEMA.md` in the live
  repo now documents only the still-active ground-truth YAML schema.)

## What's not here (stayed active)

`data/ground_truth/*.yaml` was **not** archived — it's reused as source material (species facts +
citations) for authoring the new multi-turn case cards under the new methodology.

## Reuse notes

The abstention items and their `abstention_reason` taxonomy (`outside_region`, `site_assessment_required`,
`unstated_variable`, `illegal_rate_for_layperson`) may be useful source material when designing the new
PRD's `declined` category or the lookalike-arm cards, even though the schema itself doesn't carry over.
