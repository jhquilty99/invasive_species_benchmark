# Scratchpad — active

Open work only. A task lives here from creation until it closes. The instant it closes: append its
one-line entry to `SCRATCHPAD-ARCHIVE.md`, then remove its block from this file (the removal rides with
the commit that finished the work — see `.claude/docs/scratchpad-discipline.md`).

This file is a tracker, not memory. Durable facts/preferences/decisions do not belong here — they belong
in a rule file or `DECISION-LOG.md`.

## Status

- **Repo state:** `SCOPE.md` committed, locking PRD §2. `data/SCHEMA.md` defines the corpus/item file
  formats. Ground-truth corpus is built: `data/ground_truth/*.yaml`, 6 species × 6 categories, 0
  jurisdiction-range flags (detail: DECISION-LOG.md, 2026-08-31 "Ground-truth corpus built" entry).
  `data/items.jsonl` holds **40 answerable items** (8/8/6/8/6/4 across the 6 categories) — the 20
  abstention items are deferred to a future release, preserved verbatim at
  `data/deferred/abstention-items.jsonl` (detail: DECISION-LOG.md, 2026-09-02 "Drop abstention items from
  this release" entry). **All 40 active items are now individually re-verified** against their citations
  post-xlsx-sync — freeze-gate review closed 2026-09-02 (detail: DECISION-LOG.md, "Freeze-gate review
  completed: remaining 17 items re-verified, `data/items.jsonl` frozen" entry). Not yet committed/tagged —
  see task 1 below (commit + freeze tag, now the only thing standing between this and Week 2 formally
  starting).
- **Deadline confirmed:** earliest grad application is UC Berkeley MIDS, **Oct 23, 2026** — well past
  the Sep 20 ship date, so the 3-week schedule keeps its full buffer. No replanning needed.
- **API access confirmed:** OpenAI, Anthropic, Google all active. 4th model will be a small open-weight
  model via a third-party host — exact model/host still TBD, deferred to PRD's Day 10-11 run setup.
- **Outreach:** expert-validation emails reported sent (see `outreach/EMAIL-TRACKER.md`) — that file's
  Status/Date-sent columns still need to be updated to match; not yet fixed.
- **Task list:** pulled in the full Week 2 task set (PRD §4/§10 Days 8-15: rubric, scoring sheet, doc
  bundles, run harness, runs, scoring) and reordered by dependency/PRD-day order — the freeze gate (task
  1) still leads since it blocks all of Week 2 formally starting. Rubric task (Days 8-9) is done:
  `scoring/RUBRIC.md` (detail: DECISION-LOG.md, 2026-09-01 "Scoring rubric conventions locked" entry).
- **Scoring methodology changed:** primary scoring is now a per-item checklist (atomic ground-truth
  claims + harm triggers + a catch-all flag for unanticipated wrong content), not the holistic
  Accuracy/Harm scale alone. `scoring/RUBRIC.md`'s holistic scale is kept, not deleted — it's now the
  instrument for a small convergent-validity side-check folded into the existing 20-item expert ask
  (detail: DECISION-LOG.md, 2026-09-01 "Switched primary scoring method to a per-item checklist" entry).
  Checklist-authoring cost (~300-430 rows across 40 items) is not yet placed in the Week 1/2 schedule —
  see task 2 below.
- **Targeted re-verification pass (2026-09-02):** 12 of the 40 items fixed against 4 newly-supplied/
  re-fetched sources — `MICR-METHOD-01`, `MICR-HERBLEGAL-01`, `PHRA-METHOD-01`, `PHRA-RESPROUT-01`,
  `LIGU-METHOD-01`, `LIGU-DISPOSAL-01`, `AILA-METHOD-01`, `AILA-METHOD-02`, `AILA-TIMING-01`,
  `AILA-HERBLEGAL-01`, `PHRA-HERBLEGAL-02`, `PYRU-HERBLEGAL-01` — plus 2 ground-truth cells gained new
  cited content (`microstegium-vimineum.yaml#method_selection`, `#resprout_regrowth`;
  `phragmites-australis.yaml#method_selection`). `MICR-HERBLEGAL-02`/`PHRA-METHOD-02`/`WIST-METHOD-01`
  re-checked and confirmed already correct from the 2026-09-01 freeze-gate pass. Detail: DECISION-LOG.md,
  2026-09-02 "Targeted re-verification pass" entry.
- **User-directed source pass (2026-09-02, same day):** following a separate read-only audit of all 40
  items, user supplied 4 new sources (NCDOT's High-Threat Invasive Plant Species Removal Plan Report —
  covers 5 of 6 species; NC Forest Service IS02 privet alert; NC State CNR's Bradford Pear Bounty
  article; re-verified NCDA&CS/CNS/AquaMaster/domyown). 13 items fixed/re-cited:
  `AILA-METHOD-01`, `AILA-METHOD-02`, `AILA-TIMING-01`, `LIGU-HERBLEGAL-01`, `LIGU-TIMING-01`,
  `MICR-TIMING-01`, `MICR-FOLLOWUP-01`, `PHRA-METHOD-01`, `PHRA-FOLLOWUP-01`, `PYRU-HERBLEGAL-01`,
  `PYRU-FOLLOWUP-01`, `WIST-METHOD-01` (citation strengthened only), `WIST-TIMING-01`,
  `WIST-FOLLOWUP-01`, `WIST-DISPOSAL-01` — plus matching `data/ground_truth/*.yaml` cells updated to
  match. `PHRA-METHOD-01`/`PHRA-TIMING-01`'s rate conflict resolved onto AquaMaster's actual label
  figures per user decision. Detail: DECISION-LOG.md, 2026-09-02 "User-directed source pass" entry.
  **3 findings confirmed still unbacked, left open:** `LIGU-DISPOSAL-01` (composting-specific reasoning,
  unquoted, still no cited source), `MICR-HERBLEGAL-02` (one quoted phrase from an unnamed third source),
  `PYRU-DISPOSAL-01` (one quote not found in its cited source — user said leave as-is).
- **Freeze-gate review closed (2026-09-02):** the remaining 17 items (14 untouched by either pass above +
  the 3 unbacked findings) re-verified against sources — 9 already clean, `PYRU-DISPOSAL-01` left as-is
  per standing instruction, 6 fixed (`MICR-RESPROUT-01`/`MICR-HERBLEGAL-02` — real quotes, added to the
  yaml cell; `PYRU-METHOD-01`/`PYRU-RESPROUT-02` — real quotes confirmed via NC State Extension fetch,
  added to yaml cells; `PYRU-TIMING-01` — dropped a fabricated composite quote; `WIST-HERBLEGAL-01` —
  rewrote using only confirmed rates/quotes; `LIGU-DISPOSAL-01` — dropped an unsourced composting-mechanism
  claim). All 40 active items are now individually re-verified since the xlsx sync. Detail: DECISION-LOG.md,
  2026-09-02 "Freeze-gate re-verification complete" entry.
- **Corpus-wide voice cleanup (2026-09-02):** copy review of the freeze-gate diff found 25-27 of 40 items
  still in second-person voice (inherited from the 2026-09-01 xlsx sync), against this corpus's established
  third-person convention. Per user decision, fixed before freezing rather than after: all 40 items are now
  third person (2 remaining "you"/"your" matches are inside verbatim source quotes, not narrative voice).
  `data/SCHEMA.md` now states the convention explicitly. Detail: DECISION-LOG.md, 2026-09-02 "Corpus-wide
  voice cleanup" entry.
- **Last touched:** 2026-09-02

## Open tasks (ranked)

1. **[Gate — Sun Sep 6]** Re-review complete (all 40 active items now individually re-verified — see
   Status above). Remaining: run `/commit`'s three specialist reviewers over the diff, address findings,
   then commit `data/items.jsonl` + `data/ground_truth/*.yaml` and tag the commit to **freeze the
   benchmark**. No item changes after that point for any reason. Blocks everything below — Week 2 formally
   starts after this.
2. **[New — unscheduled]** Author the accuracy/harm checklist for all 40 items: for each item, decompose
   its relevant ground-truth cell(s) into weighted atomic claims (critical vs. standard) and predefined
   harm-trigger conditions (each scored present/absent/contradicted), plus a free-text catch-all flag for
   wrong content the checklist didn't anticipate. Extends `scoring/RUBRIC.md` — does not replace its
   holistic Accuracy/Harm anchors, which are kept for task 3 (detail: DECISION-LOG.md, 2026-09-01
   "Switched primary scoring method to a per-item checklist" entry). **Not yet placed in the Days 8-9
   schedule** — ~300-430 rows across 40 items is more than the original 3-hr rubric budget assumed; needs
   its own day-by-day slot before Day 9's scoring sheet (task 4) can be built against it.
3. Prepare the expert-review packet for whenever an expert-validation reply lands (outreach sent
   2026-08-31, tracker: `outreach/EMAIL-TRACKER.md`): ask reviewers to (a) critique the task-2 checklist's
   claim/trigger decomposition for face validity and (b) independently give a holistic Accuracy/Harm score
   (per `scoring/RUBRIC.md`'s anchors) on the same ~20-item subset with no reference to the checklist, so
   checklist-derived and holistic scores can be compared for agreement. Depends on task 2 existing first;
   PRD's existing Sep 15-16 slot still applies if the reply lands on the expected Sep 7-14 window.
4. **[Day 9]** Build the scoring sheet and the blinding/shuffle script — strips model identity and
   shuffles response order so Days 13-15 scoring can be done blind (PRD §6 rule 4: human scoring primary).
   Records the task-2 checklist's per-claim and per-trigger results plus the catch-all note field per
   response, not a single holistic value (detail: DECISION-LOG.md, 2026-09-01 "Switched primary scoring
   method to a per-item checklist" entry).
5. **[Day 10]** Assemble per-species document bundles for Condition 2 (oracle grounding) from
   `data/ground_truth/*.yaml`, per PRD §3.
6. Decide the stack layout under `src/` (Python, dependency-managed via `uv` — see
   `.claude/rules/python.md`) and add the first `pyproject.toml` / test scaffold. Needed before task 7
   (the run harness) can be written — no longer deferrable now that runs are the next phase.
7. **[Day 10]** Write the run harness: executes both conditions across all 4 models at temperature 0, and
   **logs exact model version strings** (PRD §6 rule 5 — non-negotiable).
8. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4th model
   slot — PRD Day 10-11, needed before runs execute (task 9).
9. **[Days 11-12 — Gate Fri Sep 11]** Execute runs: Condition 1 first (all 4 models, 2 runs each), verify
   version-string logging; then Condition 2 (all 4 models, 2 runs each), spot-check outputs for
   truncation or refusal loops. Gate: all model responses collected by Fri Sep 11 — if behind, drop
   Condition 2 before dropping scoring time (PRD §10 dated gates).
10. **[Days 13-15 — Gate Mon Sep 14]** Score all ~320 responses blind (shuffled, identity-stripped, per
   task 4's script and the task-2 checklist): ~105 (Day 13), ~105 (Day 14), finish the remaining ~110
   (Day 15). Gate: scoring complete by Mon Sep 14 — if behind, drop Model 4 entirely (3 models still
   support every analysis per PRD §7).
11. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
   sent (currently still shows "Not sent" for all real contacts). No dependency on anything above —
   pure housekeeping, lowest priority.

## Open bugs

_None yet._

## Pending tests

_None yet — no code to test._
