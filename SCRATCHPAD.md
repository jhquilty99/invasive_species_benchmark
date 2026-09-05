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
  ClickHouse `scores` table, and (corrected 2026-09-04, see `DECISION-LOG.md`'s "Corrected misdiagnosis"
  entry) per-turn trace/span data landed fine too — it's in the event-sourced `events_core`/`events_full`
  tables this "events_only mode" deployment's UI actually reads, not the empty legacy `traces` table the
  original diagnosis checked. The one real remaining gap is dataset-run-item linkage
  (`dataset_run_items_rmt` is empty — see open task above), not trace ingestion. Headline result: G1 (identity verified) failed
  on 9/13 cards (69%), matching the derived premature-prescription rate exactly — the model-under-test
  very often gives removal/introduction/identification answers without ever committing to which
  species it's talking about, which is exactly the RQ1 gap this benchmark is designed to catch.
- **Research questions expanded (2026-09-04):** `PRODUCT_REQUIREMENTS.md` §2 replaced the old RQ1-RQ3
  with RQ1-RQ6 plus two cross-cutting analyses (C1 capability scaling, C2 actionability-vs-safety); RQ1,
  RQ3, and C2 are primary. Added a new **oracle-contrast experimental arm** to RQ1 — the 30 removal
  cards each also run once per model with every decision-relevant slot disclosed upfront, no elicitation
  required — accepted as real scope growth (removal-set run volume 30 → 60, 84 total per model instead
  of 54). RQ6 (stability) is documented but deliberately not resourced this pass. Propagated through
  `SCOPE.md` and `cards/SCHEMA.md`. Full detail: `DECISION-LOG.md`, 2026-09-04 "Expanded research
  questions to RQ1-RQ6 + C1/C2; added oracle-contrast experimental arm."
