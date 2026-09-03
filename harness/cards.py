"""Load and validate case cards (`cards/*.json`) against `harness.models.Card`."""

import json
from pathlib import Path

from harness.models import Card


def load_card(path: Path) -> Card:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Card.model_validate(data)


def load_cards(directory: Path) -> list[Card]:
    return [load_card(path) for path in sorted(directory.glob("*.json"))]
