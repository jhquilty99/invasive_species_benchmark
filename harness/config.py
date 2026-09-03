"""Application/SDK-facing configuration.

Loads API keys and Langfuse credentials from a root `.env` file (or the real
environment). This is a separate config surface from `infra/langfuse/.env`,
which is docker-compose-only and used to bring up the Langfuse stack itself.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single source of truth for API keys and Langfuse credentials.

    Missing or malformed config fails fast at import/instantiation time —
    pydantic-settings raises a validation error for any field below with no
    default whose environment variable is absent.
    """

    model_config = SettingsConfigDict(env_file=".env")

    anthropic_api_key: str
    openai_api_key: str
    google_api_key: str
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str = "http://localhost:3000"
