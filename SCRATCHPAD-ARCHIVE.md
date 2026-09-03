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
- 2026-09-01 — Rebuilt all 6 `data/ground_truth/*.yaml` files with verbatim-quoted claims (declined full
  source-page archiving) and synced `data/items.jsonl` to match, correcting two Phragmites items along the
  way (detail: DECISION-LOG.md, 2026-09-01 "Rebuilt all 6 ground-truth files..." and "Synced
  `data/items.jsonl`..." entries).
- 2026-09-01 — Drafted the accuracy/harm scoring rubric with anchor examples for every level, abstention
  scoring rules, and per-response field definitions: `scoring/RUBRIC.md` (detail: DECISION-LOG.md,
  2026-09-01 "Scoring rubric conventions locked" entry).
- 2026-09-01 — Reviewed all `ground_truth_citation`/`data/ground_truth/*.yaml` source URLs in
  `data/items.jsonl` for staleness or mismatch; replaced the one genuine problem found (Phragmites
  `method_selection`/`followup_secondary_invasion`, citing a domain the org itself now calls its "OLD
  WEBSITE") (detail: DECISION-LOG.md, 2026-09-01 "Replaced the Phragmites NC-IPC citation" entry). Not
  the same as the SCRATCHPAD.md task 1 freeze-gate review, which is broader and still open.
- 2026-09-01 — Fixed 12 `data/items.jsonl` citations (herbicide_legality item + all 20 abstention items
  audited) whose citation didn't support the specific claim it was attached to; added a
  `.claude/rules/domain-legal.md` rule after this pattern's 3rd occurrence (detail: DECISION-LOG.md,
  2026-09-01 "Fix unsupported claims in ground-truth citations..." entry).
- 2026-09-01 — Completed the freeze-gate review of all 60 `data/items.jsonl` items: checked every answer
  for completeness against its specific query and independently re-verified every citation; found and
  fixed 8 items (4 with matching `data/ground_truth/*.yaml` cell fixes) (detail: DECISION-LOG.md,
  2026-09-01 "Freeze-gate review of all 60 `data/items.jsonl` items" entry). Commit + freeze tag still
  pending — see `SCRATCHPAD.md` task 1.
- 2026-09-02 — Dropped the 20 abstention items from `data/items.jsonl` (now 40 answerable items),
  preserved verbatim at `data/deferred/abstention-items.jsonl` for a future release; updated `SCOPE.md`,
  `data/SCHEMA.md`, `PRODUCT_REQUIREMENTS.md`, and `scoring/RUBRIC.md` to match (detail: DECISION-LOG.md,
  2026-09-02 "Drop abstention items from this release; defer to a future release" entry).
- 2026-09-02 — Targeted re-verification pass: fetched 4 newly-supplied/re-fetched sources and fixed 12
  items plus 2 ground-truth cells; 3 items re-checked and confirmed already correct from the 2026-09-01
  freeze-gate pass (detail: DECISION-LOG.md, 2026-09-02 "Targeted re-verification pass" entry).
- 2026-09-02 — User-directed source pass: fetched 4 newly-supplied sources (NCDOT removal-plan report,
  NC Forest Service IS02, NC State CNR Bradford Pear Bounty article, re-verified NCDA&CS/CNS/AquaMaster/
  domyown) and fixed/re-cited 13 items plus matching ground-truth cells; resolved the
  `PHRA-METHOD-01`/`PHRA-TIMING-01` rate conflict onto AquaMaster's label figures; 3 findings confirmed
  still unbacked and left open for task 1 (detail: DECISION-LOG.md, 2026-09-02 "User-directed source
  pass" entry).
- 2026-09-02 — Freeze-gate re-verification complete: re-verified the last 17 of 40 active items, fixed 6
  and left `PYRU-DISPOSAL-01` as user-accepted; all 40 items now individually re-verified since the
  2026-09-01 xlsx sync. Commit + freeze tag still pending — see `SCRATCHPAD.md` task 1 (detail:
  DECISION-LOG.md, 2026-09-02 "Freeze-gate re-verification complete" entry).
- 2026-09-02 — Corpus-wide voice cleanup: converted the 26 remaining second-person items in
  `data/items.jsonl` to third person before freezing, per user decision; `data/SCHEMA.md` now states the
  convention explicitly (detail: DECISION-LOG.md, 2026-09-02 "Corpus-wide voice cleanup" entry).
- 2026-09-02 — `SCRATCHPAD.md` task 1 closed: committed `data/items.jsonl` + `data/ground_truth/*.yaml`
  (plus the accumulated Days 1-2 changes that had never been committed) and tagged the commit `freeze-v1`
  (commit `7d2f1b9`). The 40-item benchmark corpus is now frozen — no further item changes for any reason.
- 2026-09-02 — `SCRATCHPAD.md` task 1 (new numbering) closed: authored `scoring/checklist.jsonl` (40
  items, 260 rows of weighted atomic claims + item-specific harm triggers) and extended `scoring/RUBRIC.md`
  with the schema/weighting/harm-trigger conventions (detail: DECISION-LOG.md, 2026-09-02 "Checklist
  schema and authoring conventions locked" entry). Not yet committed.
- 2026-09-02 — Authored `scoring/SCORER-GUIDE.md`, a plain-language scorer SOP (purpose/materials/steps/
  definition of done) separate from `scoring/RUBRIC.md`'s calibration-anchor content; `PRODUCT_REQUIREMENTS.md`
  §4/§10 updated to name it as part of the Day 9 rubric deliverable (detail: DECISION-LOG.md, 2026-09-02
  "Added a plain-language scorer's guide separate from RUBRIC.md" entry). Not yet committed.
