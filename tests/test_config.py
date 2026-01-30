"""
Unit tests for configuration loader.
"""
from pathlib import Path
import json
import os
import pytest

from app.config_loader import (
    load_config,
    ConfigError,
    DEFAULT_DATA_CACHE_PATH,
    DEFAULT_LOG_LEVEL,
)


REQUIRED_ENV = {
    "AZURE_OPENAI_ENDPOINT": "https://example-inference.openai.azure.com/",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "gpt-4o-mini-autogen",
    "AZURE_OPENAI_API_VERSION": "2024-12-01-preview",
    "EVAL_OPENAI_ENDPOINT": "https://example-eval.openai.azure.com/",
    "EVAL_AZURE_AI_PROJECT_NAME": "ai-project-eval",
    "EVAL_AZURE_RESOURCE_GROUP": "rg-eval",
    "EVAL_AZURE_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000000",
}


def set_required_env(monkeypatch):
    for k, v in REQUIRED_ENV.items():
        monkeypatch.setenv(k, v)


def write_sources(tmp_path: Path, entries=None):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    sources_path = config_dir / "sources.json"
    payload = entries if entries is not None else [
        {"name": "Example", "url": "https://contoso.com", "description": "Example"}
    ]
    sources_path.write_text(json.dumps(payload), encoding="utf-8")
    return sources_path


class TestLoadConfig:
    def test_loads_from_file(self, tmp_path, monkeypatch):
        set_required_env(monkeypatch)
        write_sources(tmp_path)

        cfg = load_config(base_dir=tmp_path)

        assert cfg.inference.endpoint == REQUIRED_ENV["AZURE_OPENAI_ENDPOINT"]
        assert cfg.evaluation.project_name == REQUIRED_ENV["EVAL_AZURE_AI_PROJECT_NAME"]
        assert len(cfg.sources) == 1
        assert cfg.data_cache_path == DEFAULT_DATA_CACHE_PATH
        assert cfg.log_level == DEFAULT_LOG_LEVEL

    def test_env_override_sources(self, tmp_path, monkeypatch):
        set_required_env(monkeypatch)
        write_sources(tmp_path, entries=[])  # should be ignored due to override
        override_urls = "https://a.com, https://b.com"
        monkeypatch.setenv("CONFIG_SOURCES_URL", override_urls)

        cfg = load_config(base_dir=tmp_path)

        urls = [s["url"] for s in cfg.sources]
        assert urls == ["https://a.com", "https://b.com"]
        assert cfg.sources[0]["description"].startswith("Configured via environment")

    def test_missing_env_raises(self, tmp_path, monkeypatch):
        # Intentionally skip setting env to trigger failure
        write_sources(tmp_path)

        with pytest.raises(ConfigError) as exc:
            load_config(base_dir=tmp_path)

        assert "Missing required environment variable" in str(exc.value)

    def test_invalid_sources_json_raises(self, tmp_path, monkeypatch):
        set_required_env(monkeypatch)
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "sources.json").write_text("not-json", encoding="utf-8")

        with pytest.raises(ConfigError) as exc:
            load_config(base_dir=tmp_path)

        assert "Invalid JSON" in str(exc.value)
