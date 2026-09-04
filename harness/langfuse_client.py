"""Langfuse SDK wiring for the harness (PRD v4 Sec 6, "Technical requirements").

One self-hosted Langfuse project holds a single dataset (`DATASET_NAME`, one item per card) reused
across every run; one dataset run per (model_id, prompt_version) pair; scores attached to each run's
root span using score configs registered up front so the UI can cross-tab across runs.

SDK note (checked 2026-09-03 against the installed `langfuse==4.15.1`, the OTEL-based "v3" Python SDK):
there is no standalone "create a dataset run" call. A dataset run is created implicitly, server-side,
the first time a `DatasetRunItem` is posted under a given `run_name` (`client.api.dataset_run_items.create`,
see `link_trace_to_dataset_run` below) — or by using `Langfuse.run_experiment` / `DatasetClient.run_experiment`,
which wraps task execution *and* run creation into one callback-based call. This harness's conversation
loop lives in `openevals.run_multiturn_simulation` (`harness/conversation.py`), outside that callback
shape, so `start_dataset_run` here just materializes the run's identity + R4 reproducibility metadata,
and `link_trace_to_dataset_run` is the call that actually creates/attaches to the run in Langfuse.

"""

import logging
from dataclasses import dataclass
from typing import Any, Literal, cast

from langfuse import Langfuse
from langfuse.api import NotFoundError
from langfuse.api.commons.types.config_category import ConfigCategory
from langfuse.api.commons.types.dataset_run_item import DatasetRunItem
from langfuse.api.commons.types.score_config import ScoreConfig
from langfuse.api.commons.types.score_config_data_type import ScoreConfigDataType
from langfuse.api.core.api_error import ApiError
from langfuse.api.score_configs.types.score_configs import ScoreConfigs

from harness.config import Settings
from harness.judges.quality import QualityResults
from harness.models import (
    _REMOVAL_ONLY_FIELDS,
    Card,
    GateID,
    GateOutcome,
    GateResult,
    IntroductionQ2Label,
    Q2Label,
    QualityDimension,
    QuestionType,
)
from harness.scoring import Q1Result, is_referral_correct, q2_label_value

logger = logging.getLogger(__name__)

# --- Dataset -----------------------------------------------------------------

DATASET_NAME = "case-cards"
"""The benchmark's single Langfuse dataset (PRD Sec 6): one item per card, reused across every run."""

# --- Score names ---------------------------------------------------------------
# Derived from harness.models.GateID / QualityDimension member names, not hand-duplicated strings —
# a rename in models.py breaks these loudly (AttributeError at import) instead of silently
# desyncing the Langfuse score-config names from the enums they're supposed to mirror.

GATE_SCORE_NAMES: list[str] = [member.name for member in GateID]

NUMERIC_QUALITY_SCORE_NAMES: list[str] = [
    QualityDimension.Q3_ACTIONABILITY.name,
    QualityDimension.Q4_REGULATORY_GROUNDING.name,
    QualityDimension.Q5_FOLLOWUP.name,
]
"""Only the judge-graded 0-2 dimensions — Q1 is derived in code (PRD R3, never judged) and Q2 is
categorical (`Q2_SCORE_NAME` below), not part of this numeric list."""

Q2_SCORE_NAME = "Q2_TREATMENT_CLASS"

Q1_SCORE_NAME = "Q1_ELICITATION"
"""Q1 is computed in code, never judged (R3, see `harness/scoring.py`), but still lands as a
categorical pass/fail score for visibility in the Langfuse UI alongside the judged dimensions —
`pass` iff every `decision_relevant` slot on the card was elicited before the model's terminal turn."""

REFERRAL_CORRECT_SCORE_NAME = "REFERRAL_CORRECT"
"""RQ5 (`referral_expected`, added 2026-09-04): computed in code from Q2/G1 (R3, see
`harness/scoring.py`'s `is_referral_correct`), not judged directly. Only ever attached for a card
where `referral_expected` is `True` — skipped entirely otherwise, the same "not_applicable can't be
a numeric/this-config's-shape value, so don't attach" pattern the quality scores use."""

GATE_OUTCOME_LABELS: list[str] = ["fail", "pass", "not_applicable"]
"""Every gate is scored categorical pass/fail/not_applicable (PRD Sec 5.3)."""

Q2_LABELS: list[str] = [
    *[label.value for label in Q2Label],
    *[
        label.value
        for label in IntroductionQ2Label
        if label != IntroductionQ2Label.DECLINED
    ],
    "not_applicable",
]
"""One Q2 score config covers every question type rather than needing a separate config per type:
`removal`'s five labels (PRD Sec 5.3 + Sec 13 open question 3's `declined` addition), `introduction`'s
four non-`declined` labels (`declined` is shared, not duplicated), and `not_applicable` for
`identification` cards, which have no Q2 label set of their own (see `harness/judges/quality.py`)."""

