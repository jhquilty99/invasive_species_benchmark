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
- 2026-09-03 — Merged the new multi-turn-methodology PRD into `PRODUCT_REQUIREMENTS.md` (now v4);
  archived PRD v3's single-turn artifacts (`data/items.jsonl`, `data/deferred/abstention-items.jsonl`,
  `scoring/checklist.jsonl`, `scoring/RUBRIC.md`, `scoring/SCORER-GUIDE.md`, xlsx/build/sync scripts) to
  `archive/study-a-single-turn/` via `git mv`; updated `SCOPE.md`, `data/SCHEMA.md`, `SCRATCHPAD.md`, and
  `.claude/rules/domain-legal.md` to match (detail: DECISION-LOG.md, 2026-09-03 "Pivot to multi-turn
  simulated-conversation methodology (PRD v4)" entry).
- 2026-09-03 — Stood up a local self-hosted Langfuse instance (`infra/langfuse/`, Docker Compose, v4.28.0)
  ahead of the run harness; verified all 6 services healthy and the bootstrapped project/API key work
  end-to-end. SDK wiring into the harness itself deferred until the `pyproject.toml` scaffold exists.
- 2026-09-03 — Day 1 complete: `pyproject.toml`/`harness/` package scaffold; `cards/SCHEMA.md` +
  `harness/models.py` card schema; both PRD §13 open-question decisions; the `ailanthus-stump-resprout-01`
  test card; the slot-gated simulated user (`harness/simulated_user.py`); the `openevals` conversation
  loop + stopping condition (`harness/conversation.py`); Langfuse SDK wiring (`harness/langfuse_client.py`).
  30 passing tests (VCR cassettes recorded), ruff/mypy clean, verified end to end with a live run whose
  trace landed in the local Langfuse instance (detail: `DECISION-LOG.md`, 2026-09-03 "Resolved PRD
  §13.2..." and "Card citations trace through `data/ground_truth/*.yaml`...").
- 2026-09-03 — Added `.claude/rules/card-voice.md` specifying naive/vague/lazy-user voice rules for
  card `opening_message`, updated `cards/SCHEMA.md` and `CLAUDE.md` to reference it, and rewrote
  `cards/ailanthus-stump-resprout-01.json`'s `opening_message` to conform (detail: `DECISION-LOG.md`,
  2026-09-03 "Card `opening_message` must voice a naive, harmable user").
- 2026-09-03 — Authored `data/ground_truth/*.yaml` for all 6 native/lookalike species (*Rhus
  copallinum*, *Chionanthus virginicus*, *Leersia virginica*, *Wisteria frutescens*, *Prunus
  angustifolia*, *Phragmites australis* ssp. *americanus*), each cited and verified against real
  sources per `.claude/rules/domain-legal.md`. Closes the ground-truth-authoring half of `SCRATCHPAD.md`'s
  native-species task (split work: `chionanthus-virginicus.yaml` this session, the other 5 a parallel
  session working the same plan).
- 2026-09-03 — Authored 12 single-question-type "removal"/"decline-to-treat" cards, one per species (6
  invasive: `ligustrum-overgrown-hedge-01`, `microstegium-lawn-invasion-01`, `wisteria-fence-vine-01`,
  `pyrus-calleryana-volunteer-tree-01`, `phragmites-ditch-reed-01`, plus the pre-existing
  `ailanthus-stump-resprout-01`; 6 native: `chionanthus-virginicus-lookalike-01` this session,
  `leersia-virginica-lookalike-01`/`rhus-copallinum-lookalike-01`/`wisteria-frutescens-lookalike-01`/
  `prunus-angustifolia-lookalike-01`/`phragmites-americanus-lookalike-01` from a parallel session),
  all schema-valid (30/30 tests passing). Written before the same-day card-matrix redesign (see
  `DECISION-LOG.md`, 2026-09-03 "Card matrix restructured around question type × native status
  (RQ1-3, Q6)") — these are pre-rework-shape cards (no `question_type`/`native_status`), useful now for
  slot-classifier tuning, but do **not** fulfill the new task's "cards spanning all 3 question types"
  requirement — that's still open, blocked on the `harness/models.py` rework task.
- 2026-09-03 — Harness rework: `harness/models.py`'s `Card` model gained `question_type`, `native_status`,
  `introduction_classes`, and `ecological_framing_notes`, with a `model_validator` enforcing which fields
  are required/forbidden per `question_type` (removal / introduction / identification), matching
  `cards/SCHEMA.md`. `harness/langfuse_client.py`'s `build_dataset_item_expected_output` updated to match;
  all 12 then-existing cards migrated to the new shape (6 removal/invasive stayed removal-shaped and
  gained `ecological_framing_notes`; 6 native "decline-to-treat" cards converted to `identification`-type,
  removal-only fields dropped, `opening_message` rewritten to a "what is this?" framing). 35/35 tests
  passing (incl. new known-correct/known-incorrect coverage for the conditional-validation rule);
  ruff/mypy clean (detail: `DECISION-LOG.md`, 2026-09-03 "Harness rework: `Card` model supports
  question_type/native_status (implementation)").
- 2026-09-03 — Authored the first `introduction`-type card, `chionanthus-virginicus-introduction-01`
  (fringetree, "should I keep/plant this?"), closing the "at least one card per question type" test-card
  task — 13 cards now exist spanning all 3 question types (6 removal, 6 identification, 1 introduction).
- 2026-09-03 — Reworked `harness/models.py`'s `Card` model for the restructured schema:
  `question_type`/`native_status`/`introduction_classes`/`ecological_framing_notes` fields plus a
  validator enforcing which fields apply per `question_type` (matches `cards/SCHEMA.md` exactly);
  migrated all 12 pre-existing cards to the new shape (6 invasive cards stayed `removal`-type and
  gained `native_status`/`ecological_framing_notes`; the 6 native cards were converted from a
  removal-framed "decline to prescribe" design to `identification`-type, with opening messages
  rewritten to a "what is this plant?" framing per `.claude/rules/card-voice.md`). All cards load and
  validate; ruff/mypy clean. Closes the harness-rework half of the "cards spanning all 3 question
  types" task.
- 2026-09-03 — Authored `cards/chionanthus-virginicus-introduction-01.json`, the first
  `introduction`-type card ("should I keep/plant this?" framing, fringetree), plus schema-conformance
  tests in `tests/test_cards.py` covering all 3 `question_type` values' field requirements (parallel
  session). Closes the "cards spanning all 3 question types" task — 13 cards now exist across all 3
  question types (6 removal/invasive, 6 identification/native, 1 introduction/native), 35 tests
  passing.
- 2026-09-03 — Closed the gate-judge, quality-judging, and per-turn-Langfuse-tracing tasks: built
  `harness/judges/gates.py` (G1-G5), `harness/judges/quality.py` (Q2/Q3/Q5/Q6), `harness/scoring.py`
  (Q1 + derived metrics), `harness/_tracing.py` (real per-turn Langfuse spans), and
  `harness/scripts/run_validation.py` (end-to-end runner across all 13 cards). Added type-aware
  stopping classifiers for `introduction`/`identification` cards, resolving `PRODUCT_REQUIREMENTS.md`
  §13.5's open question along the way. 83 tests passing (cassettes recorded against the real API),
  ruff/mypy clean. Q4 (regulatory grounding) deliberately deferred (detail: `DECISION-LOG.md`,
  2026-09-03 "First-pass LLM-as-judge validation, wired through Langfuse").
- 2026-09-03 — Ran the live validation sweep (`harness/scripts/run_validation.py`) against all 13
  cards for real. Fixed a real judge-call bug found along the way (`max_tokens=1024` too low for
  `claude-sonnet-5`'s extended thinking on real transcripts, truncating JSON output — raised to 4096).
  All 116 gate/quality/Q1 scores landed in Langfuse. Found but did not fix a separate local-infra bug
  (Langfuse worker's Redis queue failing every job, so no trace/span data ingested); recovered full
  results directly from ClickHouse instead. Headline finding: G1 failed on 9/13 cards (69%) — the
  model-under-test frequently answers without committing to species identity (detail: `DECISION-LOG.md`,
  2026-09-03 "Live validation run: one real bug fixed, one local-infra bug found and deferred").
- 2026-09-04 — Expanded `PRODUCT_REQUIREMENTS.md` §2 to RQ1-RQ6 + C1/C2 (from the old 3-RQ version) and
  added an oracle-contrast experimental arm to RQ1; propagated the new numbering through `SCOPE.md` and
  `cards/SCHEMA.md` (detail: `DECISION-LOG.md`, 2026-09-04 "Expanded research questions to RQ1-RQ6 +
  C1/C2; added oracle-contrast experimental arm").
- 2026-09-04 — Built Q4 (regulatory grounding): `harness/ground_truth.py` loads `data/ground_truth/
  *.yaml` directly, `judge_q4_regulatory_grounding` scores a removal card's regulatory/legal/timing
  claims against it, `not_applicable` elsewhere — closes the task this file had tracked since the
  2026-09-03 first-pass validation build deferred it (detail: `DECISION-LOG.md`, 2026-09-04
  "Methodology-eval hardening: G6, Q4, oracle-contrast mechanism, repeat pilot").
- 2026-09-04 — Built the RQ1 oracle-contrast arm mechanism (PRD §2/§6/R6): `build_oracle_opening_
  message`, `make_simulated_user(..., oracle=True)`, `run_conversation(..., oracle=True)`,
  `start_dataset_run(..., arm=...)` giving standard/oracle runs distinct Langfuse dataset-run names and
  metadata. Validated end-to-end on a real removal card via `run_validation.py`'s new `ARM` constant —
  closes the "zero code exists" gap the methodology eval flagged (detail: `DECISION-LOG.md`, 2026-09-04
  "Methodology-eval hardening: G6, Q4, oracle-contrast mechanism, repeat pilot").
- 2026-09-04 — Added gate G6 (RQ3's harmful-action-warning-omission sub-class) and a repeated-sampling
  pilot script (`harness/scripts/run_repeat_pilot.py`, RQ6-adjacent noise characterization; RQ6 itself
  stays cut) — both surfaced by the methodology eval (detail: `DECISION-LOG.md`, 2026-09-04
  "Methodology-eval hardening: G6, Q4, oracle-contrast mechanism, repeat pilot").
- 2026-09-04 — Added RQ5 `referral_expected`/`referral_reason` schema fields (`Card` model, Q2/G1 judge
  prompts, `is_referral_correct` derived metric) and 2 new cards using them
  (`phragmites-public-water-referral-01.json` removal, `wisteria-dormant-vine-referral-01.json`
  identification) — real scope growth, 54 → 56 cards / 84 → 87 runs per model, logged the same way as
  the 2026-09-04 oracle-arm growth (detail: `DECISION-LOG.md`, 2026-09-04 "RQ5 referral_expected schema
  and card-count growth").
