from deep_researcher.state import ResearchState


def test_research_state_accepts_question_plan_and_report():
    state: ResearchState = {
        "question": "AI Agent 是什么？",
        "plan": ["背景", "应用", "趋势"],
        "report": "# 报告",
    }

    assert state["question"] == "AI Agent 是什么？"
    assert len(state["plan"]) == 3
    assert state["report"].startswith("#")
