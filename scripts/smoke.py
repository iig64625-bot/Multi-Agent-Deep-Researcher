from __future__ import annotations

import sys


try:
    from deep_researcher.config import Settings
    from deep_researcher.graph import run_research
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Could not import project modules. Run in PowerShell with "
        '$env:PYTHONPATH="src" and use the project .venv python.'
    ) from exc


def main() -> None:
    settings = Settings(
        openai_api_key="",
        tavily_api_key="",
        max_subquestions=2,
        max_search_results=1,
        max_pages_per_query=0,
        max_rewrites=1,
    )
    result = run_research("AI Agent 工程化有哪些关键趋势？", settings=settings)

    print("PYTHON:", sys.executable)
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