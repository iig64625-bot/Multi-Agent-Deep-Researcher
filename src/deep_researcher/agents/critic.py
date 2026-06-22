from __future__ import annotations

from deep_researcher.config import Settings, load_settings
from deep_researcher.llm import get_llm
from deep_researcher.prompts import CRITIC_PROMPT
from deep_researcher.state import CriticReview, ResearchState
from deep_researcher.utils.parsing import extract_json_object


def critic_node(state: ResearchState) -> ResearchState:
    settings: Settings = state.get("settings") or load_settings()
    report = state.get("report", "")
    try:
        response = get_llm(temperature=0.0, settings=settings).invoke(
            CRITIC_PROMPT.format(report=report)
        )
        parsed = extract_json_object(str(response.content))
        review: CriticReview = {
            "score": int(parsed.get("score", 0)),
            "strengths": list(parsed.get("strengths", [])),
            "weaknesses": list(parsed.get("weaknesses", [])),
            "suggestions": list(parsed.get("suggestions", [])),
        }
    except Exception as exc:
        review = {
            "score": 6 if report else 1,
            "strengths": ["已生成基础报告结构。"] if report else [],
            "weaknesses": ["Critic LLM 调用失败或输出无法解析。"],
            "suggestions": ["检查 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL 配置。"],
        }
        return {
            "critic": review,
            "messages": state.get("messages", [])
            + [f"Critic fallback due to {type(exc).__name__}: {exc}"],
        }
    return {"critic": review, "messages": state.get("messages", []) + ["Critic completed"]}