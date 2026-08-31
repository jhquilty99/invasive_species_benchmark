---
paths:
  - "**/legal/**"
  - "**/data/**"
  - "**/scenarios/**"
---

# Domain: legally constrained management advice

- This benchmark grades LLM advice against real legal/regulatory constraints on invasive species
  management. Treat scenario/ground-truth data as the source of truth — don't "correct" a scenario's
  legal framing without a `DECISION-LOG.md` entry explaining the correction and its source.
- Cite the specific regulation/jurisdiction a scenario is testing against inside the scenario file itself,
  not just in a README, so scenarios stay self-contained as the set grows.
- Jurisdiction and regulation text changes over time — if a scenario encodes a legal rule, note the date
  the rule was current as of.
