from deep_researcher.agents.writer import writer_node


class FakeResponse:
    content = "# AI Agent 报告\n\n这是简短报告。"


class FakeLLM:
    def invoke(self, prompt: str):
        assert "背景" in prompt
        return FakeResponse()


def test_writer_node_returns_report(monkeypatch):
    monkeypatch.setattr("deep_researcher.agents.writer.get_llm", lambda **kwargs: FakeLLM())

    result = writer_node(
        {
            "question": "AI Agent 对软件开发有什么影响？",
            "plan": ["背景", "应用", "趋势"],
        }
    )

    assert result["report"].startswith("# AI Agent 报告")