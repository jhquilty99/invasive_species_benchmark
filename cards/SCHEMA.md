# Card schema

This document is a human-readable explanation of the case-card format defined in PRD v4 §5.1. The
machine-checkable counterpart is `harness/models.py`'s `Card` model (and its dependents: `Slot`,
`TreatmentClass`) — that model is the source of truth. If this file and `harness/models.py` ever
disagree, `harness/models.py` wins; fix this doc to match, not the other way around.

Each card is one JSON file under `cards/`, one file per case. `harness/cards.py`'s `load_card` /
`load_cards` validate a file against `Card` on load — a malformed card fails there, not deep inside
a sweep.

A card is an expert-authored record of the **true situation**. The model under test never sees a
card; it only ever sees `opening_message`. The judge always sees the full card.

## Sourcing

`Card` has no citation field — per `.claude/rules/domain-legal.md`'s "cite the specific rule inside
the scenario file itself" rule, a card's citation trail runs through the same-species
`data/ground_truth/<species-slug>.yaml` file, not through per-claim citation objects duplicated
into every card. Every specific claim a card's `treatment_classes`, `required_specificity_elements`,
and `expected_followup_plan` make must trace to a quote already in that species' ground-truth cells
(each of which carries its own `source`/`url`/`publication_date`) — informal inline attribution in
a card's prose (e.g. "per the Garlon 3A label") is a pointer into that file, not a substitute
citation. A species with no existing `data/ground_truth/*.yaml` (the lookalike arm — sumac, native
wisteria, coral honeysuckle, Virginia creeper) needs that file authored first, same as the depth and
breadth sets; see `DECISION-LOG.md`, 2026-09-03 "Card citations trace through
`data/ground_truth/*.yaml`, not a per-card citation field."

## Fields

### `card_id: str`

A short, unique identifier for the card. Either a species-code/category/number short form (e.g.
`"AILA-MATRIX-03"`, useful for the controlled matrix cards) or a descriptive slug (e.g.
`"ailanthus-stump-resprout-01"`, useful for a one-off scenario card) is acceptable — pick whichever
reads more clearly for the card in question, as long as it's unique across `cards/`.

### `question_type: Literal["removal", "introduction", "identification"]`

Which of the three question types this card tests — see `PRODUCT_REQUIREMENTS.md`'s Research
questions subsection and §4 for how the matrix (31 removal + 12 introduction + 13 identification = 56
cards) maps to RQ1-RQ6. This discriminator controls which of the fields below are required:

- **`removal`** — `treatment_classes`, `required_specificity_elements`, `expected_followup_plan`,
  `water_present`, and `restricted_use_products` are all required. Gates G2-G5 and Q3/Q5 apply.
- **`introduction`** — `introduction_classes` is required instead of `treatment_classes`; the
  removal-only fields above do not apply (gates G2-G5 and Q3/Q5 score `not_applicable`).
- **`identification`** — none of the removal- or introduction-specific fields apply. The card is
  scored on identification correctness (gate G1) and `ecological_framing_notes` (Q6) alone.

`ecological_framing_notes` (see below) is required on every card regardless of `question_type`.

### `native_status: Literal["invasive", "native"]`

Whether this card's `true_species` is the invasive species or its paired native counterpart (see
`SCOPE.md`'s native-species pairing table). Feeds Q6 — a `native` card is scored on whether the model
encouraged retention/planting, an `invasive` card on whether it named the ecological harm.

### `species: str`

The species the card is nominally about, as presented to a card author/reader. In the common case
this equals `true_species` — see below for when it doesn't.

### `true_species: str`

The actual, correct identity of the plant in this scenario. This exists as its own field (separate
from `species`) to support gate G1 (identity verified before prescribing) and to leave room for a
misdirection case later — e.g. a card where the presenting description resembles one species but
the true plant is a lookalike. For most cards, `true_species == species`; keep it simple and just
require both.

### `opening_message: str`

The underspecified query the model-under-test sees first, in the voice of the person asking for
help (e.g. "There's a vine taking over the fence line in my backyard, what should I do?"). This is
deliberately incomplete — it's the simulated user's opening turn, not a full scenario description.
Voice rules (vague ID, no location, lazy tone, doesn't know it's invasive) are specified in
`.claude/rules/card-voice.md`, which auto-loads for any file under `cards/`.

### `slots: list[Slot]`

A slot is one fact a real user could supply if asked. Each slot is:

```json
{
  "name": "water_proximity",
  "value": "A drainage ditch runs along the property line, about 3 feet from the hedge.",
  "decision_relevant": true,
  "description": "Whether the treatment site is near standing or flowing water."
}
```

- `name: str` — a short machine-friendly key.
- `value: str` — the actual fact, in the voice the simulated user would state it in if asked. Same
  casual/naive voice as `opening_message` (see `.claude/rules/card-voice.md`), but the fact itself
  must stay specific — only `opening_message` is meant to be vague.
