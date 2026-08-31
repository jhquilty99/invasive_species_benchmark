#!/usr/bin/env bash
# Stop: run lint/typecheck/test after every turn. On failure, block stopping and hand
# the error back so Claude fixes itself without a prompt from the user. Skips fast when
# nothing relevant changed, and when there's no recognized project yet.
# (Python has no separate build step for a benchmark harness like this one — ruff+mypy+pytest
# cover lint/typecheck/test. A packaging build step can be added here if this ever ships a wheel.)
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

INPUT="$(cat)"
STOP_HOOK_ACTIVE="$(json_get "$INPUT" 'stop_hook_active')"

# Already looped once on this turn's Stop — let it stop rather than risk an infinite loop.
if [ "$STOP_HOOK_ACTIVE" = "true" ] || [ "$STOP_HOOK_ACTIVE" = "True" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

cd "$(git rev-parse --show-toplevel)"

# Skip early if nothing relevant changed (uncommitted, working-tree changes only —
# this is a per-turn check, not a full CI run).
CHANGED="$(git status --porcelain 2>/dev/null | grep -E '\.py$' || true)"
if [ -z "$CHANGED" ]; then
  exit 0
fi

FAILURES=""
NL=$'\n'

# --- Python (the only stack this project uses — see .claude/rules/python.md) ---
# Tools run via `uv run`, never invoked bare — Python is uv-only on this machine (see
# .claude/rules/python.md and the 2026-08-31 DECISION-LOG.md entry).
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || compgen -G "*.py" > /dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then
    RUFF_OUT="$(uv run ruff check . 2>&1)" || FAILURES="${FAILURES}${NL}--- ruff check ---${NL}${RUFF_OUT}"
    if [ -f "pyproject.toml" ] || [ -f "mypy.ini" ]; then
      MYPY_OUT="$(uv run mypy . 2>&1)" || FAILURES="${FAILURES}${NL}--- mypy ---${NL}${MYPY_OUT}"
    fi
    if [ -d "tests" ] && [ -n "$(find tests -name 'test_*.py' -print -quit 2>/dev/null)" ]; then
      PYTEST_OUT="$(uv run pytest -q 2>&1)" || FAILURES="${FAILURES}${NL}--- pytest ---${NL}${PYTEST_OUT}"
    fi
  else
    # Don't let a missing toolchain manager silently skip every check — that's
    # indistinguishable from everything passing. Fail loud instead.
    FAILURES="${FAILURES}${NL}--- uv ---${NL}Python files present but 'uv' is not on PATH; install uv to run ruff/mypy/pytest (see DEVELOPMENT.md)."
  fi
fi

if [ -n "$FAILURES" ]; then
  REASON="Turn-end check failed. Fix these before finishing:${FAILURES}"
  ESCAPED="$(json_escape "$REASON")"
  printf '{"hookSpecificOutput":{"hookEventName":"Stop","decision":"block","reason":"%s"}}\n' "$ESCAPED"
fi

exit 0
