from __future__ import annotations

from deep_researcher.config import Settings
from deep_researcher.graph import run_research


def main() -> None:
    settings = Settings(
        openai_api_key="",
        tavily_api_key="",
        max_subquestions=2,
        max_search_results=1,
        max_pages_per_query=0,
    )
    result = run_research("AI Agent 工程化有哪些关键趋势？", settings=settings)

    print("PLAN:", result.get("plan", []))
    print("REPORT_HEAD:", result.get("report", "")[:120].replace("\n", " "))
    print("CRITIC:", result.get("critic", {}))
    print("MESSAGES:", result.get("messages", []))

    if not result.get("plan"):
        raise SystemExit("smoke failed: missing plan")
    if not result.get("report"):
        raise SystemExit("smoke failed: missing report")
    if not result.get("critic"):
        raise SystemExit("smoke failed: missing critic")


if __name__ == "__main__":
    main()