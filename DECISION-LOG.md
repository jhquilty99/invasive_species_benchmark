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

## 2026-08-31 — 60 benchmark items written to `data/items.jsonl`

**Decision:** Wrote all 60 items directly (not delegated to subagents, unlike the ground-truth corpus)
against the six ground-truth files already read in full this session. Allocated the 40 answerable items
across species and category as: Ailanthus 7 (2 method, 2 resprout), Phragmites 7 (2 method, 2 herblegal),
Pyrus 7 (2 resprout), Microstegium 7 (2 herblegal), Ligustrum 6, Wisteria 6 — every species gets 1 item per
category as a base, with the extra items going to whichever species/category combo is richest or most
central to that species' named failure archetype, and `disposal_nontarget_risk` (only 4 of 40 slots)
dropped for Ailanthus and Phragmites to keep per-species totals balanced (6-7 each) after they picked up
two extras elsewhere. Split the 20 abstention items 5 per `abstention_reason`: the 15 tied to a locked
species (site_assessment_required, unstated_variable, illegal_rate_for_layperson) spread across all 6
species (3, 3, 2, 2, 2, 3), item_id using the real species code; the 5 `outside_region` items use real
invasives that are genuinely not a documented NC coastal-plain problem (Scotch broom, giant hogweed, yellow
starthistle, saltcedar, leafy spurge) rather than species picked arbitrarily, `species: null` and
`condition_2_documents: []` per `SCHEMA.md`.
**Rationale:** Writing directly (not via forks) avoided the concurrent-shared-file-write hazard forking
would have introduced (all 60 items live in one file, unlike the corpus's one-file-per-species split) and
needed no new research — every fact used is already verified in the ground-truth cells read into context
this session. Balancing per-species item totals (rather than letting the 8/8/6/8/6/4 category skew produce
an uneven species distribution) avoids the benchmark looking like it's testing some species more than
others by accident of category arithmetic. `outside_region` species were chosen for genuine regional
mismatch (not just "any 6th species") so the abstention criterion is actually testing something real: a
model confidently giving NC-specific rate/legality guidance for one of these would be inventing region-
specific facts no source in the corpus supports.
**Trade-offs:** Did NOT run the formal Sun Sep 6 freeze-gate review as part of this task — ran a lighter
schema-conformance check (all 60 lines parse, no duplicate `item_id`s, category/reason counts match,
`is_abstention`/`abstention_reason` consistency, every `condition_2_documents` path resolves to a real
ground-truth cell) plus a spot-check of 2 items against their cited cells for drift, but that's not the
same review PRD §4's freeze gate calls for — left as `SCRATCHPAD.md` task 1, unstarted. Did NOT include a
`ground_truth_citation` for the 5 `outside_region` abstention items (set to `null`) since no corpus source
exists for a species outside the locked 6 — consistent with their empty `condition_2_documents`.
**Rule Updated:** N — not clearly a recurring pattern yet.
**Status:** Active

## 2026-08-31 — Fixes from `/commit` review of the 60 benchmark items

**Decision:** Acting on the architecture and copy reviewers' findings over the `items.jsonl` diff:
documented in `data/SCHEMA.md` that the 5 `outside_region` item_ids intentionally collapse to the
2-segment `ABST-<NN>` form rather than the schema-literal 3-segment `<SPECIES-CODE>-<CATEGORY-CODE>-<NN>`
(was previously undocumented — the schema only said species-less items "use `ABST`" without specifying
whether that replaces one segment or two); documented that `ground_truth_citation` is `null` for those
same 5 items, for the same reason `condition_2_documents` is `[]` (no corpus source exists outside the
locked 6 species); fixed a stale `SCRATCHPAD.md` task-number cross-reference in `SCHEMA.md` (said "task
4," should say "task 1" after this session's earlier renumbering); and scrubbed second-person "you/your"
phrasing from 11 of the 40 answerable items' `ground_truth_answer` strings, which had drifted from the
third-person convention every ground-truth corpus file and all 20 abstention items already follow — the
same issue class already caught and fixed once this session in the ground-truth corpus itself.
**Rationale:** All four were concrete findings, not judgment calls — two were undocumented but intentional
data shapes that just needed the schema to say so explicitly (SCHEMA.md is meant to be the self-contained
spec per its own description), one was a cross-reference left stale by this session's own SCRATCHPAD.md
edit, and the voice drift was a straightforward reapplication of a convention this project already chose.
**Trade-offs:** Did not standardize on 3-segment `ABST-ABST-<NN>` for `outside_region` items instead of
documenting the 2-segment exception — `ABST-ABST-01` reads as more redundant than clarifying, and nothing
downstream parses `item_id` yet, so there's no compatibility cost either way; can revisit if a future
run-harness's `item_id` parser finds the 2-segment shape awkward.
**Rule Updated:** N — the "voice-convention drift recurs across independently-written files" pattern has
now shown up twice in one session (ground-truth corpus, then items.jsonl); if it recurs a third time,
worth stating the third-person convention explicitly in `data/SCHEMA.md` itself rather than relying on
reviewers to catch it each time. Flag for `/retro`.
**Status:** Active

## 2026-09-01 — Scoring rubric conventions locked

**Decision:** Wrote `scoring/RUBRIC.md` (PRD §4 Days 8-9) with worked anchor examples for every Accuracy
(0-3) and Harm (H0-H4) level, abstention scoring rules, and operational definitions for the four
per-response fields. Locked two conventions the PRD left open: **Accuracy polarity is 3 = best** (3 =
fully correct and complete, 0 = incorrect — PRD §4's prose lists the labels without pinning a direction);
and the rubric document lives at **`scoring/RUBRIC.md`**, a new top-level `scoring/` directory sibling to
`data/`. Also fixed a scoring-methodology rule not specified anywhere: when a model answers an abstention
item instead of declining, Harm is capped at H2 even if the content given is substantively correct, since
giving specific guidance where abstention was the correct behavior is itself the harm this item category
tests — content accuracy and behavioral harm are scored as separate failures. Confirmed with the user
before writing (accuracy polarity, file location) since both are arbitrary conventions with load-bearing
effects on every later accuracy figure/chart and on where task 3 builds the scoring sheet.
**Rationale:** All anchors are hand-authored, not drawn from real model output, since runs (Days 11-12)
happen after this task — PRD §4 requires anchors to exist *before* any scoring, so there's nothing else to
ground them in yet. Anchors were built directly against real corpus cells (`data/ground_truth/
wisteria-sinensis.yaml`) rather than invented scenarios, so a scorer can immediately cross-check an anchor
against the actual ground-truth prose it's calibrated to. `scoring/` (not `docs/` or repo root) groups this
file with task 3's scoring sheet and blinding script, which will need the same home.
**Trade-offs:** Did NOT wait for real model responses to write anchors — accepted the risk that some
anchors may need revision once Days 13-15 scoring surfaces a real response shape the anchors didn't
anticipate; if that happens, append a new entry rather than editing this one or the anchors silently.
Did NOT resolve the "5 abstention reasons" phrasing in `SCRATCHPAD.md` task 2 as a real discrepancy — it
meant 5 items per reason across 4 reasons (`data/SCHEMA.md`'s enum), not 5 distinct reasons; no data
changed, just restated correctly in the rubric.
**Rule Updated:** N — flag for retro (a single scoring-convention decision, not yet a recurring pattern).
**Status:** Active

## 2026-09-01 — Switched primary scoring method to a per-item checklist; holistic scale demoted to expert side-check

**Decision:** Scoring will primarily use a per-item checklist rather than the holistic Accuracy
(0-3) / Harm (H0-H4) scales alone. For each of the 60 items, decompose the relevant ground-truth
cell(s) into atomic claims (weighted critical vs. standard) and predefined harm-trigger conditions,
each scored present/absent/contradicted, plus a free-text catch-all flag for wrong content the
checklist didn't anticipate. The holistic scale from `scoring/RUBRIC.md` is not discarded — it's
folded into the existing 20-item expert-validation ask (PRD §2) as a convergent-validity side-check:
experts will (a) critique the checklist's claim/trigger decomposition for face validity and (b)
independently give a holistic score on the same items with no reference to the checklist, so the two
methods can be compared for agreement.
**Rationale:** Checklist scoring against pre-written atomic claims gives a much higher inter-rater
reliability ceiling than holistic severity judgment calls (is this omission "material," is this H2 or
H3), which is exactly where two scorers — or the human vs. LLM secondary scorer — are most likely to
diverge. It's also more auditable (every score traces to a specific ground-truth sentence rather than
a bare "Accuracy: 2"), and aggregating which claims/triggers fail across items produces most of the
Analysis 4 failure taxonomy (PRD §10) as a byproduct instead of a separate qualitative clustering
pass.
**Trade-offs:** Authoring ~450-650 checklist rows across 60 items (roughly 6-8 claims + 3-5 harm
triggers per item) is real time not currently budgeted against the Days 8-9 rubric slot in PRD §10 —
left open as an unresolved scheduling question rather than assumed to fit. A checklist only catches
wrongness it anticipated; the catch-all flag exists specifically to avoid silently missing a novel
failure mode, and reintroduces a sliver of holistic judgment by design. The critical/standard claim
weighting is itself a subjective design choice — this decision doesn't eliminate that subjectivity,
it moves it earlier (into a frozen, auditable artifact) rather than removing it. Did NOT edit the
existing 2026-09-01 "Scoring rubric conventions locked" entry above — that entry's conventions
(accuracy polarity, H0-H4 definitions, abstention capping rules) still stand as the holistic layer;
this decision extends rather than reverses it, so no `Superseded` status on that entry.
**Rule Updated:** N — flag for retro (one-off scoring-methodology decision, not yet a recurring
pattern).
**Status:** Active

## 2026-09-01 — Replaced the Phragmites NC-IPC citation with NC Forest Service Invasive Species Alert No. 6

**Decision:** Reviewed every `ground_truth_citation` in `data/items.jsonl` and its matching
`data/ground_truth/*.yaml` cell for staleness or source/URL mismatch. Found one genuine problem out of
~20 unique sources: the Phragmites `method_selection` and `followup_secondary_invasion` cells (and items
PHRA-METHOD-01, PHRA-METHOD-02, PHRA-FOLLOWUP-01) cited "NC Invasive Plant Council... Fact Sheet" at
`nc-ipc.weebly.com`, a domain whose own homepage now reads "OLD WEBSITE OF NC INVASIVE PLANT COUNCIL" and
redirects elsewhere — the org itself has deprecated that hosting. Replaced with NC Forest Service (NCDA&CS)
Invasive Species Alert No. 6, "Phragmites australis (Common Reed)" (March 2010,
`https://www.ncagr.gov/divisions/nc-forest-service/is06/download?attachment=`), a live NC state-agency
document verified (via search-indexed content, since WebFetch cannot parse this PDF's compressed text
stream) to cover the same claims the cells actually rely on: mechanical control alone being ineffective,
foliar imazapyr/glyphosate as the effective treatment, and multi-year retreatment being necessary.
**Rationale:** Every other pre-2020 citation in the corpus (GARLON 3A 2016, Compare-N-Save 2019, Harrington
& Miller 2005, Redwood et al. 2019, USFS FEIS/Gucker 2008) was checked and confirmed to be either the
actual most-recent official document (pesticide labels don't get reissued on a schedule — 2016/2019 *is*
current for those EPA registrations) or an accurately-dated research paper, so age alone wasn't disqualifying
— that's consistent with `.claude/rules/domain-legal.md`'s "note the date a rule was current as of" rather
than "sources must be recent." The NC-IPC case is different in kind: the *hosting itself* is stale, not just
the date, which is what actually makes it unfit to keep citing as a live reference.
**Trade-offs:** Did NOT touch the two Phragmites cells' prose (the ligule-width/leaf-sheath ID sentence in
`method_selection` isn't covered by the NC Forest Service alert) — swapping the citation without rewriting
the answer is a source-hygiene fix, not the legal-framing correction `.claude/rules/domain-legal.md` gates
behind more scrutiny; the ID claim itself is well-established science (Saltonstall's genetic/morphological
work, reproduced across every derivative Phragmites ID resource found during this review) and isn't being
asserted as sourced solely to the replaced citation. Did NOT replace the Greenbook AquaMaster citation
despite an initial suspicion of a date/URL mismatch — a web search corroborated a real ~09/25/2020 label
revision close to the cited 2020-10-01 date, so left it as-is rather than "fixing" something that wasn't
actually broken. Did NOT re-verify the 34 non-Phragmites citations' actual PDF *content* byte-for-byte —
WebFetch cannot parse most of this corpus's compressed-stream PDFs (confirmed repeatedly this session), so
verification for those relied on EPA PPLS registration-history lookups and search-indexed bibliographic
matches rather than full-text extraction.
**Rule Updated:** N — flag for retro: this is the second time in this project that a citation review
surfaced a problem invisible to the original authoring pass because the source's *live-ness* degraded after
being cited, not because the fact was wrong when written. If a third instance shows up, worth adding a
"prefer a stable institutional host (.gov/.edu) over a small-org site (weebly, wix, etc.) when both exist"
guideline to `.claude/rules/domain-legal.md`.
**Status:** Active

## 2026-09-01 — Rebuilt all 6 ground-truth files with verbatim-quoted claims; declined full-page archive and PRD §9 reversal

**Decision:** Rewrote every cell across all 6 `data/ground_truth/*.yaml` files so concrete claims (rates,
legal thresholds, EPA reg. numbers, specific numbers/timing windows, defining sentences) are direct quotes
in quotation marks copied exactly from the cited source, replacing the prior paraphrase-style prose. Done
via 3 parallel research subagents (2 species each), each re-fetching every cited source and re-verifying
the claim against the actual page text rather than trusting the existing citation. User separately asked
for (a) a full verbatim archive of entire source pages, and (b) reversing PRD §9's mitigation ("publish
the extracted fact grid, not source PDFs") to plan on publishing that archive. Declined both: several
sources are university-extension or manufacturer-copyrighted (Clemson/NC State/UGA/Alabama Extension,
Greenbook/CDMS/ferti-lome pesticide labels) and bulk-reproducing whole documents isn't appropriate
regardless of instruction, especially with stated intent to publish. PRD §9's mitigation stands unchanged.
Quoting depth was tiered by copyright status: federal/public-domain sources (USFS FEIS, USDA Treesearch,
EPA/label text on epa.gov, NCDA&CS as a NC state-agency publication) were quoted at whatever length stated
a fact completely; university-extension and manufacturer-copyrighted sources were quoted only in the
specific sentence(s) needed per claim.
**Rationale:** Paraphrase in a ground-truth file that doubles as Condition-2 oracle-grounding text risks
the ground truth itself drifting from what the source actually says — exactly the failure mode this
benchmark is designed to catch in *models*. Verbatim quoting removes that risk for the corpus itself.
Re-fetching and re-verifying (rather than reusing the existing citations blind) surfaced several errors in
the original paraphrase pass, now corrected: Phragmites `method_selection` had invented "ligule
width/leaf-sheath adherence... most reliable" language not present in the NC Forest Service source
(replaced with the source's actual field cues — monoculture pattern, leaf persistence, stem color) and
`timing_windows` had collapsed two distinct AquaMaster label rate entries into one invented "2% solution"
figure (now both quoted separately and correctly); Ailanthus `disposal_nontarget_risk` had the
allelopathic-suppression distance backwards (source's 2m radius was the *unaffected control* zone, not the
suppression radius — corrected); Phragmites `herbicide_legality` dropped a cited NC administrative code
(02 NCAC 09L .0502/.0503) after confirming via Cornell Law's regulations page that the citing rule is
marked expired (temporary amendment lapsed March 2022); Wisteria `disposal_nontarget_risk` dropped
composting/aquatic-drift claims that weren't verifiable in any reachable source rather than re-paraphrasing
them; Pyrus `herbicide_legality` swapped an unreadable fertilome.com label PDF for a readable
domyown.com/gertens.com reproduction of the same label text, and dropped an "Outdoor Residential Use Only /
no RUP designation" claim that wasn't confirmable in the readable copy.
**Trade-offs:** Did NOT build a `data/sources/` full-text archive — user's stated request, declined for the
copyright reason above; internal source verification during rewriting served the same "don't trust
paraphrase" goal without a persistent bulk-copy artifact. Did NOT reverse PRD §9 — the publish posture
(fact grid + citations, not source documents) is unchanged. Did NOT re-verify sources beyond what each
subagent could fetch as raw HTML/PDF text in one pass — a source that failed to yield extractable text was
flagged in the subagent's report rather than forced into a quote (none were left silently paraphrased this
pass; all flagged issues were resolved by finding an alternate readable source for the same fact). Did NOT
touch `data/items.jsonl` — item citations point at ground-truth cells/sources, not embedded answer text, so
no items needed edits.
**Rule Updated:** N — flag for retro: this is the third time this project has found the original
ground-truth authoring pass contained an error only caught by a later, independent re-verification against
the live source (see the two prior entries above: the NC-IPC dead-host swap, and the process note on the
original corpus-build entry). Worth a rule in `.claude/rules/domain-legal.md` requiring a second-source or
re-fetch verification pass on ground-truth claims before they're treated as final, not just at first
authoring.
**Status:** Active

## 2026-09-01 — Synced `data/items.jsonl` to the rewritten ground-truth corpus; corrected two Phragmites items

**Decision:** Rewrote `ground_truth_answer` for all 60 items in `data/items.jsonl` to draw on the
verbatim quotes now in `data/ground_truth/*.yaml` (previous entry) rather than the prior paraphrase,
selecting the portion of each cell relevant to the item's specific query rather than reusing the whole
cell. Updated the two Pyrus items (`PYRU-HERBLEGAL-01`, `PYRU-ABST-02`) whose `ground_truth_citation`
still pointed at the unreadable fertilome.com label PDF to the corrected domyown.com citation. Corrected
two Phragmites items whose text inherited errors from the pre-rewrite corpus: `PHRA-METHOD-01`'s
ID-marks language (now matches the corrected monoculture/leaf-persistence/stem-color cues, not the
invented ligule-width claim) and `PHRA-TIMING-01`'s rate (now the corrected 2-3 qt/acre NC figure, not
the invented "2% solution"). Also corrected `PHRA-HERBLEGAL-02` and `PHRA-ABST-02`, which asserted a
specific "NPDES Certificate of Coverage (General Permit NCG560000)" requirement that was never actually
backed by the cited AquaMaster label or any other source in the corpus (apparently added directly during
the original item-writing pass, not carried over from a ground-truth cell) — replaced with what the label
itself says: consult the state pesticide-regulating agency before applying to public waters, and the
20%-coverage/3.75-qt strip-application cap. Left the 5 `outside_region` items and most `unstated_variable`
/`site_assessment_required` abstention items largely as-is, adding quotes only where an item asserted a
specific, source-traceable fact from the same cell its `condition_2_documents` already points to (e.g.
`WIST-ABST-03`'s Tordon-is-Restricted-Use claim, `PHRA-ABST-01`'s strip-application cap) — not forced
everywhere, consistent with the prior entry's "don't weaken an already-solid claim just to force in a
quote" principle.
**Rationale:** `data/items.jsonl` isn't frozen yet (freeze gate is `SCRATCHPAD.md` task 1, dated Sun Sep
6 — today is Sep 1), so syncing it to the corrected, verbatim-quoted corpus now is in scope and cheaper
than doing it after freeze. The NPDES claim in particular is exactly the kind of thing
`.claude/rules/domain-legal.md` exists to catch: an unsourced specific legal claim baked into a
benchmark item that graders would have scored real model responses against as if it were verified ground
truth.
**Trade-offs:** Did NOT run item-writing subagents for this — done directly in one pass against the six
ground-truth files already read into context this session, avoiding the concurrent-shared-file-write
hazard the original items-writing decision (2026-08-31) already flagged for this single-file case. Did
NOT re-run the full schema-conformance/drift spot-check described in that same 2026-08-31 entry — validated
structurally (60 lines, all valid JSON, via PowerShell `ConvertFrom-Json`) but did not re-run a fresh
drift spot-check against the now-rewritten cells; the freeze-gate review (`SCRATCHPAD.md` task 1) still
needs to do that properly before Sep 6. Did NOT touch item allocation, `item_id`s, `is_abstention`,
`abstention_reason`, `jurisdiction`, or `condition_2_documents` — only `ground_truth_answer` text and the
two citation objects that had gone stale.
**Rule Updated:** N — flag for retro alongside the prior entry's re-verification pattern: this is now a
second data artifact (ground truth, then items) where an unsourced or stale claim survived until an
unrelated rewrite triggered a close re-read. Same candidate rule applies: a required re-verification pass
before either artifact is treated as final.

## 2026-09-01 — Fix unsupported claims in ground-truth citations (herbicide_legality + all 20 abstention items)

**Decision:** Domain-expert review (Hayden) flagged that several `data/items.jsonl` entries make a
specific legal/procedural claim whose attached `ground_truth_citation` doesn't actually establish that
claim — the citation is a plausible source for the species generally, but not for the specific assertion
being tested. Audited all 20 abstention items plus the one flagged answerable item
(`AILA-HERBLEGAL-01`), not just the 7 originally flagged, per user decision. Found and fixed 12 items:
`AILA-HERBLEGAL-01`, `AILA-ABST-01/02/03`, `LIGU-ABST-01/02/03`, `MICR-ABST-01/02`, `PYRU-ABST-02`,
`WIST-ABST-01/02`. Each got a `ground_truth_citation` swap to a source that was independently re-fetched
and confirmed to contain the specific claim, with the answer prose updated to quote/reference it. 8 items
(`PHRA-ABST-01/02`, `PYRU-ABST-01`, `WIST-ABST-03`, plus 4 not needing review) were checked and left
alone — their citations already directly quote the specific claim.
**Rationale:** The benchmark's entire premise is grading LLM advice against real regulatory ground truth
(`.claude/rules/domain-legal.md`) — a citation that doesn't back its own claim defeats that premise before
a single model response is ever scored. New sources used: NCDA&CS's pesticide-licensing page (who needs a
license/certification in NC); 40 CFR § 156.10(i)(2)(ii) via Cornell LII (the FIFRA misuse-clause
requirement, for the two "can I exceed the label rate" items); NC Cooperative Extension Brunswick County's
tree-care-professional guidance (for the two "consult an arborist" items); UF/IFAS's FE962 fence-and-
property-law handbook (for the property-line/neighbor-consent item, which directly addresses the
uncertainty around spraying encroaching vegetation); Corteva's own Tordon 22K product page (confirms RUP
status directly, replacing a citation that supported a different product entirely); and the already-
verified Compare-N-Save glyphosate label and AquaMaster aquatic label already used elsewhere in this
corpus, reused where their existing verified quotes ("kills all green plants" / lists aquatic sites)
directly supported a different species' identical claim.
**Trade-offs:** `AILA-HERBLEGAL-01`'s fix touches `data/items.jsonl` only, not
`data/ground_truth/ailanthus-altissima.yaml`'s `herbicide_legality` cell — that cell's existing Garlon 3A
citation still correctly backs the specific product/application quotes it makes, and the schema gives each
yaml cell only one citation slot, so the item's more specific licensing claim and the cell's
product-application claim now cite different (both individually correct) sources. Did NOT re-audit the
other 5 species' `herbicide_legality` cells or the other 40 answerable items against this same standard —
out of the scope the user approved for this pass. Three of the new citations (NCDA&CS licensing page,
Cornell LII CFR page, Corteva's product page) are live regulatory/manufacturer pages with no visible
publication date on the page itself; dated them `2026-09-01` (verification date) rather than inventing a
publication date, consistent with them being continuously-current sources rather than dated snapshots.
**Rule Updated:** Y — this is the third occurrence of the same pattern (see the two prior 2026-09-01
entries above, both left as "N — flag for retro"). Added a bullet to `.claude/rules/domain-legal.md`:
a citation must support the specific claim it's attached to, verified by re-fetching the source, not
inferred from the source being a reasonable citation for the species generally.
**Status:** Active

## 2026-09-01 — Freeze-gate review of all 60 `data/items.jsonl` items (SCRATCHPAD.md task 1)

**Decision:** Reviewed every one of the 60 items for two things in order: (1) whether
`ground_truth_answer` is a complete, effective answer to the specific scenario in `query_text` (not just
generically correct for the species), and (2) whether `ground_truth_citation` independently supports every
specific quoted/paraphrased claim in the answer, re-fetching each source fresh rather than trusting prior
verification passes. Used 3 parallel research agents batched by species (Ailanthus+Ligustrum,
Microstegium+Phragmites, Pyrus+Wisteria+the 5 generic outside-region items), each re-fetching sources
independently; I then personally re-verified every proposed fix against the live source before applying it.
Found and fixed 8 items (plus 4 matching `data/ground_truth/*.yaml` cells that had the identical problem,
since items are often drawn straight from a cell):
- `AILA-METHOD-02` + `ailanthus-altissima.yaml#method_selection`: the hand-pulling quote was attributed
  in-text to "NC State Extension" while the sole `ground_truth_citation` was Clemson's blog, which contains
  no hand-pulling guidance at all. Fixed by naming both sources in the citation (Clemson primary, for the
  herbicide-rate content; NC State named and linked inline for the hand-pull claim) — see Trade-offs.
- `LIGU-ABST-01`: cited UF/IFAS's *Florida* fence-and-property-law handbook for a boundary/consent claim —
  boundary and vegetation-trespass law is state-specific, so a Florida source can't establish NC law.
  Replaced with NC State Extension's timber-trespass page, which states NC's actual rule (G.S. § 1-539.1,
  double damages for cutting/injuring another's vegetation without consent) and directly supports the
  item's warning about spraying a neighbor's side of a shared hedge.
- `MICR-HERBLEGAL-02`: the decisive claim answering the query (no homeowner-available product exists for
  stiltgrass in a warm-season/Bermuda lawn) is Clemson HGIC's, not the cited Compare-N-Save label's — the
  label only supports the item's opening sentence. Fixed by making Clemson HGIC the primary citation and
  naming Compare-N-Save inline for its own quote.
- `PHRA-METHOD-02`: `ground_truth_citation` pointed at the NC Forest Service alert (the method_selection
  cell's source) but every specific quote in the answer is AquaMaster label language — a copy-paste
  mismatch from the item's own `condition_2_documents`, which already correctly listed both cells. Fixed by
  pointing the citation at AquaMaster, matching the content.
- `PHRA-ABST-02` + `phragmites-australis.yaml#herbicide_legality`: the query asks specifically about
  imazapyr, but the answer/citation imported glyphosate/AquaMaster's numeric caps and permit language
  wholesale. Imazapyr's actual label (Habitat, EPA Reg. 241-426) has a materially different and stricter
  rule the old answer missed entirely: DIY application is illegal on *public* water regardless of rate,
  legal only on private water with no/minimal outflow, and its rate cap (1.5 lbs ae/acre/year) and
  oxygen-depletion limit (max 1/2 of surface area per application) are both different numbers from
  AquaMaster's. Rewrote the item to state the real rule, and added the same facts to the yaml cell so
  Condition-2 oracle grounding actually supports the item drawn from it.
- `PYRU-HERBLEGAL-01` + `pyrus-calleryana.yaml#herbicide_legality`: a "within 45 minutes" application
  timing claim doesn't appear anywhere on the cited domyown.com page (confirmed by direct fetch); dropped
  the specific figure rather than swap in an unverified third-party mirror, since the underlying label
  wasn't independently confirmed to state 45 minutes anywhere.
- `WIST-METHOD-01` + `wisteria-sinensis.yaml#method_selection`: the ID paragraph attributed several precise
  quotes (pod length in inches, bloom-emergence sequencing, a three-way twining-direction comparison) to
  "NC State Extension's Plant Toolbox," a source not in `ground_truth_citation`; the actually-cited Madison
  County page doesn't contain any of them. Rewrote to use only what the cited Madison County page actually
  says (pod texture, bloom window, twining direction) — verified by direct fetch.
- `ABST-01`/`ABST-02`/`ABST-04` (Scotch broom, giant hogweed, saltcedar): all three claimed "not documented
  in NC" as their premise, which is false — verified against the NC Invasive Plant Council's official
  ranked list (PDF, extracted via `pdftotext` after WebFetch choked on it) and NCDA&CS's own page: Scotch
  broom is NC-IPC Rank 2 ("Significant Threat"), giant hogweed has a real, actively-managed NCDA&CS
  quarantine in Watauga County (6 sites, ~200-300 plants, found 2010), and saltcedar is NC-IPC Watch List A
  and flagged "should not be planted" by NC State's own Plant Toolbox. The *abstention behavior* (don't
  invent coastal-plain-specific rate/timing/legality guidance the corpus doesn't have; refer to Extension)
  was still correct in all three — only the "undocumented" framing and the missing citations were wrong.
  Added a real citation to each (previously `null`).
The other 52 items passed both checks: every remaining citation was re-fetched and its specific quoted
claims confirmed verbatim (or, for compressed-stream PDFs WebFetch can't parse — AquaMaster, Habitat, the
EPA Compare-N-Save/Garlon labels, the NC-IPC list — via `pdftotext` on the downloaded file, the same
workaround used in earlier sessions' entries above).
**Rationale:** This is the `SCRATCHPAD.md` task-1 freeze-gate review, run against the working tree as it
stood after today's earlier citation-hygiene fixes (this entry builds on those rather than redoing them) —
per user instruction, this pass adds the check those earlier fixes didn't cover: whether each answer is
actually complete for the *specific* scenario asked, not just accurate for the species in general. Several
of the 8 fixes (PHRA-ABST-02 especially) were only findable by literally re-fetching the cited source and
checking it against the specific figures in the answer, rather than trusting that a citation naming the
right species/topic was sufficient — exactly the discipline `.claude/rules/domain-legal.md` already
requires, now applied a second time by an independent reviewer.
**Trade-offs:** For `AILA-METHOD-02` and `MICR-HERBLEGAL-02`, the schema's single `citation: {source, url,
publication_date}` object per item/cell can't cleanly represent an answer that draws specific claims from
two different sources — resolved by naming the secondary source inline within the `source` string (with
its own URL) rather than dropping either claim or extending the schema to a citation list. This is a
readability compromise, not a structural fix; flagged below for `/retro` since it's now happened twice in
one pass. Did NOT reclassify `PHRA-ABST-02`'s `abstention_reason` from `illegal_rate_for_layperson` even
though the rewritten answer is arguably more of a `site_assessment_required`/`unstated_variable` case
(public vs. private water is an unstated site fact, not a rate a user is trying to exceed) — the corpus's
documented 5-items-per-reason balance (`SCRATCHPAD.md`/`DECISION-LOG.md`, 2026-08-31) is a structural
property of the 60-item set, and reclassifying one item unilaterally breaks that balance without the user
weighing in; flagged for the user's decision rather than resolved here. Did NOT extend this same
completeness/effectiveness check to the `data/ground_truth/*.yaml` cells not already touched by one of the
8 fixes above — the yaml corpus was fully rewritten with verbatim quotes earlier today and re-verified by a
different independent pass than this one; re-auditing all 36 cells for query-specific completeness (a
concept that doesn't fully apply to a cell, which has no single `query_text`) was out of this review's
scope. Left the working tree uncommitted per user instruction — no commit, no freeze tag.
**Rule Updated:** N — flag for retro: the single-citation-object schema limitation (two items this pass)
and the recurring "specific claim traced to the wrong cell/source within the same corpus" failure mode (5
of 8 fixes: AILA-METHOD-02, MICR-HERBLEGAL-02, PHRA-METHOD-02, WIST-METHOD-01, and arguably PHRA-ABST-02)
are both now recurring enough to be worth a `/retro` pass once Week 2 scoring work isn't competing for
time.
**Status:** Active

## 2026-09-01 — Synced reviewer edits from a downloaded `items-review.xlsx` back into `data/items.jsonl`

**Decision:** Wrote `scoring/sync_items_from_xlsx.py` and used it to overwrite `species`, `category`,
`is_abstention`, `abstention_reason`, `query_text`, `ground_truth_answer`, `ground_truth_citation`,
`jurisdiction`, and `jurisdiction_range_flag` for 55 of the 60 items in `data/items.jsonl` from
`C:\Users\jhqui\Downloads\items-review.xlsx` (columns A-L only). The 5 generic outside-region abstention
items (`ABST-01`..`05`) were absent from that sheet entirely and were left untouched. `item_id`,
`condition_2_documents`, and `notes` were preserved from the existing file since the sheet doesn't
represent them.
**Rationale:** User-directed sync of reviewer edits. Before applying it I flagged three anomalies in the
file and paused for confirmation rather than syncing blind: (1) the 5 missing items, (2) `ground_truth_
answer` text rewritten wholesale rather than incrementally edited — e.g. `AILA-METHOD-01`'s new answer
describes an AquaMaster "50-percent solution... and 10 percent Arsenal herbicide" cut-stump mix and cites
"NCDOT recommends," neither of which appeared in the Clemson-sourced answer verified during today's
earlier freeze-gate review, and the listed citation (still Clemson) does not obviously support those new
specific claims, and (3) columns M-P (past the real 12-column schema) contained stray paragraph fragments
that read as spillover from other rows, not real data. User confirmed these were real intended edits and
the M-P spillover was formatting noise to ignore, not a corruption signal — so the sync used only columns
A-L as instructed.
**Trade-offs:** This sync did NOT independently re-verify the new `ground_truth_answer` text against its
`ground_truth_citation` the way the freeze-gate review earlier today did — it applied the sheet's values
as given, per user instruction, without re-fetching sources for the 55 rewritten answers. That means the
freeze-gate review completed earlier today (previous entry) no longer describes the current state of
`data/items.jsonl`'s answer text for those 55 items — **the citation-support and answer-completeness
guarantees from that review do not carry over to this new text** and `SCRATCHPAD.md` task 1 has been
reopened accordingly rather than left marked reviewed. Did NOT regenerate `scoring/items-review.xlsx` from
the newly-synced `items.jsonl` in this same pass, since the user's request was specifically to update
`data/items.jsonl`, not to round-trip the sheet again.
**Rule Updated:** N — flag for retro if a similar spreadsheet-roundtrip sync recurs; for now this is
logged so a future reviewer knows why the freeze-gate review's coverage no longer matches the current file.
**Status:** Active

## 2026-09-02 — Drop abstention items from this release; defer to a future release

**Decision:** Removed the 20 abstention items (5 `outside_region` + 15 species-tied, split across
`site_assessment_required`/`unstated_variable`/`illegal_rate_for_layperson`) from `data/items.jsonl`,
which now holds 40 answerable items only. The removed items were moved verbatim — no content changes — to
a new `data/deferred/abstention-items.jsonl`, not deleted. Updated `SCOPE.md` (Items ~60 → ~40),
`data/SCHEMA.md` (item count, and the abstention-item format documentation moved under a new "§3.
Deferred: abstention items" section pointing at the new file), `PRODUCT_REQUIREMENTS.md` (item-count
table, scoring-load estimate, API-budget estimate, the Days 5-7 item table, RQ2 annotated as deferred, the
Week 3 analysis list cut from 4 to 3, §5's framing, the null-result risk mitigation in §7, the §8 effort
table, a new row in §9's "what was cut" table modeled on the existing Study B row, the Day 7/13-18
schedule rows and their hour totals), and `scoring/RUBRIC.md` (§3 "Abstention scoring" marked out of scope
for this release, left in place rather than deleted). No `data/ground_truth/*.yaml` changes — abstention
items never had their own ground-truth cells, only references into the six species' existing cells.
**Rationale:** Matches this repo's existing "defer, don't discard" pattern (PRD §9, Study B), applied here
to already-completed data rather than an unbuilt research arm — the abstention items are fully written and
were citation-reviewed in yesterday's freeze-gate pass, so nothing about them is being thrown away, just
held out of the active corpus. Preserving them in a same-schema file means reintroducing them later is a
file merge, not a rewrite.
**Trade-offs:** RQ2 ("Do models abstain when a question can't be safely answered...") goes unanswered for
this release — the single biggest real loss, on par with the already-accepted "no required expert
validation" loss in §9. Week 3 drops from 4 analyses to 3. Scoring load and most downstream hour estimates
shrank proportionally (480→320 responses; project total ~59 hrs → ~54 hrs), which incidentally absorbs
most of the PRD's previously-flagged hour overage without touching either of the two already-pre-authorized
cuts (4 species, 3 models). Did NOT touch the two *other*, unrelated "20"s already in the PRD — the
20-item run-to-run variance subset (§2/§4/§10) and the 20-item optional expert-validation spot check (§2)
— both are independent of the abstention items and stayed as-is; flagging this explicitly since the PRD
now has zero "20 abstention items" but still has two other legitimate "20"s, an easy thing for a future
read to conflate. Per `.claude/docs/decision-log.md`, did NOT retroactively mark the 2026-08-31 "Day 1
tasks: SCOPE.md..." entry (which committed the original ~60-item `SCOPE.md`) as Superseded — most of that
entry (deadline confirmation, outreach docs) is still accurate, and Status is a whole-entry field; only the
item-count value it established has changed, which this entry now documents going forward.
**Rule Updated:** Y — `SCOPE.md`, `data/SCHEMA.md`, `PRODUCT_REQUIREMENTS.md`, and `scoring/RUBRIC.md` all
updated as described above so the active documentation matches the active corpus.
**Status:** Active

## 2026-09-02 — `/retro`: two recurring patterns codified

**Decision:** Ran `/retro` over the full `DECISION-LOG.md`. Found two patterns crossing the 3+ recurrence
threshold and updated the corresponding rule files: (1) citation-accuracy failures kept surfacing only in
a *later* review pass, and recurred even the same day a fix landed — extended
`.claude/rules/domain-legal.md`'s existing citation bullet with two additions: verification must happen
at authoring time, not only in a subsequent audit (evidence: the 2026-09-01 freeze-gate review found 5
more violations on the same day the "citation must support the specific claim" bullet was added), and
when an answer draws claims from more than one source, each source must be named next to the claim it
supports (formalizing a workaround already invented twice ad hoc: `AILA-METHOD-02`, `MICR-HERBLEGAL-02`).
(2) "Defer, don't discard" on scope cuts — used three times (visual reviewer, Study B, abstention items)
and explicitly self-named as "this repo's existing pattern" by the third instance, but never written down
anywhere — added it to `CLAUDE.md`'s "Always true" section.
**Rationale:** Both patterns met the retro bar of 3+ occurrences of the same underlying issue, and both
had a tell that the tacit version wasn't working: the citation-accuracy fix already had one rule-update
attempt that didn't stop the very next pass from finding more instances, and the defer-don't-discard
pattern was being invoked by name in prose without ever having been formally stated.
**Trade-offs:** Considered but rejected four other candidates for not clearing the 3+ bar or already being
resolved without a gap: cross-file doc sync (2 instances, no recurrence since), effort-estimate/
pre-authorize-cuts heuristics (one-off strategic calls), YAML re-validate-after-batch-edit (2 instances,
no recurrence since), third-person voice-drift (2 instances, no recurrence since), and subagent/fork
self-report trust (1 incident; later multi-agent passes already show the lesson applied without a written
rule). Did NOT open a third rule change for the freeze-gate entry's single-citation-object schema
limitation as its own pattern — folded it into the citation-accuracy edit above since it shares the same
root cause (multi-source claims) rather than treating a 2-instance-in-one-pass finding as independently
meeting the 3+ bar.
**Rule Updated:** Y — `.claude/rules/domain-legal.md` (citation authoring-time + multi-source bullets) and
`CLAUDE.md` (defer-don't-discard bullet in "Always true").
**Status:** Active

## 2026-09-02 — Targeted re-verification pass: 4 new sources added, 12 items fixed (partial progress on `SCRATCHPAD.md` task 1)

**Decision:** In response to a read-only audit flagging 7 high-severity and several medium-severity
problems across the 40 active `data/items.jsonl` items, the user supplied 4 sources to re-verify against
and directed specific fixes. Fetched and read all 4 (Beam, C.L. et al. 2022 — "Evaluation of Landowner
Accessible Control Methods for Japanese Stiltgrass," USDA Forest Service Gen. Tech. Rep. SRS-268, a
Piedmont-NC field trial; NCDA&CS's Pesticides Licenses page; NC Forest Service Invasive Species Alert
No. 6 (Phragmites, already the corpus's `phragmites-australis.yaml` method_selection citation); and
NC State Extension's stiltgrass page, already `microstegium-vimineum.yaml`'s citation for 3 cells).
Confirmed each finding item-by-item against the fetched text rather than assuming the user's framing was
correct. Results:
- **Genuinely unsupported, now backed:** the Beam et al. field-trial numbers in `MICR-METHOD-01`/
  `MICR-HERBLEGAL-01` (28±14% hand-pull, 98±0% glyphosate, 79±21%/90-100% vinegar, fenoxaprop-p-ethyl/
  clethodim/sethoxydim) were real, just uncited — added to `microstegium-vimineum.yaml#method_selection`
  with a compound citation (NC State + Beam et al.) and the two items rewritten to match. The imazapyr
  rate in `PHRA-METHOD-01` ("1 to 2 percent imazapyr plus 1 percent mentholated seed oil") was also real
  and already inside the cell's existing NC Forest Service Alert No. 6 citation — added it to
  `phragmites-australis.yaml#method_selection`, and the same item's other three claims (wick-type
  application, draining the area, deepening the pond to 5-6 ft) were confirmed absent from that leaflet
  and dropped rather than fabricating a citation for them.
- **Fixed without new sources (per user instruction, findings 4-7 of the audit):** `PHRA-RESPROUT-01`'s
  `ground_truth_citation` named a different document (`ncwildlife.gov` ch. 13.9) than what its own
  `condition_2_documents` pointed at (FEIS) — realigned the citation to FEIS and rewrote the answer using
  only FEIS-supported content. `LIGU-METHOD-01` overstated the hand-pull threshold (claimed seedlings
  "under 2 inches" can be hand-pulled; the corpus says hand-pulling only works under half an inch, with
  2 inches requiring specialized tools) — corrected, and also dropped an unsupported 25% basal-bark rate
  and a Harrington & Miller stat misattributed to the wrong citation. `LIGU-DISPOSAL-01` never mentioned
  the human/pet toxicity warning that is the actual content of its own cited `disposal_nontarget_risk`
  cell, instead padding with disposal advice for species outside this benchmark (stiltgrass, oriental
  bittersweet) — rewrote to lead with the toxicity content and dropped the off-species analogies. The
  NCDA&CS licensing-page citation carried three different `publication_date` values across
  `AILA-HERBLEGAL-01`/`MICR-HERBLEGAL-01`/`PHRA-HERBLEGAL-02` for the same URL — the live page has no
  visible date, so standardized all three to `2026-09-02` (verification date) and updated the quoted
  licensing language to match the live text, which differs from what was previously quoted. While fixing
  those two, also found `AILA-HERBLEGAL-01` and `PHRA-HERBLEGAL-02` each had the *same* citation-source
  mismatch bug as finding 4 (item's own citation pointed at NCDA&CS while `condition_2_documents` pointed
  at Garlon 3A / AquaMaster respectively) — fixed the same way, primary source realigned to match
  `condition_2_documents`, NCDA&CS demoted to a named secondary source for the licensing sentence only.
- **Medium-severity, per explicit user instruction:** `AILA-METHOD-01`'s fabricated "NCDOT recommends...
  50-percent solution of this product and 10 percent Arsenal herbicide" / AquaMaster-branded dosing
  (flagged in the 2026-09-01 xlsx-sync entry as unverified new text) simplified to a generic
  "aquatic-approved glyphosate concentrate... equally legal alternative active ingredient," matching the
  phrasing the corpus already uses elsewhere. Dropped an unsupported "glyphosate at 4% v/v + 0.5% NIS"
  rate from `AILA-METHOD-02`/`AILA-TIMING-01` (not present anywhere in the Ailanthus corpus). Dropped the
  Tordon 22K/picloram RUP paragraph from `PYRU-HERBLEGAL-01` (unsupported by its NC State Extension
  citation). Left `WIST-DISPOSAL-01`'s unsourced vet-care protocol as-is per explicit instruction.
- **Checked and already correct:** `MICR-HERBLEGAL-02`, `PHRA-METHOD-02`, and `WIST-METHOD-01` — named in
  `.claude/rules/domain-legal.md`'s "5 more instances" note from the 2026-09-01 freeze-gate review — were
  re-checked and found already fixed by that prior pass; no further changes made.
**Rationale:** This directly advances `SCRATCHPAD.md` task 1 (re-review of all 40 items after the
2026-09-01 xlsx sync, whose new text was never re-verified against citations), though it is a targeted
pass driven by a specific audit and user-supplied sources, not the exhaustive item-by-item freeze-gate
review task 1 still calls for — task 1 stays open, scope narrowed to what wasn't touched this pass.
**Trade-offs:** Did NOT re-verify the remaining ~28 items not named in the audit or the rule file's
"5 more instances" note — they may still hold unverified claims from the xlsx sync; task 1 remains the
place to track that. Did NOT reconcile the different quoted phrasing now on `AILA-HERBLEGAL-01`'s
Garlon 3A/NCDA&CS citation against `ailanthus-altissima.yaml#herbicide_legality`'s cell (which still uses
the older paraphrase-era `.0503`/etc. framing) — the cell's existing citation and quotes were already
independently correct; only the item's separate licensing claim needed realigning. Did NOT investigate why
`.claude/rules/domain-legal.md` changed on disk between the start of this session and this point (new
"authoring-time" and "5 more instances" bullets appeared that weren't present in the session's initial
context) — treated as legitimate current project state rather than flagged as anomalous, consistent with
`git status` showing this file as already modified/uncommitted before this session began.
**Rule Updated:** N — this is the fourth occurrence of "a review pass finds unsupported claims the prior
pass's own rule update didn't prevent" (see the three prior 2026-09-01/09-02 entries), but the existing
rule (authoring-time verification, multi-source citation naming) already covers the mechanism; the
recurrence here is about incomplete *coverage* of the 2026-09-01 xlsx sync's blast radius, not a new
failure mode needing a new rule. Flag for `/retro` if a full task-1 pass later finds a fifth instance of
the same root cause.
**Status:** Active

## 2026-09-02 — User-directed source pass: 4 new sources fetched, 13 items fixed, 3 items confirmed still unbacked

**Decision:** Following the read-only audit that flagged 16 of 40 items, the user supplied a source
mapping for 15 items/decisions (mostly citing sources not previously in the corpus) and asked for the
ground truth to be updated so every claim traces to a real, named source, with any remaining unbacked
claims flagged rather than silently fixed. Fetched and verified all 4 newly-named sources before using
them: NCDOT's *High-Threat Invasive Plant Species and Removal Plan Report* (April 21, 2026,
`webservices.ncleg.gov/ViewDocSiteFile/118844` — a 20-page, per-species removal plan covering 5 of the
6 locked species; extracted via `pdftotext` after WebFetch choked on it), NC Forest Service Invasive
Species Alert No. 2 (Chinese privet, `ncagr.gov/divisions/nc-forest-service/is02/open` — an image-heavy
PDF also extracted via `pdftotext`), NC State CNR's "Bradford Pear Bounty Program" news article, and
re-fetches of the already-in-corpus NCDA&CS licensing page, Compare-N-Save label, AquaMaster label, and
domyown/ferti-lome page to confirm exact current wording. Updated both `data/items.jsonl` and the
matching `data/ground_truth/*.yaml` cell for every fix, per `.claude/rules/domain-legal.md`'s "name each
source next to the claim it supports" convention.
- **Resolved as genuinely real, just mis-cited (11 items):** `AILA-METHOD-01` (the "mid-summer to early
  fall" cut-stump timing and multi-year follow-up quotes are real, from NCDOT, not Clemson — the
  concurrent session's same-day "aquatic-approved glyphosate" fix was itself wrong, since neither Clemson
  nor NCDOT ever qualifies glyphosate as aquatic-specific and the tree isn't near water; reverted to
  "general-use"), `AILA-METHOD-02` (root-sucker-persistence framing traced to NCDOT, simplified since the
  specific "horizontal lateral root system" phrasing wasn't in any source), `AILA-TIMING-01` (drift-warning
  quotes are real, from Compare-N-Save and AquaMaster, not Clemson), `LIGU-TIMING-01`/`LIGU-HERBLEGAL-01`
  (the 65°F threshold, 2%-glyphosate-or-triclopyr foliar rate, and cut-stump/basal-bark percentages are
  all real, split across IS02 and NCDOT rather than the single previously-named source; dropped one
  invented "Roundup Ready-to-Use...2 percent" retail-product claim with no source at all),
  `MICR-TIMING-01`/`MICR-FOLLOWUP-01` (the "should prohibit it from growing back" and "won't have enough
  time to regrow and flower" quotes are real, from Clemson HGIC, not NC State; also surfaced a real,
  unreconciled seed-viability discrepancy between NC State's "less than 7 years" and Beam et al.'s "2 to 5
  years" — kept both, noted as differing published estimates rather than picking one), `PHRA-FOLLOWUP-01`
  (all three previously-flagged quotes are real: "visual symptoms...slow to develop" from AquaMaster,
  "brush sprayed in the fall may not be fully controlled until the following season" from Compare-N-Save,
  "extensive rhizome and stolon network" from NCDOT), `PYRU-HERBLEGAL-01` (citation swapped from NC State,
  which supports none of this item's content, to Compare-N-Save + domyown + NCDA&CS, which do),
  `PYRU-FOLLOWUP-01` (the "Kelly Oten" quotes are 100% real and correctly attributed in NC State's own CNR
  news coverage — not fabricated at all, just uncited), `WIST-TIMING-01` (drift-warning quotes real, from
  Compare-N-Save/AquaMaster; stump-spray procedure real, from Madison County), `WIST-FOLLOWUP-01` (the
  "multi-year, integrated approach...difficult to eradicate" quote is real, from NCDOT's *Wisteria*
  section — but "cutting alone only suppresses growth," which the same audit had flagged, turned out to
  trace to NCDOT's *Oriental bittersweet* section instead, a different species; dropped rather than
  mis-cited as wisteria-specific).
- **`WIST-METHOD-01`:** user said this item was fine as-is; independently confirmed anyway that the
  "window cut" technique name and the "70 feet long and 10 inches in diameter" vine-size claim — both
  flagged unverifiable in the read-only audit — are real, from NCDOT's *Wisteria* section specifically.
  Added NCDOT as a named secondary source for just those two facts without otherwise rewriting the
  user-approved text.
- **`WIST-DISPOSAL-01`:** user's supplied source (domyown/ferti-lome) supports exactly one sentence —
  "Pet safe: Yes, if used as directed on Label" — and nothing else in the item's dog first-aid/veterinary
  paragraph. Rather than leave the unsourced GI-symptom/home-treatment content in (as an earlier pass had,
  per explicit prior instruction), rewrote that paragraph to keep only what's sourced plus a directive to
  contact a vet or poison-control line on real exposure — this is also the more responsible ground-truth
  answer regardless of sourcing, since fabricated at-home veterinary dosing/timing advice is exactly the
  kind of harm this benchmark exists to catch models producing.
- **`PHRA-METHOD-01` vs. `PHRA-TIMING-01` rate conflict:** per explicit user decision, standardized on
  AquaMaster's actual 2020 label figures (0.75% handheld / 2-3 qt broadcast) in both items, replacing
  `PHRA-METHOD-01`'s separate "2 percent foliar spray" and "1-2 percent imazapyr plus mentholated seed
  oil" figures (which were real, verbatim NCDOT quotes, just for a generic 2010-era extension
  recommendation rather than the specific product label already used elsewhere in this species' corpus).
- **Confirmed still unbacked, left as findings for the user (not fixed this pass):** `LIGU-DISPOSAL-01`
  (the composting-specific claims that answer the actual query aren't in its cited source), 
  `MICR-HERBLEGAL-02` (one quoted phrase belongs to an unnamed third source — low severity), and
  `PYRU-DISPOSAL-01` (one quote, "biomass...may pose safety hazards," not found in its cited source — user
  said this item was fine, left untouched, flagging here per the user's own "if still unbacked, let me
  know" instruction).
**Rationale:** This is the most direct, evidence-based way to close out `SCRATCHPAD.md` task 1's remaining
scope: rather than guessing at fixes, verify the user's proposed sources first (several turned out to
resolve multiple previously-separate findings at once, since NCDOT's report alone covers 5 of 6 species),
and only then write them in, exactly per `.claude/rules/domain-legal.md`'s standing rule.
**Trade-offs:** Did NOT independently re-derive sources for the 3 confirmed-still-unbacked items — flagged
them for the user rather than guessing at a source that might not exist. Did NOT reconcile the
MICR-TIMING-01/MICR-FOLLOWUP-01 vs. seed-viability numeric discrepancy (7 years vs. 2-5 years) into a
single figure — both are real published estimates from different studies; picking one would be inventing
false precision the literature itself doesn't have. Did NOT extend this pass to any of the ~28 items this
pass didn't touch and the 2026-09-02 "Targeted re-verification pass" didn't already cover — `SCRATCHPAD.md`
task 1 remains open for whatever's left.
**Rule Updated:** N — this continues to be the same citation-specificity failure mode
`.claude/rules/domain-legal.md` already covers; no new pattern emerged. The NCDOT report is now a
significant new cross-species source in this corpus (covers 5 of 6 locked species) and should be checked
first for future citation gaps in this project, alongside the existing Extension/label sources.
**Status:** Active

## 2026-09-02 — Freeze-gate re-verification complete: remaining 17 items checked (commit/tag still pending)

**Decision:** Completed the re-verification portion of `SCRATCHPAD.md` task 1 by reviewing the last 17 of the 40 active items not
covered by either earlier 2026-09-02 pass: 14 items untouched by any post-xlsx-sync review, plus the 3
confirmed-still-unbacked findings (`LIGU-DISPOSAL-01`, `MICR-HERBLEGAL-02`, `PYRU-DISPOSAL-01`). Checked
each item's quoted claims against its corresponding `data/ground_truth/*.yaml` cell (itself verbatim-
quote-rebuilt and source-verified on 2026-09-01) and, where a claim wasn't in the cell, fetched the
underlying source directly (NC State Extension's stiltgrass page, NC State Extension's Callery Pear page,
Alabama Extension's wisteria page) to confirm or refute it before touching any file, per
`.claude/rules/domain-legal.md`.
- **9 items confirmed clean, no edits:** `AILA-RESPROUT-01`, `AILA-RESPROUT-02`, `AILA-FOLLOWUP-01`,
  `LIGU-RESPROUT-01`, `LIGU-FOLLOWUP-01`, `MICR-DISPOSAL-01`, `PHRA-HERBLEGAL-01`, `PYRU-RESPROUT-01`,
  `WIST-RESPROUT-01` — every quoted claim already traced to its cited ground-truth cell.
- **`PYRU-DISPOSAL-01` left as-is**, per the standing 2026-09-02 user instruction (one quote,
  "biomass...may pose safety hazards," still isn't in its cited source; user already accepted this).
- **`MICR-RESPROUT-01` and `MICR-HERBLEGAL-02`:** both quoted "shallow fibrous root system" and (only
  `MICR-RESPROUT-01`) "die with hard frost" — both confirmed real, verbatim, on NC State Extension's
  stiltgrass page, just not yet in `microstegium-vimineum.yaml#resprout_regrowth`. Added both quotes to
  that cell. `MICR-HERBLEGAL-02`'s third quote, "easy to pull up," was **not** found on that page (or any
  other corpus source) — dropped and replaced with unquoted description; NC State Extension added as a
  named secondary source on the item, and `#resprout_regrowth` added to its `condition_2_documents`.
- **`PYRU-METHOD-01`:** all quoted claims (grinding the stump, "can resprout from the roots...necessary
  for complete eradication," the Certified Tree Arborist recommendation) confirmed verbatim on NC State's
  Callery Pear page — this arborist-recommendation claim is the exact failure pattern
  `.claude/rules/domain-legal.md` names by example, so it got real scrutiny; it checked out. Added all
  three quotes to `pyrus-calleryana.yaml#method_selection` (item text unchanged).
- **`PYRU-RESPROUT-02`:** all quoted claims (weak branching/brittle wood, storm-breakage description,
  "can sprout new growth from its base," "developed by combining different rootstock") confirmed verbatim
  on the same NC State page — added to `pyrus-calleryana.yaml#resprout_regrowth`, naming NC State as a
  secondary source alongside the cell's existing UGA citation. One trivial fix: the item's thorn quote had
  an added word ("large thorns that can grow up to 4 inches long") not present in the source
  ("thorns that can grow up to 4 inches long") — corrected.
- **`PYRU-TIMING-01`:** one sentence was a fabricated composite presented as a verbatim quote ("cut the
  tree close to the ground and promptly apply a systemic herbicide such as glyphosate or triclopyr to the
  stump within 5 to 10 minutes to prevent resprouting") — this exact wording doesn't appear on the source
  page. Rewrote the item using only quotes already verbatim-confirmed in
  `pyrus-calleryana.yaml#timing_windows`; no yaml change needed.
- **`WIST-HERBLEGAL-01`:** none of its four flagged claims held up. A "2% solution of triclopyr" foliar
  rate and a "0.5% non-ionic surfactant" instruction are not on Alabama Extension's wisteria page — the
  0.5% figure in particular matches Chinese privet's cell exactly, indicating cross-species contamination.
  A Tordon "For retail sale to and use only by Certified Applicators" label quote is also not on that
  page (Alabama's own table only footnotes Tordon 101 as "Restricted Use Pesticide," which is what the
  corpus already has elsewhere). Rewrote the item to use only confirmed content: Alabama's actual
  glyphosate foliar/cut-stump rates, Madison County's already-verified 50% triclopyr stump-spray quote,
  the existing Tordon RUP footnote, and the "THE LABEL IS THE LAW" quote already verified elsewhere in
  this corpus (Compare-N-Save's label, reused here with its own citation named). Added the licensing and
  label-is-law quotes to `wisteria-sinensis.yaml#herbicide_legality` and `#resprout_regrowth` to
  `condition_2_documents`, since the item now draws on both cells.
- **`LIGU-DISPOSAL-01`:** the composting-specific mechanism claim ("ordinary home composting isn't
  reliably hot or long enough...an open compost pile is just as accessible to birds") has no source
  anywhere in this corpus's ~15 references. Dropped it; the item still fully answers "can I compost it"
  using only the two already-verified reasons (toxicity, bird-seed spread), which apply equally to a pile
  or a compost heap.
All 40 items in `data/items.jsonl` are now individually re-verified since the 2026-09-01 xlsx sync —
schema-conformance re-checked (40 valid JSON lines, no duplicate `item_id`s, every `condition_2_documents`
path resolves). This closes the *re-verification* work; the working tree is still uncommitted and untagged
— task 1's remaining step (run `/commit`'s reviewers, then commit and tag the freeze) is tracked separately
and not yet done as of this entry.

A parallel copy-review pass over this same diff caught a real regression: this pass's own freshly-written
text (`WIST-HERBLEGAL-01`, `PYRU-TIMING-01`) had drifted back into second-person ("you/your") phrasing,
the same issue already fixed twice before in this corpus (2026-08-31, both the ground-truth corpus and the
original 60 items). Both were rewritten to third person to match every touched yaml cell. The broader
pattern — the majority of `data/items.jsonl`'s answers (25 of 40, per a corpus-wide grep) currently use
second person, inherited from the 2026-09-01 xlsx sync and left untouched by both prior 2026-09-02 passes
— was corpus-wide and beyond task 1's citation-verification scope; see the next entry for how the user
chose to handle it.
**Rationale:** This is the same citation-specificity discipline `.claude/rules/domain-legal.md` already
requires, applied to the last un-reviewed slice of the corpus. Two results are worth noting: most of the
"unbacked" claims flagged for this pass turned out to be real quotes just not yet captured in the
ground-truth yaml (a coverage gap, not a fabrication), while `WIST-HERBLEGAL-01` and the fabricated
composite sentence in `PYRU-TIMING-01` were genuine integrity problems the yaml-cell cross-check caught
before they could reach the frozen corpus.
**Trade-offs:** Did not re-verify the 25 items already covered by the two earlier 2026-09-02 passes — out
of scope for this pass, already independently verified. Did not investigate whether other items besides
`WIST-HERBLEGAL-01` have similar cross-species-contaminated figures; no evidence of that pattern recurring
elsewhere was found, but this pass wasn't a full re-audit of the 25 already-verified items either.
**Rule Updated:** Y — the second-person voice drift caught by copy review is the third occurrence of this
exact pattern (2026-08-31 x2, now this entry); `data/SCHEMA.md` now states the third-person convention
explicitly, per the retro trigger the 2026-08-31 entry set for a third recurrence. The
fabricated-composite-quote issue (`PYRU-TIMING-01`) and the cross-species-figure issue
(`WIST-HERBLEGAL-01`) are each single instances of failure modes adjacent to, but not identical to, the
existing citation-specificity rule; flag both for `/retro` in case either recurs a second time.
**Status:** Active

## 2026-09-02 — Corpus-wide voice cleanup: all 40 items now third person before freezing

**Decision:** Given the choice between freezing now with known second-person phrasing baked permanently
into 25 items (freeze means "no item changes after that point for any reason"), or fixing voice across
the whole corpus first, the user chose to fix first. Rewrote `ground_truth_answer` for the 26 remaining
second-person items (the 27 flagged by the prior entry's grep, minus `WIST-HERBLEGAL-01` and
`PYRU-TIMING-01`, already fixed) to third person, matching every `data/ground_truth/*.yaml` cell's
established convention. `WIST-RESPROUT-01` needed no edit — its sole "you" is inside a verbatim source
quote, not narrative voice. Verified after: all 40 lines still parse as valid JSON, only 2 "you"/"your"
matches remain in the whole file, and both are confirmed inside verbatim source quotes (an AquaMaster
label quote in `PHRA-HERBLEGAL-02`, a Madison County quote in `WIST-RESPROUT-01`) rather than narrative
prose. No facts, numbers, rates, quoted text, citations, or non-`ground_truth_answer` fields were touched.
One incidental typo fixed outside any quote (`PYRU-RESPROUT-01`: "a aggressive" → "an aggressive").
**Rationale:** The freeze is meant to lock in a verified-accurate, stable corpus — permanently baking in a
known, twice-already-fixed style violation would have meant either breaking "no changes after freeze" to
fix it later, or shipping the benchmark with an inconsistency this project has already spent two prior
passes eliminating. Fixing it now, before the tag, avoids both.
**Trade-offs:** This expands task 1's scope beyond its original citation-verification charter — a
deliberate, user-approved exception, not a precedent for folding future unrelated cleanup into other
approved plans. Did not re-verify every single quoted claim against its source a second time during this
pass (that already happened in the citation-verification passes) — this pass's own verification was
scoped to confirming voice-only changes, i.e. that quoted text and facts were left untouched, not
re-fetching sources again.
**Rule Updated:** N — covered by the same `data/SCHEMA.md` rule addition from the prior entry.
**Status:** Active

## 2026-09-02 — Checklist schema and authoring conventions locked; all 40 item checklists authored

**Decision:** Closed `SCRATCHPAD.md` task 1 (the per-item checklist required by the 2026-09-01 scoring-
methodology switch). Wrote `scoring/checklist.jsonl` — one JSON object per item, 40 lines, `item_id`
joining to `data/items.jsonl`, JSONL to match that file's existing convention rather than the
ground-truth corpus's per-species YAML, since this is authored by decomposing already-verified prose, not
new hand-written long-form content. Each item has `claims` (atomic facts from its `ground_truth_answer`,
weighted `critical`/`standard`) and `harm_triggers` (item-specific response-checkable conditions, each
tagged `H1`-`H4`). Locked two conventions, both confirmed with the user before writing per the same bar
the 2026-09-01 rubric-conventions entry set (arbitrary conventions with load-bearing downstream effects):
a claim is **critical** if its omission/contradiction is what `scoring/RUBRIC.md`'s existing Accuracy
anchors already call a drop to ≤1 (wrong-ID risk, the one method that actually works, a safety/legal
constraint central to the item's `failure_archetype`) and **standard** if omission only drops Accuracy to
2 (supporting detail); a harm trigger is a concrete, item-specific condition (not the generic species-level
anchors already in RUBRIC §2) that, if present in a response, sets Harm to at least the stated level.
Extended `scoring/RUBRIC.md` with a new §5 documenting both conventions and added two per-response fields
to existing §4 (`checklist_catchall_flag`, `checklist_catchall_note`) for wrong content the checklist
didn't anticipate — these are scorer fields defined once, not authored per item. Authored all 40 items'
checklists directly (not via subagent forks), species by species, working from the already source-verified
`ground_truth_answer` text — no new research needed, since freeze-gate re-verification (prior entries) had
already confirmed every claim in that text traces to a real source.
**Rationale:** Reusing RUBRIC's already-locked Accuracy anchors for the critical/standard weighting rule,
rather than inventing a second competing definition of "important," keeps the checklist consistent with
conventions already approved and keeps the eventual convergent-validity comparison (task 2) meaningful — a
checklist built on different judgment criteria than the holistic scale it's being validated against would
undermine that comparison. Direct authoring (no forks) follows the same reasoning as the original
2026-08-31 items.jsonl decision: single shared output file, no research step to parallelize, and this
project's history (2026-08-31 fork-scoping incident, and every "review pass finds unsupported claims"
entry above) shows content-authoring quality on this corpus degrades under delegation.
**Trade-offs:** Deliberately did NOT decide how per-claim/per-trigger present/absent/contradicted marks
roll up into a single Accuracy/Harm number for analysis — left for task 3's scoring-sheet design, so this
entry doesn't quietly pre-empt a decision that task hasn't been scoped yet. Did NOT force every item to a
fixed claim/trigger count: an initial full pass produced 176 claims + 72 triggers (248 rows), below
SCRATCHPAD's ~300-430 planning estimate; per-item review showed the shortfall was concentrated in
resprout/timing/followup items whose source `ground_truth_answer` text is genuinely a short paragraph (not
a coverage gap), but harm-trigger coverage specifically was thin (13 items with only 1 trigger) for what's
meant to be the primary scoring instrument — added one further content-grounded trigger to each of those
13 items (no new facts introduced, only additional response-failure conditions already implied by the
item's existing claims), landing at 176 claims + 84 triggers (260 rows total, later 261 after the fidelity
check in the next entry). This is below the original
budget estimate but reflects the actual content depth of the corpus rather than a padded count; did not
force further additions purely to hit the 300 floor, consistent with the "don't force it" principle already
established for verbatim quoting and abstention-item citations elsewhere in this corpus. Validated
structurally via a one-off `uv run python` check (not a committed script, since the `src/` stack layout —
`SCRATCHPAD.md` task 5 — is still open and this doesn't need a permanent tool): all 40 `item_id`s present
exactly once, valid JSON, `weight` restricted to `critical`/`standard`, `harm_level` restricted to
`H1`-`H4`, and every `claim_id`/`trigger_id` follows the `<item_id>-C<N>`/`-T<N>` pattern with no
duplicates. Did not commit as part of this task; left for the user's normal review-then-commit flow.
**Rule Updated:** N — flag for retro: this is the first structured-schema (not prose) content-authoring
decision for scoring material, same pattern as the 2026-09-01 rubric-conventions entry (confirm arbitrary,
load-bearing conventions with the user before writing). If a third scoring-content schema decision comes
up before task 3's scoring sheet is built, worth checking whether a single conventions doc should hold all
three instead of three separate entries.
**Status:** Active

## 2026-09-02 — Fidelity check of `scoring/checklist.jsonl` against `data/items.jsonl`

**Decision:** Per user request, cross-checked every one of the 40 items' claims and harm triggers in
`scoring/checklist.jsonl` against its source `ground_truth_answer` text in `data/items.jsonl` for two
failure modes: invented content (a claim asserting something the source doesn't say) and missing content
(a load-bearing fact in the source with no corresponding claim). Found and fixed two issues:
- **Omission — `AILA-METHOD-01`:** the source states that treating a standing tree (hack-and-squirt)
  without felling "will leave a dead standing skeleton that could eventually pose a falling safety hazard
  ... and require removal." This was in the original draft but never made it into the written file. Added
  back as `AILA-METHOD-01-C9` (standard weight).
- **Over-reach, then corrected on user challenge — `WIST-METHOD-01-C1`:** the claim included a clause that
  twining direction "is not presented as a reliable distinguishing test" between Chinese and American
  wisteria. Neither `data/items.jsonl` nor `data/ground_truth/wisteria-sinensis.yaml` connects twining
  direction to species identification at all — both only state the "counterclockwise" fact as a general
  Chinese-wisteria trait, unrelated to the pod-texture ID test. Initially trimmed the clause as an
  unsupported inference. The user pushed back ("I like the twining direction part — are you sure no source
  has that information?"), which correctly forced a check of the *live* source rather than just the
  corpus's quoted excerpt: fetched
  `https://madison.ces.ncsu.edu/news/on-the-lookout-for-non-native-invasive-plant-species-chinese-wisteria/`
  directly. The live page confirms the corpus's framing exactly — it lists pod texture (and an incomplete
  sentence gesturing at "flower colors") as the actual distinguishing test, and mentions the
  counterclockwise climb only as a separate, general Chinese-wisteria fact, never connecting the two. So
  the original clause's *content* was accurate, just wrongly deleted instead of correctly reframed: added
  back as `WIST-METHOD-01-C9` (the counterclockwise fact as its own standalone descriptive claim) and a
  new `WIST-METHOD-01-T4` harm trigger for a response that wrongly claims twining direction distinguishes
  the two species — a real, plausible LLM failure mode given how commonly (and inaccurately) twining
  direction is cited as a wisteria-species test in general gardening content, and one this specific,
  now-verified source lets the checklist flag with confidence.
All other 38 items' claims and triggers were confirmed to trace directly to their source
`ground_truth_answer` text, with no fabricated facts and no other significant omissions. Row count moved
from 260 to 263 net (the `AILA-METHOD-01` fix, the `WIST-METHOD-01` reframe, and the new harm trigger).
Re-ran the structural validation script from the prior entry after every edit — still clean (40/40
item_id coverage, no duplicates, valid enums, consistent id format).
**Rationale:** This is the same authoring-time-verification discipline `.claude/rules/domain-legal.md`
already requires for citations, applied here to checklist claim/trigger text derived from already-verified
content — a self-authored artifact benefits from exactly this kind of independent line-by-line check before
it becomes the primary scoring instrument, the same way ground-truth cells and items got repeated
re-verification passes before freeze.
**Trade-offs:** Did NOT re-verify the underlying `ground_truth_citation`s themselves (e.g. the known,
user-accepted `PYRU-DISPOSAL-01` citation gap) — out of scope; this check was scoped to checklist-vs-item
fidelity, not re-opening citation verification already closed by the freeze-gate passes. Did NOT re-fetch
every other item's live source to check for similarly under-used content beyond what's quoted in the
corpus — the `WIST-METHOD-01` case was checked only because the user specifically challenged it; a
systematic "re-fetch every source and check for unused-but-relevant content" pass is real additional scope,
not assumed to be covered by this one instance. Did NOT treat the corrected fix as grounds to re-examine
every other trimmed/edited claim for the same "deleted instead of reframed" mistake beyond this one pass.
**Rule Updated:** N — flag for retro: this surfaces two related but distinct lessons. (1) A checklist claim
adding its own inference on top of decomposed source content is a real failure mode, distinct from the
existing citation-specificity pattern in `.claude/rules/domain-legal.md` (which is about citations not
supporting claims, not about claims overreaching their own source) — worth a rule if a second instance
shows up. (2) When a claim looks unsupported by the *quoted* excerpt in the corpus, the corrective action is
to re-fetch the live source before deleting — not to assume the corpus's quote selection is exhaustive.
This is really the same "verify against the live source, not the last-verified snapshot" discipline
`.claude/rules/domain-legal.md` already states for citations, just newly shown to apply to *checklist*
content too, not only ground-truth citations. If a second instance of either recurs, fold (2) into that
rule file explicitly rather than leaving it implicit.
**Status:** Active

## 2026-09-02 — Added a plain-language scorer's guide separate from RUBRIC.md

**Decision:** Author `scoring/SCORER-GUIDE.md` as an operational SOP for the person scoring responses
(purpose/materials/steps/definition of done), kept separate from `scoring/RUBRIC.md` rather than folded
into it.
**Rationale:** RUBRIC.md is written for the person building/calibrating the instrument (weighting
rationale, anchor examples, cross-scale worked example) — a scorer sitting down cold to score one response
needs a short checklist-style walkthrough, not the calibration reasoning. Splitting the audiences keeps
both documents legible for their actual reader.
**Trade-offs:** Deliberately did NOT merge this into RUBRIC.md as a new top section — that would keep
growing a document already serving a different audience. Also did NOT wait for the Day-9 scoring sheet
(SCRATCHPAD.md task 2) to exist first; the guide describes what gets recorded (claims/triggers/per-response
fields) independent of the sheet's eventual UI, and will gain a pointer to the sheet once that task ships.
**Rule Updated:** N — flag for retro. If this repo keeps splitting "builder-facing" vs "operator-facing"
docs (rubric vs scorer guide; run harness vs runbook), that's a naming/pattern worth a rule.
**Status:** Active

## 2026-09-03 — Fixes from `/commit` review of the checklist/scorer-guide commit

**Decision:** Acting on the architecture and copy reviewers' findings over the checklist/RUBRIC/
SCORER-GUIDE diff (both reviewers independently flagged the same issue, one flagged two more):
- Added `scoring/build_checklist_xlsx.py`, mirroring the existing `scoring/build_items_review_xlsx.py`
  pattern, and regenerated `scoring/checklist.xlsx` from it. The committed `.xlsx` had no generator
  script — an unregenerable binary artifact that would silently drift from `checklist.jsonl` on the next
  edit (which had already happened once this session, per the prior "Fidelity check" entry).
- Fixed two stale numeric task cross-references in `scoring/RUBRIC.md` §5 ("task 2"/"task 3") that
  `SCRATCHPAD.md`'s own renumbering in this same diff made wrong on arrival — replaced with name-only
  references (no number), consistent with how `DECISION-LOG.md` already cites work by title/date rather
  than by `SCRATCHPAD.md` task number.
- Fixed `scoring/SCORER-GUIDE.md`: it undercounted RUBRIC §4's six per-response fields as "five" (treating
  `checklist_catchall_note` as uncounted rather than conditional), and described `harm_triggers` as things
  a response "should not say" when a meaningful share of actual triggers in `checklist.jsonl` are
  omission-type conditions (e.g. `LIGU-METHOD-01-T3`, `MICR-HERBLEGAL-02-T2`) — reworded both to match
  RUBRIC §4/§5's actual field count and "condition" language.
- Renamed `WIST-METHOD-01-C2b` to `WIST-METHOD-01-C9` in `checklist.jsonl` (and the corresponding
  DECISION-LOG reference in the prior "Fidelity check" entry, still uncommitted at the time of this fix) —
  the letter-suffixed ID didn't match the documented `<item_id>-C<N>` pattern that entry itself claimed was
  validated. Used the next free integer rather than renumbering `C3`-`C8`, matching how the `-T4` trigger
  was already appended out of positional order elsewhere in the same item.
**Rationale:** All four fixes are corrections to internal consistency (a doc citing a number that doesn't
exist, a generated artifact with no generator, a guide undercounting its own rubric, an ID breaking its own
documented pattern) rather than new design decisions — no alternative approaches were weighed.
**Trade-offs:** Did NOT add a `pyproject.toml` dependency entry for `openpyxl` even though
`build_checklist_xlsx.py` needs it — that's the same known, already-tracked gap (`SCRATCHPAD.md` task 4,
flagged by the 2026-09-02 freeze-gate architecture review) that `build_items_review_xlsx.py` already has;
fixing it here would be unrelated scope creep into a task not yet reached. Did NOT re-run the full
structural validator script from the "Checklist schema locked" entry after the `C9` rename — confirmed
uniqueness and pattern-conformance manually (grep for `WIST-METHOD-01-C2b` returned zero hits after the
edit, and `C9` doesn't collide with any existing claim_id for that item).
**Rule Updated:** N — flag for retro: this is the second time a RUBRIC.md/checklist doc has cited a
`SCRATCHPAD.md` task *number* and gone stale (see the "task 1 (new numbering)" callouts already in
`SCRATCHPAD-ARCHIVE.md`). If a third instance shows up, worth a rule: reference documents should never
cite `SCRATCHPAD.md` by task number, only by task description or a `DECISION-LOG.md` entry title/date.
**Status:** Active