---
paths:
  - "**/*.py"
---

# Python conventions

- Python is installed and run exclusively through `uv` — `uv python install`, `uv add`/`uv sync`,
  `uv run ...`. Never bare `pip`, `venv`, or `conda`. This machine's system `python`/`python3` resolve
  to non-functional Windows Store stub aliases; `uv` manages its own pinned interpreter and sidesteps
  that entirely.
- Python 3.11+. Type hints on all function signatures.
- Formatting/linting: `ruff` (format + check, default rule set — pyflakes + pycodestyle core, no extended
  rule plugins). Type checking: `mypy`, standard (non-strict) mode — real type errors are caught, but
  `mypy --strict`'s blanket "no implicit Any anywhere" is not enforced. Matches this file's own "type hints
  on all signatures" without going further, given the schedule.
- Dependencies declared in `pyproject.toml`, not loose `requirements.txt` files. Dev-only dependencies
  (`pytest`, `pytest-recording`/`vcrpy`, `ruff`, `mypy`) go in via `uv add --dev <pkg>`, landing in
  `pyproject.toml`'s `[dependency-groups]` — never hand-edited into the main dependency list.
- No bare `except:` — catch specific exceptions.
- Prefer `pathlib.Path` over `os.path`.

The dependency-manager decision is closed — see the 2026-08-31 `DECISION-LOG.md` entry ("Standardize
on uv for all Python installs/runs"). The rest of this file (layout, concurrency, data modeling, config,
testing, logging) was decided 2026-09-03 — see `DECISION-LOG.md`, "Python harness conventions locked" —
working through what PRD v4's harness (openevals + self-hosted Langfuse, §6) actually needs.

## Project layout

Single `pyproject.toml` at the repo root — one uv-managed project, one venv, one lockfile for everything
Python in this repo (not an isolated project under `harness/`). `harness/` is a **flat-layout package**:
it IS the import root (`import harness.judges`, not `import src.harness.judges`), matching PRD v4 §12's
own naming for the release-artifact directory exactly — no separate `src/` indirection.

```
harness/                       # the package itself
  __init__.py
  config.py                    # pydantic-settings Settings: API keys, Langfuse creds, from root .env
  models.py                    # pydantic v2: Card, Slot, GateResult, QualityScore, RunMetadata...
  cards.py                     # load + validate cards/*.json against models.py
  simulated_user.py            # slot classifier + slot-gated response generator (PRD §5.2)
  conversation.py              # openevals.run_multiturn_simulation wiring, stopping condition
  judges/
    __init__.py
    gates.py                   # G1-G5, isolated judge calls (R2 — no combined rubric call)
    quality.py                 # Q2-Q5 judge calls
    prompts/                   # versioned judge prompt text (R4: pinned judge prompt version per run)
  scoring.py                   # Q1 + all derived metrics — computed in code only, never judged (R3)
  sweep.py                     # sweep runner: ThreadPoolExecutor across (model x card) pairs
  leakage_check.py             # R5 transcript leakage check
  langfuse_client.py           # Langfuse SDK: dataset, tracing, run metadata (R4)
  scripts/                     # plain module entrypoints, no CLI framework
    run_sweep.py                 # uv run python -m harness.scripts.run_sweep
    run_leakage_check.py
    setup_annotation_queue.py
tests/
  conftest.py
  cassettes/                   # VCR-style recorded API responses (see Testing below)
  test_*.py
```

`cards/`, `results/`, and `infra/langfuse/` (PRD v4 §12) stay outside `harness/` — they're data/deployment
artifacts, not Python package contents.

## Concurrency

Individual functions (simulate one conversation, judge one gate) are plain synchronous code — no
`async`/`await` anywhere in `harness/`. Concurrency happens at exactly one place: `sweep.py`'s top-level
runner, using a `ThreadPoolExecutor` to parallelize across `(model, card)` pairs. If a future bottleneck
needs finer-grained concurrency, that's a new decision (log it), not a default to reach for.

## Data modeling

Pydantic v2 for every runtime data structure that crosses a validation boundary: cards loaded from
`cards/*.json`, gate/quality judge outputs, run metadata. Validates on load — a malformed card fails at
`cards.py`'s load step, not deep inside a sweep. Reuse the same models to generate the card JSON schema
PRD v4 §12 calls for (`cards/SCHEMA.md`'s machine-checkable counterpart), rather than maintaining the
schema by hand separately from the Python types.

## Config and secrets

A `pydantic-settings` `Settings` class in `harness/config.py` is the single source of truth for API keys
(OpenAI, Anthropic, Google, the open-weight host) and Langfuse credentials, loaded from a root `.env` /
real environment variables. Missing or malformed config fails fast at startup, not partway through a
sweep. This is a separate config surface from `infra/langfuse/.env` (which is docker-compose-only, for
bringing up the Langfuse stack itself) — the two are not the same `.env` file and should not be merged.

## Testing

`pytest`. Tests that would otherwise hit paid LLM APIs (OpenAI/Anthropic/Google/open-weight host, and
judge calls) use recorded cassettes (`pytest-recording` / `vcrpy`) under `tests/cassettes/` — record once
against the real API, replay on every normal test run. Re-recording a cassette is a deliberate, explicit
action (delete the cassette file and re-run with recording enabled), never an accidental side effect of
running the suite. No test hits a real paid API by default.

## Logging

Standard library `logging`, plain text format — no `structlog`, no JSON formatter. Structured, queryable
context per card/model/run (R1's "deciding evidence," R4's reproducibility metadata) is Langfuse's job via
its tracing and run metadata, not the application log's. Application logs stay for operator-facing
progress/error visibility while a sweep runs, not as the system of record for scores or evidence.
