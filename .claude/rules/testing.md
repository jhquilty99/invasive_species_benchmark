---
paths:
  - "**/*test*.py"
  - "**/tests/**"
---

# Testing conventions

- `pytest` is the test runner. Test files: `test_*.py` under `tests/`, mirroring the flat `harness/`
  package layout (see `.claude/rules/python.md`).
- A benchmark scoring/grading function gets a test asserting on at least one known-correct and one
  known-incorrect example input — this domain has real legal stakes, so silent scoring drift is the
  costliest failure mode here.
- Don't mock the LLM being benchmarked in a test that's supposed to validate scoring logic — use a fixed
  recorded response fixture instead, so scoring bugs aren't masked by a mock that always returns what the
  test expects.
