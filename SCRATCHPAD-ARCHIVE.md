# Scratchpad — archive

Append-only. One line per closed task, written the instant it closes (see `.claude/docs/scratchpad-discipline.md`).
Format: `- YYYY-MM-DD — <task> (detail: DECISION-LOG.md#<slug> if applicable)`

Full detail blocks for anything non-trivial live in `DECISION-LOG.md`, not here — this file is a closed-task
index, not a history of *why*.

## Archived

- 2026-08-31 — Committed `SCOPE.md` locking PRD §2 scope (6 species, ~60 items, 4 models, 2 conditions,
  1 scored run) — the PRD's Day 1 task.
- 2026-08-31 — Confirmed earliest grad application deadline (UC Berkeley MIDS, Oct 23, 2026) — Sep 20
  ship date keeps its full buffer, no replanning needed.
- 2026-08-31 — Sent expert-validation emails to candidates in `outreach/EMAIL-TRACKER.md` (per user
  confirmation; tracker's Sent/Date-sent columns still need a matching update — flagged, not fixed here).
- 2026-08-31 — Confirmed API access/budget for OpenAI, Anthropic, and Google; locked the 4-model
  line-up shape (3 closed APIs + 1 open-weight model via a third-party host, TBD) (detail:
  DECISION-LOG.md, 2026-08-31 "API access confirmed" entry).
- 2026-08-31 — Defined the benchmark dataset/scenario file format: `data/SCHEMA.md`, ground-truth as
  per-species YAML, items as `data/items.jsonl` (detail: DECISION-LOG.md, 2026-08-31 "Benchmark dataset
  scenario file format" entry).
- 2026-08-31 — Built the ground-truth corpus: 6 species × 6 categories, `data/ground_truth/*.yaml`,
  0 jurisdiction-range flags (detail: DECISION-LOG.md, 2026-08-31 "Ground-truth corpus built" entry).
- 2026-08-31 — Closed the Fri Sep 4 "grid-complete gate" task as moot: the corpus finished 4 days ahead
  of that gate, so the pre-authorized cut-to-4-species contingency never triggered.
- 2026-08-31 — Wrote all 60 benchmark items to `data/items.jsonl`: 40 answerable (8/8/6/8/6/4 across the
  6 categories) + 20 abstention (5 per reason), schema-checked (detail: DECISION-LOG.md, 2026-08-31 "60
  benchmark items written" entry). Freeze-gate review (SCRATCHPAD.md task 1) still open.
