from __future__ import annotations

from langgraph.graph import END, StateGraph

from deep_researcher.agents.critic import critic_node
from deep_researcher.agents.planner import planner_node
from deep_researcher.agents.researcher import researcher_node
from deep_researcher.agents.synthesizer import synthesizer_node
from deep_researcher.agents.writer import writer_node
from deep_researcher.config import Settings, load_settings
from deep_researcher.state import ResearchState


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
    graph.add_edge("critic", END)
    return graph.compile()


def run_research(question: str, settings: Settings | None = None) -> ResearchState:
    config = settings or load_settings()
    initial_state: ResearchState = {
        "question": question,
        "settings": config,
        "messages": ["Workflow started"],
    }
    return build_graph().invoke(initial_state)