ScoreDataType = Literal["NUMERIC", "CATEGORICAL", "BOOLEAN", "TEXT", "CORRECTION"]


@dataclass(frozen=True)
class ScoreConfigSpec:
    """One score config to register, before it's been created in Langfuse."""

    name: str
    data_type: ScoreConfigDataType
    categories: list[ConfigCategory] | None = None
    min_value: float | None = None
    max_value: float | None = None
    description: str = ""


def _categorical_categories(labels: list[str]) -> list[ConfigCategory]:
    return [
        ConfigCategory(value=float(i), label=label) for i, label in enumerate(labels)
    ]


def build_score_config_specs() -> list[ScoreConfigSpec]:
    """The full set of score configs this benchmark needs: 5 gates + Q2 (categorical), Q3-Q5 (numeric).

    Pure data — no network call. Used both by `ensure_score_configs` and directly in tests.
    """
    specs = [
        ScoreConfigSpec(
            name=name,
            data_type=ScoreConfigDataType.CATEGORICAL,
            categories=_categorical_categories(GATE_OUTCOME_LABELS),
            description="Gate outcome: pass / fail / not_applicable.",
        )
        for name in GATE_SCORE_NAMES
    ]
    specs.append(
        ScoreConfigSpec(
            name=Q2_SCORE_NAME,
            data_type=ScoreConfigDataType.CATEGORICAL,
            categories=_categorical_categories(Q2_LABELS),
            description="Q2 classification: treatment-class for removal cards, keep/plant "
            "recommendation for introduction cards, or not_applicable for identification cards.",
        )
    )
    specs.extend(
        ScoreConfigSpec(
            name=name,
            data_type=ScoreConfigDataType.NUMERIC,
            min_value=0,
            max_value=2,
            description=f"{name} quality score, 0-2.",
        )
        for name in NUMERIC_QUALITY_SCORE_NAMES
    )
    specs.append(
        ScoreConfigSpec(
            name=Q1_SCORE_NAME,
            data_type=ScoreConfigDataType.CATEGORICAL,
            categories=_categorical_categories(["fail", "pass"]),
            description="Q1 elicitation (computed in code, R3): pass iff every decision-relevant "
            "slot was elicited before the model's terminal turn.",
        )
    )
    specs.append(
        ScoreConfigSpec(
            name=REFERRAL_CORRECT_SCORE_NAME,
            data_type=ScoreConfigDataType.CATEGORICAL,
            categories=_categorical_categories(["fail", "pass"]),
            description="RQ5 referral correctness (computed in code, R3): pass iff a "
            "referral_expected=True card's model response correctly declined and referred. Only "
            "ever attached on a referral_expected card.",
        )
    )
    return specs


# --- Client construction -------------------------------------------------------


def get_langfuse_client(settings: Settings) -> Langfuse:
    """Build a Langfuse client from explicit config, never from ambient env vars.

    `harness.config.Settings` stays the single source of truth (per `.claude/rules/python.md`'s
    "Config and secrets" section) — credentials are passed through explicitly rather than relying on
    the SDK's own `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`/`LANGFUSE_HOST` env var auto-detection.
    """
    return Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )


# --- Dataset + dataset items ---------------------------------------------------


def get_or_create_dataset(client: Langfuse, name: str = DATASET_NAME) -> Any:
    """Create-or-get the project's one dataset. Returns a `DatasetClient`."""
    try:
        return client.get_dataset(name)
    except NotFoundError:
        logger.info("Langfuse dataset %r not found; creating it.", name)
        client.create_dataset(name=name)
        return client.get_dataset(name)


def build_dataset_item_input(card: Card) -> dict[str, Any]:
    """`input`: opening message + slot list, structured (PRD Sec 6 data model) — a judge or human
    later needs to see what was gated, not just a raw text blob."""
    dumped = card.model_dump(mode="json")
    return {
        "opening_message": dumped["opening_message"],
        "species": dumped["species"],
        "slots": dumped["slots"],
    }


def build_dataset_item_expected_output(card: Card) -> dict[str, Any]:
    """`expected_output`: the ground truth a judge scores model output against.

    Field set is `question_type`-conditional, matching `Card` itself (`cards/SCHEMA.md`): a
    `removal` card's expected_output carries `treatment_classes` and its four siblings; an
    `introduction` card's carries `introduction_classes` instead; an `identification` card's
    carries neither. `ecological_framing_notes` (Q6) is always included.
    """
    dumped = card.model_dump(mode="json")
    result: dict[str, Any] = {
        "true_species": dumped["true_species"],
        "question_type": dumped["question_type"],
        "native_status": dumped["native_status"],
        "ecological_framing_notes": dumped["ecological_framing_notes"],
    }
    if card.question_type == QuestionType.REMOVAL:
        result.update({field: dumped[field] for field in _REMOVAL_ONLY_FIELDS})
    elif card.question_type == QuestionType.INTRODUCTION:
        result["introduction_classes"] = dumped["introduction_classes"]
    return result


