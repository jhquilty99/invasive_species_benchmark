---
paths:
  - "**/*.py"
---

# Python conventions

- Python 3.11+. Type hints on all function signatures.
- Formatting/linting: `ruff` (format + check). Type checking: `mypy`.
- Dependencies declared in `pyproject.toml`, not loose `requirements.txt` files.
- No bare `except:` — catch specific exceptions.
- Prefer `pathlib.Path` over `os.path`.

This file is empty of project-specific patterns because there's no code yet — the first non-trivial
Python decision (project layout, dependency manager, test runner) should get a `DECISION-LOG.md` entry
and update this file's `Rule Updated` trail.
