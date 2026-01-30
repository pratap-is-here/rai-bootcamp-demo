"""
Configuration loader for the RAI Bootcamp demo.

Responsibilities:
- Load environment-driven settings for inference and evaluation resources.
- Load configurable SharePoint sources from JSON file or environment override.
- Provide a simple, validated configuration object for downstream modules.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


DEFAULT_SOURCES_FILENAME = "sources.json"
DEFAULT_DATA_CACHE_PATH = "./data_cache.json"
DEFAULT_LOG_LEVEL = "INFO"
CONFIG_SOURCES_URL_ENV = "CONFIG_SOURCES_URL"


@dataclass
class InferenceConfig:
    endpoint: str
    deployment_name: str
    api_version: str


@dataclass
class EvaluationConfig:
    endpoint: str
    project_name: str
    resource_group: str
    subscription_id: str


@dataclass
class AppConfig:
    inference: InferenceConfig
    evaluation: EvaluationConfig
    sources: List[Dict[str, Any]]
    data_cache_path: str
    log_level: str


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


def _load_sources(base_dir: Path) -> List[Dict[str, Any]]:
    """Load sources from env override or the default JSON file."""
    override_urls = os.getenv(CONFIG_SOURCES_URL_ENV)
    if override_urls:
        urls = [u.strip() for u in override_urls.split(",") if u.strip()]
        if not urls:
            raise ConfigError("CONFIG_SOURCES_URL is set but contains no URLs")
        return [
            {
                "name": url,
                "url": url,
                "description": "Configured via environment override",
            }
            for url in urls
        ]

    sources_path = base_dir / "config" / DEFAULT_SOURCES_FILENAME
    if not sources_path.exists():
        raise ConfigError(f"Sources file not found: {sources_path}")

    with sources_path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in sources file: {e}") from e

    if not isinstance(data, list):
        raise ConfigError("Sources file must contain a JSON array")

    return data


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def load_config(base_dir: Path | None = None) -> AppConfig:
    """Load and validate configuration for the demo application."""
    base = Path(base_dir) if base_dir else Path(__file__).resolve().parents[1]

    inference = InferenceConfig(
        endpoint=_require_env("AZURE_OPENAI_ENDPOINT"),
        deployment_name=_require_env("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        api_version=_require_env("AZURE_OPENAI_API_VERSION"),
    )

    evaluation = EvaluationConfig(
        endpoint=_require_env("EVAL_OPENAI_ENDPOINT"),
        project_name=_require_env("EVAL_AZURE_AI_PROJECT_NAME"),
        resource_group=_require_env("EVAL_AZURE_RESOURCE_GROUP"),
        subscription_id=_require_env("EVAL_AZURE_SUBSCRIPTION_ID"),
    )

    sources = _load_sources(base)

    data_cache_path = os.getenv("DATA_CACHE_PATH", DEFAULT_DATA_CACHE_PATH)
    log_level = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL)

    return AppConfig(
        inference=inference,
        evaluation=evaluation,
        sources=sources,
        data_cache_path=data_cache_path,
        log_level=log_level,
    )
