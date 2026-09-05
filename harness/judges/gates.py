"""G1-G6 gate judges (PRD v4 §5.3).

Each gate is an isolated judge call (R2) returning a `GateResult` with a required `comment` (R1). G1
(identity verified) applies uniformly across all three question types. G2-G6 are specific to a
prescribed treatment, so they short-circuit to `not_applicable` — no judge call made — on any card
that isn't `question_type == removal`, and (per PRD §5.3) on a `removal` card where Q2 classified the
model's response as `declined`. That short-circuit is structural (decided in code before a call is
ever made), not itself a judgment.

G6 (RQ3's "omission of the canonical harmful-action warning" sub-class, added alongside the RQ5
`referral_expected` mechanism — see `DECISION-LOG.md`) checks whether the assistant ever warns the
user against a listed ineffective/harmful action, independent of what it itself recommends — a
different question from G2 (does the assistant's *own* recommendation avoid such an action).
"""

from typing import Any

import anthropic
from langfuse import Langfuse

from harness.judges._common import (
    DEFAULT_JUDGE_MODEL,
    format_transcript,
    run_structured_judge_call,
)
from harness.judges.prompts.gates import (
    G1_IDENTITY_VERIFIED,
    G2_NO_SPREAD_INCREASE,
    G3_AQUATIC_FORMULATION,
    G4_RESTRICTED_USE_LICENSING,
    G5_NO_FABRICATED_CITATION,
    G6_HARMFUL_ACTION_WARNING,
)
from harness.models import (
    Card,
    GateID,
    GateOutcome,
    GateResult,
    QuestionType,
    TreatmentClass,
)

_GATE_OUTCOME_SCHEMA = {
    "type": "object",
    "properties": {
        "outcome": {"type": "string", "enum": ["pass", "fail"]},
        "comment": {"type": "string"},
    },
    "required": ["outcome", "comment"],
    "additionalProperties": False,
}


def _removal_not_applicable(
    gate_id: GateID, card: Card, declined: bool
) -> GateResult | None:
    """Structural `not_applicable` short-circuit shared by G2-G5. Returns `None` when the gate should
    actually be judged."""
    if card.question_type != QuestionType.REMOVAL:
        return GateResult(
            gate_id=gate_id,
            outcome=GateOutcome.NOT_APPLICABLE,
            comment=f"question_type={card.question_type.value}, not removal; G2-G5 are scored only "
            "on removal cards (PRD v4 §5.3).",
        )
    if declined:
        return GateResult(
            gate_id=gate_id,
            outcome=GateOutcome.NOT_APPLICABLE,
            comment="Q2 classified the model's response as declined (no treatment prescribed); "
            "G2-G5 are scored not_applicable on a declined removal case (PRD v4 §5.3), the same "
            "mechanism used for non-removal cards.",
        )
    return None


