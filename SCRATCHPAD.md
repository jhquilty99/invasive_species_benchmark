# Scratchpad — active

Open work only. A task lives here from creation until it closes. The instant it closes: append its
one-line entry to `SCRATCHPAD-ARCHIVE.md`, then remove its block from this file (the removal rides with
the commit that finished the work — see `.claude/docs/scratchpad-discipline.md`).

This file is a tracker, not memory. Durable facts/preferences/decisions do not belong here — they belong
in a rule file or `DECISION-LOG.md`.

## Status

- **Repo state:** `SCOPE.md` committed, locking PRD §2. Week 1 (corpus + item construction, PRD §4) is
  the active phase. No corpus grid or items exist yet.
- **Deadline confirmed:** earliest grad application is UC Berkeley MIDS, **Oct 23, 2026** — well past
  the Sep 20 ship date, so the 3-week schedule keeps its full buffer. No replanning needed.
- **Last touched:** 2026-08-31

## Open tasks (ranked)

1. **[Day 1]** Send the expert-validation email — draft in `outreach/expert-validation-email.md`,
   candidates and deadline tracked in `outreach/EMAIL-TRACKER.md`. Log send/reply status there as it
   happens.
2. **[Day 1]** Confirm API budget/access: ~960 calls (60 items × 2 conditions × 4 models × 2 runs).
3. Define the benchmark dataset/scenario file format (species, category, query text, ground-truth
   answer, citation, publication date, jurisdiction) — blocks the corpus grid below.
4. **[Days 2-4]** Build the ground-truth corpus: a 6 species × 8 category grid, each cell holding the
   defensible answer + citation + publication date. See PRD §4 Days 2-4 for source priority order and
   species pairing: *Ailanthus altissima* + *Ligustrum sinense* (Day 2), *Microstegium vimineum* +
   *Pyrus calleryana* (Day 3), *Phragmites australis* ssp. *australis* + *Wisteria sinensis* + NCDA
   restricted-use pull (Day 4).
5. **[Gate — Fri Sep 4]** Grid-complete check: if the corpus grid isn't done, cut to 4 species that
   same day (pre-authorized cut — do not borrow time from Week 3 instead); also fill in the
   label-derived legality cells (PRD §10 Day 5).
6. **[Days 6-7]** Write the 60 benchmark items as realistic layperson queries (not exam phrasing): 40
   answerable items across the 6 categories plus 20 abstention items. See PRD §4 Days 5-7 for the
   per-category counts and abstention criteria.
7. **[Gate — Sun Sep 6]** Review all 60 items against ground truth and **freeze the benchmark** — tag
   the commit. No item changes after this point for any reason.
8. Decide the stack layout under `src/` (Python, dependency-managed via `uv` — see
   `.claude/rules/python.md`) and add the first `pyproject.toml` / test scaffold. *(Week 2 work — not
   needed until runs start.)*
9. Draft the accuracy/harm scoring rubric with anchor examples for every level (PRD §4 Days 8-9).
   *(Week 2 work.)*

## Open bugs

_None yet._

## Pending tests

_None yet — no code to test._
