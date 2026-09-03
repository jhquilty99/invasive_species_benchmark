"""Pydantic v2 data models for case cards, judge outputs, and run metadata.

Source of truth for `cards/SCHEMA.md` — reused (per `.claude/rules/python.md`) to generate the
card JSON schema rather than maintaining it by hand in two places. Keep the two in sync.
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


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


class IntroductionClass(str, Enum):
    ENCOURAGED = "encouraged"
    NEUTRAL = "neutral"
    DISCOURAGED = "discouraged"
    HARMFUL_TO_ENCOURAGE = "harmful_to_encourage"


class QuestionType(str, Enum):
    REMOVAL = "removal"
    INTRODUCTION = "introduction"
    IDENTIFICATION = "identification"


class NativeStatus(str, Enum):
    INVASIVE = "invasive"
    NATIVE = "native"


class Q2Label(str, Enum):
    """Judge-output labels for a `removal` card. Q2's label set is `question_type`-conditional per
    `cards/SCHEMA.md` — an `introduction` card's judge gets its own label set (`IntroductionClass`'s
    four values plus a `declined` counterpart), not yet defined here since the Q2 judge itself isn't
    built (see `SCRATCHPAD.md`'s quality-judging task)."""

    ACCEPTABLE = "acceptable"
    SUBOPTIMAL_BUT_SAFE = "suboptimal_but_safe"
    INEFFECTIVE = "ineffective"
    HARMFUL = "harmful"
    DECLINED = "declined"


_REMOVAL_ONLY_FIELDS = (
    "treatment_classes",
    "required_specificity_elements",
    "expected_followup_plan",
    "water_present",
    "restricted_use_products",
)


class Card(BaseModel):
    """One expert-authored case (`cards/SCHEMA.md`). The model under test never sees this; the judge
    always does.

    Field requirements are conditional on `question_type` — see `cards/SCHEMA.md`'s field-by-field
    breakdown, enforced below by `_check_question_type_fields`: `removal` cards require the five
    removal-only fields and forbid `introduction_classes`; `introduction` cards require
    `introduction_classes` and forbid the five removal-only fields; `identification` cards forbid
    both. `ecological_framing_notes` is required on every card regardless of `question_type`.
    """

    card_id: str
    species: str
    true_species: str
    question_type: QuestionType
    native_status: NativeStatus
    opening_message: str
    slots: list[Slot]
    treatment_classes: dict[TreatmentClass, list[str]] | None = None
    """Per-card, not universal: which specific actions/products fall into each class depends on
    this card's situation (e.g. water proximity on a ditch-side privet card vs. a suburban Callery
    pear card) — never treat a class's contents as fixed across cards for the same species."""
    required_specificity_elements: list[str] | None = None
    expected_followup_plan: str | None = None
    water_present: bool | None = None
    restricted_use_products: list[str] | None = None
    introduction_classes: dict[IntroductionClass, list[str]] | None = None
    ecological_framing_notes: str

    @model_validator(mode="after")
    def _check_question_type_fields(self) -> Self:
        set_removal_fields = [
            f for f in _REMOVAL_ONLY_FIELDS if getattr(self, f) is not None
        ]
        if self.question_type == QuestionType.REMOVAL:
            missing = [f for f in _REMOVAL_ONLY_FIELDS if getattr(self, f) is None]
            if missing:
                raise ValueError(f"question_type 'removal' requires fields: {missing}")
            if self.introduction_classes is not None:
                raise ValueError(
                    "question_type 'removal' must not set introduction_classes"
                )
        elif self.question_type == QuestionType.INTRODUCTION:
            if self.introduction_classes is None:
                raise ValueError(
                    "question_type 'introduction' requires introduction_classes"
                )
            if set_removal_fields:
                raise ValueError(
                    f"question_type 'introduction' must not set removal-only fields: {set_removal_fields}"
                )
        elif self.question_type == QuestionType.IDENTIFICATION:
            if set_removal_fields:
                raise ValueError(
                    f"question_type 'identification' must not set removal-only fields: {set_removal_fields}"
                )
            if self.introduction_classes is not None:
                raise ValueError(
                    "question_type 'identification' must not set introduction_classes"
                )
        return self


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
    Q2_CLASSIFICATION = "classification"
    Q3_ACTIONABILITY = "actionability"
    Q4_REGULATORY_GROUNDING = "regulatory_grounding"
    Q5_FOLLOWUP = "followup"
    Q6_ECOLOGICAL_FRAMING = "ecological_framing"


class QualityScore(BaseModel):
    """Judge-graded 0-2 dimensions only (Q3-Q6).

    Q1 is derived in code, never judged (PRD R3). Q2 is a classification, not a graded score — see
    `Q2Classification` below. Q3 and Q5 apply to `removal` cards only (`not_applicable` otherwise,
    per `cards/SCHEMA.md`) — that conditional isn't modeled here yet since the quality judges
    themselves aren't built (see `SCRATCHPAD.md`'s quality-judging task); Q4 and Q6 apply to every
    `question_type`.
    """

    dimension: Literal[
        QualityDimension.Q3_ACTIONABILITY,
        QualityDimension.Q4_REGULATORY_GROUNDING,
        QualityDimension.Q5_FOLLOWUP,
        QualityDimension.Q6_ECOLOGICAL_FRAMING,
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
