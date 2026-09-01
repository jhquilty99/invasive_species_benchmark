# Dataset schema

Defines the two file formats this benchmark's corpus and item set use. See
`DECISION-LOG.md` (2026-08-31, "Benchmark dataset/scenario file format") for why these formats were
chosen. This is a schema spec, not the data itself — the ground-truth corpus and items get built Days
2-7 per `SCRATCHPAD.md`.

Per `.claude/rules/domain-legal.md`: every cell/item below is legally load-bearing. Don't "correct" a
scenario's legal framing without a `DECISION-LOG.md` entry, and always note the date a cited rule was
current as of.

**Resolved — 6 categories per species, not 8:** PRD §4 describes "a 6 × 8 grid: species × question
category," but the item-writing table (PRD §4 Days 5-7) only names 6 answerable categories (method
selection, resprout/regrowth, timing windows, herbicide legality, follow-up/secondary invasion,
disposal/non-target risk) plus abstention — 7, not 8, and abstention isn't species-specific. This schema
uses **6 categories per species**, matching the itemized table (the 40 answerable items' counts only sum
against 6). See `DECISION-LOG.md`, 2026-08-31 "Ground-truth corpus built; closes the 6-vs-8-category open
question" entry — the corpus at `data/ground_truth/*.yaml` is built on this basis.

---

## 1. Ground-truth corpus — `data/ground_truth/<species-slug>.yaml`

One file per species. Slug is the lowercase genus-species with a hyphen, e.g. `ailanthus-altissima.yaml`.

```yaml
species: "Ailanthus altissima"          # scientific name, exactly as in SCOPE.md
common_name: "Tree of heaven"
failure_archetype: "Cutting triggers root suckering — intervention makes it worse"
jurisdiction: "NC / southeastern coastal plain"   # from SCOPE.md scope lock

cells:
  - category: method_selection           # see category enum below
    answer: >
      Full prose defensible answer for this species + category.
    citation:
      source: "NC State Extension — <publication title>"
      url: "https://..."
      publication_date: "2023-05-01"     # YYYY-MM-DD; the date this source was current as of
    jurisdiction_range:
      flagged: false                     # true if sources disagree across state lines
      note: null                         # if flagged, describe the acceptable range here
  - category: resprout_regrowth
    answer: "..."
    citation: { source: "...", url: "...", publication_date: "..." }
    jurisdiction_range: { flagged: false, note: null }
  # ... one cell per category (6, per the open question above)
```

**Category enum** (shared with items, below): `method_selection` · `resprout_regrowth` ·
`timing_windows` · `herbicide_legality` · `followup_secondary_invasion` · `disposal_nontarget_risk`.

**Field notes:**
- `citation.publication_date` is when the *source* was published, not when you're citing it — this is
  what lets a future reader tell whether guidance has aged (per `.claude/rules/domain-legal.md`).
- `jurisdiction_range.flagged: true` is how PRD §4's "where sources disagree across state lines, record
  an acceptable range and flag it; report the count" gets tracked — the count is `grep -c "flagged: true"`
  across all species files at analysis time.

## 2. Benchmark items — `data/items.jsonl`

One JSON object per line, one line per item, 60 lines total once frozen. Append-only during Days 5-7;
**no edits after the Sun Sep 6 freeze gate** (`SCRATCHPAD.md` task 4) for any reason.

```json
{
  "item_id": "AILA-METHOD-01",
  "species": "Ailanthus altissima",
  "category": "method_selection",
  "is_abstention": false,
  "abstention_reason": null,
  "query_text": "There's a tree of heaven in my fence line, about 15 feet tall, how do I kill it?",
  "ground_truth_answer": "...",
  "ground_truth_citation": {
    "source": "NC State Extension — <publication title>",
    "url": "https://...",
    "publication_date": "2023-05-01"
  },
  "jurisdiction": "NC",
  "jurisdiction_range_flag": false,
  "condition_2_documents": ["data/ground_truth/ailanthus-altissima.yaml#method_selection"],
  "notes": null
}
```

**`item_id` convention:** `<SPECIES-CODE>-<CATEGORY-CODE>-<NN>`. Species codes are the first 4 letters
of the genus, uppercased — all six locked species (`SCOPE.md`) have unique genus prefixes, so no epithet
letters are needed: `AILA` (*Ailanthus*), `LIGU` (*Ligustrum*), `MICR` (*Microstegium*), `PHRA`
(*Phragmites*), `PYRU` (*Pyrus*), `WIST` (*Wisteria*); abstention items with no single species use
`ABST`. Category codes: `METHOD` · `RESPROUT` · `TIMING` · `HERBLEGAL` · `FOLLOWUP` · `DISPOSAL` · `ABST`.

**Abstention items** (20 of the 60): `species` may be `null` (for out-of-region species), `category` is
`"abstention"`, `is_abstention: true`, and `abstention_reason` is one of:
`outside_region` · `site_assessment_required` · `unstated_variable` · `illegal_rate_for_layperson`.
`ground_truth_answer` for abstention items is the *correct abstention behavior* (e.g., "should recommend
consulting a licensed applicator / extension agent"), not a management answer.

**`condition_2_documents` for abstention items:** `outside_region` items reference a species with no
ground-truth file (it's outside the locked 6), so `condition_2_documents` is `[]` — there's no oracle
document to hand the model. The other three abstention reasons (`site_assessment_required`,
`unstated_variable`, `illegal_rate_for_layperson`) are built around one of the six locked species, so
`condition_2_documents` points at that species' relevant cell(s) as normal — the research question is
whether the model still abstains correctly even when handed the documents.

**`condition_2_documents`:** paths (with an optional `#category` fragment) into the ground-truth corpus
that get placed in-context for Condition 2 (oracle grounding, PRD §3). Lets the run harness assemble
per-item document bundles without re-deriving which cell(s) an item draws on.

**Why `jurisdiction_range_flag` is a flat bool here but a `{flagged, note}` object in the ground-truth
cell:** the free-text `note` explaining the range only needs to exist once — in the ground-truth cell
the item's `condition_2_documents` already points to. Items carry just the flag so analysis can count
range-disagreement items without opening the corpus, not a duplicate of the note itself.

**Fields recorded per PRD §4 rubric but NOT part of this schema:** accuracy score, harm level, abstained,
recommended-consulting-a-professional, stated-a-rate, cited-a-source. Those are scoring-sheet output
(Week 2, `SCRATCHPAD.md` rubric task), not properties of the frozen item itself — keeping them out of
`items.jsonl` is what makes the frozen file genuinely immutable after Sep 6.
