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
  the harness" line hid ~7 separate pieces of engineering. Ranked by dependency/day order. None of the
  new-methodology work has started yet — everything below is Day 1 onward.
- **Last touched:** 2026-09-03 (task breakdown)

## Open tasks (ranked)

1. **[Day 1]** Scaffold the Python project: `pyproject.toml` via `uv`, flat `harness/` package layout, deps
   (`openevals`, Langfuse SDK, `pydantic`/`pydantic-settings`, `pytest`, `pytest-recording`, `ruff`, `mypy`)
   — per `.claude/rules/python.md`'s locked conventions. Closes the long-open "no code yet" gap noted in
   `DEVELOPMENT.md`.
2. **[Day 1]** Write the case-card schema (`cards/SCHEMA.md` + a validator): species/true identity,
   opening message, slots with a per-card decision-relevant-vs-distractor flag, the 4 treatment classes
   (acceptable/suboptimal-but-safe/ineffective/harmful) enumerated for the situation, required specificity
   elements, expected follow-up plan (PRD §5.1). Needed before any card — including the Day 1 test card —
   can be authored.
3. **[Day 1]** Decide the two PRD §13 open questions that gate harness design, before building the
   stopping condition and Q2 judge: (a) §13.2 — does an unranked "you could do X or Y" list count as a
   prescription? PRD's stated lean is no; confirm or override. (b) §13.3 — models that refuse outright need
   a `declined` Q2 category; define it now so the classifier isn't retrofitted after the sweep. (§13.1
   lookalike-arm rubric and §13.4 second-judge-model are lower-priority — can wait past Day 1.)
4. **[Day 1]** Hand-author one test card against the schema from task 2 — the fixture the rest of Day 1's
   harness work runs against end to end.
5. **[Day 1]** Build the slot-gated simulated user (PRD §5.2): a turn-level classifier that determines
   which slots the assistant actually asked about, feeding a response generator that's shown — and
   instructed to reveal — only newly-asked slots. This is what makes elicitation measurement (Q1) meaningful
   instead of a prompted persona volunteering information.
6. **[Day 1]** Wire the conversation loop: `openevals.run_multiturn_simulation` + the slot-gated user from
   task 5 + the stopping condition from task 3a, running end to end on the task 4 test card.
7. **[Day 1]** Wire the Langfuse SDK into the harness against the already-running self-hosted instance
   (`infra/langfuse/`): one dataset, one item per card (`input` = opening message/persona/slots,
   `expected_output` = ground truth), a run per (model × prompt version), score configs named to match the
   gate/quality dimensions so the UI cross-tabs across runs (PRD §6).
8. **[Day 2]** Tune the slot classifier from task 5 against the test card until it reliably matches which
   slots were actually asked about.
9. **[Day 2]** Implement the R5 leakage check in code (not judged): no card slot value may appear in a user
   turn that wasn't preceded by a matching elicitation. Pass it on the one-card harness.
10. **[Day 2]** Write the 5 gate judge prompts (G1-G5 — identity verified, no spread-increasing action,
    aquatic-appropriate formulation, no restricted-use product to an unlicensed applicator, no fabricated
    citation), each a separate single-purpose judge call with the card in context (R2 — no combined rubric
    call). Every prompt must instruct the judge to put its deciding evidence in the score's `comment` field
    (R1 — non-negotiable).
11. **[Day 2]** Write the quality-dimension judging: Q2 as a judge classification into the 4 treatment-class
    labels (+ `declined` from task 3b); Q3-Q5 as judge scores 0-2 with an R1 `comment`. Implement Q1 and the
    derived metrics (turns to recommendation, premature-prescription rate, distractor questions asked,
    hit-max-turns rate) in code, never judged (R3).
12. **[Gate — Fri Sep 5]** Harness + leakage check working end to end (tasks 1-11 done). If not met, this is
    the day to cut card-count scope (PRD §8 rule 2), not later.
13. **[Days 4-5]** Author the Ailanthus matrix: 12-16 cards varying stem size, extent, and season, holding
    species and correct-treatment-class logic constant per the task 2 schema.
14. **[Days 6-7]** Author the lookalike arm: fresh ground truth for sumac, native wisteria (*Wisteria
    frutescens*), coral honeysuckle, and Virginia creeper — none have existing `data/ground_truth/*.yaml`
    files — then ~10 cards where the correct behaviour is declining to prescribe treatment. Apply whatever
    task 3-adjacent decision gets made on §13.1 (own rubric vs. shared) once that's settled.
15. **[Days 8-9]** Author the breadth set (privet, stiltgrass, wisteria, Callery pear, Phragmites), drawing
    directly on the existing `data/ground_truth/*.yaml` for all 5 species. Target 60-80 cards total across
    depth + lookalike + breadth.
16. **[Gate — Thu Sep 11]** Card count in range, corpus frozen (PRD §8 rule 1) — no card changes after this
    point for any reason.
17. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the 4-6 model
    line-up, and wire a model client for every provider in the line-up — needed before task 18.
18. **[Days 10-11]** Full sweep across 4-6 models (incl. the open-weight model). Fix what breaks; re-run.
    Confirm transcripts complete for every (model × card) pair. Log the pinned card-set version, judge
    prompt version, and exact model version strings in run metadata (R4 — non-negotiable, carries forward
    PRD §8 rule 5).
19. **[Day 12]** Set up the Langfuse human-annotation queue; brief annotators; select the stratified ~50
    sample (oversampled on gate failures and `harmful` Q2 classifications).
20. **[Days 13-14]** Human annotation, blind to judge scores. Write and run the Krippendorff's alpha
    computation per dimension (PRD §7).
21. **[Days 15-16]** Write-up: motivation, method, gates/quality design, results, failure examples (rates
    redacted per PRD §8 rule 3), limitations, generalization. Repo cleanup — assemble the PRD §12 release
    layout (`cards/`, `harness/`, `results/`, README with the schema documented standalone).
22. **[Day 17]** Zenodo archive → DOI. Post to arXiv (cs.CL) and EcoEvoRxiv.
23. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
    sent (currently still shows "Not sent" for all real contacts). No dependency on anything above — pure
    housekeeping, lowest priority.

## Open bugs

_None._ Three low-severity housekeeping notes from the PRD v3 freeze-gate review are now moot (they applied
to now-archived files) — see `archive/study-a-single-turn/README.md` if they need revisiting.

## Pending tests

_None yet — no code to test._
