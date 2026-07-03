from pathlib import Path
import os
from unittest.mock import patch

from yt_video_qa.config import ConfigError, load_settings


def test_load_settings_from_environment_without_dotenv_file():
    env = {
        "AZURE_OPENAI_API_KEY": "key",
        "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com/",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "AZURE_OPENAI_DEPLOYMENT": "deployment",
        "AZURE_OPENAI_MAX_TRANSCRIPT_CHARS": "500",
    }
    with patch.dict(os.environ, env, clear=True):
        settings = load_settings(Path("does-not-exist.env"))

    assert settings.api_key == "key"
    assert settings.deployment == "deployment"
    assert settings.max_transcript_chars == 500


def test_load_settings_reports_missing_values():
    with patch.dict(os.environ, {}, clear=True):
        try:
            load_settings(Path("does-not-exist.env"))
        except ConfigError as exc:
            assert "AZURE_OPENAI_API_KEY" in str(exc)
            assert "AZURE_OPENAI_DEPLOYMENT" in str(exc)
        else:
            raise AssertionError("Expected ConfigError")
