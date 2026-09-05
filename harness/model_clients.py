"""Multi-vendor model-under-test dispatch.

Minimal scope, deliberately: only the model-under-test needs to speak 3 vendors. Judges, the two
stopping-condition classifiers, and the slot classifier all stay Anthropic-only — PRD v4 §7 only
needs human-vs-judge agreement, not cross-judge-family agreement, for the SME-validation deliverable
this was built for (a same-vendor judge/subject optics risk is `SCRATCHPAD.md` task 7's separate,
not-yet-built stretch goal). That keeps this module to "plain chat completion across 3 vendors," not
structured JSON-schema output across 3 vendors.

Each vendor branch is a plain, non-structured chat call — no JSON schema, no tools — mirroring what
`harness.conversation.make_model_under_test` already does for Anthropic. Call shapes below were
confirmed 2026-09-04 by reading the actually-installed SDK source (`openai==3.7.0`,
`google-genai==2.22.0`), not assumed from memory:

- OpenAI keeps the classic `client.chat.completions.create(model=..., messages=[...])` shape, with
  the system prompt passed as a `"system"`-role message inside `messages` (no separate `system`
  kwarg, unlike Anthropic) — confirmed against
  `openai/resources/chat/completions/completions.py`'s `create` signature.
- google-genai uses `client.models.generate_content(model=..., contents=[...], config=
  types.GenerateContentConfig(system_instruction=...))`, where each `contents` entry's role is
  `"user"` or `"model"` (never `"assistant"`), and the response exposes a `.text` convenience
  property — confirmed against `google/genai/models.py` and `google/genai/types.py`.
"""

from dataclasses import dataclass
from enum import Enum

import anthropic
import openai
from google import genai
from google.genai import types as genai_types

from harness._trajectory import first_text_block
from harness.config import Settings


class Vendor(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


MODEL_VENDOR_MAP: dict[str, Vendor] = {
    "claude-opus-5": Vendor.ANTHROPIC,
    "gpt-5.6-sol": Vendor.OPENAI,
    "gemini-3.1-pro-preview": Vendor.GOOGLE,
}
"""Explicit, pinned model-ID -> vendor table (R4/PRD hard rule 5: log exact model version strings)
— matches `harness.ground_truth`'s "explicit table, not a generic dispatcher" pattern, since the
vendor set is small and fixed.

Picked 2026-09-04 by checking each vendor's official API docs directly (`developers.openai.com`,
`ai.google.dev`), then verifying against this project's own account (`client.models.list()`) rather
than trusting docs alone — OpenAI's actual newest flagship, `gpt-6-astra` ("our most capable model,
built for the hardest end-to-end work"), 404s on this project's API key (a real, confirmed
enterprise-phased-rollout access gap, not a bug — `openai.NotFoundError: model_not_found`), so
`gpt-5.6-sol` is used instead: the previous-generation flagship this key can actually call
("the main flagship option for professional applications" per OpenAI's own docs), still materially
newer than `claude-opus-5`'s own generation lineage. Google's `gemini-3.1-pro-preview` (the
"Pro"-tier frontier reasoning model, matching Claude Opus's positioning) called successfully.
**Flagged for user confirmation before the real sweep spends budget**: (1) if/when this project's
OpenAI account gains `gpt-6-astra` access, that's the more defensible pick and this entry should be
updated; (2) Google's naming this cycle is genuinely ambiguous — some sources describe a
"Flash"-tier model as more capable than "Pro" while Pro itself is still labeled `preview`, so that
pick is a judgment call, not an unambiguous fact, unlike the Anthropic entry.
"""


@dataclass
class ModelClients:
    """One client per vendor, built once and shared across every (model, card) pair in a sweep."""

    anthropic: anthropic.Anthropic
    openai: openai.OpenAI
    google: genai.Client


def build_model_clients(settings: Settings | None = None) -> ModelClients:
    settings = settings or Settings()  # type: ignore[call-arg]
    return ModelClients(
        anthropic=anthropic.Anthropic(api_key=settings.anthropic_api_key),
        openai=openai.OpenAI(api_key=settings.openai_api_key),
        google=genai.Client(api_key=settings.google_api_key),
    )


def _generate_anthropic(
    client: anthropic.Anthropic,
    *,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int,
) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,  # type: ignore[arg-type]
    )
    return first_text_block(response.content)


def _generate_openai(
    client: openai.OpenAI,
    *,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int,
) -> str:
    full_messages = [{"role": "system", "content": system}, *messages]
    response = client.chat.completions.create(
        model=model,
        messages=full_messages,  # type: ignore[arg-type]
        max_completion_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def _generate_google(
    client: genai.Client,
    *,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int,
) -> str:
    contents = [
        {
            "role": "model" if message["role"] == "assistant" else "user",
            "parts": [{"text": message["content"]}],
        }
        for message in messages
    ]
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=genai_types.GenerateContentConfig(
            system_instruction=system, max_output_tokens=max_tokens
        ),
    )
    return response.text or ""


def generate_chat_response(
    clients: ModelClients,
    *,
    model: str,
    system: str,
    messages: list[dict[str, str]],
    max_tokens: int = 4096,
) -> str:
    """Dispatch a plain (non-structured) chat completion to whichever vendor `model` maps to.

    `messages` always uses the Anthropic/OpenAI-style `{"role": "user" | "assistant", "content":
    ...}` shape — the Google branch translates it to Gemini's `"user"`/`"model"` roles internally,
    so callers never need to know which vendor a given `model` id belongs to.

    `max_tokens=4096` mirrors `harness.conversation.make_model_under_test`'s own default: this
    codebase has twice hit a thinking-capable Anthropic model silently truncating to zero text
    because a low `max_tokens` budget was entirely consumed by reasoning tokens before any text was
    emitted (see `DECISION-LOG.md`'s 2026-09-03 entries) — the same failure mode is plausible for
    `gpt-6-astra` and `gemini-3.1-pro-preview`, both plausibly reasoning-capable models, so this
    default stays generous rather than re-discovering that bug a third time per vendor.
    """
    vendor = MODEL_VENDOR_MAP.get(model)
    if vendor is None:
        raise ValueError(
            f"Unknown model id {model!r} — add it to MODEL_VENDOR_MAP before using it as a "
            "model-under-test."
        )
    if vendor == Vendor.ANTHROPIC:
        return _generate_anthropic(
            clients.anthropic,
            model=model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
        )
    if vendor == Vendor.OPENAI:
        return _generate_openai(
            clients.openai,
            model=model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
        )
    return _generate_google(
        clients.google,
        model=model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
    )
