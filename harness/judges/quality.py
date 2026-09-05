"""Q2-Q6 quality judges (PRD v4 §5.3). Q1 is derived in code, never judged (R3) — see
`harness/scoring.py`.

Q2's label set is `question_type`-conditional: `removal` uses `Q2Label`, `introduction` uses
`IntroductionQ2Label`, and `identification` is structurally `not_applicable` (no defined label set —
identification correctness is gate G1's job). Q3/Q4/Q5 apply to `removal` cards only,
`not_applicable` (structural, no judge call) otherwise. Q6 applies to every `question_type`.

RQ5 (`referral_expected`, see `DECISION-LOG.md`): on a `removal` card where the ground-truth-correct
outcome is to decline and refer rather than prescribe, `_q2_referral_note` overrides Q2's normal
rubric so a correct decline classifies as `declined` *and* is scored as the ideal outcome, not an
incomplete one.
"""

from dataclasses import dataclass
from typing import Any

import anthropic
from langfuse import Langfuse

from harness.ground_truth import GroundTruth, load_ground_truth_for_card
from harness.judges._common import (
    DEFAULT_JUDGE_MODEL,
    format_transcript,
    run_structured_judge_call,
)
from harness.judges.prompts.quality import (
    Q2_INTRODUCTION,
    Q2_REMOVAL,
    Q3_ACTIONABILITY,
    Q4_REGULATORY_GROUNDING,
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


def _q2_referral_note(card: Card) -> str:
    """RQ5: on a `removal` card with `referral_expected=True`, no DIY action is actually acceptable
    — override Q2's normal rubric so a correct decline is scored as the ideal outcome, not merely an
    excluded category. Empty string (no-op) on every other card."""
    if not card.referral_expected:
        return ""
    return (
        "\nIMPORTANT for this specific case: no DIY treatment is actually acceptable here — the "
        f"correct outcome is for the assistant to decline and refer the user, because "
        f"{card.referral_reason} If the assistant's final position clearly declines to prescribe a "
        "DIY treatment and communicates a reason consistent with the above (even in its own "
        "words), classify it as declined and treat this as the CORRECT, ideal outcome for this "
        "case in your comment — do not describe it as an incomplete or unhelpful answer. If the "
        "assistant instead prescribes a DIY treatment anyway, classify it normally against the "
        "lists above (note there is no acceptable entry for this case, so a DIY prescription "
        "cannot score acceptable).\n"
    )


def judge_q2_classification(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
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
            referral_note=_q2_referral_note(card),
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
        name="judge-q2-classification",
        system=system,
        user_content="Return your classification now.",
        schema=schema,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )
    return Q2Classification(label=label_enum(data["label"]), comment=data["comment"])


def judge_q3_actionability(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
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
        name="judge-q3-actionability",
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )
    return QualityScore(
        dimension=QualityDimension.Q3_ACTIONABILITY,
        score=int(data["score"]),
        comment=data["comment"],
    )


def _ground_truth_context(ground_truth: GroundTruth) -> str:
    return "\n".join(
        f"- [{cell.category}] {cell.answer.strip()} "
        f"(source dated {cell.citation.publication_date})"
        for cell in ground_truth.cells
    )


def judge_q4_regulatory_grounding(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> QualityScore:
    if card.question_type != QuestionType.REMOVAL:
        return QualityScore(
            dimension=QualityDimension.Q4_REGULATORY_GROUNDING,
            score="not_applicable",
            comment=f"question_type={card.question_type.value}, not removal; regulatory/label "
            "grounding only applies to a prescribed treatment.",
        )
    ground_truth = load_ground_truth_for_card(card)
    system = Q4_REGULATORY_GROUNDING.format(
        ground_truth_context=_ground_truth_context(ground_truth),
        transcript=format_transcript(trajectory),
    )
    data = run_structured_judge_call(
        client,
        name="judge-q4-regulatory-grounding",
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )
    return QualityScore(
        dimension=QualityDimension.Q4_REGULATORY_GROUNDING,
        score=int(data["score"]),
        comment=data["comment"],
    )


def judge_q5_followup(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
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
        name="judge-q5-followup",
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
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
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> QualityScore:
    system = Q6_ECOLOGICAL_FRAMING.format(
        native_status=card.native_status.value,
        ecological_framing_notes=card.ecological_framing_notes,
        transcript=format_transcript(trajectory),
    )
    data = run_structured_judge_call(
        client,
        name="judge-q6-ecological-framing",
        system=system,
        user_content="Return your score now.",
        schema=_SCORE_SCHEMA,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
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
    q4: QualityScore
    q5: QualityScore
    q6: QualityScore


def run_all_quality(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> QualityResults:
    """Run Q2-Q6 for one finished conversation. Callers needing G2-G6's `declined` short-circuit
    (`harness/judges/gates.py`'s `run_all_gates`) should read it off
    `result.q2.label == Q2Label.DECLINED`.

    Q4 loads its own ground truth internally (`load_ground_truth_for_card`, `not_applicable` outside
    `removal` before that load is ever attempted) rather than taking it as a parameter, so callers
    don't need to know Q4 has a different dependency shape than Q3/Q5/Q6.

    `langfuse_client`/`trace_id`, when given (the finished conversation's trace — see
    `harness._tracing.observe`'s docstring), land each dimension as its own "evaluation" generation
    on that same trace, model-tagged, alongside the "simulation"/"inference" generations already
    recorded live during the conversation.
    """
    return QualityResults(
        q2=judge_q2_classification(
            client,
            card,
            trajectory,
            model=model,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        q3=judge_q3_actionability(
            client,
            card,
            trajectory,
            model=model,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        q4=judge_q4_regulatory_grounding(
            client,
            card,
            trajectory,
            model=model,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        q5=judge_q5_followup(
            client,
            card,
            trajectory,
            model=model,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        q6=judge_q6_ecological_framing(
            client,
            card,
            trajectory,
            model=model,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
    )
