"""Slot-gated simulated user (PRD v4 §5.2).

A slot-gated callable, not a prompted persona. On each turn a classifier (`classify_asked_slots`)
determines which of the card's slots the assistant's latest message actually asked about; only
slots newly classified as asked — filtered to ones not already revealed earlier in this
conversation — are passed to the response generator (`generate_user_response`), which is
instructed to convey those values and nothing else. This is what makes elicitation measurement
possible: a prompted simulated user volunteers information, and the moment it does, "did the
assistant ask the right questions" stops being measurable. Gating happens in code, before any
text generation, so leakage of un-asked slot values is structurally impossible rather than merely
discouraged by a system prompt.

`make_simulated_user(card)` builds the combined callable matching the exact signature
`openevals.simulators.run_multiturn_simulation` calls its `user` argument with: a positional
`trajectory` (the accumulated list of message dicts so far) plus keyword-only `thread_id` and
`turn_counter` (verified against the installed `openevals` 0.2.x source —
`openevals/simulators/multiturn.py`'s `_wrap`/`run_multiturn_simulation`, which calls
`simulated_user(trajectory, thread_id=thread_id, turn_counter=turn_counter)` with a `thread_id`
that is fixed for the lifetime of one `run_multiturn_simulation(...)` call). Revealed-slot state
is therefore safely keyed by `thread_id` in a dict closed over by the returned callable — safe
under `sweep.py`'s `ThreadPoolExecutor`-parallelized (model, card) runs because each concurrent
run gets its own `thread_id` and writes only its own dict entry; nothing here uses a bare mutable
module-level global.
"""

import json
import logging
from collections.abc import Callable
from typing import Any

import anthropic

from harness._trajectory import (
    first_text_block,
    latest_assistant_text,
)
from harness.config import Settings
from harness.models import Card, Slot

logger = logging.getLogger(__name__)

# Harness infrastructure, not the model under test — a fast/cheap model following a constrained
# structured-output instruction is sufficient, and 2 calls fire here on every conversation turn.
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

_SlotClassifierSystemPrompt = (
    "You classify which of a fixed list of candidate facts (slots) an assistant's message is "
    "asking the user to provide. A slot counts as 'asked' only if the assistant's message poses "
    "a question (or an equivalent request for information) that the slot's fact would answer. "
    "Do not mark a slot as asked just because it is thematically related to the message — the "
    "assistant must actually be requesting that specific information. Return only slot names "
    "drawn exactly from the candidate list."
)


def classify_asked_slots(
    client: anthropic.Anthropic,
    assistant_message: str,
    slots: list[Slot],
    *,
    model: str = DEFAULT_MODEL,
) -> list[str]:
    """Classify which of `slots` the assistant's latest message asked about.

    Uses a JSON-schema-constrained structured output (the response's `asked_slot_names` array is
    constrained to an enum of the card's actual slot names) rather than free-text parsing, so the
    result is reliably parseable and can't reference a slot that doesn't exist on this card.
    """
    if not slots:
        return []

    slot_names = [slot.name for slot in slots]
    candidate_facts = "\n".join(f"- {slot.name}: {slot.description}" for slot in slots)
    schema = {
        "type": "object",
        "properties": {
            "asked_slot_names": {
                "type": "array",
                "items": {"type": "string", "enum": slot_names},
            }
        },
        "required": ["asked_slot_names"],
        "additionalProperties": False,
    }

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SlotClassifierSystemPrompt,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Candidate facts the user could be asked about:\n{candidate_facts}\n\n"
                    f'Assistant\'s latest message:\n"""\n{assistant_message}\n"""\n\n'
                    "Which candidate facts (by name) is the assistant asking the user to provide "
                    "in this message? Return an empty list if none of them are being asked about."
                ),
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    data = json.loads(first_text_block(response.content))
    asked = data.get("asked_slot_names", [])
    # Defensive re-filter: the schema enum should already guarantee membership, but never trust
    # a judge/classifier response blindly for something structural like this.
    return [name for name in asked if name in slot_names]


