from deep_researcher.agents.researcher import researcher_node
from deep_researcher.config import Settings, load_settings


def test_researcher_fallback_ignores_live_env_keys(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "fake-live-key-for-test")
    load_settings.cache_clear()

    result = researcher_node(
        {
            "question": "AI Agent",
            "plan": ["背景是什么？"],
            "settings": Settings(openai_api_key="", tavily_api_key=""),
            "messages": [],
        }
    )

    assert result["citations"] == []
    assert "背景是什么？" == result["findings"][0]["subquestion"]
    load_settings.cache_clear()


def test_fallback_settings_ignore_live_openai_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-live-key-for-test")
    load_settings.cache_clear()

    result = researcher_node(
        {
            "question": "AI Agent",
            "plan": ["风险是什么？"],
            "settings": Settings(openai_api_key="", tavily_api_key=""),
            "messages": [],
        }
    )

    assert result["citations"] == []
    assert result["findings"][0]["subquestion"] == "风险是什么？"
    load_settings.cache_clear()