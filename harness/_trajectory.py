"""Shared helpers for reading `openevals` trajectory/content-block shapes.

Used by both `harness/conversation.py` and `harness/simulated_user.py`, which each need to pull
plain text out of an Anthropic response or an accumulated trajectory — kept here once so a future
fix to either shape (a new Anthropic content-block type, an `openevals` message-schema change)
only needs to happen in one place.
"""

from collections.abc import Iterable
from typing import Any


def first_text_block(blocks: Iterable[Any]) -> str:
    """Return the text of the first `text`-type content block, or `""` if none is present."""
    for block in blocks:
        if getattr(block, "type", None) == "text":
            return str(getattr(block, "text", ""))
    return ""


def extract_message_text(content: str | list[dict[str, Any]]) -> str:
    """Extract plain text from a trajectory message's `content`, which may be a string or a
    list of content blocks (per `openevals`' `ChatCompletionMessage`)."""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "\n".join(parts)


def latest_assistant_text(trajectory: list[dict[str, Any]]) -> str:
    for message in reversed(trajectory):
        if message.get("role") == "assistant":
            return extract_message_text(message.get("content", ""))
    raise ValueError(
        "No assistant message found in trajectory; the caller was invoked out of order "
        "(expected an assistant turn to already be present)."
    )
