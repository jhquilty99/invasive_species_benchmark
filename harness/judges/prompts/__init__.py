"""Versioned judge prompt text (PRD R4: pin the judge prompt version per run).

`gates.py` and `quality.py` hold the actual system prompts; this module just carries the version
stamp `harness/scripts/run_validation.py` records into `RunMetadata`/Langfuse run metadata. Bump this
any time a prompt in either module changes in a way that could move scores — the whole point of R4 is
that a run's metadata says exactly which prompt text produced its scores.
"""

JUDGE_PROMPT_VERSION = "v1"
