from __future__ import annotations

from langchain_openai import ChatOpenAI

from deep_researcher.config import Settings, load_settings


def get_llm(temperature: float = 0.2, settings: Settings | None = None) -> ChatOpenAI:
    config = settings or load_settings()
    if not config.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return ChatOpenAI(
        model=config.resolved_model(),
        api_key=config.openai_api_key,
        base_url=config.openai_base_url,
        temperature=temperature,
    )