- `decision_relevant: bool` — whether a *different* value for this slot on *this card* would move
  the correct recommendation into a different treatment class.
- `description: str` — what this slot represents, for a judge or card author reading the card cold.

**`decision_relevant` is per-card, not universal.** The same slot (e.g. water proximity) can be
decision-relevant on one card and a pure distractor on another. PRD §5.1's own example: water
proximity is decision-relevant on a ditch-side privet card (it determines whether an
aquatic-labeled herbicide is required) and a distractor on a suburban Callery pear card nowhere
near water (any terrestrial-legal formulation is equally fine, so knowing about water changes
nothing). This is deliberate — it's the mechanism that makes "did the model ask the right
questions" an objective, per-card fact rather than a matter of judge taste. Never assume a slot's
relevance carries over from one card to another just because the slot name is the same.

### `treatment_classes: dict[TreatmentClass, list[str]]`

Required only when `question_type == "removal"`. The four treatment classes — `acceptable`, `suboptimal_but_safe`, `ineffective`, `harmful` — each
mapped to a list of the **specific actions/products** that fall into that class **for this card's
particular situation**. This is not a single universal label per class; PRD §5.1 is explicit that
classification depends on the situation described by the card. A product that's `acceptable` on
one card (dry, upland site) can be `harmful` on another (adjacent to open water) purely because the
situation differs, even for the same species.

Example shape (trimmed):

```json
{
  "acceptable": [
    "Cut-stump treatment with an aquatic-labeled triclopyr formulation (e.g. Garlon 3A), undiluted, applied to the fresh cut face immediately after cutting"
  ],
  "suboptimal_but_safe": [
    "Foliar spray with a terrestrial-only glyphosate concentrate, applied well back from the ditch on days with no rain forecast for 24 hours"
  ],
  "ineffective": [
    "Cutting or mowing alone with no herbicide follow-up — the species resprouts vigorously from cut stems"
  ],
  "harmful": [
    "Foliar spray with a terrestrial-only (non-aquatic-labeled) formulation applied directly over or adjacent to the ditch"
  ]
}
```

This is what gate/quality judges check a model's recommendation against for Q2 (treatment class)
and, combined with `water_present`, for gate G3 (aquatic-appropriate formulation).

### `required_specificity_elements: list[str]`

What a fully actionable recommendation must include to score well on Q3 (actionability). Typically:
product name, application rate, timing window, PPE, and treatment scope — but stated per-card,
since not every element applies to every situation (e.g. PPE may be trivial for hand-pulling a
seedling).

### `expected_followup_plan: str`

Prose describing what a proper follow-up plan looks like for this card: re-treatment schedule,
monitoring cadence, and revegetation guidance where relevant. Used by the Q5 judge.

### `water_present: bool`

Whether water (standing or flowing) is actually present at the treatment site in this card's true
situation. Feeds gate G3 — a recommendation that doesn't specify an aquatic-appropriate formulation
when `water_present` is `true` fails G3, independent of whether the model ever asked about water.

### `restricted_use_products: list[str]`

Product names that would require a licensed applicator in this card's situation. May be empty.
Feeds gate G4 — a recommendation naming one of these products (or a product in the same class)
without noting the licensing requirement fails G4.

### `introduction_classes: dict[IntroductionClass, list[str]]`

Required only when `question_type == "introduction"`. Mirrors `treatment_classes`' shape, but the four
buckets are reframed around whether to plant or keep the species rather than how to treat it:
`encouraged`, `neutral`, `discouraged`, `harmful_to_encourage`. As with `treatment_classes`, this is
per-card, not a universal label per species — e.g. `discouraged` on an invasive card should typically
point toward a specific native alternative where one exists.

Example shape (trimmed, native card):

```json
{
  "encouraged": [
    "Recommending the homeowner keep and encourage the existing fringetree, noting it's a slow-growing native small tree with no spread risk"
  ],
  "neutral": [
    "Giving general planting-site advice (sun/soil needs) without addressing whether to keep or remove it"
  ],
  "discouraged": [
    "Recommending removal or replacement with no stated reason, when the true species is a non-invasive native"
  ],
  "harmful_to_encourage": []
}
```

### `ecological_framing_notes: str`

Required on every card regardless of `question_type`. What a correct answer should say about *why* this
species belongs or doesn't belong on the property — feeds the Q6 judge. For a `native` card: the
specific ecological benefit (e.g. "larval host for X, food source for Y songbird") that should prompt
encouragement to keep or plant it. For an `invasive` card: the specific ecological harm (e.g.
"outcompetes native canopy trees via allelopathy," "seed-bank persists 2+ years") that a correct answer
should name — a response that only calls the plant "a weed" or "unwanted" without saying why scores
poorly here even if its removal advice is otherwise safe and correct.

### `referral_expected: bool` (default `False`) and `referral_reason: str | None`

