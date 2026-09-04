"""Pydantic v2 data models for case cards, judge outputs, and run metadata.

Source of truth for `cards/SCHEMA.md` — reused (per `.claude/rules/python.md`) to generate the
card JSON schema rather than maintaining it by hand in two places. Keep the two in sync.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Self

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
    """Judge-output labels for a `removal` card."""

    ACCEPTABLE = "acceptable"
    SUBOPTIMAL_BUT_SAFE = "suboptimal_but_safe"
    INEFFECTIVE = "ineffective"
    HARMFUL = "harmful"
    DECLINED = "declined"


class IntroductionQ2Label(str, Enum):
    """Judge-output labels for an `introduction` card — mirrors `IntroductionClass`'s four values
    plus a `declined` counterpart, matching `Q2Label`'s shape for `removal` cards.

    `identification` cards score Q2 `not_applicable` (structural, no label set of their own) — see
    `harness/judges/quality.py` and `DECISION-LOG.md`'s "First-pass LLM-as-judge validation" entry.
    """

    ENCOURAGED = "encouraged"
    NEUTRAL = "neutral"
    DISCOURAGED = "discouraged"
    HARMFUL_TO_ENCOURAGE = "harmful_to_encourage"
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
    referral_expected: bool = False
    """True when this card's ground-truth-correct behavior is to decline a DIY prescription/
    identification and refer the user to a licensed applicator, an in-person assessment, or lab/
    extension confirmation, rather than treat or identify further (RQ5). Feeds Q2 on `removal`
    cards and G1 on `identification` cards — see `cards/SCHEMA.md`."""
    referral_reason: str | None = None
    """Required when `referral_expected` is `True`: why remote text advice can't safely resolve
    this case (e.g. a licensing/permitting threshold, or a diagnostic that genuinely isn't
    available remotely). Interpolated into the Q2/G1 judge prompts so the judge scores a correct
    decline as the ideal outcome rather than an incomplete one."""

    @model_validator(mode="after")
    def _check_referral_fields(self) -> Self:
        if self.referral_expected and self.referral_reason is None:
            raise ValueError("referral_expected=True requires referral_reason")
        if self.referral_expected and self.question_type == QuestionType.INTRODUCTION:
            raise ValueError(
                "referral_expected is only meaningful on 'removal' (Q2) or 'identification' (G1) "
                "cards — neither Q2_INTRODUCTION nor any gate has a referral-aware branch for "
                "'introduction' cards, so it would silently no-op there."
            )
        return self

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
    G6_HARMFUL_ACTION_WARNING = "harmful_action_warning"


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
    `Q2Classification` below. Q3, Q4, and Q5 apply to `removal` cards only — `score` is the string
    `"not_applicable"` on any other `question_type`, the same structural-short-circuit mechanism
    `GateResult` uses for G2-G5, rather than a judge call being asked to decide something the card
    doesn't have an answer for. Q6 applies to every `question_type`.
    """

    dimension: Literal[
        QualityDimension.Q3_ACTIONABILITY,
        QualityDimension.Q4_REGULATORY_GROUNDING,
        QualityDimension.Q5_FOLLOWUP,
        QualityDimension.Q6_ECOLOGICAL_FRAMING,
    ]
    score: Annotated[int, Field(ge=0, le=2)] | Literal["not_applicable"]
    comment: str


class Q2Classification(BaseModel):
    """`label` is `not_applicable` (structural, no judge call) on `identification` cards — Q2 has no
    defined label set for that question type, and G1 already carries identification correctness (see
    `harness/judges/quality.py` and `DECISION-LOG.md`'s "First-pass LLM-as-judge validation" entry).

    Sharp edge: `Q2Label.DECLINED` and `IntroductionQ2Label.DECLINED` are both `str` enums with the
    same value (`"declined"`), so plain equality (`label == Q2Label.DECLINED`) matches either one
    correctly regardless of which class it's actually an instance of — but `model_validate`/JSON
    deserialization of a bare `{"label": "declined", ...}` dict always resolves to `Q2Label` (the
    first union member listed here), never `IntroductionQ2Label`, since nothing here disambiguates by
    the source card's `question_type`. Every other label value is unambiguous (`Q2Label` and
    `IntroductionQ2Label`'s non-`declined` members don't share string values, so pydantic's union
    resolution picks the right class), so only a deserialized `declined` classification is affected.
    `harness/results_store.py`'s `SweepResult` **does** round-trip `Q2Classification` through JSON
    (`model_dump_json`/`model_validate_json`, for on-disk sweep persistence), so this sharp edge is
    live today, not hypothetical — a deserialized `SweepResult` for an `introduction` card whose Q2
    was `declined` comes back as `Q2Label.DECLINED`, not `IntroductionQ2Label.DECLINED`. Still
    harmless in practice because every current consumer (`harness/scoring.py`'s `q2_label_value`,
    `is_declined`, `is_referral_correct`) compares by `.value` or via `==` against `Q2Label.DECLINED`
    specifically (which matches by value regardless of the actual class), never
    `isinstance(label, IntroductionQ2Label)`. Don't add that kind of `isinstance` check against a
    `label` that may have come from `SweepResult` deserialization without accounting for this.
    """

    label: Q2Label | IntroductionQ2Label | Literal["not_applicable"]
    comment: str


class RunMetadata(BaseModel):
    card_set_version: str
    judge_prompt_version: str
    model_id: str
    run_timestamp: datetime
