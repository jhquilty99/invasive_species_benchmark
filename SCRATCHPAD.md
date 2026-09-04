# Scratchpad — active

Open work only. A task lives here from creation until it closes. The instant it closes: append its
one-line entry to `SCRATCHPAD-ARCHIVE.md`, then remove its block from this file (the removal rides with
the commit that finished the work — see `.claude/docs/scratchpad-discipline.md`).

This file is a tracker, not memory. Durable facts/preferences/decisions do not belong here — they belong
in a rule file or `DECISION-LOG.md`.

## Status

- **Methodology pivot (2026-09-03):** the project moved from PRD v3's single-turn, item-based design to
  PRD v4's multi-turn, card-based design. `PRODUCT_REQUIREMENTS.md`, `SCOPE.md`, and `data/SCHEMA.md` are
  rewritten to match. PRD v3's artifacts (`data/items.jsonl`, `data/deferred/abstention-items.jsonl`,
  `scoring/checklist.jsonl`, `scoring/RUBRIC.md`, `scoring/SCORER-GUIDE.md`, and the xlsx/build/sync
  scripts) are archived at `archive/study-a-single-turn/` via `git mv` — not deleted. `data/ground_truth/
  *.yaml` (6 species, 6 categories each, 0 jurisdiction-range flags) stays active and is reused as source
  material for the new case cards. Full rationale: `DECISION-LOG.md`, 2026-09-03 "Pivot to multi-turn
  simulated-conversation methodology (PRD v4)".
- **Deadline confirmed:** earliest grad application is UC Berkeley MIDS, **Oct 23, 2026** — well past the
  ~Sep 20 target, so the schedule keeps its full buffer. No replanning needed.
- **API access confirmed:** OpenAI, Anthropic, Google all active. One of the 4-6 models must be
  open-weight — exact model/host still TBD.
- **Outreach:** expert-validation emails reported sent (see `outreach/EMAIL-TRACKER.md`) — that file's
  Status/Date-sent columns still need to be updated to match; not yet fixed. (PRD v4 §7's "second expert
  reviews the cards" ask, if a reply lands, is a separate follow-up from this outreach.)
- **Task list:** replaced entirely with PRD v4 §10's 17-day schedule, then broken down (2026-09-03, same
  day) from one bullet per day into the actual build steps each day bundles — the original "Day 1: build
  the harness" line hid ~7 separate pieces of engineering. Ranked by dependency/day order.
- **Day 1 complete (2026-09-03):** harness scaffold, card schema, both PRD §13 open-question decisions,
  the Ailanthus test card, slot-gated simulated user, conversation loop, and Langfuse wiring are all built,
  tested (30 passing tests, VCR cassettes recorded), and verified end to end with a live run whose trace
  landed in Langfuse. Three things worth knowing for Day 2: the slot classifier (see the slot-classifier
  tuning task below) still needs tuning — a live run showed it occasionally gating on topic proximity
  rather than an explicit question; the stopping condition needed a fix mid-build for
  conditional/branching recommendations (see `DECISION-LOG.md`, 2026-09-03 "Resolved PRD §13.2..."); and
  the Langfuse trace that landed is a single flat span with the whole transcript dumped as `output` (from
  a one-off script outside the repo, not the harness itself) rather than real per-turn tracing — see the
  per-turn Langfuse tracing task below. Full detail: `DECISION-LOG.md`'s 2026-09-03 entries from
  "Resolved PRD §13.2..." onward.
- **Card matrix restructured (2026-09-03):** the card design moved from depth-axis/breadth-set/
  lookalike-arm to a fixed 54-card matrix crossing 3 question types (removal / introduction /
  identification) with native status, adding RQ1-3 and a new Q6 ecological-framing quality dimension.
  `PRODUCT_REQUIREMENTS.md`, `SCOPE.md`, and `cards/SCHEMA.md` rewritten to match. Full detail:
  `DECISION-LOG.md`, 2026-09-03 "Card matrix restructured around question type × native status
  (RQ1-3, Q6)".
