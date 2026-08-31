# Commit / review workflow

## Plan Mode is the default

For any non-trivial change: enter Plan Mode, read and draft the plan only, get the user's approval, then
implement. One approved plan = one scope = one commit. If something unrelated comes up mid-implementation,
don't fold it in — note it in `SCRATCHPAD.md` and raise it as a separate plan.

## Before committing: run the specialist reviewers in parallel

Use `/commit` (or invoke this manually) to spawn, concurrently, over the pending diff:

- **architecture reviewer** (`.claude/agents/reviewer-architecture.md`) — types, structure, reuse.
- **copy reviewer** (`.claude/agents/reviewer-copy.md`) — docs/strings/voice consistency, since this
  benchmark's output text and scenario copy is user (and grader)-facing.
- **investigator** (`.claude/agents/investigator.md`) — read-only root-cause pass. Run this one *before*
  writing a fix for any reported bug, not just before committing — patching a symptom without it is how
  "the same bug keeps coming back" starts.

Findings that cross domains (e.g. an architecture finding that's really a root-cause issue) escalate to a
second pass touching both reviewers. Findings clearly out of scope for a reviewer auto-skip rather than
getting force-fit into that reviewer's report.

## After the reviewers

Address findings, then commit. Write the `DECISION-LOG.md` entry (see `.claude/docs/decision-log.md`) for
anything non-trivial that came out of the review, and archive any `SCRATCHPAD.md` tasks the commit closes
(see `.claude/docs/scratchpad-discipline.md`).
