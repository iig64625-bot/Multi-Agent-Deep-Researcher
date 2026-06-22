from deep_researcher.agents.researcher import researcher_node


def test_researcher_node_fallback_without_tavily_key():
    result = researcher_node({"question": "AI Agent", "plan": ["背景是什么？"], "messages": []})

    assert result["findings"][0]["subquestion"] == "背景是什么？"
    assert result["citations"] == []