- **Native ground truth done (2026-09-03):** all 6 native species now have `data/ground_truth/*.yaml`.
- **Harness rework done, 12 cards migrated (2026-09-03):** `harness/models.py`'s `Card` model now has
  `question_type`/`native_status`/`introduction_classes`/`ecological_framing_notes` with a validator
  enforcing which fields apply per question type, matching `cards/SCHEMA.md` exactly.
  `harness/langfuse_client.py`'s dataset-item builder updated to match. All 6 invasive cards stayed
  `removal`-type and gained `native_status: invasive` + `ecological_framing_notes`; the 6 native cards
  were converted from a removal-framed "decline to prescribe" design to `identification`-type (opening
  messages rewritten to a "what is this plant?" framing per `.claude/rules/card-voice.md`, removal-only
  fields dropped, `ecological_framing_notes` added). Full detail: `DECISION-LOG.md`, 2026-09-03 "Harness
  rework: `Card` model supports question_type/native_status (implementation)".
- **First `introduction`-type card authored (2026-09-03):** `cards/chionanthus-virginicus-introduction-01.json`
  — fringetree, "should I keep/plant this?" framing, using `introduction_classes`. 13 cards now exist
  spanning all 3 question types (6 removal/invasive, 6 identification/native, 1 introduction/native); all
  13 load and validate (verified via `harness.cards.load_cards`).
- **First-pass LLM-as-judge validation, wired through Langfuse (2026-09-03):** gate judges
  (`harness/judges/gates.py`, G1-G5), quality judges (`harness/judges/quality.py`, Q2/Q3/Q5/Q6), and
  Q1 + derived metrics (`harness/scoring.py`) are all built and tested. Real per-turn Langfuse tracing
  landed too (`harness/_tracing.py`, wired into `conversation.py`/`simulated_user.py`), closing that
  task ahead of schedule. Along the way: added type-aware stopping classifiers for
  `introduction`/`identification` cards (the old one only recognized a treatment recommendation),
  which also resolved `PRODUCT_REQUIREMENTS.md` §13.5's open question (Q1 now applies to
  `identification` cards). Q4 (regulatory grounding) is still not built — deferred, not forgotten.
  Full detail: `DECISION-LOG.md`, 2026-09-03 "First-pass LLM-as-judge validation, wired through
  Langfuse".
