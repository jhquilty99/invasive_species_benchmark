# Decision Log

Append-only. One entry per non-trivial decision. Never edit a past entry — append a new one that
supersedes it and link back. See `.claude/docs/decision-log.md` for when an entry is warranted and how
the retrospective (`/retro`) uses this file.

## Template

```markdown
## YYYY-MM-DD — <short title>

**Decision:** What was decided.
**Rationale:** Why this, not the alternatives considered.
**Trade-offs:** What I deliberately did NOT do, and why — stops re-litigating this later.
**Rule Updated:** Y/N — if Y, which rule file and what changed. If N but this feels like it could recur,
  flag it here for `/retro` to pick up.
**Status:** Active | Superseded by YYYY-MM-DD entry | Reverted.
```

## Entries

## 2026-08-31 — Skip the visual specialist reviewer for now

**Decision:** Set up three of the four specialist reviewers (architecture, copy/voice, root-cause
investigator) and omit the visual reviewer, rather than defining it unused.
**Rationale:** This repo is a benchmark harness with no UI — a visual reviewer has nothing to review yet,
and a defined-but-never-triggered agent is dead weight in `.claude/agents/`.
**Trade-offs:** Deliberately did NOT stub out a placeholder `reviewer-visual.md` "for later" — if a UI
ever gets built (e.g. a results dashboard), add it then, with real conventions to review against, instead
of guessing at them now.
**Rule Updated:** N — flag for retro. If this benchmark grows a UI, `/commit`'s reviewer list
(`.claude/docs/git-workflow.md`) should gain a fourth parallel reviewer at that point.
**Status:** Active.

## 2026-08-31 — Fixes from first `/commit` review of the scaffolding commit