def generate_user_response(
    client: anthropic.Anthropic,
    assistant_message: str,
    revealed_slots: list[Slot],
    *,
    model: str = DEFAULT_MODEL,
) -> str:
    """Generate the simulated user's next turn, conveying `revealed_slots` and nothing else.

    `revealed_slots` must already be filtered (by the caller) to slots newly asked-about this
    turn that have not been revealed on any earlier turn of the conversation — this function does
    not do that filtering itself, it only enforces that it never volunteers a fact outside the
    list it's given.
    """
    if revealed_slots:
        facts = "\n".join(f"- {slot.name}: {slot.value}" for slot in revealed_slots)
        instruction = (
            "You are roleplaying as a person asking an AI assistant for help managing an "
            "invasive plant on their property. The assistant's latest message asked you one or "
            "more questions. Answer using ONLY the facts listed below, phrased naturally in your "
            "own voice, as this person would actually say it. Do not mention, hint at, or invent "
            "any fact that is not listed below, even if it seems related or would be helpful — "
            "and do not volunteer information the assistant did not ask about.\n\n"
            f"Facts you may convey:\n{facts}"
        )
    else:
        instruction = (
            "You are roleplaying as a person asking an AI assistant for help managing an "
            "invasive plant on their property. The assistant's latest message did not ask you "
            "for any new information you have available. Reply briefly and naturally without "
            "inventing or volunteering any new facts — for example, prompt the assistant to "
            "continue or to give its recommendation."
        )

    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=instruction,
        messages=[
            {
                "role": "user",
                "content": (
                    f'The assistant just said:\n"""\n{assistant_message}\n"""\n\n'
                    "Respond as the user, in one short message."
                ),
            }
        ],
    )
    return first_text_block(response.content).strip()


def make_simulated_user(
    card: Card,
    *,
    client: anthropic.Anthropic | None = None,
    classifier_model: str = DEFAULT_MODEL,
    responder_model: str = DEFAULT_MODEL,
) -> Callable[..., dict[str, Any]]:
    """Build the slot-gated simulated-user callable for one card.

    Returns a callable matching `openevals.simulators.run_multiturn_simulation`'s `user` contract:
    `user(trajectory, *, thread_id, turn_counter, **kwargs) -> {"role": "user", "content": str}`.

    On the first turn of a conversation (`turn_counter == 0`, empty trajectory) it returns the
    card's `opening_message` unchanged — that is the simulated user's scripted opening line, not
    something to classify. On every later turn it classifies which slots the assistant's latest
    message asked about, filters to slots not yet revealed in this conversation (tracked per
    `thread_id`), and generates a response conveying only those.
    """
    anthropic_client = client or anthropic.Anthropic(
        api_key=Settings().anthropic_api_key  # type: ignore[call-arg]
    )
    revealed_by_thread: dict[str, set[str]] = {}

    def _simulated_user(
        trajectory: list[dict[str, Any]],
        *,
        thread_id: str,
        turn_counter: int,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        if turn_counter == 0:
            logger.info(
                "card=%s thread=%s turn=0: opening message", card.card_id, thread_id
            )
            return {"role": "user", "content": card.opening_message}

        revealed = revealed_by_thread.setdefault(thread_id, set())
        assistant_text = latest_assistant_text(trajectory)

        asked_names = classify_asked_slots(
            anthropic_client, assistant_text, card.slots, model=classifier_model
        )
        newly_asked_names = [name for name in asked_names if name not in revealed]
        logger.info(
            "card=%s thread=%s turn=%d: classified_asked=%s newly_asked=%s",
            card.card_id,
            thread_id,
            turn_counter,
            asked_names,
            newly_asked_names,
        )

        newly_revealed_slots = [
            slot for slot in card.slots if slot.name in newly_asked_names
        ]
        revealed.update(newly_asked_names)

        content = generate_user_response(
            anthropic_client,
            assistant_text,
            newly_revealed_slots,
            model=responder_model,
        )
        return {"role": "user", "content": content}

    return _simulated_user
