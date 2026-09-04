"""R5 transcript leakage check (PRD v4 §6 R5): no card slot value may appear in a user turn that
was not preceded by a matching elicitation.

Re-derives, from a finished trajectory, exactly which slots were legitimately revealed as of each
user turn — reusing `harness.simulated_user.classify_asked_slots` the same way
`harness.scoring.compute_q1` already does, so this check and Q1's own elicitation window can't
silently disagree about what counts as "asked" — then flags any user turn whose text contains a
not-yet-revealed slot's value. A hard, mechanical filter, not a judge call, so a contaminated
transcript never survives into a stratified human-review sample — a future sample-selection step
(not yet built, see `SCRATCHPAD.md`) is expected to exclude every `LeakageReport.leaked` result up
front; `harness/sweep.py` already computes it per result so that filter has the field to key off.

The substring match this uses is deliberately simple (case-insensitive containment, short values
skipped to cut obvious false positives) rather than an LLM judgment call — R5 exists specifically
so leakage detection doesn't depend on another model's judgment being reliable. That simplicity is
a known source of false positives/negatives (a slot value that's a common phrase could coincidentally
appear in unrelated user text; a paraphrased leak wouldn't match at all) — acceptable for a hard
exclusion filter where the cost of a false positive is "one fewer candidate transcript to sample
from," not a wrong score.
"""

from dataclasses import dataclass, field
from typing import Any

import anthropic

from harness._trajectory import extract_message_text
from harness.models import Card
from harness.simulated_user import DEFAULT_MODEL, classify_asked_slots

_MIN_MATCHABLE_VALUE_LENGTH = 3
"""Slot values shorter than this are skipped — a 1-2 character value (or an empty one) is too
likely to appear coincidentally in ordinary conversation text to be meaningful leakage evidence."""


@dataclass
class LeakageReport:
    leaked: bool
    leaked_slots: list[str]
    """Names of slots whose value appeared in a user turn before being legitimately revealed."""
    details: list[str] = field(default_factory=list)
    """One human-readable line per leak, e.g. 'turn 3: slot "water_proximity" value appeared in a
    user turn before any assistant turn asked about it.'"""


def check_leakage(
    client: anthropic.Anthropic,
    card: Card,
    trajectory: list[dict[str, Any]],
    *,
    oracle: bool = False,
    model: str = DEFAULT_MODEL,
) -> LeakageReport:
    """Mechanically re-scan a finished conversation for R5 leakage.

    `oracle=True` matches `harness.simulated_user.build_oracle_opening_message`'s behavior: every
    `decision_relevant` slot's value is treated as legitimately revealed from turn 0, since the
    oracle-contrast arm discloses them upfront by design rather than gating them behind
    elicitation — flagging them as "leaked" there would be flagging the arm's own mechanism, not a
    real contamination.
    """
    revealed: set[str] = (
        {slot.name for slot in card.slots if slot.decision_relevant}
        if oracle
        else set()
    )
    leaked_slots: list[str] = []
    details: list[str] = []

    for index, message in enumerate(trajectory):
        role = message.get("role")
        text = extract_message_text(message.get("content", ""))

        if role == "user":
            text_lower = text.lower()
            for slot in card.slots:
                if slot.name in revealed:
                    continue
                value = slot.value.strip()
                if len(value) < _MIN_MATCHABLE_VALUE_LENGTH:
                    continue
                if value.lower() in text_lower:
                    leaked_slots.append(slot.name)
                    details.append(
                        f'turn {index}: slot "{slot.name}" value appeared in a user turn before '
                        "any assistant turn asked about it."
                    )
        elif role == "assistant":
            revealed.update(classify_asked_slots(client, text, card.slots, model=model))

    return LeakageReport(
        leaked=bool(leaked_slots),
        leaked_slots=sorted(set(leaked_slots)),
        details=details,
    )