**Decision:** Acting on the architecture and copy reviewers' findings over the initial scaffolding diff:
fixed a contradiction in `CLAUDE.md` about what `SCRATCHPAD-ARCHIVE.md` is for (it claimed the archive
holds the "why" behind closed tasks; the archive's own header and `DEVELOPMENT.md` both say that's
`DECISION-LOG.md`'s job — `CLAUDE.md` now agrees); added `PRODUCT_REQUIREMENTS.md` to `CLAUDE.md`'s and
`DEVELOPMENT.md`'s routing so it isn't an orphaned file; reworded `reviewer-copy.md` so it states the
no-comments-unless-non-obvious convention directly instead of citing it as an undocumented "repo default";
stripped `post-turn-check.sh`'s Node/Go/Rust detection down to Python-only, since this project is
single-stack; and untracked `.claude/settings.local.json` (added `.gitignore`) since its committed content
was one-off manual-testing permission entries, not an intentional shared policy.
**Rationale:** All four were concrete, verifiable findings from the parallel reviewers, not judgment calls
requiring new design — straightforward to fix in the same commit that introduced them.
**Trade-offs:** Deliberately did NOT add a general Python `.gitignore` (venv/`__pycache__`/etc.) in this
pass — that's real scope, not part of the settings.local.json finding, and belongs with the first
`pyproject.toml` (see `SCRATCHPAD.md` open task #2). Also did NOT add a cross-reference doc-sync mechanism
between `CLAUDE.md`'s "Enforcement" and `DEVELOPMENT.md`'s "What happens automatically" — added a one-line
pointer instead of solving the general two-copies-of-the-same-fact problem.
**Rule Updated:** N — flag for retro. Two commits in a row have now needed a "keep docs about the same
system in sync" fix (this one, plus the original archive/CLAUDE.md mismatch found in the same review) —
if a third instance shows up, it's worth a rule about single-sourcing cross-file descriptions.
**Status:** Active.

## 2026-08-31 — Selected LLM advice-quality benchmark as pre-application research project

**Decision:** Build a benchmark measuring LLM accuracy and harm on invasive plant management advice, targeting a preprint before graduate application deadlines. Selected from six candidates surfaced during problem-space brainstorming.

**Rationale:** Pesticide labels are legally binding under FIFRA, so "the model was wrong" is externally adjudicable — rare among high-stakes advice domains, where expert disagreement muddies every benchmark. That property makes a small study defensible, and choosing a domain *for that reason* is the part that signals research judgment. It also scores highest on LLM-work showcase: the object of study is model behavior, not a dataset the model happened to help produce.

**Trade-offs:**
- **Retail nativar labeling audit** rejected: needs a spring sampling season; a single fall snapshot is the weak version reviewers would object to.
- **Lepidoptera-host extraction dataset** rejected despite being the better long-term play — it compounds, produces open infrastructure, and naturally earns a collaborator. Roughly 3 months, and the LLM work is instrumental rather than the contribution. Revisit after this ships.
- **Plant-ID hard-case benchmark** rejected: computer vision, not LLM work.
- **Nursery availability gap / deer-list disagreement / nectar dearth mapping** rejected: light or no model involvement.
- **Accepting no compounding asset.** This publishes and stops. Chosen because the deadline is fixed and a shipped artifact beats a better project that misses.

**Rule Updated:** N — flag for `/retro`: when a deadline is fixed, rank candidates by ship probability before ranking by value. The two highest-value options here were both unshippable in the window, and I nearly anchored on one.

**Status:** Active

## 2026-08-31 — Replaced retrieval system with oracle grounding as Condition 2

**Decision:** Instead of building a hybrid BM25 + dense retriever over the ground-truth corpus, place the correct source documents directly in context for the grounded condition.

**Rationale:** With six species the corpus is hand-assemblable per species, so a retriever adds engineering cost and a confound without adding a claim I want to make. Oracle grounding answers a cleaner question: it measures the **upper bound** on what retrieval can fix. If harm persists when the model has been handed the right documents, no retrieval engineering closes that gap — which is a stronger and more durable result than benchmarking one retriever I'd have built under time pressure. Saves ~10 hrs.

**Trade-offs:**
- **Cannot claim anything about RAG engineering** — no statement about chunking, reranking, or retrieval quality. Accepted; that was never the contribution.
- **Loses realism.** Real systems retrieve imperfectly, so the grounded condition is optimistic relative to any deployed tool. This cuts the right direction: it makes residual harm a floor, not an artifact of bad retrieval.
- Must be stated explicitly in methods as a design choice, not a shortcut, or a reviewer reads it as one.

**Rule Updated:** N — flag for `/retro`: when a component is a confound rather than a contribution, check whether the idealized version answers a better question before building the realistic one.

**Status:** Active

## 2026-08-31 — Compressed to 3 weeks; deferred commercial product audit

**Decision:** Ship Study A alone by 2026-09-20 — 6 species, ~60 items, 4 models, 2 conditions, 1 scored run. Study B (audit of commercial AI gardening products) deferred to a standalone follow-up.

**Rationale:** The hybrid design was stronger as a paper — foundation-model hallucination and product-layer criterion omission are structurally different failures at two layers of one stack, and Study B answered the "we already know models hallucinate" objection directly. But it required ToS review across six products, subscription budget, a second region (the two native-specific tools are Texas-focused), and manual-only collection. That's a week minimum with external dependencies I don't control. Study A alone is fully self-contained desk work.

**Trade-offs:**
- **Lost the most eye-catching finding.** A native-specific tool recommending a state-listed invasive would have carried the paper. Deferred rather than discarded — the category isn't going anywhere and this extends rather than requires rewriting.
- **Expert validation demoted to optional.** Email sent day 1 with a 2-hour ask; ships without a reply. Harm scoring becomes one person's judgment. This is the largest quality concession and belongs in limitations, not hidden.
- **Bare zero-shot condition dropped.** Can't isolate the persona-prompt effect. Kept the persona-prompted condition because it's more realistic and more favorable to the model, making failures more damning.
- **6 species / 60 items / 4 models.** Binding constraint is hand-scoring load (~480 responses ≈ 6 hrs), not corpus availability. Wider CIs accepted.
- **Preprint only, no journal submission.** Preprint is what matters for applications; submission can follow.

**Rule Updated:** N — two candidates for `/retro`:
1. *Phase-level effort estimates understate totals.* Phase view read ~45 hrs; the dated calendar surfaced ~59. Build the day-by-day before committing to a duration.
2. *Pre-authorize cuts at named dates.* "4 species on Sep 4, 3 models on Sep 14" converts two likely crises into scheduled decisions. Generalize to any deadline-bound work.

**Status:** Active

## 2026-08-31 — Standardize on uv for all Python installs/runs

**Decision:** Python interpreter installs and all Python execution (scripts, tools, tests) go
exclusively through astral's `uv` — never bare `pip`, `venv`, or `conda`.
**Rationale:** Closes the dependency-manager decision that `SCRATCHPAD.md` (open task #2) and this
log had both flagged as pending. `uv` manages its own pinned interpreter, which sidesteps this
machine's broken `python`/`python3` Windows Store stub aliases (documented in `.claude/hooks/lib.sh`).
It also produces a lockfile (`uv.lock`), consistent with the existing "`pyproject.toml`, not loose
`requirements.txt`" rule.
**Trade-offs:** Does NOT decide the `src/` stack layout or add the first `pyproject.toml` — that
stays open as `SCRATCHPAD.md` task #2. Does NOT rule out conda-only scientific/geo packages if one is
ever needed — revisit only if a hard conda-only dependency shows up.
**Rule Updated:** Y — `.claude/rules/python.md` now mandates `uv` for install/run.
**Status:** Active

## 2026-08-31 — Day 1 tasks: SCOPE.md, deadline confirmed, expert-outreach docs added

**Decision:** Committed `SCOPE.md` (PRD §2 locked scope), confirmed the earliest graduate application
deadline (UC Berkeley MIDS, Oct 23, 2026 — well past the Sep 20 ship date, no replanning needed), and
added `outreach/expert-validation-email.md` plus `outreach/EMAIL-TRACKER.md` as a separate, narrowly
scoped tracker for the three expert-validation contacts. `SCRATCHPAD.md` was re-ranked around the PRD's
dated Week 1 schedule and both closed tasks were archived.
**Rationale:** These were PRD §4/§10 Day 1 tasks. The email/tracker got their own files rather than
living inline in `SCRATCHPAD.md` because per-contact send/reply state is a different shape of data (one
row per recipient) than a ranked task list, and keeping the email template separate from its status log
means editing the pitch doesn't touch the tracking rows.
**Trade-offs:** The parallel reviewers over this diff also caught and fixed three issues in the same
commit: (1) `.claude/hooks/post-turn-check.sh`'s `uv` requirement silently skipped *all* checks when
`uv` was missing instead of failing loud — added an `else` branch so a missing toolchain manager reports
as a failure, not a silent pass; (2) `outreach/EMAIL-TRACKER.md` is invisible to
`.claude/hooks/scratchpad-audit.sh` (which only watches `SCRATCHPAD.md`) — documented this as a
deliberate, scoped exception in `.claude/docs/scratchpad-discipline.md` rather than silently accepting
the blind spot; (3) candidate/deadline detail was duplicated across `SCRATCHPAD.md` and both outreach
files — trimmed `SCRATCHPAD.md` task 1 down to a pointer. Did NOT teach `scratchpad-audit.sh` to also
read `outreach/EMAIL-TRACKER.md` — three rows don't justify the hook complexity; revisit if more
per-contact trackers like this get added.
**Rule Updated:** Y — `.claude/docs/scratchpad-discipline.md` now documents the `EMAIL-TRACKER.md`
exception and the rule that any future tracker like it needs the same explicit call-out.
**Status:** Active