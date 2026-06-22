from deep_researcher.agents.planner import planner_node
from deep_researcher.config import Settings


class FakeResponse:
    content = "1. 背景是什么？\n2. 风险是什么？"


class FakeLLM:
    def invoke(self, prompt: str):
        return FakeResponse()


def test_planner_passes_state_settings_to_llm(monkeypatch):
    captured = {}

    def fake_get_llm(**kwargs):
        captured.update(kwargs)
        return FakeLLM()

    settings = Settings(openai_model="custom-test-model", max_subquestions=2)
    monkeypatch.setattr("deep_researcher.agents.planner.get_llm", fake_get_llm)

    result = planner_node({"question": "AI Agent", "settings": settings})

    assert result["plan"] == ["背景是什么？", "风险是什么？"]
    assert captured["settings"].resolved_model() == "custom-test-model"