from __future__ import annotations

from deep_researcher.config import Settings, load_settings
from deep_researcher.llm import get_llm
from deep_researcher.prompts import SYNTHESIZER_PROMPT
from deep_researcher.state import Finding, ResearchState


def _format_findings(findings: list[Finding]) -> str:
    return "\n\n".join(
        f"## {item.get('subquestion', '')}\n{item.get('summary', '')}" for item in findings
    )


def synthesizer_node(state: ResearchState) -> ResearchState:
    settings: Settings = state.get("settings") or load_settings()
    findings = state.get("findings", [])
    fallback = _format_findings(findings)
    try:
        response = get_llm(temperature=0.2, settings=settings).invoke(
            SYNTHESIZER_PROMPT.format(question=state["question"], findings=fallback)
        )
        synthesis = str(response.content)
    except Exception as exc:
        synthesis = fallback or "暂无可综合的研究发现。"
        return {
            "synthesis": synthesis,
            "messages": state.get("messages", [])
            + [f"Synthesizer fallback due to {type(exc).__name__}: {exc}"],
        }
    return {
        "synthesis": synthesis,
        "messages": state.get("messages", []) + ["Synthesizer completed"],
    }