"""Q2-Q6 quality judges (PRD v4 §5.3). Q1 is derived in code, never judged (R3) — see
`harness/scoring.py`. Q4 (regulatory grounding) is deferred, not built in this pass.

Q2's label set is `question_type`-conditional: `removal` uses `Q2Label`, `introduction` uses
`IntroductionQ2Label`, and `identification` is structurally `not_applicable` (no defined label set —
identification correctness is gate G1's job). Q3/Q5 apply to `removal` cards only, `not_applicable`
(structural, no judge call) otherwise. Q6 applies to every `question_type`.
"""

from dataclasses import dataclass
from typing import Any

import anthropic

from harness.judges._common import (
    DEFAULT_JUDGE_MODEL,
    format_transcript,
    run_structured_judge_call,
)
from harness.judges.prompts.quality import (
    Q2_INTRODUCTION,
    Q2_REMOVAL,
    Q3_ACTIONABILITY,
    Q5_FOLLOWUP,
    Q6_ECOLOGICAL_FRAMING,
)
from harness.models import (
    Card,
    IntroductionClass,
    IntroductionQ2Label,
    Q2Classification,
    Q2Label,
    QualityDimension,
    QualityScore,
    QuestionType,
    TreatmentClass,
)

_Q2_REMOVAL_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": [label.value for label in Q2Label]},
        "comment": {"type": "string"},
    },
    "required": ["label", "comment"],
    "additionalProperties": False,
}

_Q2_INTRODUCTION_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {
            "type": "string",
            "enum": [label.value for label in IntroductionQ2Label],
        },
        "comment": {"type": "string"},
    },
    "required": ["label", "comment"],
    "additionalProperties": False,
}

_SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "enum": [0, 1, 2]},
        "comment": {"type": "string"},
    },
    "required": ["score", "comment"],
    "additionalProperties": False,
}


def _joined(actions: list[str]) -> str:
    return "; ".join(actions) or "none listed"


def judge_q2_classification(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
) -> Q2Classification:
    if card.question_type == QuestionType.IDENTIFICATION:
        return Q2Classification(
            label="not_applicable",
            comment="identification cards have no defined Q2 label set; identity correctness is "
            "gate G1's job.",
        )

    transcript = format_transcript(trajectory)
    if card.question_type == QuestionType.REMOVAL:
        assert (
            card.treatment_classes is not None
        )  # guaranteed by question_type == removal
        system = Q2_REMOVAL.format(
            acceptable_actions=_joined(
                card.treatment_classes.get(TreatmentClass.ACCEPTABLE, [])
            ),
            suboptimal_but_safe_actions=_joined(
                card.treatment_classes.get(TreatmentClass.SUBOPTIMAL_BUT_SAFE, [])
            ),
            ineffective_actions=_joined(
                card.treatment_classes.get(TreatmentClass.INEFFECTIVE, [])
            ),
            harmful_actions=_joined(
                card.treatment_classes.get(TreatmentClass.HARMFUL, [])
            ),
            transcript=transcript,
        )
        schema = _Q2_REMOVAL_SCHEMA
        label_enum: type[Q2Label | IntroductionQ2Label] = Q2Label
    else:  # QuestionType.INTRODUCTION
        assert (
            card.introduction_classes is not None
        )  # guaranteed by question_type == introduction
        system = Q2_INTRODUCTION.format(
            encouraged_actions=_joined(
                card.introduction_classes.get(IntroductionClass.ENCOURAGED, [])
            ),
            neutral_actions=_joined(
                card.introduction_classes.get(IntroductionClass.NEUTRAL, [])
            ),
            discouraged_actions=_joined(
                card.introduction_classes.get(IntroductionClass.DISCOURAGED, [])
            ),
            harmful_to_encourage_actions=_joined(
                card.introduction_classes.get(
                    IntroductionClass.HARMFUL_TO_ENCOURAGE, []
                )
            ),
            transcript=transcript,
        )
        schema = _Q2_INTRODUCTION_SCHEMA
        label_enum = IntroductionQ2Label

    data = run_structured_judge_call(
        client,
        system=system,
        user_content="Return your classification now.",
        schema=schema,
        model=model,
    )
    return Q2Classification(label=label_enum(data["label"]), comment=data["comment"])


def judge_q3_actionability(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
) -> QualityScore:
    if card.question_type != QuestionType.REMOVAL:
        return QualityScore(
            dimension=QualityDimension.Q3_ACTIONABILITY,
            score="not_applicable",
            comment=f"question_type={card.question_type.value}, not removal; actionability only "
            "applies to a prescribed treatment.",
        )
    assert card.required_specificity_elements is not None
    system = Q3_ACTIONABILITY.format(
        required_specificity_elements=_joined(card.required_specificity_elements),
        transcript=format_transcript(trajectory),
    )
    data = run_structured_judge_call(
        client,
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
    )
    return QualityScore(
        dimension=QualityDimension.Q3_ACTIONABILITY,
        score=int(data["score"]),
        comment=data["comment"],
    )


def judge_q5_followup(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
) -> QualityScore:
    if card.question_type != QuestionType.REMOVAL:
        return QualityScore(
            dimension=QualityDimension.Q5_FOLLOWUP,
            score="not_applicable",
            comment=f"question_type={card.question_type.value}, not removal; a follow-up "
            "treatment plan only applies to a prescribed treatment.",
        )
    assert card.expected_followup_plan is not None
    system = Q5_FOLLOWUP.format(
        expected_followup_plan=card.expected_followup_plan,
        transcript=format_transcript(trajectory),
    )
    data = run_structured_judge_call(
        client,
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
    )
    return QualityScore(
        dimension=QualityDimension.Q5_FOLLOWUP,
        score=int(data["score"]),
        comment=data["comment"],
    )


def judge_q6_ecological_framing(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
) -> QualityScore:
    system = Q6_ECOLOGICAL_FRAMING.format(
        native_status=card.native_status.value,
        ecological_framing_notes=card.ecological_framing_notes,
        transcript=format_transcript(trajectory),
    )
    data = run_structured_judge_call(
        client,
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
    )
    return QualityScore(
        dimension=QualityDimension.Q6_ECOLOGICAL_FRAMING,
        score=int(data["score"]),
        comment=data["comment"],
    )


@dataclass
class QualityResults:
    q2: Q2Classification
    q3: QualityScore
    q5: QualityScore
    q6: QualityScore


def run_all_quality(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
) -> QualityResults:
    """Run Q2, Q3, Q5, Q6 for one finished conversation. Callers needing G2-G5's `declined`
    short-circuit (`harness/judges/gates.py`'s `run_all_gates`) should read it off
    `result.q2.label == Q2Label.DECLINED`."""
    return QualityResults(
        q2=judge_q2_classification(client, card, trajectory, model=model),
        q3=judge_q3_actionability(client, card, trajectory, model=model),
        q5=judge_q5_followup(client, card, trajectory, model=model),
        q6=judge_q6_ecological_framing(client, card, trajectory, model=model),
    )
