# Developing on invasive_species_benchmark

This is a plain-language guide to working in this repo, whether you're a human contributor or Claude
Code. For the machine-facing rules and automation, see `CLAUDE.md` — this file is the human-readable
version of the same system.

## What this repo is

A benchmark for evaluating LLM-generated management advice in a legally constrained domain (invasive
species control), where advice has to hold up against real regulatory constraints, not just sound
plausible.

## Getting set up

There's no code yet beyond this scaffolding — `SCRATCHPAD.md` has the current open tasks. Once a
`pyproject.toml` exists (this project's stack is Python), the usual flow will be:

```
pip install -e ".[dev]"   # or your preferred env manager
pytest                     # run the test suite
ruff check .               # lint
mypy .                     # typecheck
```

## How the project stays legible

This repo uses a small set of files and automated checks so that context survives between sessions —
yours and Claude's. The short version:

| File / mechanism | Job |
|---|---|
| `CLAUDE.md` | Routes Claude to the right rule file for the situation — durable facts and conventions. |
| `SCRATCHPAD.md` | The active to-do list: open tasks, bugs, pending tests. **Open work only.** |
| `SCRATCHPAD-ARCHIVE.md` | One-line record of every finished task, written the moment it closes. |
| `DECISION-LOG.md` | One entry per non-trivial decision — what, why, and what was deliberately *not* done. |
| `PRODUCT_REQUIREMENTS.md` | The research plan: scope, species list, goals, and schedule. |
| `.claude/hooks/` | Automated checks that run on their own (see below) — not just suggestions. |
| `.claude/agents/` | Specialist reviewers you can run before a commit. |

The underlying idea: **durable facts go in rules/memory, open work goes in the tracker, and finished work
has to actually leave the tracker** — not pile up until someone does a big cleanup. If you notice tasks
sitting in `SCRATCHPAD.md` long after they're done, that's drift; archive them (see below) rather than
letting it accumulate.

## What happens automatically

You don't need to remember to do these — they're wired into Claude Code as hooks in `.claude/settings.json`
(same list as `CLAUDE.md`'s "Enforcement" section, in plain language):

- **After every turn**, a check runs typecheck/lint/tests on whatever changed and hands any failure
  straight back, so a broken change doesn't get left half-fixed.
- **Before any file write**, writes to `.env` files, keys, credentials, or `.claude/settings.json` itself
  are refused automatically.
- **At the start of every prompt**, the current git branch and working-tree status are attached
  automatically — no need to ask "what branch am I on."
- **At the start of every session**, a quick audit compares recent commits against `SCRATCHPAD.md` and
  flags anything that looks finished but hasn't been archived yet.

## How to contribute a change

1. **Plan first.** For anything beyond a trivial fix, Claude works in Plan Mode by default: it reads and
   drafts a plan, you approve it, then it implements. One approved plan = one scope = one commit — if
   something unrelated comes up, it goes on `SCRATCHPAD.md` as a separate item rather than getting folded in.
2. **Implement and let the automated checks run.** Failures get fixed before the turn is considered done.
3. **Review before committing.** Run `/commit` — it spawns a few focused reviewers (architecture/types,
   copy/voice, and a root-cause investigator when there's a bug in scope) in parallel over the pending
   diff, and folds their findings in before committing.
4. **Log the decision.** If the change involved a non-obvious choice (a library, a data format, a scope
   boundary), it gets a `DECISION-LOG.md` entry — what was decided, why, and what was deliberately *not*
   done. This is what keeps the same debate from happening again in a month.
5. **Close the loop on `SCRATCHPAD.md`.** The instant a task is done, its one-line entry goes into
   `SCRATCHPAD-ARCHIVE.md`. The task's full detail block gets removed from `SCRATCHPAD.md` as part of the
   commit that finishes it.

Run `/retro` occasionally (roughly weekly, or whenever `DECISION-LOG.md` feels like it's accumulating
similar entries) — it looks for anything that's come up 3+ times and proposes turning it into an explicit
rule, so the project gets easier to work in over time instead of just accumulating history.

## Adding a new kind of contributor guidance

If you find yourself explaining the same thing to Claude more than once, it probably belongs in a rule
file (`.claude/rules/` for something tied to a file type/path, `.claude/docs/` for something tied to a
situation like "about to commit") rather than repeated in conversation. See `CLAUDE.md`'s routing table
for where things currently live.
