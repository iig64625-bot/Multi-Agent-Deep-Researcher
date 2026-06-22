from __future__ import annotations

from deep_researcher.config import Settings, load_settings
from deep_researcher.llm import get_llm
from deep_researcher.prompts import RESEARCH_SUMMARY_PROMPT
from deep_researcher.state import Citation, Finding, ResearchState
from deep_researcher.tools.search import TavilySearchClient
from deep_researcher.tools.web_reader import WebReader


def _format_evidence(sources: list[Citation]) -> str:
    chunks: list[str] = []
    for source in sources:
        index = source.get("id", "?")
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        snippet = source.get("snippet", "")
        chunks.append(f"[{index}] {title}\nURL: {url}\n内容：{snippet}")
    return "\n\n".join(chunks)


def _sources_to_read(sources: list[Citation], max_pages_per_query: int) -> list[Citation]:
    if max_pages_per_query <= 0:
        return []
    return sources[:max_pages_per_query]


def researcher_node(state: ResearchState) -> ResearchState:
    settings: Settings = state.get("settings") or load_settings()
    search_client = TavilySearchClient(settings=settings)
    reader = WebReader(settings=settings)
    findings: list[Finding] = []
    citations: list[Citation] = []
    next_id = 1
    messages = state.get("messages", [])

    for subquestion in state.get("plan", []):
        raw_sources = search_client.search(subquestion, max_results=settings.max_search_results)
        enriched: list[Citation] = []
        read_urls = {
            source.get("url", "")
            for source in _sources_to_read(raw_sources, settings.max_pages_per_query)
        }

        for source in raw_sources:
            source_url = source.get("url", "")
            page_text = reader.read(source_url) if source_url in read_urls else ""
            snippet = page_text or source.get("snippet", "")
            citation: Citation = {**source, "id": next_id, "snippet": snippet[:1200]}
            next_id += 1
            enriched.append(citation)
            citations.append(citation)

        if not raw_sources:
            summary = "未配置 Tavily API Key、搜索无结果或搜索服务异常，无法获取实时外部资料。"
        else:
            try:
                response = get_llm(temperature=0.2, settings=settings).invoke(
                    RESEARCH_SUMMARY_PROMPT.format(
                        subquestion=subquestion,
                        evidence=_format_evidence(enriched),
                    )
                )
                summary = str(response.content)
            except Exception as exc:
                summary = "\n".join(
                    f"- {source.get('title', 'Untitled')}：{source.get('snippet', '')[:300]}"
                    for source in enriched
                )
                messages.append(f"Researcher summary fallback for '{subquestion}': {exc}")
        findings.append({"subquestion": subquestion, "summary": summary, "sources": enriched})

    messages.append(f"Researcher completed with {len(citations)} citations")
    return {"findings": findings, "citations": citations, "messages": messages}