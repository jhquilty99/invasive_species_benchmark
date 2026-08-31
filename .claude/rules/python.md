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
- Formatting/linting: `ruff` (format + check). Type checking: `mypy`.
- Dependencies declared in `pyproject.toml`, not loose `requirements.txt` files.
- No bare `except:` — catch specific exceptions.
- Prefer `pathlib.Path` over `os.path`.

The dependency-manager decision is closed — see the 2026-08-31 `DECISION-LOG.md` entry ("Standardize
on uv for all Python installs/runs"). What's still open is the `src/` stack layout and the first
`pyproject.toml`/test scaffold (see `SCRATCHPAD.md`).
