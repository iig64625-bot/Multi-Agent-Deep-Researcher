from __future__ import annotations

import re

import httpx

from deep_researcher.config import Settings, load_settings
from deep_researcher.utils.parsing import normalize_whitespace

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    BeautifulSoup = None


class WebReader:
    """Fetch and extract readable text from web pages."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()

    def read(self, url: str, max_chars: int = 3500) -> str:
        if not url:
            return ""
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MultiAgentDeepResearcher/0.1)"
        }
        try:
            with httpx.Client(
                timeout=self.settings.request_timeout_seconds,
                follow_redirects=True,
                headers=headers,
            ) as client:
                response = client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return ""

        text = self._extract_text(response.text)
        return text[:max_chars]

    def _extract_text(self, html: str) -> str:
        if BeautifulSoup is not None:
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
                tag.decompose()
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            text = normalize_whitespace(" ".join(soup.stripped_strings))
            if title and not text.startswith(title):
                text = f"{title}. {text}"
            return text

        html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.I | re.S)
        html = re.sub(r"<[^>]+>", " ", html)
        html = html.replace("&nbsp;", " ").replace("&amp;", "&")
        return normalize_whitespace(html)