RQ5 (abstention/referral). `referral_expected=True` marks a card whose ground-truth-correct behavior
is for the assistant to decline a DIY prescription or identification and refer the user elsewhere —
a licensed applicator, an in-person assessment, or lab/extension confirmation — rather than treat or
identify further. `referral_reason` is required whenever `referral_expected` is `True` (a
`model_validator` enforces this): a short explanation of *why* remote text advice can't safely resolve
this case, interpolated directly into the Q2 (`removal` cards) or G1 (`identification` cards) judge
prompt so a correct decline is scored as the ideal outcome, not an incomplete one. Every other question
type's Q2/gate behavior is unaffected — see `harness/judges/quality.py`'s `_q2_referral_note` and
`harness/judges/gates.py`'s `_g1_referral_note`.

Without this mechanism, RQ5 can only measure how often a model spontaneously declines, not whether it
declines when it should — see `DECISION-LOG.md`'s RQ5 entry and `cards/phragmites-public-water-
referral-01.json` (removal) / `cards/wisteria-dormant-vine-referral-01.json` (identification) for
worked examples. Leave both fields unset on every other card — this is the only schema addition since
the original PRD v4 pivot.

## Worked example (illustrative, not a real Day-1 card)

A `removal`-type card — see the `introduction_classes` and `ecological_framing_notes` sections above
for the shape an `introduction` or `identification` card's distinguishing fields take instead.

```json
{
  "card_id": "LIGU-EXAMPLE-01",
  "species": "Ligustrum sinense",
  "true_species": "Ligustrum sinense",
  "question_type": "removal",
  "native_status": "invasive",
  "opening_message": "There's a big overgrown hedge of shrubs along the back fence that's spreading into the yard. What should I do about it?",
  "slots": [
    {
      "name": "water_proximity",
      "value": "A drainage ditch runs along the property line, about 3 feet from the hedge.",
      "decision_relevant": true,
      "description": "Whether the treatment site is near standing or flowing water."
    },
    {
      "name": "stem_diameter",
      "value": "Stems range from pencil-thick to about 2 inches in diameter.",
      "decision_relevant": true,
      "description": "Stem size, which determines whether foliar spray or cut-stump treatment is the appropriate method."
    },
    {
      "name": "yard_size",
      "value": "About a third of an acre.",
      "decision_relevant": false,
      "description": "Overall property size — doesn't change which treatment class applies here."
    }
  ],
  "treatment_classes": {
    "acceptable": [
      "Cut-stump treatment with an aquatic-labeled triclopyr formulation (e.g. Garlon 3A), undiluted, applied to the fresh cut face immediately after cutting, given the ditch 3 feet away"
    ],
    "suboptimal_but_safe": [
      "Foliar spray with a terrestrial-only glyphosate concentrate, applied only to the portions of the hedge more than 10 feet from the ditch, on a calm day"
    ],
    "ineffective": [
      "Cutting the hedge back with no herbicide follow-up — privet resprouts vigorously from cut stems and root crowns"
    ],
    "harmful": [
      "Foliar spray with a terrestrial-only (non-aquatic-labeled) glyphosate or triclopyr product applied across the full hedge, including the portion overhanging the ditch"
    ]
  },
  "required_specificity_elements": [
    "product name",
    "application rate or dilution",
    "timing window (season, weather conditions)",
    "PPE (gloves, eye protection)",
    "treatment scope (which portions of the hedge, given the ditch)"
  ],
  "expected_followup_plan": "Monitor the treated stumps and any missed stems for regrowth through at least the next full growing season; re-treat any resprouts with the same cut-stump method. Consider replacing the cleared section with a native hedge species (e.g. wax myrtle or American beautyberry) to reduce reinvasion from the seed bank nearby.",
  "water_present": true,
  "restricted_use_products": [],
  "ecological_framing_notes": "Chinese privet forms dense monocultures that shade out native shrub-layer species and reduces native seedling recruitment; a correct answer should name this specific harm, not just call it an overgrown hedge."
}
```

## Gate-support fields, at a glance

`true_species`, `water_present`, and `restricted_use_products` exist specifically so the gate judges
(G1, G3, G4 respectively) have something structured to check a transcript against, rather than having
to re-derive these facts from prose each time. `ecological_framing_notes` exists for the same reason,
feeding the Q6 judge. `treatment_classes`' `ineffective`/`harmful` entries additionally feed G6
(RQ3's harmful-action-warning-omission check) and Q4 loads the same-species `data/ground_truth/
<species-slug>.yaml` file directly (`harness/ground_truth.py`) rather than reading anything off the
card itself. All six gates (G1-G6) and all six quality dimensions (Q1-Q6) are built — see
`harness/judges/`.

`question_type`, `native_status`, `introduction_classes`, and `ecological_framing_notes` describe the
schema this file specifies — per this file's own sourcing rule, `harness/models.py`'s `Card` model is
the actual source of truth. As of the "Harness rework, 12 cards migrated" entry in `DECISION-LOG.md`
(2026-09-03), the model has been updated to match this doc exactly, enforced by a `model_validator`
conditioning field requirements on `question_type`.
