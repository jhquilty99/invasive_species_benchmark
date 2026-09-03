# Scope lock

Locked scope for the multi-turn card-based benchmark (PRD v4). The scope-lock table and species table
below are extracted verbatim from `PRODUCT_REQUIREMENTS.md` §4; the working title and geography come from
the PRD's header and §1. The persona carries forward unchanged from PRD v3's scope lock — PRD v4 doesn't
restate it explicitly, but nothing in the pivot touches who the assistant is advising. This file exists so
the locked numbers are checkable at a glance without re-reading the full PRD. If any value here needs to
change, that's a scope-growth decision — see PRD §8 rule 2 ("no scope growth") and log it in
`DECISION-LOG.md` before editing this file.

Supersedes the PRD v3 scope lock this file held through 2026-09-02. See `DECISION-LOG.md`, 2026-09-03
"Pivot to multi-turn simulated-conversation methodology (PRD v4)".

**Working title:** A gated, card-grounded benchmark for multi-turn invasive species management advice
**Geography:** North Carolina / southeastern coastal plain
**Persona:** Private landowner, no pesticide applicator license

| Decision | Value |
|---|---|
| Species | 6 (Ailanthus depth axis + 5-species breadth set) |
| Lookalike arm | ~10 cards, 4 native/non-invasive species |
| Cards | 60–80 total (12–16 Ailanthus matrix + ~10 lookalike + breadth set) |
| Models | 4–6, at least one open-weight |
| Judge | LLM primary for the full sweep; human annotation validates a ~50-conversation sample |
| Expert validation | Second expert review of the cards themselves — out of reach this release, flagged as a limitation |

## Species (6, chosen for maximum divergence in correct action)

| Species | Common name | Failure archetype it probes |
|---|---|---|
| *Ailanthus altissima* | Tree of heaven | Cutting triggers root suckering — intervention makes it worse. Depth axis: 12–16 card matrix varying stem size, extent, and season. |
| *Ligustrum sinense* | Chinese privet | Secondary invasion after removal — the "now what" gap |
| *Microstegium vimineum* | Japanese stiltgrass | Annual, seed-bank driven — timing is everything |
| *Wisteria sinensis* | Chinese wisteria | Native lookalike (*W. frutescens*, American wisteria) — wrong ID, wrong action |
| *Pyrus calleryana* | Callery / Bradford pear | Rootstock resprouting after cut |
| *Phragmites australis* ssp. *australis* | Common reed (introduced lineage) | Subspecies matters; aquatic-adjacent → formulation legality |

All 6 species already have researched ground truth at `data/ground_truth/*.yaml`, reused directly as card
source material — no new species research needed for the depth or breadth cards.

## Lookalike arm (~10 cards, 4 species — fresh ground truth required)

Sumac, native wisteria (*Wisteria frutescens*), coral honeysuckle, Virginia creeper — native or
non-invasive plants where the correct behaviour is not to prescribe treatment. None have existing
ground-truth files in this repo.

**Pre-authorized cuts** (see PRD §8 rule 2 and §10 dated gate): if the harness + leakage check gate (Fri
Sep 5) isn't met, cut card-count target toward the low end of 60–80 rather than slipping the sweep date.
Card count is the correct thing to cut before the lookalike arm or the annotation work. No other scope
growth or shrinkage without a `DECISION-LOG.md` entry.

**Ship date:** ~Sunday, September 20, 2026 (buffer day; PRD §10's 17-day schedule targets Fri Sep 19).
