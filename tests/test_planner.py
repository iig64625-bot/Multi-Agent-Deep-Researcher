from deep_researcher.agents.planner import planner_node


class FakeResponse:
    content = "1. 背景是什么？\n2. 主要应用有哪些？\n3. 未来趋势是什么？"


class FakeLLM:
    def invoke(self, prompt: str):
        assert "AI Agent" in prompt
        return FakeResponse()


def test_planner_node_returns_three_clean_items(monkeypatch):
    monkeypatch.setattr("deep_researcher.agents.planner.get_llm", lambda **kwargs: FakeLLM())

    result = planner_node({"question": "AI Agent 对软件开发有什么影响？"})

    assert result == {"plan": ["背景是什么？", "主要应用有哪些？", "未来趋势是什么？"]}