def upsert_card_dataset_item(
    client: Langfuse, card: Card, dataset_name: str = DATASET_NAME
) -> Any:
    """Add or update the dataset item for one card.

    Uses the card's own `card_id` as the Langfuse dataset item id, so re-running this for an edited
    card upserts in place (`create_dataset_item` upserts on `id`) instead of creating duplicates.
    """
    return client.create_dataset_item(
        dataset_name=dataset_name,
        id=card.card_id,
        input=build_dataset_item_input(card),
        expected_output=build_dataset_item_expected_output(card),
        metadata={"card_id": card.card_id},
    )


# --- Score config registration -------------------------------------------------


def ensure_score_configs(client: Langfuse) -> list[ScoreConfig]:
    """Create-or-get every score config this benchmark needs.

    Reads existing configs first and skips any name already registered (idempotent by construction,
    not by relying on error handling). As a defensive fallback for a race against another process
    registering the same config concurrently, a duplicate-name conflict from the create call itself
    (`ApiError` with a 4xx "already exists" status) is also treated as already-registered rather than
    raised — anything else propagates.
    """
    existing: ScoreConfigs = client.api.score_configs.get(limit=100)
    existing_names = {c.name for c in existing.data}

    created: list[ScoreConfig] = []
    for spec in build_score_config_specs():
        if spec.name in existing_names:
            logger.debug("Score config %r already registered; skipping.", spec.name)
            continue
        try:
            cfg = client.api.score_configs.create(
                name=spec.name,
                data_type=spec.data_type,
                categories=spec.categories,
                min_value=spec.min_value,
                max_value=spec.max_value,
                description=spec.description,
            )
        except ApiError as exc:
            if exc.status_code in (400, 409):
                logger.info(
                    "Score config %r rejected as duplicate (status %s); treating as already registered.",
                    spec.name,
                    exc.status_code,
                )
                continue
            raise
        created.append(cfg)
    return created


# --- Dataset runs ---------------------------------------------------------------


@dataclass(frozen=True)
class DatasetRunHandle:
    """Identity + R4 reproducibility metadata for one (model_id, prompt_version) dataset run.

    See this module's docstring: Langfuse has no standalone "create run" call in this SDK version, so
    this handle doesn't itself talk to the API — `link_trace_to_dataset_run` is what actually creates
    the run server-side, the first time it's called for a given `run_name`.
    """

    run_name: str
    model_id: str
    prompt_version: str
    metadata: dict[str, Any]


def start_dataset_run(
    model_id: str,
    prompt_version: str,
    *,
    card_set_version: str | None = None,
    arm: str = "standard",
) -> DatasetRunHandle:
    """Build the handle for a (model_id, prompt_version[, arm]) dataset run.

    `run_name` doubles as the run's identity in the Langfuse UI. `metadata` carries PRD R4's
    reproducibility fields (model ID, prompt version, and optionally the pinned card set version) —
    attach it to every trace/dataset-run-item created under this run.

    `arm` (R6, PRD §6): `"standard"` (the default) keeps `run_name` exactly as before — not a
    breaking rename for existing standard-arm runs. Any other value (the RQ1 oracle-contrast arm
    passes `"oracle"`) is appended to `run_name` so the two arms land as distinct Langfuse dataset
    runs instead of colliding under one name, and is always included in `metadata` regardless of
    value so a run's arm is checkable without parsing `run_name`.
    """
    metadata: dict[str, Any] = {
        "model_id": model_id,
        "prompt_version": prompt_version,
        "arm": arm,
    }
    if card_set_version is not None:
        metadata["card_set_version"] = card_set_version
    run_name = f"{model_id}__{prompt_version}"
    if arm != "standard":
        run_name = f"{run_name}__{arm}"
    return DatasetRunHandle(
        run_name=run_name,
        model_id=model_id,
        prompt_version=prompt_version,
        metadata=metadata,
    )


def link_trace_to_dataset_run(
    client: Langfuse,
    run: DatasetRunHandle,
    *,
    dataset_item_id: str,
    trace_id: str,
    observation_id: str | None = None,
) -> DatasetRunItem:
    """Attach one conversation's trace to `run`, creating the dataset run server-side on first call."""
    return client.api.dataset_run_items.create(
        run_name=run.run_name,
        dataset_item_id=dataset_item_id,
        trace_id=trace_id,
        observation_id=observation_id,
        metadata=run.metadata,
    )


# --- Scores ----------------------------------------------------------------------


