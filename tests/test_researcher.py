from deep_researcher.agents.researcher import researcher_node
from deep_researcher.config import Settings


def test_researcher_node_fallback_without_tavily_key():
    result = researcher_node(
        {
            "question": "AI Agent",
            "plan": ["背景是什么？"],
            "settings": Settings(openai_api_key="", tavily_api_key=""),
            "messages": [],
        }
    )

    assert result["findings"][0]["subquestion"] == "背景是什么？"
    assert result["citations"] == []


def test_researcher_max_pages_zero_skips_web_reader(monkeypatch):
    class FakeSearchClient:
        def __init__(self, settings):
            pass

        def search(self, query: str, max_results: int | None = None):
            return [
                {
                    "title": "Source",
                    "url": "https://example.com",
                    "snippet": "Search snippet",
                    "source": "test",
                }
            ]

    class ExplodingReader:
        def __init__(self, settings):
            pass

        def read(self, url: str):
            raise AssertionError("WebReader should not be called when max_pages_per_query=0")

    monkeypatch.setattr("deep_researcher.agents.researcher.TavilySearchClient", FakeSearchClient)
    monkeypatch.setattr("deep_researcher.agents.researcher.WebReader", ExplodingReader)

    result = researcher_node(
        {
            "question": "AI Agent",
            "plan": ["背景是什么？"],
            "settings": Settings(
                openai_api_key="",
                tavily_api_key="fake-key",
                max_pages_per_query=0,
            ),
            "messages": [],
        }
    )

    assert result["citations"][0]["snippet"] == "Search snippet"
    assert result["findings"][0]["sources"][0]["url"] == "https://example.com"