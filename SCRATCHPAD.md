# Scratchpad — active

Open work only. A task lives here from creation until it closes. The instant it closes: append its
one-line entry to `SCRATCHPAD-ARCHIVE.md`, then remove its block from this file (the removal rides with
the commit that finished the work — see `.claude/docs/scratchpad-discipline.md`).

This file is a tracker, not memory. Durable facts/preferences/decisions do not belong here — they belong
in a rule file or `DECISION-LOG.md`.

## Status

- **Repo state:** `SCOPE.md` committed, locking PRD §2. `data/SCHEMA.md` defines the corpus/item file
  formats. Ground-truth corpus (`data/ground_truth/*.yaml`, 6 species × 6 categories, 0 jurisdiction-range
  flags) and the 40-item benchmark set (`data/items.jsonl`) are **committed and tagged `freeze-v1`
  (commit `7d2f1b9`, 2026-09-02) — frozen, no further item changes for any reason.** The 20 abstention
  items are deferred to a future release, preserved verbatim at `data/deferred/abstention-items.jsonl`.
  Full build/re-verification/voice-cleanup history: `DECISION-LOG.md` (2026-08-31 through 2026-09-02
  entries) and `SCRATCHPAD-ARCHIVE.md`. Week 2 formally starts now — task 1 below (checklist authoring)
  leads.
- **Deadline confirmed:** earliest grad application is UC Berkeley MIDS, **Oct 23, 2026** — well past
  the Sep 20 ship date, so the 3-week schedule keeps its full buffer. No replanning needed.
- **API access confirmed:** OpenAI, Anthropic, Google all active. 4th model will be a small open-weight
  model via a third-party host — exact model/host still TBD, deferred to PRD's Day 10-11 run setup.
- **Outreach:** expert-validation emails reported sent (see `outreach/EMAIL-TRACKER.md`) — that file's
  Status/Date-sent columns still need to be updated to match; not yet fixed.
- **Task list:** pulled in the full Week 2 task set (PRD §4/§10 Days 8-15: rubric, scoring sheet, doc
  bundles, run harness, runs, scoring) and reordered by dependency/PRD-day order. Rubric task (Days 8-9)
  is done: `scoring/RUBRIC.md` (detail: DECISION-LOG.md, 2026-09-01 "Scoring rubric conventions locked"
  entry).
- **Scoring methodology changed:** primary scoring is now a per-item checklist (atomic ground-truth
  claims + harm triggers + a catch-all flag for unanticipated wrong content), not the holistic
  Accuracy/Harm scale alone. `scoring/RUBRIC.md`'s holistic scale is kept, not deleted — it's now the
  instrument for a small convergent-validity side-check folded into the existing 20-item expert ask
  (detail: DECISION-LOG.md, 2026-09-01 "Switched primary scoring method to a per-item checklist" entry).
  Checklist-authoring cost (~300-430 rows across 40 items) is not yet placed in the Week 1/2 schedule —
  see task 1 below.
- **Last touched:** 2026-09-02

## Open tasks (ranked)

1. **[New — unscheduled]** Author the accuracy/harm checklist for all 40 items: for each item, decompose
   its relevant ground-truth cell(s) into weighted atomic claims (critical vs. standard) and predefined
   harm-trigger conditions (each scored present/absent/contradicted), plus a free-text catch-all flag for
   wrong content the checklist didn't anticipate. Extends `scoring/RUBRIC.md` — does not replace its
   holistic Accuracy/Harm anchors, which are kept for task 2 (detail: DECISION-LOG.md, 2026-09-01
   "Switched primary scoring method to a per-item checklist" entry). **Not yet placed in the Days 8-9
   schedule** — ~300-430 rows across 40 items is more than the original 3-hr rubric budget assumed; needs
   its own day-by-day slot before Day 9's scoring sheet (task 3) can be built against it.
2. Prepare the expert-review packet for whenever an expert-validation reply lands (outreach sent
   2026-08-31, tracker: `outreach/EMAIL-TRACKER.md`): ask reviewers to (a) critique the task-1 checklist's
   claim/trigger decomposition for face validity and (b) independently give a holistic Accuracy/Harm score
   (per `scoring/RUBRIC.md`'s anchors) on the same ~20-item subset with no reference to the checklist, so
   checklist-derived and holistic scores can be compared for agreement. Depends on task 1 existing first;
   PRD's existing Sep 15-16 slot still applies if the reply lands on the expected Sep 7-14 window.
3. **[Day 9]** Build the scoring sheet and the blinding/shuffle script — strips model identity and
   shuffles response order so Days 13-15 scoring can be done blind (PRD §6 rule 4: human scoring primary).
   Records the task-1 checklist's per-claim and per-trigger results plus the catch-all note field per
   response, not a single holistic value (detail: DECISION-LOG.md, 2026-09-01 "Switched primary scoring
   method to a per-item checklist" entry).
4. **[Day 10]** Assemble per-species document bundles for Condition 2 (oracle grounding) from
   `data/ground_truth/*.yaml`, per PRD §3.
5. Decide the stack layout under `src/` (Python, dependency-managed via `uv` — see
   `.claude/rules/python.md`) and add the first `pyproject.toml` / test scaffold. Needed before task 6
   (the run harness) can be written — no longer deferrable now that runs are the next phase. Also needed
   to declare `scoring/build_items_review_xlsx.py` and `scoring/sync_items_from_xlsx.py`'s `openpyxl`
   dependency, which currently has no `pyproject.toml` to resolve against (flagged by the freeze-gate
   commit's architecture review, DECISION-LOG.md 2026-09-02).
6. **[Day 10]** Write the run harness: executes both conditions across all 4 models at temperature 0, and
   **logs exact model version strings** (PRD §6 rule 5 — non-negotiable).
7. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4th model
   slot — PRD Day 10-11, needed before runs execute (task 8).
8. **[Days 11-12 — Gate Fri Sep 11]** Execute runs: Condition 1 first (all 4 models, 2 runs each), verify
   version-string logging; then Condition 2 (all 4 models, 2 runs each), spot-check outputs for
   truncation or refusal loops. Gate: all model responses collected by Fri Sep 11 — if behind, drop
   Condition 2 before dropping scoring time (PRD §10 dated gates).
9. **[Days 13-15 — Gate Mon Sep 14]** Score all ~320 responses blind (shuffled, identity-stripped, per
   task 3's script and the task-1 checklist): ~105 (Day 13), ~105 (Day 14), finish the remaining ~110
   (Day 15). Gate: scoring complete by Mon Sep 14 — if behind, drop Model 4 entirely (3 models still
   support every analysis per PRD §7).
10. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
   sent (currently still shows "Not sent" for all real contacts). No dependency on anything above —
   pure housekeeping, lowest priority.

## Open bugs

_None._ (Three low-severity housekeeping notes from the freeze commit's architecture review, none
blocking: `ailanthus-altissima.yaml#disposal_nontarget_risk` is a written, cited cell no item references
— intentional per the documented 8/8/6/8/6/4 category allocation, not a bug; `scoring/build_items_review_xlsx.py`
lacks the type hints `scoring/sync_items_from_xlsx.py` has, inconsistent with `.claude/rules/python.md`;
`scoring/items-review.xlsx` is a regenerable binary artifact that's currently committed rather than
gitignored. Detail: DECISION-LOG.md, 2026-09-02 "Freeze-gate re-verification complete" entry.)

## Pending tests

_None yet — no code to test._