def attach_score(
    client: Langfuse,
    *,
    name: str,
    value: float | str,
    comment: str,
    trace_id: str | None = None,
    dataset_run_id: str | None = None,
    observation_id: str | None = None,
    data_type: ScoreDataType | None = None,
) -> None:
    """Attach one score to a trace/observation (PRD Sec 6: "Scores attached to the run's root span").

    `comment` is a required, non-optional argument — PRD R1: every judged score must carry the
    deciding evidence in its `comment` field, non-negotiable.

    `Langfuse.create_score` is `@overload`-typed with `value`'s type (float vs str) constraining which
    `data_type` literals are valid; branching on `isinstance(value, str)` here lets mypy resolve the
    right overload per branch instead of the two colliding on a plain union call.
    """
    if isinstance(value, str):
        client.create_score(
            name=name,
            value=value,
            comment=comment,
            trace_id=trace_id,
            dataset_run_id=dataset_run_id,
            observation_id=observation_id,
            data_type=cast(
                Literal["CATEGORICAL", "TEXT", "CORRECTION"] | None, data_type
            ),
        )
    else:
        client.create_score(
            name=name,
            value=value,
            comment=comment,
            trace_id=trace_id,
            dataset_run_id=dataset_run_id,
            observation_id=observation_id,
            data_type=cast(Literal["NUMERIC", "BOOLEAN"] | None, data_type),
        )


# --- Score-attachment helpers ---------------------------------------------------
# Shared by every script that runs a finished conversation's judges and needs to push the results
# to Langfuse (`harness/scripts/run_validation.py`, `harness/sweep.py`) — pulled out here after the
# same set of calls started duplicating across call sites, the same reasoning
# `harness/scoring.py`'s `q2_label_value`/`is_declined` docstrings already give for why those moved.


def attach_gate_scores(
    client: Langfuse, trace_id: str, gate_results: list[GateResult]
) -> None:
    for result in gate_results:
        attach_score(
            client,
            name=result.gate_id.name,
            value=result.outcome.value,
            comment=result.comment,
            trace_id=trace_id,
            data_type="CATEGORICAL",
        )


def attach_quality_scores(
    client: Langfuse, trace_id: str, quality_results: QualityResults
) -> None:
    attach_score(
        client,
        name=Q2_SCORE_NAME,
        value=q2_label_value(quality_results.q2.label),
        comment=quality_results.q2.comment,
        trace_id=trace_id,
        data_type="CATEGORICAL",
    )
    for score in (
        quality_results.q3,
        quality_results.q4,
        quality_results.q5,
        quality_results.q6,
    ):
        if score.score == "not_applicable":
            logger.info(
                "%s not_applicable; a numeric score config can't hold that value, skipping "
                "Langfuse attach for this dimension on this card.",
                score.dimension.value,
            )
            continue
        attach_score(
            client,
            name=score.dimension.name,
            value=score.score,
            comment=score.comment,
            trace_id=trace_id,
            data_type="NUMERIC",
        )


def attach_q1_score(client: Langfuse, trace_id: str, q1_result: Q1Result) -> None:
    attach_score(
        client,
        name=Q1_SCORE_NAME,
        value="pass" if q1_result.all_decision_relevant_elicited else "fail",
        comment=(
            f"Elicited before terminal turn: {q1_result.elicited_decision_relevant_slots}. "
            f"Missing: {q1_result.missing_decision_relevant_slots}. "
            f"Distractor slots asked anyway: {q1_result.distractor_slots_asked}."
        ),
        trace_id=trace_id,
        data_type="CATEGORICAL",
    )


def g1_outcome(gate_results: list[GateResult]) -> GateOutcome:
    (g1,) = (r for r in gate_results if r.gate_id == GateID.G1_IDENTITY_VERIFIED)
    return g1.outcome


def attach_referral_correct_score(
    client: Langfuse,
    trace_id: str,
    card: Card,
    *,
    q2_label: Q2Label | IntroductionQ2Label | str,
    gate_results: list[GateResult],
) -> None:
    """RQ5: only attached when `card.referral_expected` is `True` — `is_referral_correct` returns
    `None` otherwise, and `None` isn't a value this score's config can hold, same reasoning as the
    not_applicable-quality-score skip in `attach_quality_scores`."""
    outcome = g1_outcome(gate_results)
    referral_correct = is_referral_correct(card, q2_label=q2_label, g1_outcome=outcome)
    if referral_correct is None:
        return
    attach_score(
        client,
        name=REFERRAL_CORRECT_SCORE_NAME,
        value="pass" if referral_correct else "fail",
        comment=f"referral_expected card; q2_label={q2_label!r}, g1_outcome={outcome.value!r}.",
        trace_id=trace_id,
        data_type="CATEGORICAL",
    )
