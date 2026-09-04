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
  **supersedes/narrows PRD §7's plan for tasks 8-9 below**, not just extends it: (1) the sample size is
  trimmed to ~20 conversations (not ~50), matching the ~2-hour ask `outreach/expert-validation-email.md`
  already promised the contacted SMEs — the user chose "trim the sample" over renegotiating that ask;
  (2) SMEs review a spreadsheet export, not the Langfuse annotation queue tasks 8-9 assumed, since
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

## Open tasks (ranked)

1. **[SME-validation plan, next up]** Run the dry run: `harness/sweep.py`'s `run_sweep` against the
   existing 15-card corpus × the 3 wired models (`claude-opus-5`/`gpt-5.6-sol`/`gemini-3.1-pro-preview`,
   pending the confirmation flagged above) × standard arm. Serves two purposes at once — rehearses the
   sweep/persistence/leakage-filter pipeline cheaply, and gives a real R5 leakage-rate baseline that
   decides task 2 below. Spends real API budget across all 3 vendors for the first time; get the model
   picks confirmed first.
2. Tune the slot classifier (`harness/simulated_user.py`) against the test cards until it reliably
   matches which slots were actually asked about — a live Day 1 run showed it can over-trigger on topic
   proximity rather than an explicit question. **Conditional on task 1's leakage baseline**: only invest
   here if that baseline shows leakage is systemic, not reflexively (see the approved plan's reasoning).
3. **[SME-validation plan]** Author ~5-6 more `introduction`-type cards (currently 1/12 exist) — the one
   real card-authoring gap for a ~20-item stratified sample across all 3 question types (removal and
   identification already have enough breadth at 7 cards each). Use the existing native-counterpart
   pairing table (`PRODUCT_REQUIREMENTS.md` §4) and the already-complete `data/ground_truth/*.yaml` for
   all 12 species — no new research needed. Can run in parallel with tasks 4-6 below; only needs to land
   before the real (non-dry-run) sweep.
4. **[SME-validation plan]** Build the stratified sample-selection logic (`harness/sampling.py` +
   `harness/scripts/select_sme_sample.py`): ~20 conversations, stratified across the 3 question types,
   oversampled on gate failures/`harmful` Q2, round-robin across the 3 models, excluding every
   `leakage_detected` result. Depends on task 1's real (non-dry-run) sweep output.
5. **[SME-validation plan]** Build the SME-facing xlsx export (`uv add openpyxl` first;
   `harness/scripts/build_sme_review_xlsx.py`, modeled on `archive/study-a-single-turn/scoring/
   build_checklist_xlsx.py` and `build_items_review_xlsx.py`): rubric/instructions sheet distilled from
   the judge prompts, a card-reference sheet, and per-question-type score-entry sheets with dropdown
   validation — blind to judge scores by construction, model identity coded as Model A/B/C per the
   user's choice. Depends on task 4's selection output.
6. **[SME-validation plan]** Build the read-back script (`harness/scripts/sync_sme_review_xlsx.py`,
   mirroring the archived `sync_items_from_xlsx.py`'s load/validate/merge pattern) once task 5's sheet
   layout is settled. Doesn't block sending the artifact to SMEs — build it any time before responses
   start coming back.
7. Fix `link_trace_to_dataset_run` (`harness/langfuse_client.py`): `dataset_run_items_rmt` is 0 rows in
   ClickHouse, so traces from the 2026-09-03 run were never actually grouped under a dataset run, even
   though the traces themselves are fine (see `DECISION-LOG.md`, 2026-09-04 "Corrected misdiagnosis" —
   the earlier "trace/span ingestion is broken" diagnosis was wrong; per-turn traces are populated and
   browsable in the Langfuse UI today, confirmed via direct ClickHouse query). Needs real investigation
   into why `client.api.dataset_run_items.create` isn't landing a row, before cross-run comparison in the
   Langfuse UI (PRD §6) works for any future run.
8. **[Gate — Fri Sep 5]** Harness + leakage check working end to end. Gate judges, quality judges,
   per-turn Langfuse tracing, a live 13-card validation run, and the R5 leakage checker are all done
   (see Status above); still blocked on the slot-classifier task above if it turns out to be needed. If
   not met, this is the day to cut card-count scope (PRD §8 rule 2), not later.
9. **[Days 6-9]** Author the remaining full 56-card matrix (beyond task 3's smaller SME-validation-only
   slice): 31 removal cards total (6 invasive species × 5 condition variations, plus the
   `phragmites-public-water-referral-01` referral card — 7 already exist, 24 more needed), 12
   introduction cards total (6 invasive + 6 native — 1 exists, 11 more needed, task 3 covers ~5-6 of
   these early), 13 identification cards total (12 species plus the `wisteria-dormant-vine-referral-01`
   referral card — 7 already exist, 6 more needed for the invasive species).
10. **[Gate — Thu Sep 11]** 56 cards complete, corpus frozen (PRD §8 rule 1) — no card changes after this
    point for any reason. (Was 54; +2 for the 2026-09-04 RQ5 `referral_expected` cards — see
    `DECISION-LOG.md`, 2026-09-04 "RQ5 referral_expected schema and card-count growth".)
11. Pick the specific open-weight model and host (Together.ai/Groq/Fireworks/local) for the eventual
    full 4-6 model line-up — the 3 vendors wired this session (`harness/model_clients.py`:
    Anthropic/OpenAI/Google) cover the non-open-weight slots but not this one, which PRD §4 locks as
    non-droppable. Also still open: the cross-judge-validation config knob the methodology eval flagged
    (a same-vendor judge/subject optics risk — judges stayed Anthropic-only this session, deliberately,
    per `DECISION-LOG.md`'s 2026-09-04 "Built R5 leakage check..." entry) — add a config knob to re-run
    `run_all_quality`/`run_all_gates` on existing trajectories with a second, different-vendor judge
    model, and report cross-judge-family agreement alongside the human-vs-judge Krippendorff's alpha (§7).
12. **[Days 10-11]** Full production sweep across the eventual 4-6 model line-up (incl. the open-weight
    model), both arms (standard + oracle) for the removal set — 87 conversation-model pairs per model,
    not 56. The sweep mechanism itself (`harness/sweep.py`, `harness/results_store.py`) is now built
    and used for the smaller SME-validation sweep (tasks 1-6 above) — this task is running it again at
    full scale once the corpus is frozen (task 10) and the full model line-up is wired (task 11). Fix
    what breaks; re-run. Confirm transcripts complete for every (model × card × arm) pair. Log the
    pinned card-set version, judge prompt version, and exact model version strings in run metadata (R4
    — non-negotiable, carries forward PRD §8 rule 5).
13. **[Day 12, superseded in scope by the SME-validation plan above — re-evaluate once tasks 1-6 ship]**
    PRD §7's original plan: set up a Langfuse human-annotation queue, brief annotators, select a
    stratified ~50 sample. The SME-validation plan (tasks 1-6) covers a trimmed ~20-item version of this
    same validation need via a spreadsheet instead of the Langfuse queue — decide whether this task is
    still needed on top of that (e.g. a second, larger/non-SME annotation pass) or fully superseded,
    once the SME sample is actually sent and results start coming back.
14. **[Days 13-14]** Human annotation, blind to judge scores. Write and run the Krippendorff's alpha
    computation per dimension, including Q6 (PRD §7) — now likely computed from task 6's read-back
    script output (the SME xlsx responses) rather than a Langfuse annotation queue, per the plan above.
15. **[Days 15-16]** Write-up: motivation, method, gates/quality design, results, failure examples (rates
    redacted per PRD §8 rule 3), limitations, generalization. Repo cleanup — assemble the PRD §12 release
    layout (`cards/`, `harness/`, `results/`, README with the schema documented standalone). Include the
    §5.4 reporting-granularity pre-registration (counts-only vs. CI'd metrics — PRD §5.4, added
    2026-09-04) so the analysis doesn't overclaim on the thin-cell metrics the methodology eval flagged.
16. **[Day 17]** Zenodo archive → DOI. Post to arXiv (cs.CL) and EcoEvoRxiv.
17. **[Added 2026-09-04]** Decide RQ6's (stability, PRD §2/§13) implementation scope — repeated-sampling
    budget per card and the new simulated-user behaviors ("corrects the model," "presses for a specific
    treatment") it needs — before committing any further sweep volume beyond the 2026-09-04 repeated-
    sampling pilot (`harness/scripts/run_repeat_pilot.py`, RQ6-adjacent noise characterization only, not
    RQ6 itself). Not blocking anything above; no dependency, just needs a decision before it's picked up.
18. Fix `outreach/EMAIL-TRACKER.md`'s Status/Date-sent columns to reflect the emails that were actually
    sent (currently still shows "Not sent" for all real contacts). No dependency on anything above — pure
    housekeeping, lowest priority.
19. **[Added 2026-09-04, found during `/commit` copy review]** `harness/simulated_user.py`'s
    `generate_user_response` tells the roleplay model it's "asking an AI assistant for help managing an
    **invasive plant**" in both branches' instruction text — in tension with `.claude/rules/card-voice.md`'s
    "Doesn't know it's invasive" rule for the persona it's playing. Pre-existing (predates the 2026-09-04
    tone tweak, not introduced by it); unclear yet whether it actually leaks into generated turns 1+ or is
    just an internal framing the model never echoes — needs a quick check against a few real transcripts
    before deciding whether to reword. Low priority, no dependency on anything above.

## Open bugs

Pre-existing, unrelated to the current build: `tests/test_cards.py:81` indexes
`Card.treatment_classes` without a `None`-check, which mypy correctly flags — noticed 2026-09-03 while
building the judges, not caused by that work, and low-severity enough not to block it. Fix opportunistically.

Three low-severity housekeeping notes from the PRD v3 freeze-gate review are otherwise moot (they applied
to now-archived files) — see `archive/study-a-single-turn/README.md` if they need revisiting.

## Pending tests

126 tests passing (up from 83 as of the 2026-09-04 methodology-eval hardening pass — `harness/`
unit/integration tests, VCR cassettes recorded for the Anthropic-hitting ones, including the new
G6/Q4/referral/oracle-arm cassettes — see `tests/cassettes/`), covering the gate judges (now G1-G6),
quality judges (now Q2-Q6, all six built), Q1/derived metrics, the two stopping-condition classifiers,
the oracle-contrast mechanism, and the RQ5 `referral_expected` conditional judge blocks. All 15
`cards/*.json` files load and validate against the `Card` model (13 + the 2 new RQ5 referral cards);
ruff/mypy clean except the pre-existing `test_cards.py:81` finding noted above. No dedicated tests yet
for the R5 leakage check (still not built).
