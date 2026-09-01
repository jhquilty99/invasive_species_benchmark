# Scratchpad — active

Open work only. A task lives here from creation until it closes. The instant it closes: append its
one-line entry to `SCRATCHPAD-ARCHIVE.md`, then remove its block from this file (the removal rides with
the commit that finished the work — see `.claude/docs/scratchpad-discipline.md`).

This file is a tracker, not memory. Durable facts/preferences/decisions do not belong here — they belong
in a rule file or `DECISION-LOG.md`.

## Status

- **Repo state:** `SCOPE.md` committed, locking PRD §2. `data/SCHEMA.md` defines the corpus/item file
  formats. Week 1 (corpus + item construction, PRD §4) is the active phase. No corpus grid or items
  exist yet.
- **Deadline confirmed:** earliest grad application is UC Berkeley MIDS, **Oct 23, 2026** — well past
  the Sep 20 ship date, so the 3-week schedule keeps its full buffer. No replanning needed.
- **API access confirmed:** OpenAI, Anthropic, Google all active. 4th model will be a small open-weight
  model via a third-party host — exact model/host still TBD, deferred to PRD's Day 10-11 run setup.
- **Outreach:** expert-validation emails reported sent (see `outreach/EMAIL-TRACKER.md`) — that file's
  Status/Date-sent columns still need to be updated to match; not yet fixed.
- **Last touched:** 2026-08-31

## Open tasks (ranked)

1. **[Days 2-4]** Build the ground-truth corpus: a 6 species × 6 category grid per `data/SCHEMA.md`
   (see its "open question" note — the PRD's "6×8" wording doesn't match the 6-category item table; this
   schema assumes 6 and flags it for confirmation before Day 2 starts if that's wrong). See PRD §4
   Days 2-4 for source priority order and species pairing: *Ailanthus altissima* + *Ligustrum sinense*
   (Day 2), *Microstegium vimineum* + *Pyrus calleryana* (Day 3), *Phragmites australis* ssp.
   *australis* + *Wisteria sinensis* + NCDA restricted-use pull (Day 4).
2. **[Gate — Fri Sep 4]** Grid-complete check: if the corpus grid isn't done, cut to 4 species that
   same day (pre-authorized cut — do not borrow time from Week 3 instead); also fill in the
   label-derived legality cells (PRD §10 Day 5).
3. **[Days 6-7]** Write the 60 benchmark items into `data/items.jsonl` per `data/SCHEMA.md`, as
   realistic layperson queries (not exam phrasing): 40 answerable items across the 6 categories plus 20
   abstention items. See PRD §4 Days 5-7 for the per-category counts and abstention criteria.
4. **[Gate — Sun Sep 6]** Review all 60 items against ground truth and **freeze the benchmark** — tag
   the commit. No item changes after this point for any reason.
5. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
   sent (currently still shows "Not sent" for all real contacts).
6. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4th model
   slot — PRD Day 10-11, but can happen earlier if convenient.
7. Decide the stack layout under `src/` (Python, dependency-managed via `uv` — see
   `.claude/rules/python.md`) and add the first `pyproject.toml` / test scaffold. *(Week 2 work — not
   needed until runs start.)*
8. Draft the accuracy/harm scoring rubric with anchor examples for every level (PRD §4 Days 8-9).
   *(Week 2 work.)*

## Open bugs

_None yet._

## Pending tests

_None yet — no code to test._
