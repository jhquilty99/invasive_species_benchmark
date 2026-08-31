---
description: Run the parallel specialist reviewers over the pending diff, address findings, then commit.
allowed-tools: Bash(git:*), Agent, Read, Grep, Glob, Edit
---

Follow `.claude/docs/git-workflow.md`.

1. Run `git status` and `git diff` (staged + unstaged) to see what's pending. If there's nothing to
   commit, say so and stop.
2. Spawn these agents concurrently over the pending diff (one Agent call per reviewer, all in the same
   message so they run in parallel):
   - `reviewer-architecture` — types/structure/reuse findings.
   - `reviewer-copy` — docs/strings/scenario-copy findings.
   - `investigator` — only if there's a reported bug in scope of this diff; skip otherwise.
3. Collect findings. A finding that clearly crosses domains (e.g. an architecture finding that's really a
   root cause, or vice versa) gets a second pass from the other relevant reviewer before you act on it. A
   finding that's out of scope for its reviewer's lane is dropped, not force-fit into a report.
4. Address the findings that hold up. Don't fold in unrelated cleanup while you're at it — if you spot
   something else worth doing, add it to `SCRATCHPAD.md` instead.
5. Write a `DECISION-LOG.md` entry (per `.claude/docs/decision-log.md`) if anything non-trivial came out
   of the review.
6. If this commit closes any `SCRATCHPAD.md` task, archive it now per `.claude/docs/scratchpad-discipline.md`
   — append the one-line entry, and remove the task's detail block from `SCRATCHPAD.md` as part of this
   same commit.
7. Stage and commit. Confirm the commit message with the user before running `git commit` unless they've
   already approved the exact message.
