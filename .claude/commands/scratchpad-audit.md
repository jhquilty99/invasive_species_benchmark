---
description: Cross-reference git log against SCRATCHPAD.md's open tasks and flag anything overdue to archive.
allowed-tools: Bash(bash .claude/hooks/scratchpad-audit.sh), Read, Edit
---

Run `.claude/hooks/scratchpad-audit.sh` (this is the same check that runs automatically at session start)
and report what it flags.

For anything flagged as overdue: confirm with the user (or infer confidently from the commit itself) that
the task is actually done, then immediately append its one-line entry to `SCRATCHPAD-ARCHIVE.md` and remove
its detail block from `SCRATCHPAD.md`, per `.claude/docs/scratchpad-discipline.md`. Don't batch multiple
flagged items into a single sweep without archiving each — that's the exact drift this command exists to
catch.

If nothing is flagged, say so plainly.
