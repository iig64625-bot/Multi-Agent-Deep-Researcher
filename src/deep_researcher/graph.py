from __future__ import annotations

from langgraph.graph import END, StateGraph

from deep_researcher.agents.critic import critic_node
from deep_researcher.agents.planner import planner_node
from deep_researcher.agents.researcher import researcher_node
from deep_researcher.agents.synthesizer import synthesizer_node
from deep_researcher.agents.writer import writer_node
from deep_researcher.config import Settings, load_settings
from deep_researcher.state import ResearchState


def should_rewrite(state: ResearchState) -> str:
    settings: Settings = state.get("settings") or load_settings()
    score = int(state.get("critic", {}).get("score", 0))
    rewrite_count = state.get("rewrite_count", 0)
    if score < 7 and rewrite_count < settings.max_rewrites:
        return "rewrite"
    return "end"


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "synthesizer")
    graph.add_edge("synthesizer", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges("critic", should_rewrite, {"rewrite": "writer", "end": END})
    return graph.compile()


def run_research(question: str, settings: Settings | None = None) -> ResearchState:
    config = settings or load_settings()
    initial_state: ResearchState = {
        "question": question,
        "settings": config,
        "rewrite_count": 0,
        "messages": ["Workflow started"],
    }
    return build_graph().invoke(initial_state)