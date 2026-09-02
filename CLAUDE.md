# invasive_species_benchmark — index

Benchmarking LLM management advice in a legally constrained domain (invasive species). This file is a
router, not documentation: ~60 lines of triggers pointing to leaf files. Read the leaf file only when
its condition matches — don't preload everything.

## Always true

- Plan Mode is the default workflow for any non-trivial change: read + write only to the plan file until
  the user approves, then implement. One plan = one scope = one commit. Don't fold unrelated fixes into
  an approved plan — start a new one.
- Every completed task gets a one-line entry appended to `SCRATCHPAD-ARCHIVE.md` **the moment it closes**
  — not batched later. See `.claude/docs/scratchpad-discipline.md`.
- Every non-trivial decision gets a `DECISION-LOG.md` entry using the fixed template. The `Rule Updated`
  field is load-bearing — if a decision reveals a pattern, update the rule file now or flag it for
  retrospective. See `.claude/docs/decision-log.md`.
- A durable fact (a preference, a project convention, a lesson that's always true) goes in a rule file or
  `DECISION-LOG.md`. Open work (something that needs doing, then stops mattering) goes in
  `SCRATCHPAD.md`. Don't put open work in memory, and don't let closed work linger in the active
  scratchpad — see `.claude/docs/scratchpad-discipline.md`.
- When cutting scope, defer rather than discard: keep the cut content in a form that's cheap to
  reintroduce later (a same-schema file, an unbuilt-but-documented component, a row in a "what was cut"
  table) instead of deleting it outright. Established practice — see the visual-reviewer omission, Study
  B, and the abstention-items removal in `DECISION-LOG.md`.

## Conditional triggers

| When you are... | Read |
|---|---|
| Writing or editing Python code | `.claude/rules/python.md` (auto-loads for `*.py`) |
| Writing or editing tests | `.claude/rules/testing.md` (auto-loads for test files) |
| Working with the benchmark's legal/domain source material | `.claude/rules/domain-legal.md` (auto-loads under `legal/`, `data/`, `scenarios/`) |
| About to commit, or asked to review changes | `.claude/docs/git-workflow.md` |
| Writing a `DECISION-LOG.md` entry | `.claude/docs/decision-log.md` |
| Updating `SCRATCHPAD.md` or `SCRATCHPAD-ARCHIVE.md` | `.claude/docs/scratchpad-discipline.md` |
| Understanding the benchmark's scope, goals, species list, or schedule | `PRODUCT_REQUIREMENTS.md` |

The three `.claude/rules/*.md` files above are path-scoped and load automatically when you touch a
matching file. The three `.claude/docs/*.md` files are situational, not path-scoped — read them yourself
when the situation in the left column applies; nothing loads them for you.

## Enforcement (hooks, not prompts)

These run regardless of what's in context — see `.claude/settings.json`:

- **Stop**: typecheck + test run after every turn; failures are handed back so the turn isn't done until
  they pass.
- **PreToolUse (Write/Edit)**: writes to secrets/signing/config files are refused by deny-list.
- **UserPromptSubmit**: current branch + working-tree status are attached automatically.
- **Scratchpad audit**: cross-references git log against tasks marked done-but-still-active and flags
  anything overdue to archive.

## Project state

Current status, ranked open tasks, and known issues live in `SCRATCHPAD.md`. Read it at the start of a
session. `SCRATCHPAD-ARCHIVE.md` is a one-line index of what's already closed — open it to see *what's*
done. For the *why* behind a closed task, see `DECISION-LOG.md` instead.