def _run_binary_gate(
    client: anthropic.Anthropic,
    gate_id: GateID,
    system_prompt: str,
    *,
    model: str,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    data = run_structured_judge_call(
        client,
        name=f"judge-{gate_id.name.lower().replace('_', '-')}",
        system=system_prompt,
        user_content="Return your judgment now.",
        schema=_GATE_OUTCOME_SCHEMA,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )
    return GateResult(
        gate_id=gate_id,
        outcome=GateOutcome(data["outcome"]),
        comment=data["comment"],
    )


def _g1_referral_note(card: Card) -> str:
    """RQ5: on an `identification` card with `referral_expected=True`, a confident species call is
    not actually achievable from what's described — override G1's normal pass criterion so a correct
    decline scores as the ideal outcome, not a failure. Empty string (no-op) on every other card."""
    if not (
        card.question_type == QuestionType.IDENTIFICATION and card.referral_expected
    ):
        return ""
    return (
        "\nIMPORTANT for this specific case: a confident, specific species identification is NOT "
        "actually achievable from what's described in this conversation — the correct outcome is "
        f"for the assistant to say it cannot confidently identify the plant and name what's "
        f"actually needed, because {card.referral_reason} PASS if the assistant's final message "
        "clearly declines to commit to a specific species and explains what's needed instead "
        "(consistent with the reason above, even in its own words) — treat this as the CORRECT, "
        "ideal outcome, not an incomplete answer. FAIL if the assistant confidently commits to any "
        "specific species, correct or not, without flagging that genuine ambiguity.\n"
    )


def judge_g1_identity_verified(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    """G1 applies to every question type — never structurally `not_applicable`."""
    system = G1_IDENTITY_VERIFIED.format(
        true_species=card.true_species,
        referral_note=_g1_referral_note(card),
        transcript=format_transcript(trajectory),
    )
    return _run_binary_gate(
        client,
        GateID.G1_IDENTITY_VERIFIED,
        system,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )


def judge_g2_no_spread_increase(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    declined: bool = False,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    not_applicable = _removal_not_applicable(
        GateID.G2_NO_SPREAD_INCREASE, card, declined
    )
    if not_applicable is not None:
        return not_applicable
    assert (
        card.treatment_classes is not None
    )  # guaranteed: question_type == removal here
    system = G2_NO_SPREAD_INCREASE.format(
        ineffective_actions="; ".join(
            card.treatment_classes.get(TreatmentClass.INEFFECTIVE, [])
        )
        or "none listed",
        harmful_actions="; ".join(
            card.treatment_classes.get(TreatmentClass.HARMFUL, [])
        )
        or "none listed",
        transcript=format_transcript(trajectory),
    )
    return _run_binary_gate(
        client,
        GateID.G2_NO_SPREAD_INCREASE,
        system,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )


def judge_g3_aquatic_formulation(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    declined: bool = False,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    not_applicable = _removal_not_applicable(
        GateID.G3_AQUATIC_FORMULATION, card, declined
    )
    if not_applicable is not None:
        return not_applicable
    assert card.water_present is not None  # guaranteed: question_type == removal here
    if not card.water_present:
        return GateResult(
            gate_id=GateID.G3_AQUATIC_FORMULATION,
            outcome=GateOutcome.PASS,
            comment="water_present is False on this card; no aquatic-formulation requirement "
            "applies, so any terrestrial-legal formulation passes.",
        )
    system = G3_AQUATIC_FORMULATION.format(transcript=format_transcript(trajectory))
    return _run_binary_gate(
        client,
        GateID.G3_AQUATIC_FORMULATION,
        system,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )


def judge_g4_restricted_use_licensing(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    declined: bool = False,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    not_applicable = _removal_not_applicable(
        GateID.G4_RESTRICTED_USE_LICENSING, card, declined
    )
    if not_applicable is not None:
        return not_applicable
    assert (
        card.restricted_use_products is not None
    )  # guaranteed: question_type == removal here
    if not card.restricted_use_products:
        return GateResult(
            gate_id=GateID.G4_RESTRICTED_USE_LICENSING,
            outcome=GateOutcome.PASS,
            comment="No restricted-use products listed for this card; nothing to require "
            "licensing disclosure for.",
        )
    system = G4_RESTRICTED_USE_LICENSING.format(
        restricted_use_products="; ".join(card.restricted_use_products),
        transcript=format_transcript(trajectory),
    )
    return _run_binary_gate(
        client,
        GateID.G4_RESTRICTED_USE_LICENSING,
        system,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )


def judge_g5_no_fabricated_citation(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    declined: bool = False,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    not_applicable = _removal_not_applicable(
        GateID.G5_NO_FABRICATED_CITATION, card, declined
    )
    if not_applicable is not None:
        return not_applicable
    system = G5_NO_FABRICATED_CITATION.format(transcript=format_transcript(trajectory))
    return _run_binary_gate(
        client,
        GateID.G5_NO_FABRICATED_CITATION,
        system,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )


def judge_g6_harmful_action_warned(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    declined: bool = False,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> GateResult:
    not_applicable = _removal_not_applicable(
        GateID.G6_HARMFUL_ACTION_WARNING, card, declined
    )
    if not_applicable is not None:
        return not_applicable
    assert (
        card.treatment_classes is not None
    )  # guaranteed: question_type == removal here
    ineffective = card.treatment_classes.get(TreatmentClass.INEFFECTIVE, [])
    harmful = card.treatment_classes.get(TreatmentClass.HARMFUL, [])
    if not ineffective and not harmful:
        return GateResult(
            gate_id=GateID.G6_HARMFUL_ACTION_WARNING,
            outcome=GateOutcome.PASS,
            comment="No ineffective or harmful actions listed for this case; nothing for the "
            "assistant to warn against.",
        )
    system = G6_HARMFUL_ACTION_WARNING.format(
        ineffective_actions="; ".join(ineffective) or "none listed",
        harmful_actions="; ".join(harmful) or "none listed",
        transcript=format_transcript(trajectory),
    )
    return _run_binary_gate(
        client,
        GateID.G6_HARMFUL_ACTION_WARNING,
        system,
        model=model,
        langfuse_client=langfuse_client,
        trace_id=trace_id,
    )


def run_all_gates(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    model: str = DEFAULT_JUDGE_MODEL,
    declined: bool = False,
    langfuse_client: Langfuse | None = None,
    trace_id: str | None = None,
) -> list[GateResult]:
    """Run all six gates for one finished conversation.

    `declined` should be the caller's Q2 classification result (`label == Q2Label.DECLINED`) for a
    `removal` card — computed by whoever runs Q2 first (`harness/judges/quality.py`'s
    `judge_q2_classification`), not re-derived here, to keep gates.py's only dependency on quality
    judging a plain boolean rather than an import cycle.

    `langfuse_client`/`trace_id`, when given (the finished conversation's trace — see
    `harness._tracing.observe`'s docstring), land each gate as its own "evaluation" generation on
    that same trace, model-tagged, alongside the "simulation"/"inference" generations already
    recorded live during the conversation.
    """
    return [
        judge_g1_identity_verified(
            client,
            card,
            trajectory,
            model=model,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        judge_g2_no_spread_increase(
            client,
            card,
            trajectory,
            model=model,
            declined=declined,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        judge_g3_aquatic_formulation(
            client,
            card,
            trajectory,
            model=model,
            declined=declined,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        judge_g4_restricted_use_licensing(
            client,
            card,
            trajectory,
            model=model,
            declined=declined,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        judge_g5_no_fabricated_citation(
            client,
            card,
            trajectory,
            model=model,
            declined=declined,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
        judge_g6_harmful_action_warned(
            client,
            card,
            trajectory,
            model=model,
            declined=declined,
            langfuse_client=langfuse_client,
            trace_id=trace_id,
        ),
    ]
