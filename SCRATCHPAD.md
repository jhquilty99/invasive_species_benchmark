# Scratchpad — active

Open work only. A task lives here from creation until it closes. The instant it closes: append its
one-line entry to `SCRATCHPAD-ARCHIVE.md`, then remove its block from this file (the removal rides with
the commit that finished the work — see `.claude/docs/scratchpad-discipline.md`).

This file is a tracker, not memory. Durable facts/preferences/decisions do not belong here — they belong
in a rule file or `DECISION-LOG.md`.

## Status

- **Repo state:** `SCOPE.md` committed, locking PRD §2. `data/SCHEMA.md` defines the corpus/item file
  formats. Ground-truth corpus is built: `data/ground_truth/*.yaml`, 6 species × 6 categories, 0
  jurisdiction-range flags (detail: DECISION-LOG.md, 2026-08-31 "Ground-truth corpus built" entry). All 60
  benchmark items are written to `data/items.jsonl` — 40 answerable (8/8/6/8/6/4 across the 6 categories)
  + 20 abstention (5 per reason) — schema-checked, no drift found against a spot-check of the corpus
  (detail: DECISION-LOG.md, 2026-08-31 "60 benchmark items written" entry). Not yet reviewed/frozen — see
  task 1 below.
- **Deadline confirmed:** earliest grad application is UC Berkeley MIDS, **Oct 23, 2026** — well past
  the Sep 20 ship date, so the 3-week schedule keeps its full buffer. No replanning needed.
- **API access confirmed:** OpenAI, Anthropic, Google all active. 4th model will be a small open-weight
  model via a third-party host — exact model/host still TBD, deferred to PRD's Day 10-11 run setup.
- **Outreach:** expert-validation emails reported sent (see `outreach/EMAIL-TRACKER.md`) — that file's
  Status/Date-sent columns still need to be updated to match; not yet fixed.
- **Last touched:** 2026-08-31

## Open tasks (ranked)

1. **[Gate — Sun Sep 6]** Review all 60 items in `data/items.jsonl` against ground truth and **freeze the
   benchmark** — tag the commit. No item changes after this point for any reason. (The items are written
   and pass a schema-conformance check plus a spot-check for drift against the cited ground-truth cells —
   see DECISION-LOG.md 2026-08-31 "60 benchmark items written" — but that's not the same as the full
   freeze-gate review this task calls for.)
2. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
   sent (currently still shows "Not sent" for all real contacts).
3. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4th model
   slot — PRD Day 10-11, but can happen earlier if convenient.
4. Decide the stack layout under `src/` (Python, dependency-managed via `uv` — see
   `.claude/rules/python.md`) and add the first `pyproject.toml` / test scaffold. *(Week 2 work — not
   needed until runs start.)*
5. Draft the accuracy/harm scoring rubric with anchor examples for every level (PRD §4 Days 8-9).
   *(Week 2 work.)*

## Open bugs

_None yet._

## Pending tests

_None yet — no code to test._
