from __future__ import annotations

import httpx

from deep_researcher.config import Settings, load_settings
from deep_researcher.state import Citation


class TavilySearchClient:
    """Small Tavily Search API wrapper with safe fallbacks."""

    endpoint = "https://api.tavily.com/search"

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()

    def search(self, query: str, max_results: int | None = None) -> list[Citation]:
        if not self.settings.tavily_api_key:
            return []
        payload = {
            "api_key": self.settings.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": max_results or self.settings.max_search_results,
        }
        try:
            with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
                response = client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError, TypeError):
            return []

        results: list[Citation] = []
        for item in data.get("results", []):
            results.append(
                {
                    "title": item.get("title") or item.get("url", "Untitled"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content") or item.get("snippet", ""),
                    "source": "tavily",
                }
            )
        return results