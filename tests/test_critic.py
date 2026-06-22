import json

from deep_researcher.agents.critic import critic_node


class FakeResponse:
    content = json.dumps(
        {
            "score": 8,
            "strengths": ["结构清晰"],
            "weaknesses": ["引用偏少"],
            "suggestions": ["增加来源"],
        },
        ensure_ascii=False,
    )


class FakeLLM:
    def invoke(self, prompt: str):
        assert "报告" in prompt
        return FakeResponse()


def test_critic_node_returns_review(monkeypatch):
    monkeypatch.setattr("deep_researcher.agents.critic.get_llm", lambda **kwargs: FakeLLM())

    result = critic_node({"question": "AI Agent", "report": "# 报告"})

    assert result["critic"]["score"] == 8
    assert result["critic"]["suggestions"] == ["增加来源"]