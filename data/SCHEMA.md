# Dataset schema

Defines the ground-truth corpus format this benchmark's card authoring draws on. See `DECISION-LOG.md`
(2026-08-31, "Benchmark dataset/scenario file format") for why this format was chosen, and 2026-09-03
"Pivot to multi-turn simulated-conversation methodology (PRD v4)" for why this file no longer documents a
benchmark-item format.

Per `.claude/rules/domain-legal.md`: every cell below is legally load-bearing. Don't "correct" a species
cell's legal framing without a `DECISION-LOG.md` entry, and always note the date a cited rule was current
as of.

**This file previously also documented `data/items.jsonl`'s single-turn item schema and the deferred
abstention-item format.** Both were part of PRD v3's single-turn design, now superseded — see
`DECISION-LOG.md`, 2026-09-03. That documentation, and the files it described, moved to
`archive/study-a-single-turn/SCHEMA.md` and `archive/study-a-single-turn/data/` for historical reference.
The new case-card schema (PRD v4, `cards/`) will get its own `cards/SCHEMA.md` when card authoring starts —
not yet written.

---

## Ground-truth corpus — `data/ground_truth/<species-slug>.yaml`

**Active — reused as source material for card authoring.** One file per species. Slug is the lowercase
genus-species with a hyphen, e.g. `ailanthus-altissima.yaml`.

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
  # ... one cell per category (6)
```

**Category enum:** `method_selection` · `resprout_regrowth` · `timing_windows` · `herbicide_legality` ·
`followup_secondary_invasion` · `disposal_nontarget_risk`.

**Field notes:**
- `citation.publication_date` is when the *source* was published, not when you're citing it — this is
  what lets a future reader tell whether guidance has aged (per `.claude/rules/domain-legal.md`).
- `jurisdiction_range.flagged: true` marks a cell where sources disagree across state lines; the count is
  `grep -c "flagged: true"` across all species files at analysis time.

**Species covered (6):** Ailanthus altissima, Ligustrum sinense, Microstegium vimineum, Phragmites
australis, Pyrus calleryana, Wisteria sinensis — see `SCOPE.md` for the full species table and failure
archetypes. The new lookalike-arm species (sumac, native wisteria, coral honeysuckle, Virginia creeper)
have no ground-truth file yet; authoring one for each is part of the PRD v4 timeline (§10).
