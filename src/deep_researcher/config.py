from __future__ import annotations

import os
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    model_name: str = ""
    tavily_api_key: str = ""
    max_subquestions: int = 4
    max_search_results: int = 5
    max_pages_per_query: int = 3
    max_rewrites: int = 1
    request_timeout_seconds: float = 15.0

    def resolved_model(self) -> str:
        return self.openai_model or self.model_name or "gpt-4o-mini"

    def model_copy(self, update: dict | None = None) -> Settings:
        return replace(self, **(update or {}))


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _load_streamlit_secrets() -> dict[str, Any]:
    try:
        import streamlit as st
    except Exception:
        return {}

    try:
        return dict(st.secrets)
    except Exception:
        return {}


def _get_config_value(
    name: str,
    default: str,
    secrets: dict[str, Any],
) -> str:
    env_value = os.getenv(name)
    if env_value not in (None, ""):
        return env_value

    secret_value = secrets.get(name)
    if secret_value not in (None, ""):
        return str(secret_value)

    return default


def _build_settings_from_sources(secrets: dict[str, Any]) -> Settings:
    model_name = _get_config_value("MODEL_NAME", "", secrets)
    openai_model = _get_config_value(
        "OPENAI_MODEL",
        model_name or "gpt-4o-mini",
        secrets,
    )
    return Settings(
        openai_api_key=_get_config_value("OPENAI_API_KEY", "", secrets),
        openai_base_url=_get_config_value(
            "OPENAI_BASE_URL",
            "https://api.openai.com/v1",
            secrets,
        ),
        openai_model=openai_model,
        model_name=model_name,
        tavily_api_key=_get_config_value("TAVILY_API_KEY", "", secrets),
        max_subquestions=_int_env("MAX_SUBQUESTIONS", 4),
        max_search_results=_int_env("MAX_SEARCH_RESULTS", 5),
        max_pages_per_query=_int_env("MAX_PAGES_PER_QUERY", 3),
        max_rewrites=_int_env("MAX_REWRITES", 1),
        request_timeout_seconds=_float_env("REQUEST_TIMEOUT_SECONDS", 15.0),
    )


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    load_dotenv(override=False)
    secrets = _load_streamlit_secrets()
    return _build_settings_from_sources(secrets)