- **Live validation run complete (2026-09-03):** `harness/scripts/run_validation.py` ran all 13 cards
  against `claude-opus-5` for real. Fixed a real bug found along the way: judge calls at
  `max_tokens=1024` were getting truncated mid-JSON (`claude-sonnet-5`'s extended thinking eating the
  budget, same failure mode already documented for `claude-opus-5` as model-under-test) — bumped to
  4096 in `harness/judges/_common.py`. All 116 gate/quality/Q1 scores landed correctly in Langfuse's
  ClickHouse `scores` table. **Found and partially worked around a separate local-infra bug**: the
  `langfuse-worker` container was failing every queue job with Redis socket timeouts, so trace/span
  data and dataset-run-item linking never got ingested (confirmed via a bare `span+flush()` smoke test
  after restarting the worker — still didn't land), even though direct score-writes were unaffected.
  Restarting the worker did not fix live ingestion either — needs real investigation, not blocking
  since the scores themselves are the primary signal. Headline result: G1 (identity verified) failed
  on 9/13 cards (69%), matching the derived premature-prescription rate exactly — the model-under-test
  very often gives removal/introduction/identification answers without ever committing to which
  species it's talking about, which is exactly the RQ1 gap this benchmark is designed to catch.
- **Last touched:** 2026-09-03 (first-pass judge + Langfuse validation build, live run complete)

## Open tasks (ranked)

1. **[Day 2]** Tune the slot classifier (`harness/simulated_user.py`) against the test cards until it
   reliably matches which slots were actually asked about — a live Day 1 run showed it can over-trigger on
   topic proximity rather than an explicit question.
2. **[Day 2]** Implement the R5 leakage check in code (not judged): no card slot value may appear in a user
   turn that wasn't preceded by a matching elicitation. Pass it on the test-card harness.
3. Fix the local Langfuse stack's trace/span ingestion: the `langfuse-worker` container was failing
   every queue job with Redis socket timeouts during the 2026-09-03 live run, so no trace, observation,
   or dataset-run-item data landed (scores did, since those write directly rather than through the
   worker's queue). Restarting the worker did not fix it — a bare span-create-then-flush smoke test
   still didn't land afterward. Needs real investigation (Redis connectivity from the worker container,
   possibly a stale connection pool or a `docker compose down && up -d` full reset) before per-turn
   traces are actually browsable in the Langfuse UI for any future run.
4. **[Gate — Fri Sep 5]** Harness + leakage check working end to end. Gate judges, quality judges,
   per-turn Langfuse tracing, and a live 13-card validation run are all done (see the Status note
   above); still blocked on the slot-classifier and R5-leakage-check tasks above. If not met, this is
   the day to cut card-count scope (PRD §8 rule 2), not later.
5. Build the Q4 (regulatory grounding) judge — deferred out of the first-pass validation build since it
   needs a `data/ground_truth/*.yaml` lookup mechanism none of the other dimensions need. Not blocking the
   Fri Sep 5 gate (PRD table doesn't restrict it to removal-only, but it wasn't in this task's original
   scope either); pick this up before the full sweep so every sweep run has a complete quality dimension
   set.
6. **[Days 6-9]** Author the remaining 54-card matrix: 30 removal cards total (6 invasive species × 5
   condition variations — 6 already exist as one-per-species starting cards, 24 more needed), 12
   introduction cards total (6 invasive + 6 native — 1 exists, 11 more needed), 12 identification cards
   total (same 12 species — 6 already exist as the migrated native cards, 6 more needed for the invasive
   species), drawing on existing `data/ground_truth/*.yaml` for all 12 species (invasive and native ground
   truth both complete).
7. **[Gate — Thu Sep 11]** 54 cards complete, corpus frozen (PRD §8 rule 1) — no card changes after this
   point for any reason.
8. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4-6 model
   line-up, and wire a model client for every provider in the line-up — needed before the full sweep task.
9. **[Days 10-11]** Full sweep across 4-6 models (incl. the open-weight model). Fix what breaks; re-run.
    Confirm transcripts complete for every (model × card) pair. Log the pinned card-set version, judge
    prompt version, and exact model version strings in run metadata (R4 — non-negotiable, carries forward
    PRD §8 rule 5).
10. **[Day 12]** Set up the Langfuse human-annotation queue; brief annotators; select the stratified ~50
    sample (oversampled on gate failures and `harmful` Q2 classifications, stratified across all 3
    question types).
11. **[Days 13-14]** Human annotation, blind to judge scores. Write and run the Krippendorff's alpha
    computation per dimension, including Q6 (PRD §7).
12. **[Days 15-16]** Write-up: motivation, method, gates/quality design, results, failure examples (rates
    redacted per PRD §8 rule 3), limitations, generalization. Repo cleanup — assemble the PRD §12 release
    layout (`cards/`, `harness/`, `results/`, README with the schema documented standalone).
13. **[Day 17]** Zenodo archive → DOI. Post to arXiv (cs.CL) and EcoEvoRxiv.
14. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
    sent (currently still shows "Not sent" for all real contacts). No dependency on anything above — pure
    housekeeping, lowest priority.

## Open bugs

Pre-existing, unrelated to the current build: `tests/test_cards.py:81` indexes
`Card.treatment_classes` without a `None`-check, which mypy correctly flags — noticed 2026-09-03 while
building the judges, not caused by that work, and low-severity enough not to block it. Fix opportunistically.

Three low-severity housekeeping notes from the PRD v3 freeze-gate review are otherwise moot (they applied
to now-archived files) — see `archive/study-a-single-turn/README.md` if they need revisiting.

## Pending tests

83 tests passing (`harness/` unit/integration tests, VCR cassettes recorded for the Anthropic-hitting
ones — see `tests/cassettes/`), including new coverage for the gate judges, quality judges, Q1/derived
metrics, and the two new stopping-condition classifiers. All 13 `cards/*.json` files load and validate
against the `Card` model; ruff/mypy clean except the pre-existing `test_cards.py:81` finding noted above.
No dedicated tests yet for the R5 leakage check (not built) or Q4 (not built, deferred).
