"""Application configuration loaded from a local environment file."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


class ConfigError(RuntimeError):
    """Raised when required local configuration is missing or invalid."""


@dataclass(frozen=True)
class AzureOpenAISettings:
    api_key: str
    endpoint: str
    api_version: str
    deployment: str
    max_transcript_chars: int = 120_000


def load_settings(env_path: str | Path = ".env") -> AzureOpenAISettings:
    """Load Azure OpenAI settings from `.env` and process environment variables."""

    path = Path(env_path)
    if path.exists():
        try:
            from dotenv import load_dotenv
        except ModuleNotFoundError as exc:
            raise ConfigError(
                "python-dotenv is not installed. Run `pip install -r requirements.txt`."
            ) from exc
        load_dotenv(path, override=False)

    values = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "").strip(),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip(),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        joined = ", ".join(missing)
        raise ConfigError(f"Missing required Azure OpenAI setting(s): {joined}.")

    max_chars_value = os.getenv("AZURE_OPENAI_MAX_TRANSCRIPT_CHARS", "120000").strip()
    try:
        max_transcript_chars = int(max_chars_value)
    except ValueError as exc:
        raise ConfigError("AZURE_OPENAI_MAX_TRANSCRIPT_CHARS must be an integer.") from exc
    if max_transcript_chars <= 0:
        raise ConfigError("AZURE_OPENAI_MAX_TRANSCRIPT_CHARS must be greater than zero.")

    return AzureOpenAISettings(
        api_key=values["AZURE_OPENAI_API_KEY"],
        endpoint=values["AZURE_OPENAI_ENDPOINT"],
        api_version=values["AZURE_OPENAI_API_VERSION"],
        deployment=values["AZURE_OPENAI_DEPLOYMENT"],
        max_transcript_chars=max_transcript_chars,
    )