- **Methodology eval + hardening pass (2026-09-04):** ran a full evaluation of whether the design as
  spec'd could answer RQ1-RQ6/C1/C2 reliably at target scale (see `reports/2026-09-03-first-pass-
  validation-findings.md` for the run this was evaluating). Findings and the resulting build are logged
  across several `DECISION-LOG.md` entries dated 2026-09-04: **G6** (new gate, RQ3's harmful-action-
  warning-omission sub-class), **Q4 built** (regulatory grounding, `harness/ground_truth.py` loads
  `data/ground_truth/*.yaml` directly), **oracle-contrast mechanism built** (`build_oracle_opening_
  message`, `make_simulated_user(..., oracle=True)`, `run_conversation(..., oracle=True)`,
  `start_dataset_run(..., arm=...)` — closes the "zero code exists" gap task 9 below was tracking),
  **repeated-sampling pilot** (`harness/scripts/run_repeat_pilot.py`, cheap RQ6-adjacent noise
  characterization — RQ6 itself stays cut), **RQ5 `referral_expected`/`referral_reason` schema fields +
  2 new cards** (real scope growth: 54 → 56 cards, 84 → 87 runs/model — logged same as the 2026-09-04
  oracle-arm growth), and **cross-vendor second judge deferred** to task 8 below (a same-vendor judge/
  subject optics risk, logged but not built this pass — `harness/config.py` already carries unused
  `openai_api_key`/`google_api_key` for when task 8 builds the real multi-vendor adapter). `JUDGE_
  PROMPT_VERSION` bumped v1 → v2. 126 tests passing (up from 83), all new judge-hitting tests
  cassette-recorded against the real API.
- **Last touched:** 2026-09-04 (methodology eval + hardening pass: G6, Q4, oracle-arm mechanism, repeat
  pilot, RQ5 schema/cards; corrected the Langfuse trace-ingestion misdiagnosis; made the simulated
  user's mid-conversation turns lazier/less polite; built the R5 leakage checker, a 3-vendor
  model-under-test client, and sweep persistence toward the SME-validation deliverable below)
- **SME-validation plan approved and partly built (2026-09-04):** the user asked for the fastest path
  to a properly human-validated dataset SMEs can review (see `DECISION-LOG.md`'s "Built R5 leakage
  check, multi-vendor model client, and sweep persistence..." entry for the full build list) — this
  **supersedes/narrows PRD §7's plan for tasks 10-11 below**, not just extends it: (1) the sample size is
  trimmed to ~20 conversations (not ~50), matching the ~2-hour ask `outreach/expert-validation-email.md`
  already promised the contacted SMEs — the user chose "trim the sample" over renegotiating that ask;
  (2) SMEs review a spreadsheet export, not the Langfuse annotation queue tasks 10-11 assumed, since
  external SMEs shouldn't need Langfuse accounts. Built so far: R5 leakage check
  (`harness/leakage_check.py`), a 3-vendor (Anthropic/OpenAI/Google) model-under-test dispatch
  (`harness/model_clients.py`, wired into `harness/conversation.py`), and sweep persistence
  (`harness/results_store.py`, `harness/sweep.py`). **Not yet built:** the stratified sample-selection
  logic, the SME-facing xlsx export, and the read-back script — all still open, see the tasks below.
  **Two picks need the user's confirmation before real budget is spent** (flagged in
  `harness/model_clients.py`'s `MODEL_VENDOR_MAP` docstring and the DECISION-LOG entry): `gpt-5.6-sol`
  substituted for the inaccessible `gpt-6-astra` (this project's OpenAI key 404s on it — re-pick if/when
  access lands), and `gemini-3.1-pro-preview` despite some sources describing a "Flash"-tier Gemini
  model as more capable this cycle.
- **Dry-run sweep complete, sample-selection logic built (2026-09-04):** the dry run (45 `(card, model)`
  pairs across the existing 15-card corpus × 3 models) finished with 0 R5 leakage flags, 0 duplicate
  keys — was blocked mid-run by an Anthropic Console spend-limit cap (not account balance; raising the
  limit is what actually unblocked it). `harness/sampling.py` + `harness/scripts/select_sme_sample.py`
  are built, tested, and run against that dry-run output — got 20/20 by redistributing the introduction
  stratum's shortfall (only 3 of 6 wanted available: 1 card × 3 models) into removal/identification.
  **This 20-item output is not send-ready** — introduction has no real per-card diversity yet, so
  authoring more `introduction` cards (open task below) still gates sending anything to SMEs. Full
  detail: `DECISION-LOG.md`, 2026-09-04 "Ran the SME-validation dry-run sweep to completion; built and
  ran stratified sample selection".
- **6 more `introduction` cards authored (2026-09-04):** closes the old task 1 blocker — the
  `introduction` set is now 7 cards (4 invasive, 3 native), with 3 of the 6 native/invasive pairs
  (privet/fringetree, Chinese/American wisteria, Callery pear/Chickasaw plum) fully covered on both
  sides. All 21 cards load, ruff/mypy clean, 158/158 tests pass. Full detail: `DECISION-LOG.md`,
  2026-09-04 "Authored 6 more `introduction`-type cards, unblocking real SME-sample diversity". The
  re-run sweep and sample selection this unblocked are now both complete — see the next two entries.
- **Real sweep complete over the 21-card corpus (2026-09-04):** `wip-2026-09-04-sme-validation-21card`
  finished 63/63 `(card, model)` pairs (21 cards × 3 models × standard arm), 0 R5 leakage flags, an even
  21/21/21 split across removal/introduction/identification. Survived an accidental mid-run interruption
  (the machine slept) with zero wasted spend — `run_sweep`'s existing per-`(card, model, arm)` resume
  logic picked up cleanly from the 29 pairs already on disk. Hit and fixed one real bug along the way:
  `judge_q4_regulatory_grounding` reproducibly failed on `phragmites-public-water-referral-01` ×
  `claude-opus-5` (extended thinking exhausting the 4096-token budget before any text output, given that
  card's unusually large ground-truth-plus-transcript prompt) — bumped `harness/judges/_common.py`'s
  `run_structured_judge_call` default `max_tokens` to 8192 (same fix pattern as the 2026-09-03 1024→4096
  bump) and it passed. Full detail: `DECISION-LOG.md`, 2026-09-04 "Ran the real (non-dry-run)
  SME-validation sweep over the expanded 21-card corpus; bumped judge call max_tokens 4096 -> 8192...".
- **Send-ready 20-item SME sample selected (2026-09-04):** re-ran `harness/scripts/select_sme_sample.py`
  against the completed 21-card sweep (no code changes needed beyond re-pointing its
  `CARD_SET_VERSION` constant) — closes the old task 1 blocker for real this time. Got 20/20 with
  genuine per-stratum diversity: 7 removal / 7 identification / 6 introduction, 12 flagged / 8
  unflagged. The introduction stratum specifically now spans 4 distinct cards across all 3 models,
  replacing the dry run's degenerate "1 card × 3 models" stratum. Selection written to
  `results/sweep/wip-2026-09-04-sme-validation-21card/sample_selection.json`. Full detail:
  `DECISION-LOG.md`, 2026-09-04 "Ran stratified sample selection against the real 21-card sweep: a
  genuinely send-ready 20-item SME sample". Still not blinded (model identity is real) and still needs
  the xlsx export — both already tracked below, not new scope.

## Open tasks (ranked)

1. Tune the slot classifier (`harness/simulated_user.py`) against the test cards until it reliably
   matches which slots were actually asked about — a live Day 1 run showed it can over-trigger on topic
   proximity rather than an explicit question. **Conditional**: the completed 21-card sweep showed 0/63 R5
   leakage flags (on top of the earlier dry run's 0/45), so this looks unnecessary — only revisit if
   leakage shows up in a future run.
2. **[SME-validation plan, next up]** Build the SME-facing xlsx export (`uv add openpyxl` first;
   `harness/scripts/build_sme_review_xlsx.py`, modeled on `archive/study-a-single-turn/scoring/
   build_checklist_xlsx.py` and `build_items_review_xlsx.py`): rubric/instructions sheet distilled from
   the judge prompts, a card-reference sheet, and per-question-type score-entry sheets with dropdown
   validation — blind to judge scores by construction, model identity coded as Model A/B/C per the
   user's choice. Depends on the now-complete sample selection (see Status above,
   `results/sweep/wip-2026-09-04-sme-validation-21card/sample_selection.json`).
3. **[SME-validation plan]** Build the read-back script (`harness/scripts/sync_sme_review_xlsx.py`,
   mirroring the archived `sync_items_from_xlsx.py`'s load/validate/merge pattern) once task 2's sheet
   layout is settled. Doesn't block sending the artifact to SMEs — build it any time before responses
   start coming back.
4. Fix `link_trace_to_dataset_run` (`harness/langfuse_client.py`): `dataset_run_items_rmt` is 0 rows in
   ClickHouse, so traces from the 2026-09-03 run were never actually grouped under a dataset run, even
   though the traces themselves are fine (see `DECISION-LOG.md`, 2026-09-04 "Corrected misdiagnosis" —
   the earlier "trace/span ingestion is broken" diagnosis was wrong; per-turn traces are populated and
   browsable in the Langfuse UI today, confirmed via direct ClickHouse query). Needs real investigation
   into why `client.api.dataset_run_items.create` isn't landing a row, before cross-run comparison in the
   Langfuse UI (PRD §6) works for any future run.
5. **[Gate — Fri Sep 5]** Harness + leakage check working end to end. Gate judges, quality judges,
   per-turn Langfuse tracing, a live 13-card validation run, and the R5 leakage checker are all done
   (see Status above); still blocked on the slot-classifier task above if it turns out to be needed. If
   not met, this is the day to cut card-count scope (PRD §8 rule 2), not later.
6. **[Days 6-9]** Author the remaining full 56-card matrix (beyond the 7-card SME-validation-slice
   `introduction` set already authored, see Status above): 31 removal cards total (6 invasive species ×
   5 condition variations, plus the `phragmites-public-water-referral-01` referral card — 7 already
   exist, 24 more needed), 12 introduction cards total (6 invasive + 6 native — 7 exist, 5 more needed:
   winged sumac, stiltgrass, whitegrass, and the 2 Phragmites subspecies), 13 identification cards total
   (12 species plus the `wisteria-dormant-vine-referral-01` referral card — 7 already exist, 6 more
   needed for the invasive species).
7. **[Gate — Thu Sep 11]** 56 cards complete, corpus frozen (PRD §8 rule 1) — no card changes after this
   point for any reason. (Was 54; +2 for the 2026-09-04 RQ5 `referral_expected` cards — see
   `DECISION-LOG.md`, 2026-09-04 "RQ5 referral_expected schema and card-count growth".)
8. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the eventual
   full 4-6 model line-up — the 3 vendors wired this session (`harness/model_clients.py`:
   Anthropic/OpenAI/Google) cover the non-open-weight slots but not this one, which PRD §4 locks as
   non-droppable. Also still open: the cross-judge-validation config knob the methodology eval flagged
   (a same-vendor judge/subject optics risk — judges stayed Anthropic-only this session, deliberately,
   per `DECISION-LOG.md`'s 2026-09-04 "Built R5 leakage check..." entry) — add a config knob to re-run
   `run_all_quality`/`run_all_gates` on existing trajectories with a second, different-vendor judge
   model, and report cross-judge-family agreement alongside the human-vs-judge Krippendorff's alpha (§7).
9. **[Days 10-11]** Full production sweep across the eventual 4-6 model line-up (incl. the open-weight
   model), both arms (standard + oracle) for the removal set — 87 conversation-model pairs per model,
   not 56. The sweep mechanism itself (`harness/sweep.py`, `harness/results_store.py`) is now built
   and proven across two real sweeps (the completed dry run and the completed 21-card SME-validation
   sweep, plus tasks 2-3 above) — this task is running it again at full scale once the corpus is frozen
   (task 7) and the full model line-up is wired (task 8). Fix what breaks; re-run. Confirm transcripts
   complete for every (model × card × arm) pair. Log the pinned card-set version, judge prompt version,
   and exact model version strings in run metadata (R4 — non-negotiable, carries forward PRD §8 rule 5).
10. **[Day 12, superseded in scope by the SME-validation plan above — re-evaluate once tasks 2-3 ship]**
    PRD §7's original plan: set up a Langfuse human-annotation queue, brief annotators, select a
    stratified ~50 sample. The SME-validation plan (the completed sweep and sample selection, tasks 2-3
    above, plus the already-completed introduction-card authoring) covers a trimmed ~20-item version of
    this same validation need via a spreadsheet instead of the Langfuse queue — decide whether this task
    is still needed on top of that (e.g. a second, larger/non-SME annotation pass) or fully superseded,
    once the SME sample is actually sent and results start coming back.
11. **[Days 13-14]** Human annotation, blind to judge scores. Write and run the Krippendorff's alpha
    computation per dimension, including Q6 (PRD §7) — now likely computed from task 3's read-back
    script output (the SME xlsx responses) rather than a Langfuse annotation queue, per the plan above.
12. **[Days 15-16]** Write-up: motivation, method, gates/quality design, results, failure examples (rates
    redacted per PRD §8 rule 3), limitations, generalization. Repo cleanup — assemble the PRD §12 release
    layout (`cards/`, `harness/`, `results/`, README with the schema documented standalone). Include the
    §5.4 reporting-granularity pre-registration (counts-only vs. CI'd metrics — PRD §5.4, added
    2026-09-04) so the analysis doesn't overclaim on the thin-cell metrics the methodology eval flagged.
13. **[Day 17]** Zenodo archive → DOI. Post to arXiv (cs.CL) and EcoEvoRxiv.
14. **[Added 2026-09-04]** Decide RQ6's (stability, PRD §2/§13) implementation scope — repeated-sampling
    budget per card and the new simulated-user behaviors ("corrects the model," "presses for a specific
    treatment") it needs — before committing any further sweep volume beyond the 2026-09-04 repeated-
    sampling pilot (`harness/scripts/run_repeat_pilot.py`, RQ6-adjacent noise characterization only, not
    RQ6 itself). Not blocking anything above; no dependency, just needs a decision before it's picked up.
15. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
    sent (currently still shows "Not sent" for all real contacts). No dependency on anything above — pure
    housekeeping, lowest priority.
16. **[Added 2026-09-04, found during `/commit` copy review]** `harness/simulated_user.py`'s
    `generate_user_response` tells the roleplay model it's "asking an AI assistant for help managing an
    **invasive plant**" in both branches' instruction text — in tension with `.claude/rules/card-voice.md`'s
    "Doesn't know it's invasive" rule for the persona it's playing. Pre-existing (predates the 2026-09-04
    tone tweak, not introduced by it); unclear yet whether it actually leaks into generated turns 1+ or is
    just an internal framing the model never echoes — needs a quick check against a few real transcripts
    before deciding whether to reword. Low priority, no dependency on anything above.
17. **[Added 2026-09-04, found during `/commit` architecture review]** `harness/simulated_user.py`'s
    `DEFAULT_MODEL` and `harness/conversation.py`'s `DEFAULT_INFRA_MODEL` are two independently-defined
    constants that happen to hold the same literal string (`"claude-haiku-4-5-20251001"`) today.
    `run_conversation` always threads `DEFAULT_INFRA_MODEL` down to the simulated user (so that's the
    constant this session's new Langfuse `simulated_user_classifier_model`/`simulated_user_responder_model`
    run-metadata fields are correctly sourced from), but `harness/leakage_check.py`'s R5 rescan calls
    `simulated_user.classify_asked_slots` directly and falls back to `simulated_user.DEFAULT_MODEL`
    instead — a real model this rescan runs against that no run-level metadata field currently names, and
    a silent-drift risk if either constant is ever bumped without the other. Worth either unifying to one
    constant or threading `leakage_check.check_leakage` a `model` param sourced the same way the other
    infra calls are. Low priority, no dependency on anything above.
18. **[Added 2026-09-04, found during `/commit` copy review of the new `introduction` cards]**
    `cards/ailanthus-stump-resprout-01.json`'s `ecological_framing_notes` (already committed, not part of
    that diff) describes tree-of-heaven seed as "wind/water-dispersed" — `data/ground_truth/
    ailanthus-altissima.yaml` documents seed-bank persistence and viability but never states a dispersal
    mechanism, so this claim isn't traceable to the cited source under `.claude/rules/domain-legal.md`'s
    citation rule. Caught while fixing the same unsourced-dispersal-mechanism issue in the new
    `ailanthus-altissima-introduction-01.json` card. Low priority, worth folding into a future citation
    audit pass rather than a one-off fix — no dependency on anything above.
19. **[Added 2026-09-04, found during `/commit` copy review of the Langfuse-tracing/sampling diff]**
    `harness/langfuse_client.py`'s `build_score_config_specs` docstring says "5 gates" — `GateID` (and
    the `GATE_SCORE_NAMES` list this function actually iterates) has 6 members (G1-G6) since G6 was
    added in an earlier session; the docstring was never updated to match. Pre-existing, not touched by
    the diff this was found in. Low priority, one-line fix whenever this file is next touched.

## Open bugs

**Simulated user leaks non-NC location (found 2026-09-04, evaluating answers by hand):** when the
transcript's location question prompts the simulated user (`harness/simulated_user.py`) for where the
plant/property is, it sometimes answers with a state or region other than North Carolina — occasionally
inventing one outright. `.claude/rules/card-voice.md` fixes geography globally as NC-only via `SCOPE.md`
(cards never restate it), and nothing in `simulated_user.py`'s prompt currently pins the roleplay model
to that constraint, so it's free to improvise. Needs a fix constraining the simulated user to always
answer "North Carolina" (or a vague NC-consistent phrase like "here" / "my area") for any
location/region/state question, and never name another state. Not yet scoped whether this also
double-checks as an R5 leakage-adjacent case (`harness/leakage_check.py`) — worth checking whether any
already-run transcripts leaked a wrong state before this is fixed.

Pre-existing, unrelated to the current build: `tests/test_cards.py:81` indexes
`Card.treatment_classes` without a `None`-check, which mypy correctly flags — noticed 2026-09-03 while
building the judges, not caused by that work, and low-severity enough not to block it. Fix opportunistically.

Three low-severity housekeeping notes from the PRD v3 freeze-gate review are otherwise moot (they applied
to now-archived files) — see `archive/study-a-single-turn/README.md` if they need revisiting.

## Pending tests

158 tests passing (up from 126 as of the 2026-09-04 methodology-eval hardening pass — `harness/`
unit/integration tests, VCR cassettes recorded for the Anthropic-hitting ones, including the new
G6/Q4/referral/oracle-arm cassettes — see `tests/cassettes/`), covering the gate judges (now G1-G6),
quality judges (now Q2-Q6, all six built), Q1/derived metrics, the two stopping-condition classifiers,
the oracle-contrast mechanism, the RQ5 `referral_expected` conditional judge blocks, per-trace judge
tracing (`tests/test_tracing.py`), and `harness/sampling.py`'s stratified selection logic (pure,
no-LLM tests — leakage exclusion, flagged oversampling, model round-robin, shortfall redistribution,
determinism). All 21 `cards/*.json` files load and validate against the `Card` model (13 + the 2 new
RQ5 referral cards + the 6 new 2026-09-04 `introduction` cards);
ruff/mypy clean except the pre-existing `test_cards.py:81` finding noted above. No dedicated tests yet
for the R5 leakage check (still not built).
