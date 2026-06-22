from __future__ import annotations

import os
from dataclasses import dataclass, replace
from functools import lru_cache

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


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    load_dotenv(override=False)
    model_name = os.getenv("MODEL_NAME", "")
    openai_model = os.getenv("OPENAI_MODEL", model_name or "gpt-4o-mini")
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=openai_model,
        model_name=model_name,
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        max_subquestions=_int_env("MAX_SUBQUESTIONS", 4),
        max_search_results=_int_env("MAX_SEARCH_RESULTS", 5),
        max_pages_per_query=_int_env("MAX_PAGES_PER_QUERY", 3),
        request_timeout_seconds=_float_env("REQUEST_TIMEOUT_SECONDS", 15.0),
    )
