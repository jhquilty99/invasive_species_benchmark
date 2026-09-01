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

## 2026-08-31 — API access confirmed; 4-model line-up locks OpenAI + Anthropic + Google + one open-weight model

**Decision:** Confirmed active API access (keys + billing) for OpenAI, Anthropic (Claude), and Google
(Gemini). The 4th model slot required by PRD §4 ("4 models spanning capability tiers and providers;
include one small open-weight model") will be a small open-weight model served through a third-party
inference host (e.g. Together.ai, Groq, Fireworks) or run locally — exact host and model deferred to the
Day 10-11 model-selection step in PRD §4/§10, where exact version strings get logged per the PRD's
"non-negotiable" rule.
**Rationale:** Confirming provider-level access answers PRD §4 Day 1's "Confirm API budget" task now,
without forcing a premature pick of the specific open-weight model before the run harness exists. Total
call volume (~960 calls across 4 models × 2 conditions × 60 items × 2 runs) is small enough that
per-token cost across any of these hosts is not a budget risk regardless of which one gets picked.
**Trade-offs:** Did NOT lock the specific open-weight model or host today — that stays open, but is
covered by PRD's existing Day 10-11 schedule rather than a new `SCRATCHPAD.md` item. Did NOT drop the
open-weight requirement (one option considered and rejected): PRD §2/§4 locks it explicitly, and "no
scope growth" (PRD §6 rule 2) cuts both ways — dropping a locked requirement isn't an authorized cut.
**Rule Updated:** N — not a recurring pattern yet.
**Status:** Active

## 2026-08-31 — Benchmark dataset/scenario file format

**Decision:** Two separate file formats: (1) the ground-truth corpus as one YAML file per species under
`data/ground_truth/`, each holding every category cell for that species (answer + citation + publication
date + jurisdiction range flag); (2) benchmark items as a single JSON Lines file `data/items.jsonl`, one
JSON object per item, referencing the relevant ground-truth cell(s) for Condition 2 (oracle) grounding.
See `data/SCHEMA.md` for the full field definitions and worked examples.
**Rationale:** YAML per species keeps ground-truth cells human-readable and easy to hand-write/edit
during Days 2-4 corpus construction — long-form prose answers with citations read better than JSON. JSONL
for items keeps the frozen 60-item set append-only and diff-friendly, and is a natural input format for a
scripted run harness later (Week 2) without committing to a database or ORM prematurely.
**Trade-offs:** Did NOT design the run-harness or scoring-sheet format yet — that's Week 2 work
(`SCRATCHPAD.md`: stack layout, rubric). Did NOT unify ground-truth and items into one file — kept
separate because the ground-truth grid is the source of truth items get checked against, and collapsing
them would make "did an item's ground truth change after freeze" harder to audit. Did NOT resolve PRD
§4's "6 × 8 grid" language against its own 6-category item table before writing this schema — `SCHEMA.md`
assumes 6 categories per species (matching the item table's counts) and flags the discrepancy inline for
whoever starts the Days 2-4 corpus, rather than silently picking a number that changes how many
ground-truth cells get written per species.
**Rule Updated:** N — flag for retro if a second data-format decision comes up before code exists (would
suggest a `.claude/rules/data-format.md` is worth creating instead of one-off decisions).
**Status:** Active

## 2026-08-31 — Ground-truth corpus built; closes the 6-vs-8-category open question

**Decision:** Wrote all six `data/ground_truth/<species-slug>.yaml` files (Ailanthus altissima, Ligustrum
sinense, Microstegium vimineum, Pyrus calleryana, Phragmites australis ssp. australis, Wisteria sinensis),
each with exactly 6 cells, closing `data/SCHEMA.md`'s open question in favor of **6 categories per species**
(matching the item-writing table's per-category counts, not the PRD's "6×8" prose). Every cell's citation
was WebFetch-verified against the actual source (not a search snippet) before being written; homeowner-
legal herbicide products were independently confirmed against EPA labels or EPA's product database.
**Rationale:** The 6-category reading is the only one the frozen item table (40 answerable items across
6 named categories) actually sums against; treating "6×8" as a typo in the PRD prose rather than a real
8th category avoids inventing a category with no corresponding items downstream.
**Trade-offs:** Zero `jurisdiction_range.flagged: true` cells across all 36 — every category where multiple
states were checked (NC/SC/GA/AL sources) showed consistent guidance, so PRD §4's "record and flag
cross-state disagreement" mechanism exists but wasn't triggered this pass. Did NOT attempt a second-source
cross-check on every cell (would have doubled research time for marginal benefit); relied on picking the
single best-fit source per PRD's priority order and fetching it directly instead.
**Process note (flag for `/retro`):** Building this surfaced two subagent-tooling issues worth a pattern
check if they recur: (1) launching a `fork`-type subagent from inside a `fork` subagent is rejected
("Fork is not available inside a forked worker") — not obvious from the tool description, and the first
symptom was the *fork itself* behaving as if it were the parent coordinator (spawning further agents,
reviewing other agents' output) rather than doing its own assigned research, which took an explicit
coordinator interjection to catch and correct; (2) this cost real rework — the fork's assigned species pair
(Ailanthus, Ligustrum) went undone until caught. If a second incident like this shows up, worth a rule
about verifying a forked/subagent's actual file output rather than trusting its self-report before
considering that portion of a delegated task done.
**Rule Updated:** N — flag for retro (see process note above).
**Status:** Active

## 2026-08-31 — Fixes from `/commit` review of the ground-truth corpus

**Decision:** Acting on the architecture and copy reviewers' findings over the corpus diff: normalized
`phragmites-australis.yaml` and `wisteria-sinensis.yaml` (the two files that diverged stylistically from
the other four, per the copy reviewer) from second-person ("you," "your own property") to the same
third-person "a North Carolina landowner... themselves" construction used throughout the other four
files, in both `herbicide_legality` cells and one `method_selection` opening line; removed the blank
lines between `cells:` entries in those same two files to match the other four's formatting; updated
`data/SCHEMA.md` to actually resolve its own "6 vs 8 categories" open question (it previously still read
as unresolved even though this session's earlier decision-log entry claimed to close it) rather than
leaving a stale note in the file that's supposed to be the self-contained spec; fixed a broken
`DECISION-LOG.md#<anchor>` link in `SCRATCHPAD.md`/`SCRATCHPAD-ARCHIVE.md` that didn't match how markdown
actually slugifies the heading, switching both to the plain-text reference style every prior archive entry
already uses; and added a `SCRATCHPAD-ARCHIVE.md` line for the Fri Sep 4 "grid-complete gate" task, which
this session's edits had silently dropped from `SCRATCHPAD.md`'s task list with no archive trail — it's
now recorded as closed-moot (the corpus finished 4 days early, so the cut-to-4-species contingency never
triggered).
**Rationale:** All were concrete, verifiable findings, not judgment calls requiring new design — the kind
of thing this repo's own `.claude/docs/scratchpad-discipline.md` exists to prevent recurring.
**Trade-offs:** The reformatting script used to strip the blank lines had a bug that also deleted the
`cells:` key from both files (an `awk` one-liner that discarded a non-matching lookahead line instead of
printing it) — caught immediately by re-running the schema-conformance check that had passed before the
edit, not by manual inspection. Did NOT skip re-validating after every edit in this pass as a result; every
YAML edit in this corpus is now followed by the same conformance check, which is worth keeping as a rule
of thumb for future edits to these files rather than a one-off recovery.
**Rule Updated:** N — the "always re-validate generated YAML after any batch edit" habit is now demonstrated
twice in this session (see process note in the prior entry); flag for `/retro`.
**Status:** Active