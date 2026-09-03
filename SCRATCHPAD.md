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
  13 load and validate (verified via `harness.cards.load_cards`). 35 tests passing; ruff/mypy clean. What's
  still open: the Q2/Q6/gate judges themselves aren't written yet (quality-judging and gate-judge tasks
  below), so none of this is scored end-to-end yet.
- **Last touched:** 2026-09-03 (first introduction-type card authored; all 3 question types now covered)

## Open tasks (ranked)

1. **[Day 2]** Tune the slot classifier (`harness/simulated_user.py`) against the test cards until it
   reliably matches which slots were actually asked about — a live Day 1 run showed it can over-trigger on
   topic proximity rather than an explicit question.
2. **[Day 2]** Implement the R5 leakage check in code (not judged): no card slot value may appear in a user
   turn that wasn't preceded by a matching elicitation. Pass it on the test-card harness.
3. **[Day 2]** Write the gate judge prompts (G1-G5 — identity verified, no spread-increasing action,
   aquatic-appropriate formulation, no restricted-use product to an unlicensed applicator, no fabricated
   citation), each a separate single-purpose judge call with the card in context (R2 — no combined rubric
   call), with G2-G5 scoring `not_applicable` outside removal cards per the `Card` model's `question_type`
   field (already implemented — see the Status note above). Every prompt must instruct the judge to put
   its deciding evidence in the score's `comment` field (R1 — non-negotiable).
4. **[Day 2]** Write the quality-dimension judging: Q2 as a judge classification, type-conditional per
   the `Card` model (5 treatment-class labels incl. `declined` for removal cards; a parallel 5-label
   encourage/discourage set for introduction cards; identification correctness for identification cards);
   Q3/Q5 as judge scores 0-2 with an R1 `comment` (removal cards only, `not_applicable` otherwise); the
   new Q6 (ecological framing, 0-2, all question types, scored against each card's
   `ecological_framing_notes`). Implement Q1 and the derived metrics (turns to recommendation,
   premature-prescription rate, distractor questions asked, hit-max-turns rate) in code, never judged
   (R3) — pending the open question on whether Q1 applies to identification cards at all
   (`PRODUCT_REQUIREMENTS.md` §13.5).
5. **[Day 2]** Instrument per-turn Langfuse tracing in `harness/conversation.py` and
   `harness/simulated_user.py`: every individual Anthropic call (model-under-test turn, slot classifier,
   response generator, stopping-condition classifier) should land as its own nested span/generation under
   the conversation's trace, not — as Day 1 shipped it — a single flat `output` blob covering the whole
   transcript, dumped by a one-off script outside the repo rather than the harness itself. Not required for
   the Fri Sep 5 gate below, but should land before the full sweep task (so every sweep run is properly
   traced from the start) and definitely before the human-annotation queue task (annotators need to review
   actual per-turn conversations, not a flat blob).
6. **[Gate — Fri Sep 5]** Harness + leakage check working end to end (the slot-classifier, leakage-check,
   gate-judge, and quality-judging tasks above all done, on top of Day 1's already-working harness). If not
   met, this is the day to cut card-count scope (PRD §8 rule 2), not later.
7. **[Days 6-9]** Author the remaining 54-card matrix: 30 removal cards total (6 invasive species × 5
   condition variations — 6 already exist as one-per-species starting cards, 24 more needed), 12
   introduction cards total (6 invasive + 6 native — 1 exists, 11 more needed), 12 identification cards
   total (same 12 species — 6 already exist as the migrated native cards, 6 more needed for the invasive
   species), drawing on existing `data/ground_truth/*.yaml` for all 12 species (invasive and native ground
   truth both complete).
8. **[Gate — Thu Sep 11]** 54 cards complete, corpus frozen (PRD §8 rule 1) — no card changes after this
   point for any reason.
9. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4-6 model
   line-up, and wire a model client for every provider in the line-up — needed before the full sweep task.
10. **[Days 10-11]** Full sweep across 4-6 models (incl. the open-weight model). Fix what breaks; re-run.
    Confirm transcripts complete for every (model × card) pair. Log the pinned card-set version, judge
    prompt version, and exact model version strings in run metadata (R4 — non-negotiable, carries forward
    PRD §8 rule 5).
11. **[Day 12]** Set up the Langfuse human-annotation queue; brief annotators; select the stratified ~50
    sample (oversampled on gate failures and `harmful` Q2 classifications, stratified across all 3
    question types).
12. **[Days 13-14]** Human annotation, blind to judge scores. Write and run the Krippendorff's alpha
    computation per dimension, including Q6 (PRD §7).
13. **[Days 15-16]** Write-up: motivation, method, gates/quality design, results, failure examples (rates
    redacted per PRD §8 rule 3), limitations, generalization. Repo cleanup — assemble the PRD §12 release
    layout (`cards/`, `harness/`, `results/`, README with the schema documented standalone).
14. **[Day 17]** Zenodo archive → DOI. Post to arXiv (cs.CL) and EcoEvoRxiv.
15. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
    sent (currently still shows "Not sent" for all real contacts). No dependency on anything above — pure
    housekeeping, lowest priority.

## Open bugs

_None._ Three low-severity housekeeping notes from the PRD v3 freeze-gate review are now moot (they applied
to now-archived files) — see `archive/study-a-single-turn/README.md` if they need revisiting.

## Pending tests

35 tests passing (`harness/` unit/integration tests, VCR cassettes recorded for the Anthropic-hitting
ones — see `tests/cassettes/`). All 13 `cards/*.json` files load and validate against the updated `Card`
model (verified 2026-09-03 via `harness.cards.load_cards`); ruff/mypy clean. No dedicated tests yet for
work not yet built: leakage check, gate/quality judges (incl. the new Q6), per-turn Langfuse tracing.
