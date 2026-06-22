import httpx

from deep_researcher.config import Settings
from deep_researcher.tools.search import TavilySearchClient
from deep_researcher.tools.web_reader import WebReader


def test_tavily_search_without_api_key_returns_empty_list():
    client = TavilySearchClient(Settings(tavily_api_key=""))

    assert client.search("AI Agent") == []


def test_web_reader_network_error_returns_empty_string(monkeypatch):
    def fake_get(self, url: str):
        raise httpx.ConnectError("network down")

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    reader = WebReader(Settings())

    assert reader.read("https://bad.example") == ""