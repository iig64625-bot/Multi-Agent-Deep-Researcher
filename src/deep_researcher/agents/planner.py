from __future__ import annotations

from deep_researcher.config import Settings, load_settings
from deep_researcher.llm import get_llm
from deep_researcher.prompts import PLANNER_PROMPT
from deep_researcher.state import ResearchState
from deep_researcher.utils.parsing import extract_numbered_items


def planner_node(state: ResearchState) -> ResearchState:
    settings: Settings = state.get("settings") or load_settings()
    question = state["question"]
    max_items = settings.max_subquestions
    try:
        response = get_llm(temperature=0.1, settings=settings).invoke(
            PLANNER_PROMPT.format(question=question, max_items=max_items)
        )
        plan = extract_numbered_items(str(response.content), limit=max_items)
    except Exception as exc:
        plan = [
            f"{question} 的背景与定义是什么？",
            f"{question} 的当前进展和关键事实是什么？",
            f"{question} 的主要风险、争议和限制是什么？",
            f"{question} 的未来趋势与行动建议是什么？",
        ][:max_items]
        messages = state.get("messages", []) + [
            f"Planner fallback due to {type(exc).__name__}: {exc}"
        ]
        return {"plan": plan, "messages": messages}

    result: ResearchState = {"plan": plan or [question]}
    if "messages" in state:
        result["messages"] = state.get("messages", []) + ["Planner completed"]
    return result