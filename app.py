from __future__ import annotations

import time

import streamlit as st

from deep_researcher.config import Settings, load_settings
from deep_researcher.graph import run_research

st.set_page_config(page_title="Multi-Agent Deep Researcher", page_icon="🔎", layout="wide")


def render_sidebar(settings: Settings) -> Settings:
    st.sidebar.title("运行配置")
    st.sidebar.caption("支持 OpenAI-compatible LLM API 与 Tavily Search API。")

    model = st.sidebar.text_input("OPENAI_MODEL", value=settings.resolved_model())
    base_url = st.sidebar.text_input("OPENAI_BASE_URL", value=settings.openai_base_url)
    max_subquestions = st.sidebar.slider("Planner 子问题数量", 2, 6, settings.max_subquestions)
    max_search_results = st.sidebar.slider("每个子问题搜索结果", 1, 8, settings.max_search_results)
    max_pages = st.sidebar.slider("每个子问题读取网页", 0, 5, settings.max_pages_per_query)

    st.sidebar.divider()
    st.sidebar.write("API Key 状态")
    st.sidebar.write("LLM:", "✅ 已配置" if settings.openai_api_key else "⚠️ 未配置")
    st.sidebar.write("Tavily:", "✅ 已配置" if settings.tavily_api_key else "⚠️ 未配置")

    return settings.model_copy(
        update={
            "openai_model": model,
            "openai_base_url": base_url,
            "max_subquestions": max_subquestions,
            "max_search_results": max_search_results,
            "max_pages_per_query": max_pages,
        }
    )


def render_sources(citations: list[dict]) -> None:
    if not citations:
        st.info("暂无引用来源。配置 TAVILY_API_KEY 后可获取实时搜索来源。")
        return
    for citation in citations:
        citation_id = citation.get("id", "?")
        title = citation.get("title") or "Untitled"
        url = citation.get("url") or ""
        st.markdown(f"**[{citation_id}] {title}**")
        if url:
            st.markdown(url)
        if citation.get("snippet"):
            st.caption(citation["snippet"][:500])


def main() -> None:
    settings = render_sidebar(load_settings())

    st.title("🔎 Multi-Agent Deep Researcher")
    st.caption("Planner → Researcher → Synthesizer → Writer → Critic 的多智能体深度研究助手")

    with st.expander("如何开始", expanded=not settings.openai_api_key):
        st.markdown(
            """
            1. 复制 `.env.example` 为 `.env`。
            2. 填写 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`。
            3. 填写 `TAVILY_API_KEY` 以启用联网搜索与引用。
            4. 运行 `streamlit run app.py`。
            """
        )

    question = st.text_area(
        "输入研究问题",
        value="2026 年 AI Agent 工程化的关键趋势、风险与落地建议是什么？",
        height=120,
    )

    if st.button("开始深度研究", type="primary", disabled=not question.strip()):
        started_at = time.perf_counter()
        with st.spinner("多智能体正在执行：规划、搜索、阅读、综合、写作、评审..."):
            final_state = run_research(question.strip(), settings=settings)
        elapsed = time.perf_counter() - started_at
        st.success(f"研究完成，用时 {elapsed:.1f} 秒")

        report_tab, source_tab, process_tab, critic_tab = st.tabs(
            ["Markdown 报告", "引用来源", "执行过程", "Critic 评审"]
        )

        with report_tab:
            report = final_state.get("report", "")
            st.markdown(report)
            st.download_button(
                "下载 Markdown",
                data=report.encode("utf-8"),
                file_name="deep_research_report.md",
                mime="text/markdown",
            )

        with source_tab:
            render_sources(final_state.get("citations", []))

        with process_tab:
            st.subheader("Planner 输出")
            st.json(final_state.get("plan", []))
            st.subheader("Researcher 发现")
            st.json(final_state.get("findings", []))
            st.subheader("Synthesizer 输出")
            st.markdown(final_state.get("synthesis", ""))
            st.subheader("运行日志")
            st.json(final_state.get("messages", []))

        with critic_tab:
            st.json(final_state.get("critic", {}))


if __name__ == "__main__":
    main()
