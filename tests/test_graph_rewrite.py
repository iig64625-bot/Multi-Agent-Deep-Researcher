from deep_researcher.config import Settings
from deep_researcher.graph import run_research


class FakeCriticResponse:
    def __init__(self, score: int):
        self.content = (
            f'{{"score": {score}, "strengths": ["ok"], '
            '"weaknesses": ["needs work"], "suggestions": ["rewrite"]}'
        )


class FakeWriterResponse:
    def __init__(self, title: str):
        self.content = f"# {title}\n\nReport body"


class SequentialLLM:
    def __init__(self):
        self.writer_calls = 0
        self.critic_calls = 0

    def invoke(self, prompt: str):
        if "只输出 JSON" in prompt:
            self.critic_calls += 1
            score = 6 if self.critic_calls == 1 else 8
            return FakeCriticResponse(score)
        if "生成一份带引用的 Markdown 深度研究报告" in prompt:
            self.writer_calls += 1
            return FakeWriterResponse(f"Draft {self.writer_calls}")
        raise AssertionError("Unexpected prompt")


def test_low_score_triggers_single_rewrite(monkeypatch):
    llm = SequentialLLM()
    monkeypatch.setattr("deep_researcher.agents.writer.get_llm", lambda **kwargs: llm)
    monkeypatch.setattr("deep_researcher.agents.critic.get_llm", lambda **kwargs: llm)

    result = run_research(
        "AI Agent 工程化有哪些关键趋势？",
        settings=Settings(openai_api_key="x", tavily_api_key="", max_rewrites=1),
    )

    assert llm.writer_calls == 2
    assert llm.critic_calls == 2
    assert result["rewrite_count"] == 1
    assert result["critic"]["score"] == 8


def test_max_rewrites_stops_on_low_score(monkeypatch):
    class AlwaysLowLLM(SequentialLLM):
        def invoke(self, prompt: str):
            if "只输出 JSON" in prompt:
                self.critic_calls += 1
                return FakeCriticResponse(6)
            if "生成一份带引用的 Markdown 深度研究报告" in prompt:
                self.writer_calls += 1
                return FakeWriterResponse(f"Draft {self.writer_calls}")
            raise AssertionError("Unexpected prompt")

    llm = AlwaysLowLLM()
    monkeypatch.setattr("deep_researcher.agents.writer.get_llm", lambda **kwargs: llm)
    monkeypatch.setattr("deep_researcher.agents.critic.get_llm", lambda **kwargs: llm)

    result = run_research(
        "AI Agent 工程化有哪些关键趋势？",
        settings=Settings(openai_api_key="x", tavily_api_key="", max_rewrites=1),
    )

    assert llm.writer_calls == 2
    assert llm.critic_calls == 2
    assert result["rewrite_count"] == 1
    assert result["critic"]["score"] == 6