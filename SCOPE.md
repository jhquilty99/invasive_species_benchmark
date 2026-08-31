# Scope lock

Frozen scope for the three-week benchmark. The scope-lock table and species table below are extracted
verbatim from `PRODUCT_REQUIREMENTS.md` §2; the working title, geography, and persona come from the PRD's
header; the pre-authorized cuts and ship date come from §6 and §10. This file exists so the locked numbers
are checkable at a glance without re-reading the full PRD. If any value here needs to change, that's a
scope-growth decision — see PRD §6 rule 2 ("no scope growth") and log it in `DECISION-LOG.md` before
editing this file.

**Working title:** Fluent and Wrong — Benchmarking LLM Management Advice in a Legally Constrained Domain
**Geography:** North Carolina / southeastern coastal plain
**Persona:** Private landowner, no pesticide applicator license

| Decision | Value |
|---|---|
| Species | 6 |
| Items | ~60 |
| Models | 4 |
| Conditions | 2 |
| Scored runs | 1 (second run on a 20-item subset for variance only) |
| Judge | Human primary; LLM secondary with agreement reported |
| Expert validation | Optional, 20-item spot check. Ships without it. |

## Species (6, chosen for maximum divergence in correct action)

| Species | Common name | Failure archetype it probes |
|---|---|---|
| *Ailanthus altissima* | Tree of heaven | Cutting triggers root suckering — intervention makes it worse |
| *Ligustrum sinense* | Chinese privet | Secondary invasion after removal — the "now what" gap |
| *Microstegium vimineum* | Japanese stiltgrass | Annual, seed-bank driven — timing is everything |
| *Phragmites australis* ssp. *australis* | Common reed (introduced lineage) | Subspecies matters; aquatic-adjacent → formulation legality |
| *Pyrus calleryana* | Callery / Bradford pear | Rootstock resprouting after cut |
| *Wisteria sinensis* | Chinese wisteria | Native lookalike (*W. frutescens*, American wisteria) — wrong ID, wrong action |

**Pre-authorized cuts** (see PRD §6 rule 2 and §10 dated gates): cut to 4 species if the ground-truth grid
isn't complete by Fri Sep 4; drop to 3 models if scoring isn't complete by Mon Sep 14. No other scope
growth or shrinkage without a `DECISION-LOG.md` entry.

**Ship date:** Sunday, September 20, 2026.
