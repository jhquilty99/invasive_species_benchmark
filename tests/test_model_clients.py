"""Tests for `harness.model_clients` — the multi-vendor model-under-test dispatch.

The three vendor branches (`test_generate_chat_response_*`) are cassette-recorded against the real
APIs deliberately — this module exists specifically because the SDK call shapes weren't already
proven out anywhere else in this codebase (unlike the Anthropic branch, which mirrors
`harness.conversation.make_model_under_test`'s already-working call), so a mocked test would defeat
the point: it would pass even if the actual OpenAI/Google call shape were wrong.
"""

from typing import Any

import openai
import pytest
from google import genai

from harness.model_clients import (
    MODEL_VENDOR_MAP,
    ModelClients,
    Vendor,
    generate_chat_response,
)


@pytest.fixture
def vcr_config() -> dict[str, Any]:
    return {
        "filter_headers": ["x-api-key", "authorization", "x-goog-api-key"],
        "filter_query_parameters": ["key"],
    }


def _clients(*, openai_key: str = "unused", google_key: str = "unused") -> ModelClients:
    import anthropic

    return ModelClients(
        anthropic=anthropic.Anthropic(api_key="unused"),
        openai=openai.OpenAI(api_key=openai_key),
        google=genai.Client(api_key=google_key),
    )


def test_model_vendor_map_has_one_entry_per_vendor() -> None:
    vendors = set(MODEL_VENDOR_MAP.values())
    assert vendors == {Vendor.ANTHROPIC, Vendor.OPENAI, Vendor.GOOGLE}


def test_generate_chat_response_raises_on_unknown_model() -> None:
    with pytest.raises(ValueError, match="Unknown model id"):
        generate_chat_response(
            _clients(),
            model="not-a-real-model",
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "hi"}],
        )


@pytest.mark.vcr()
def test_generate_chat_response_openai_returns_text() -> None:
    import os

    clients = _clients(
        openai_key=os.environ.get("OPENAI_API_KEY", "test-key-for-cassette-replay")
    )

    text = generate_chat_response(
        clients,
        model="gpt-5.6-sol",
        system="You are a helpful assistant. Reply in exactly three words.",
        messages=[{"role": "user", "content": "Say hello."}],
        max_tokens=1024,
    )

    assert isinstance(text, str)
    assert text.strip() != ""


@pytest.mark.vcr()
def test_generate_chat_response_google_returns_text() -> None:
    import os

    clients = _clients(
        google_key=os.environ.get("GOOGLE_API_KEY", "test-key-for-cassette-replay")
    )

    text = generate_chat_response(
        clients,
        model="gemini-3.1-pro-preview",
        system="You are a helpful assistant. Reply in exactly three words.",
        messages=[{"role": "user", "content": "Say hello."}],
        max_tokens=1024,
    )

    assert isinstance(text, str)
    assert text.strip() != ""


@pytest.mark.vcr()
def test_generate_chat_response_google_multi_turn_translates_roles() -> None:
    """Confirms the assistant->model role translation actually round-trips through a real call
    (a wrong role name would surface as an API error here, not a silent bug)."""
    import os

    clients = _clients(
        google_key=os.environ.get("GOOGLE_API_KEY", "test-key-for-cassette-replay")
    )

    text = generate_chat_response(
        clients,
        model="gemini-3.1-pro-preview",
        system="You are a helpful assistant.",
        messages=[
            {
                "role": "user",
                "content": "My favorite color is teal. Just acknowledge that.",
            },
            {"role": "assistant", "content": "Got it, teal."},
            {"role": "user", "content": "What's my favorite color? One word answer."},
        ],
        max_tokens=1024,
    )

    assert "teal" in text.lower()
