---
paths:
  - "**/legal/**"
  - "**/data/**"
  - "**/scenarios/**"
  - "**/cards/**"
---

# Domain: legally constrained management advice

- This benchmark grades LLM advice against real legal/regulatory constraints on invasive species
  management. Treat scenario/ground-truth data as the source of truth — don't "correct" a scenario's
  legal framing without a `DECISION-LOG.md` entry explaining the correction and its source.
- Cite the specific regulation/jurisdiction a scenario is testing against inside the scenario file itself,
  not just in a README, so scenarios stay self-contained as the set grows.
- Jurisdiction and regulation text changes over time — if a scenario encodes a legal rule, note the date
  the rule was current as of.
- A citation must support the *specific* claim it's attached to, not just be "a reasonable source for this
  species." Reusing a species' usual product-label/extension citation for a different, more specific legal
  claim (e.g. a licensing rule, a boundary-law question, a FIFRA misuse clause, an arborist-consultation
  recommendation) is the failure mode this line exists to catch — it produced three separate corrections in
  this repo's history (see `DECISION-LOG.md`: 2026-09-01 "Synced `data/items.jsonl`...", and 2026-09-01
  "Fix unsupported claims in ground-truth citations..."). Before writing or approving a citation, check
  that the specific quoted/paraphrased claim actually appears in that source — re-fetch and verify it,
  don't infer it from the source's general topic.
- This check is not satisfied by a later review pass alone — the freeze-gate review on 2026-09-01 found 5
  more instances of the same failure (`AILA-METHOD-02`, `MICR-HERBLEGAL-02`, `PHRA-METHOD-02`,
  `WIST-METHOD-01`, arguably `PHRA-ABST-02`) on the same day this rule was first written, meaning
  verification has to happen while writing the claim, not only when auditing it afterward.
- When a cell or item's answer draws specific claims from more than one source, name each source next to
  the claim it supports (inline in the `source` string, or a named secondary source in the prose) rather
  than picking one citation to represent the whole answer — the schema's single `citation` object per
  cell/item can't hold more than one, so this is the sanctioned way to keep every claim traceable.
