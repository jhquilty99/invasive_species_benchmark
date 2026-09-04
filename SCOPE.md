# Scope lock

Locked scope for the multi-turn card-based benchmark (PRD v4). The scope-lock table and species table
below are extracted verbatim from `PRODUCT_REQUIREMENTS.md` §4; the working title and geography come from
the PRD's header and §1. The persona carries forward unchanged from PRD v3's scope lock — PRD v4 doesn't
restate it explicitly, but nothing in the pivot touches who the assistant is advising. This file exists so
the locked numbers are checkable at a glance without re-reading the full PRD. If any value here needs to
change, that's a scope-growth decision — see PRD §8 rule 2 ("no scope growth") and log it in
`DECISION-LOG.md` before editing this file.

Supersedes the PRD v3 scope lock this file held through 2026-09-02. See `DECISION-LOG.md`, 2026-09-03
"Pivot to multi-turn simulated-conversation methodology (PRD v4)". The lookalike-arm section below
supersedes this file's own same-day "Lookalike arm restructured to a 1:1 species pairing" entry in turn
— see `DECISION-LOG.md`, 2026-09-03 "Card matrix restructured around question type × native status
(RQ1-3, Q6)".

**Working title:** A gated, card-grounded benchmark for multi-turn invasive species management advice
**Geography:** North Carolina / southeastern coastal plain
**Persona:** Private landowner, no pesticide applicator license

| Decision | Value |
|---|---|
| Species | 6 invasive + 6 native, each native paired 1:1 with an invasive counterpart |
| Card matrix | 56 total, fixed: 31 removal + 12 introduction + 13 identification — see matrix below |
| Models | 4–6, at least one open-weight |
| Judge | LLM primary for the full sweep; human annotation validates a ~50-conversation sample |
| Expert validation | Second expert review of the cards themselves — out of reach this release, flagged as a limitation |
| Oracle-contrast arm (RQ1) | Removal set (31 cards) also runs once per model with every decision-relevant slot disclosed upfront — 62 conversation runs for the removal set, 87 total per model. Added 2026-09-04, see `DECISION-LOG.md` that date; mechanism built and validated end-to-end same day. |
| RQ5 `referral_expected` cards | 1 removal + 1 identification card whose ground-truth-correct outcome is to decline and refer, not prescribe/identify — the source of the 54→56 card-count growth above. Added 2026-09-04, see `DECISION-LOG.md` that date. |

## Card matrix (56 cards, 3 question types × native status)

| Set | Question type | Species | Cards |
|---|---|---|---|
| 1 | Removal ("what do I do about this plant?") | 6 invasive only | 6 × 5 condition variations + 1 RQ5 referral card = 31 |
| 2 | Introduction ("should I plant/keep this?") | 6 invasive + 6 native = 12 | 12 |
| 3 | Identification ("what is this plant?") | 6 invasive + 6 native = 12 | 6 × 2 + 1 RQ5 referral card = 13 |
| | | | **56 total** |

This design answers the six research questions plus two cross-cutting analyses in
`PRODUCT_REQUIREMENTS.md` §2 (RQ1-RQ6, C1-C2) — see that section for the full list rather than
re-deriving the mapping here, since a second, independent restatement of the mapping is exactly what
drifted out of sync with the PRD once already (fixed 2026-09-04, see `DECISION-LOG.md` that date). In
short: set 3 (identification) + set 2 (introduction) + gate G1 + Q6 answer RQ2 (discrimination and
framing); set 1 (removal) + Q1/Q2/Q3/Q4 answer RQ1 (situational elicitation, including the oracle-contrast
arm below) and RQ4 (situational appropriateness).

## Invasive species (6, chosen for maximum divergence in correct action)

| Species | Common name | Failure archetype it probes |
|---|---|---|
| *Ailanthus altissima* | Tree of heaven | Cutting triggers root suckering — intervention makes it worse. Removal set varies stem size, extent, and season across its 5 conditions. |
| *Ligustrum sinense* | Chinese privet | Secondary invasion after removal — the "now what" gap |
| *Microstegium vimineum* | Japanese stiltgrass | Annual, seed-bank driven — timing is everything |
| *Wisteria sinensis* | Chinese wisteria | Native lookalike (*W. frutescens*, American wisteria) — wrong ID, wrong action |
| *Pyrus calleryana* | Callery / Bradford pear | Rootstock resprouting after cut |
| *Phragmites australis* ssp. *australis* | Common reed (introduced lineage) | Subspecies matters; aquatic-adjacent → formulation legality |

All 6 species already have researched ground truth at `data/ground_truth/*.yaml`, reused directly as card
source material — no new species research needed for the removal set.

## Native species (6, paired 1:1 with an invasive counterpart — fresh ground truth required)

Each native/non-invasive species is the plant a landowner in the study region could plausibly mistake
for its paired invasive — the mechanism that makes RQ2 (discrimination and framing) a per-species,
checkable fact rather than a generic "is this a treatment target" question. None have existing
ground-truth files in this repo.
Unlike the prior "lookalike arm" design (declining-to-prescribe only), native species now get the same
introduction and identification questions their invasive counterpart gets (set 2 and set 3 above) — they
no longer appear in the removal set, which stays invasive-only.

| Invasive | Native counterpart | Common name |
|---|---|---|
| *Ailanthus altissima* | *Rhus copallinum* (pending confirmation) | Winged sumac |
| *Ligustrum sinense* | *Chionanthus virginicus* | Fringetree |
| *Microstegium vimineum* | *Leersia virginica* | Whitegrass |
| *Wisteria sinensis* | *Wisteria frutescens* | Native (American) wisteria |
| *Pyrus calleryana* | *Prunus angustifolia* | Chickasaw plum |
| *Phragmites australis* ssp. *australis* | *Phragmites australis* ssp. *americanus* | Native Phragmites |

**Pre-authorized cuts** (see PRD §8 rule 2 and §10 dated gate): if the harness + leakage check gate (Fri
Sep 5) isn't met, cut condition variations per species (5 → 3) in the removal set before cutting an
entire question-type set or the native arm — the matrix is now uniform across species rather than
depth-vs-breadth, so the correct place to shrink is the per-species variation count, not a whole set.
No other scope growth or shrinkage without a `DECISION-LOG.md` entry.

**Ship date:** ~Sunday, September 20, 2026 (buffer day; PRD §10's 17-day schedule targets Fri Sep 19).
