# Scratchpad discipline

Two different jobs live near each other here — don't mash them:

- **Memory** (rule files, `DECISION-LOG.md`) holds durable facts: preferences, conventions, lessons
  that are always true.
- **The tracker** (`SCRATCHPAD.md` + `SCRATCHPAD-ARCHIVE.md`) holds open work: things that need doing,
  then stop being relevant.

If something feels like it's "falling through the cracks," that's almost always a tracker problem
(missing exit trigger), not a memory problem. Don't reach for "add more memory" to fix it.

## The exit path (this is the part that rots if skipped)

A task closing has two steps, and they happen at different times:

1. **The instant a task closes** — append its one-line entry to `SCRATCHPAD-ARCHIVE.md` immediately.
   This is cheap (one line) and has zero reason to be deferred. Do it before moving to the next thing.
2. **When the commit for that work happens** — remove the task's full detail block from the active
   `SCRATCHPAD.md`. This rides with the commit, not with step 1.

Never let step 1 wait for step 2. A task marked done in conversation but not yet archived is exactly the
failure mode this file exists to prevent.

## The audit (catches drift when step 1 gets skipped anyway)

The scratchpad audit hook cross-references `git log` against tasks in `SCRATCHPAD.md` that look done but
aren't archived, and flags anything overdue. If it flags something, archive it immediately rather than
batching — a bulk cleanup of 15+ stale entries is the exact symptom this system is designed to prevent.

## Ranking

Keep `SCRATCHPAD.md`'s open task list ranked by priority, not by creation order. Re-rank when priorities
change instead of leaving a stale order.

## Scoped trackers outside SCRATCHPAD.md

`outreach/EMAIL-TRACKER.md` is a deliberate, narrow exception to "the tracker is `SCRATCHPAD.md`": it
logs per-contact send/reply state for external correspondence, which is a different shape of data (a row
per recipient, not a row per task) than the ranked task list is built for. It is **not** covered by
`.claude/hooks/scratchpad-audit.sh`, which only cross-references `git log` against `SCRATCHPAD.md` — so
its rows won't be flagged if they go stale. Keep `SCRATCHPAD.md` holding the pointer to it (one line: send
the email, log status there) rather than restating candidate/deadline detail in both places. Don't add a
third tracker like this without either teaching the audit hook about it or accepting the same blind spot.
