"""Loader for `data/ground_truth/*.yaml` (PRD v4's card-authoring source material).

Q4 (regulatory grounding, `harness/judges/quality.py`) is the first thing in this codebase that
reads these files at run time rather than only as human source material for card authoring — every
cell already carries a dated `citation`, which is exactly what Q4 needs to check a model's
regulatory/legal/timing claims against.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel

from harness.models import Card

GROUND_TRUTH_DIR = Path(__file__).resolve().parent.parent / "data" / "ground_truth"


class GroundTruthCitation(BaseModel):
    source: str
    url: str
    publication_date: str
    """Kept as a raw string, not a `date` — some sources in these files carry a verified-current
    date with no publication date of their own (e.g. "verified current 2026-09-02, page carries no
    publication date" folded into `source`), so this field isn't guaranteed to parse as a clean
    ISO date."""


class JurisdictionRange(BaseModel):
    flagged: bool
    note: str | None = None


class GroundTruthCell(BaseModel):
    category: str
    answer: str
    citation: GroundTruthCitation
    jurisdiction_range: JurisdictionRange


class GroundTruth(BaseModel):
    species: str
    common_name: str
    failure_archetype: str
    jurisdiction: str
    cells: list[GroundTruthCell]


_SPECIES_SLUGS: dict[str, str] = {
    "Ailanthus altissima": "ailanthus-altissima",
    "Ligustrum sinense": "ligustrum-sinense",
    "Microstegium vimineum": "microstegium-vimineum",
    "Wisteria sinensis": "wisteria-sinensis",
    "Pyrus calleryana": "pyrus-calleryana",
    "Phragmites australis ssp. australis": "phragmites-australis",
    "Chionanthus virginicus": "chionanthus-virginicus",
    "Leersia virginica": "leersia-virginica",
    "Phragmites australis ssp. americanus": "phragmites-australis-americanus",
    "Prunus angustifolia": "prunus-angustifolia",
    "Rhus copallinum": "rhus-copallinum",
    "Wisteria frutescens": "wisteria-frutescens",
}
"""Explicit `true_species` -> `data/ground_truth/<slug>.yaml` mapping rather than a generic
slugify function — several of these species carry a "ssp." qualifier that a naive slugify would
mangle, and the species set is fixed and small (PRD v4 §4's 6 invasive + 6 native pairing), so an
explicit table is more robust than parsing the qualifier out programmatically."""


def load_ground_truth(
    species_slug: str, *, directory: Path = GROUND_TRUTH_DIR
) -> GroundTruth:
    path = directory / f"{species_slug}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return GroundTruth.model_validate(data)


def load_ground_truth_for_card(
    card: Card, *, directory: Path = GROUND_TRUTH_DIR
) -> GroundTruth:
    """Resolve and load the ground-truth file for `card.true_species`.

    Raises `KeyError` for a species with no entry in `_SPECIES_SLUGS` — every removal-set species
    (the only `question_type` Q4 scores, per `harness/judges/quality.py`) already has one, so this
    is a real authoring error, not a case to silently skip, if it's ever hit.
    """
    slug = _SPECIES_SLUGS.get(card.true_species)
    if slug is None:
        raise KeyError(
            f"No ground-truth slug mapping for species {card.true_species!r}; add it to "
            "harness.ground_truth._SPECIES_SLUGS."
        )
    return load_ground_truth(slug, directory=directory)
