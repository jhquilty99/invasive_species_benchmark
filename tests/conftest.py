"""Shared pytest configuration.

Wires `pytest-recording` (vcrpy under the hood) so every recorded HTTP
cassette lives under `tests/cassettes/`, in a subdirectory per test module —
regardless of how deeply test files end up nested. Record mode defaults to
`pytest-recording`'s own default, "none": cassettes are replayed, never
re-recorded, unless `--record-mode` is passed explicitly on the command
line. No test hits a real paid API by default.
"""

import os
from pathlib import Path

import anthropic
import pytest

CASSETTES_DIR = Path(__file__).parent / "cassettes"


@pytest.fixture(scope="module")
def vcr_cassette_dir(request: pytest.FixtureRequest) -> str:
    """Centralize cassettes under tests/cassettes/<test module name>/."""
    module_name = Path(str(request.node.fspath)).stem
    return str(CASSETTES_DIR / module_name)


@pytest.fixture
def anthropic_test_client() -> anthropic.Anthropic:
    """An `anthropic.Anthropic` client for VCR-marked tests.

    The Anthropic SDK validates auth headers locally before a request ever reaches vcrpy's HTTP
    interception layer, so a bare `anthropic.Anthropic()` fails even on cassette replay if
    `ANTHROPIC_API_KEY` isn't set in the environment — replaying a cassette doesn't remove the need
    for *some* key-shaped string. Falls back to a dummy value so replay works with no real
    credentials present; recording (`--record-mode=once`) needs a real `ANTHROPIC_API_KEY` exported
    into the environment, which is a deliberate, explicit action, never an accidental default.
    """
    return anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY", "test-key-for-cassette-replay")
    )
