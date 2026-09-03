"""Pydantic v2 data models for case cards, judge outputs, and run metadata.

Source of truth for `cards/SCHEMA.md` — reused (per `.claude/rules/python.md`) to generate the
card JSON schema rather than maintaining it by hand in two places. Keep the two in sync.
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Slot(BaseModel):
    name: str
    value: str
    decision_relevant: bool
    description: str


class TreatmentClass(str, Enum):
    ACCEPTABLE = "acceptable"
    SUBOPTIMAL_BUT_SAFE = "suboptimal_but_safe"
    INEFFECTIVE = "ineffective"
    HARMFUL = "harmful"


class Q2Label(str, Enum):
    ACCEPTABLE = "acceptable"
    SUBOPTIMAL_BUT_SAFE = "suboptimal_but_safe"
    INEFFECTIVE = "ineffective"
    HARMFUL = "harmful"
    DECLINED = "declined"


class Card(BaseModel):
    """One expert-authored case (PRD v4 §5.1). The model under test never sees this; the judge always does."""

    card_id: str
    species: str
    true_species: str
    opening_message: str
    slots: list[Slot]
    treatment_classes: dict[TreatmentClass, list[str]]
    """Per-card, not universal: which specific actions/products fall into each class depends on
    this card's situation (e.g. water proximity on a ditch-side privet card vs. a suburban Callery
    pear card) — never treat a class's contents as fixed across cards for the same species."""
    required_specificity_elements: list[str]
    expected_followup_plan: str
    water_present: bool
    restricted_use_products: list[str]


class GateID(str, Enum):
    G1_IDENTITY_VERIFIED = "identity_verified"
    G2_NO_SPREAD_INCREASE = "no_spread_increase"
    G3_AQUATIC_FORMULATION = "aquatic_formulation"
    G4_RESTRICTED_USE_LICENSING = "restricted_use_licensing"
    G5_NO_FABRICATED_CITATION = "no_fabricated_citation"


class GateOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"


class GateResult(BaseModel):
    gate_id: GateID
    outcome: GateOutcome
    comment: str
    """Deciding evidence for this outcome — required per PRD R1, non-negotiable for every judged score."""


class QualityDimension(str, Enum):
    Q1_ELICITATION = "elicitation"
    Q2_TREATMENT_CLASS = "treatment_class"
    Q3_ACTIONABILITY = "actionability"
    Q4_REGULATORY_GROUNDING = "regulatory_grounding"
    Q5_FOLLOWUP = "followup"


class QualityScore(BaseModel):
    """Judge-graded 0-2 dimensions only (Q3-Q5).

    Q1 is derived in code, never judged (PRD R3). Q2 is a five-label classification, not a
    graded score — see `Q2Classification` below.
    """

    dimension: Literal[
        QualityDimension.Q3_ACTIONABILITY,
        QualityDimension.Q4_REGULATORY_GROUNDING,
        QualityDimension.Q5_FOLLOWUP,
    ]
    score: int = Field(ge=0, le=2)
    comment: str


class Q2Classification(BaseModel):
    label: Q2Label
    comment: str


class RunMetadata(BaseModel):
    card_set_version: str
    judge_prompt_version: str
    model_id: str
    run_timestamp: datetime
