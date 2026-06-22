from __future__ import annotations

from deep_researcher.config import Settings, load_settings
from deep_researcher.llm import get_llm
from deep_researcher.prompts import WRITER_PROMPT
from deep_researcher.state import Citation, ResearchState


def _format_citations(citations: list[Citation]) -> str:
    if not citations:
        return "暂无外部来源。"
    return "\n".join(
        f"[{item.get('id', index)}] {item.get('title', 'Untitled')} - {item.get('url', '')}"
        for index, item in enumerate(citations, start=1)
    )


def _fallback_report(state: ResearchState) -> str:
    question = state.get("question", "研究问题")
    plan = state.get("plan", [])
    synthesis = state.get("synthesis", "暂无综合洞察。")
    citations = state.get("citations", [])
    summary = (
        "本报告由 Multi-Agent Deep Researcher 自动生成，基于 Planner、Researcher、"
        "Synthesizer、Writer、Critic 工作流完成。"
    )
    lines = [
        f"# {question}",
        "",
        "## 摘要",
        summary,
        "",
        "## 研究计划",
    ]
    lines.extend(f"- {item}" for item in plan)
    lines.extend(["", "## 关键发现", synthesis, "", "## 参考来源"])
    if citations:
        lines.extend(
            f"[{item.get('id', index)}] {item.get('title', 'Untitled')} - {item.get('url', '')}"
            for index, item in enumerate(citations, start=1)
        )
    else:
        lines.append("暂无外部来源。请配置 TAVILY_API_KEY 后重新运行。")
    return "\n".join(lines)


def writer_node(state: ResearchState) -> ResearchState:
    settings: Settings = state.get("settings") or load_settings()
    plan_text = "\n".join(f"- {item}" for item in state.get("plan", []))
    synthesis = state.get("synthesis") or plan_text
    try:
        response = get_llm(temperature=0.3, settings=settings).invoke(
            WRITER_PROMPT.format(
                question=state["question"],
                synthesis=synthesis,
                citations=_format_citations(state.get("citations", [])),
            )
        )
        report = str(response.content)
    except Exception as exc:
        report = _fallback_report({**state, "synthesis": synthesis})
        return {
            "report": report,
            "messages": state.get("messages", []) + [f"Writer fallback: {exc}"],
        }
    return {"report": report, "messages": state.get("messages", []) + ["Writer completed"]}