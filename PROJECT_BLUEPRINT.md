# Multi-Agent Deep Researcher 项目蓝图

> **For Hermes:** 这是一个用于 1-2 周快速上手、可写入简历的 AI Agent Native 项目规划。当前只提供蓝图与代码骨架，不执行实现。

**Goal:** 用 Python 构建一个「多智能体深度研究助手」：输入一个研究问题，系统自动规划、联网搜索、阅读网页、综合总结、生成带引用的 Markdown 报告，并通过 Critic Agent 做一次质量检查。

**Architecture:** 项目以 LangGraph 的有向状态图为核心，将任务拆成 Planner / Researcher / Synthesizer / Writer / Critic 五个节点。每个节点都是一个 Agent 或 LLM 节点，围绕共享 State 读写中间结果，最终生成可展示的报告。

**Tech Stack:** Python 3.11+、LangGraph、LangChain、OpenAI-compatible LLM API、Tavily Search API、httpx、BeautifulSoup4、Streamlit、pytest、ruff、python-dotenv。

---

## 1. 项目定位

### 项目名称

**Agentic Deep Research Assistant / 多智能体深度研究助手**

### 一句话介绍

一个基于 LangGraph 的多智能体研究系统，能够自动拆解用户问题、并行搜索资料、抽取网页信息、生成带引用的研究报告，并用 Critic Agent 对报告进行自我评审。

### 简历价值

这个项目能展示：

1. **Agent Native 架构**：不是简单调用一次 LLM，而是由多个 Agent 协作完成任务。
2. **工具调用能力**：Agent 能调用搜索、网页读取、引用整理等工具。
3. **工作流编排能力**：使用 LangGraph 管理状态、节点、条件边和迭代流程。
4. **工程化能力**：有前端 Demo、测试、Docker、README、可复现配置。
5. **可量化效果**：可以统计工具调用次数、报告引用数量、生成耗时、Critic 评分。

---

## 2. MVP 功能范围

### 必做功能

- 用户输入一个研究问题。
- Planner Agent 将问题拆成 3-5 个子问题。
- Researcher Agent 对每个子问题调用搜索工具。
- Web Reader 抓取搜索结果网页正文。
- Synthesizer Agent 整理发现，去重并保留来源 URL。
- Writer Agent 生成 Markdown 报告。
- Critic Agent 对报告给出评分和改进建议。
- Streamlit 页面展示报告、引用和执行过程。

### 暂不做功能

- 用户登录系统。
- 长期记忆数据库。
- 复杂权限系统。
- 多用户并发队列。
- 浏览器自动操作。
- 向量数据库 RAG。

这些可以作为后续增强，但 1-2 周内先不做，避免项目失控。

---

## 3. 推荐目录结构

```text
agentic-deep-researcher/
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── app.py                         # Streamlit 入口
├── src/
│   └── deep_researcher/
│       ├── __init__.py
│       ├── config.py              # 环境变量与模型配置
│       ├── graph.py               # LangGraph 工作流定义
│       ├── state.py               # 全局状态结构
│       ├── llm.py                 # LLM 客户端封装
│       ├── prompts.py             # Prompt 模板
│       ├── schemas.py             # Pydantic 输出结构
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── planner.py
│       │   ├── researcher.py
│       │   ├── synthesizer.py
│       │   ├── writer.py
│       │   └── critic.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── search.py          # Tavily 搜索
│       │   └── web_reader.py      # 网页正文抽取
│       └── utils/
│           ├── __init__.py
│           └── citations.py       # 引用格式化
├── tests/
│   ├── test_state.py
│   ├── test_citations.py
│   ├── test_planner.py
│   └── test_graph_smoke.py
└── examples/
    ├── sample_question.md
    └── sample_report.md
```

---

## 4. 核心数据结构

### `src/deep_researcher/state.py`

```python
from __future__ import annotations

from typing import Annotated, TypedDict
import operator


class Source(TypedDict):
    title: str
    url: str
    snippet: str
    content: str


class ResearchFinding(TypedDict):
    sub_question: str
    summary: str
    sources: list[Source]


class Critique(TypedDict):
    score: int
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]


class ResearchState(TypedDict, total=False):
    question: str
    plan: list[str]
    findings: Annotated[list[ResearchFinding], operator.add]
    synthesized_notes: str
    report: str
    critique: Critique
    iteration: int
```

说明：

- `question`：用户原始问题。
- `plan`：Planner 拆出来的子问题列表。
- `findings`：每个子问题对应的搜索结果和总结。
- `synthesized_notes`：综合后的中间笔记。
- `report`：最终 Markdown 报告。
- `critique`：质量评审结果。
- `iteration`：反思迭代次数，MVP 中最多 1 次。

---

## 5. 配置与依赖

### `requirements.txt`

```txt
langgraph>=0.2.60
langchain>=0.3.0
langchain-openai>=0.2.0
python-dotenv>=1.0.1
pydantic>=2.8.0
tavily-python>=0.5.0
httpx>=0.27.0
beautifulsoup4>=4.12.3
readability-lxml>=0.8.1
streamlit>=1.37.0
pytest>=8.3.0
ruff>=0.6.0
```

### `.env.example`

```bash
# OpenAI-compatible API
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

# Search
TAVILY_API_KEY=your_tavily_key_here

# App
MAX_SEARCH_RESULTS=5
MAX_WEB_CHARS=6000
MAX_ITERATIONS=1
```

### `src/deep_researcher/config.py`

```python
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")

    tavily_api_key: str = Field(alias="TAVILY_API_KEY")
    max_search_results: int = Field(default=5, alias="MAX_SEARCH_RESULTS")
    max_web_chars: int = Field(default=6000, alias="MAX_WEB_CHARS")
    max_iterations: int = Field(default=1, alias="MAX_ITERATIONS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

注意：如果使用 `pydantic_settings`，需要在 `requirements.txt` 里额外加：

```txt
pydantic-settings>=2.4.0
```

---

## 6. LLM 封装

### `src/deep_researcher/llm.py`

```python
from langchain_openai import ChatOpenAI

from deep_researcher.config import get_settings


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=temperature,
    )
```

---

## 7. Prompt 设计

### `src/deep_researcher/prompts.py`

```python
PLANNER_PROMPT = """
你是一个研究任务规划专家。

用户问题：{question}

请将这个问题拆解成 3 到 5 个可以独立研究的子问题。
要求：
1. 子问题之间尽量不重复。
2. 子问题应该覆盖背景、现状、关键争议、代表案例、未来趋势。
3. 输出必须是 JSON 数组，不要输出额外解释。

示例输出：
["子问题1", "子问题2", "子问题3"]
"""

RESEARCHER_PROMPT = """
你是一个研究员。你会看到一个子问题和若干网页资料。

子问题：{sub_question}

网页资料：
{sources}

请完成：
1. 用中文总结和该子问题相关的关键事实。
2. 不要编造资料中没有的信息。
3. 保留引用 URL。
4. 输出 Markdown。
"""

SYNTHESIZER_PROMPT = """
你是一个信息综合专家。

原始问题：{question}

研究发现：
{findings}

请将不同研究员的发现合并成结构化研究笔记。
要求：
1. 去除重复信息。
2. 合并相似观点。
3. 标注重要引用来源。
4. 明确哪些结论证据强，哪些只是推测。
"""

WRITER_PROMPT = """
你是一个专业研究报告撰写者。

原始问题：{question}

综合研究笔记：
{synthesized_notes}

请生成一份中文 Markdown 研究报告。
结构必须包含：
1. 标题
2. 摘要
3. 背景
4. 核心发现
5. 分析与讨论
6. 风险与局限
7. 结论
8. 参考来源

要求：
- 语言清晰，适合放入作品集。
- 所有关键事实尽量附带来源链接。
- 不要编造不存在的引用。
"""

CRITIC_PROMPT = """
你是一个严苛的研究报告评审员。

原始问题：{question}

报告：
{report}

请从以下维度评分：
1. 是否回答了问题。
2. 结构是否清晰。
3. 引用是否充分。
4. 是否存在明显空泛或幻觉内容。

请输出 JSON：
{{
  "score": 1到10的整数,
  "strengths": ["优点1"],
  "weaknesses": ["不足1"],
  "suggestions": ["建议1"]
}}
"""
```

---

## 8. 工具层代码骨架

### `src/deep_researcher/tools/search.py`

```python
from tavily import TavilyClient

from deep_researcher.config import get_settings


def search_web(query: str) -> list[dict]:
    settings = get_settings()
    client = TavilyClient(api_key=settings.tavily_api_key)

    response = client.search(
        query=query,
        max_results=settings.max_search_results,
        search_depth="advanced",
    )

    results = []
    for item in response.get("results", []):
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
            }
        )
    return results
```

### `src/deep_researcher/tools/web_reader.py`

```python
import httpx
from bs4 import BeautifulSoup

from deep_researcher.config import get_settings


def read_web_page(url: str) -> str:
    settings = get_settings()

    try:
        response = httpx.get(
            url,
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = " ".join(soup.get_text(" ").split())
    return text[: settings.max_web_chars]
```

### `src/deep_researcher/utils/citations.py`

```python
def format_sources(sources: list[dict]) -> str:
    lines = []
    for idx, source in enumerate(sources, start=1):
        title = source.get("title") or "Untitled"
        url = source.get("url") or ""
        snippet = source.get("snippet") or ""
        content = source.get("content") or ""
        lines.append(
            f"[{idx}] {title}\nURL: {url}\n摘要: {snippet}\n正文片段: {content[:1200]}"
        )
    return "\n\n".join(lines)
```

---

## 9. Agent 节点代码骨架

### `src/deep_researcher/agents/planner.py`

```python
import json

from deep_researcher.llm import get_llm
from deep_researcher.prompts import PLANNER_PROMPT
from deep_researcher.state import ResearchState


def planner_node(state: ResearchState) -> ResearchState:
    llm = get_llm(temperature=0.1)
    prompt = PLANNER_PROMPT.format(question=state["question"])
    response = llm.invoke(prompt)

    try:
        plan = json.loads(response.content)
    except json.JSONDecodeError:
        plan = [line.strip("- ") for line in response.content.splitlines() if line.strip()]

    plan = [item for item in plan if isinstance(item, str) and item.strip()]
    return {"plan": plan[:5], "iteration": state.get("iteration", 0)}
```

### `src/deep_researcher/agents/researcher.py`

```python
from deep_researcher.llm import get_llm
from deep_researcher.prompts import RESEARCHER_PROMPT
from deep_researcher.state import ResearchFinding, ResearchState
from deep_researcher.tools.search import search_web
from deep_researcher.tools.web_reader import read_web_page
from deep_researcher.utils.citations import format_sources


def research_one_sub_question(sub_question: str) -> ResearchFinding:
    search_results = search_web(sub_question)

    enriched_sources = []
    for item in search_results:
        content = read_web_page(item["url"])
        enriched_sources.append({**item, "content": content})

    llm = get_llm(temperature=0.2)
    prompt = RESEARCHER_PROMPT.format(
        sub_question=sub_question,
        sources=format_sources(enriched_sources),
    )
    response = llm.invoke(prompt)

    return {
        "sub_question": sub_question,
        "summary": response.content,
        "sources": enriched_sources,
    }


def researcher_node(state: ResearchState) -> ResearchState:
    findings = []
    for sub_question in state["plan"]:
        findings.append(research_one_sub_question(sub_question))
    return {"findings": findings}
```

MVP 先串行搜索即可。第二周可以改成并发：`asyncio.gather` 或 LangGraph map-reduce 风格。

### `src/deep_researcher/agents/synthesizer.py`

```python
from deep_researcher.llm import get_llm
from deep_researcher.prompts import SYNTHESIZER_PROMPT
from deep_researcher.state import ResearchState


def synthesizer_node(state: ResearchState) -> ResearchState:
    findings_text = "\n\n".join(
        f"## {finding['sub_question']}\n{finding['summary']}"
        for finding in state.get("findings", [])
    )

    llm = get_llm(temperature=0.2)
    prompt = SYNTHESIZER_PROMPT.format(
        question=state["question"],
        findings=findings_text,
    )
    response = llm.invoke(prompt)
    return {"synthesized_notes": response.content}
```

### `src/deep_researcher/agents/writer.py`

```python
from deep_researcher.llm import get_llm
from deep_researcher.prompts import WRITER_PROMPT
from deep_researcher.state import ResearchState


def writer_node(state: ResearchState) -> ResearchState:
    llm = get_llm(temperature=0.3)
    prompt = WRITER_PROMPT.format(
        question=state["question"],
        synthesized_notes=state["synthesized_notes"],
    )
    response = llm.invoke(prompt)
    return {"report": response.content}
```

### `src/deep_researcher/agents/critic.py`

```python
import json

from deep_researcher.llm import get_llm
from deep_researcher.prompts import CRITIC_PROMPT
from deep_researcher.state import ResearchState


def critic_node(state: ResearchState) -> ResearchState:
    llm = get_llm(temperature=0.1)
    prompt = CRITIC_PROMPT.format(
        question=state["question"],
        report=state["report"],
    )
    response = llm.invoke(prompt)

    try:
        critique = json.loads(response.content)
    except json.JSONDecodeError:
        critique = {
            "score": 7,
            "strengths": ["报告已生成"],
            "weaknesses": ["评审结果未能解析为 JSON"],
            "suggestions": [response.content],
        }

    return {
        "critique": critique,
        "iteration": state.get("iteration", 0) + 1,
    }
```

---

## 10. LangGraph 工作流骨架

### `src/deep_researcher/graph.py`

```python
from langgraph.graph import END, START, StateGraph

from deep_researcher.agents.critic import critic_node
from deep_researcher.agents.planner import planner_node
from deep_researcher.agents.researcher import researcher_node
from deep_researcher.agents.synthesizer import synthesizer_node
from deep_researcher.agents.writer import writer_node
from deep_researcher.config import get_settings
from deep_researcher.state import ResearchState


def should_rewrite(state: ResearchState) -> str:
    settings = get_settings()
    critique = state.get("critique", {})
    score = int(critique.get("score", 0) or 0)
    iteration = state.get("iteration", 0)

    if score < 7 and iteration < settings.max_iterations:
        return "rewrite"
    return "finish"


def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("writer", writer_node)
    builder.add_node("critic", critic_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "synthesizer")
    builder.add_edge("synthesizer", "writer")
    builder.add_edge("writer", "critic")

    builder.add_conditional_edges(
        "critic",
        should_rewrite,
        {
            "rewrite": "writer",
            "finish": END,
        },
    )

    return builder.compile()


def run_research(question: str) -> ResearchState:
    graph = build_graph()
    return graph.invoke({"question": question, "iteration": 0})
```

---

## 11. Streamlit Demo 骨架

### `app.py`

```python
import streamlit as st

from deep_researcher.graph import run_research


st.set_page_config(page_title="Agentic Deep Researcher", layout="wide")

st.title("🧠 Agentic Deep Researcher")
st.caption("基于 LangGraph 的多智能体深度研究助手")

question = st.text_area(
    "输入你的研究问题",
    value="AI Agent 在企业知识管理中的应用现状、挑战和趋势是什么？",
    height=100,
)

run = st.button("开始研究", type="primary")

if run:
    if not question.strip():
        st.warning("请输入研究问题")
        st.stop()

    with st.spinner("Agent 正在规划、搜索、阅读和写报告..."):
        result = run_research(question.strip())

    st.subheader("研究计划")
    for idx, item in enumerate(result.get("plan", []), start=1):
        st.write(f"{idx}. {item}")

    st.subheader("最终报告")
    st.markdown(result.get("report", ""))

    st.subheader("Critic 评审")
    st.json(result.get("critique", {}))

    with st.expander("中间研究发现"):
        st.json(result.get("findings", []))
```

本地运行：

```bash
PYTHONPATH=src streamlit run app.py
```

Windows Git Bash 下也可以用：

```bash
export PYTHONPATH=src
streamlit run app.py
```

---

## 12. 测试规划

### `tests/test_citations.py`

```python
from deep_researcher.utils.citations import format_sources


def test_format_sources_contains_title_and_url():
    sources = [
        {
            "title": "Test Title",
            "url": "https://example.com",
            "snippet": "short snippet",
            "content": "long content",
        }
    ]

    output = format_sources(sources)

    assert "Test Title" in output
    assert "https://example.com" in output
    assert "short snippet" in output
```

### `tests/test_state.py`

```python
from deep_researcher.state import ResearchState


def test_research_state_accepts_question():
    state: ResearchState = {"question": "What is AI Agent?"}
    assert state["question"] == "What is AI Agent?"
```

### `tests/test_graph_smoke.py`

```python
from deep_researcher.graph import build_graph


def test_build_graph():
    graph = build_graph()
    assert graph is not None
```

运行测试：

```bash
PYTHONPATH=src pytest -q
```

运行代码检查：

```bash
ruff check .
```

---

## 13. README 应包含的内容

### `README.md` 推荐结构

```md
# Agentic Deep Researcher

基于 LangGraph 的多智能体深度研究助手。

## Features

- Planner Agent 自动拆解研究问题
- Researcher Agent 调用 Tavily 搜索并读取网页
- Synthesizer Agent 综合多来源信息
- Writer Agent 生成带引用的 Markdown 报告
- Critic Agent 自动评审报告质量
- Streamlit 在线 Demo

## Architecture

放一张架构图：
User -> Planner -> Researcher -> Synthesizer -> Writer -> Critic

## Quick Start

1. 克隆项目
2. 创建虚拟环境
3. 安装依赖
4. 配置 `.env`
5. 启动 Streamlit

## Demo

放截图 / GIF / 在线链接。

## Evaluation

| Question | Tool Calls | Sources | Critic Score | Time |
|---|---:|---:|---:|---:|
| AI Agent 企业应用 | 15 | 10 | 8/10 | 65s |

## Resume Highlights

- 使用 LangGraph 设计多 Agent 工作流
- 实现搜索、网页读取、引用整理等工具调用
- 通过 Critic Agent 实现自我评审闭环
```

---

## 14. 第一天具体怎么动手

### Day 1 目标

当天不要追求完整 Agent 系统。目标只有三个：

1. 创建项目骨架。
2. 跑通一次 LLM 调用。
3. 跑通一个最小 LangGraph：`planner -> writer`。

### Step 1：创建项目目录

```bash
mkdir agentic-deep-researcher
cd agentic-deep-researcher
mkdir -p src/deep_researcher/agents src/deep_researcher/tools src/deep_researcher/utils tests examples
mkdir -p .hermes/plans

touch README.md requirements.txt .env.example .gitignore app.py
touch src/deep_researcher/__init__.py
touch src/deep_researcher/config.py src/deep_researcher/llm.py src/deep_researcher/prompts.py src/deep_researcher/state.py src/deep_researcher/graph.py
touch src/deep_researcher/agents/__init__.py src/deep_researcher/agents/planner.py src/deep_researcher/agents/writer.py
touch tests/test_graph_smoke.py
```

### Step 2：创建虚拟环境

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
python -m pip install --upgrade pip
```

如果是 macOS / Linux：

```bash
source .venv/bin/activate
```

### Step 3：安装最小依赖

先只装最小依赖：

```bash
pip install langgraph langchain langchain-openai python-dotenv pydantic pydantic-settings streamlit pytest ruff
```

冻结依赖：

```bash
pip freeze > requirements.txt
```

### Step 4：写 `.env.example`

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
TAVILY_API_KEY=your_tavily_key_here
MAX_SEARCH_RESULTS=5
MAX_WEB_CHARS=6000
MAX_ITERATIONS=1
```

复制一份真实配置：

```bash
cp .env.example .env
```

然后手动填入 API Key。

### Step 5：先写最小 `state.py`

```python
from typing import TypedDict


class ResearchState(TypedDict, total=False):
    question: str
    plan: list[str]
    report: str
```

### Step 6：先写最小 `llm.py`

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        temperature=temperature,
    )
```

### Step 7：写最小 Planner

```python
from deep_researcher.llm import get_llm
from deep_researcher.state import ResearchState


def planner_node(state: ResearchState) -> ResearchState:
    llm = get_llm(temperature=0.1)
    response = llm.invoke(
        f"请将这个研究问题拆成3个子问题，只输出每行一个子问题：{state['question']}"
    )
    plan = [line.strip("- 1234567890.、") for line in response.content.splitlines() if line.strip()]
    return {"plan": plan[:3]}
```

### Step 8：写最小 Writer

```python
from deep_researcher.llm import get_llm
from deep_researcher.state import ResearchState


def writer_node(state: ResearchState) -> ResearchState:
    llm = get_llm(temperature=0.3)
    plan_text = "\n".join(f"- {item}" for item in state.get("plan", []))
    response = llm.invoke(
        f"请基于下面研究提纲写一份简短中文报告：\n问题：{state['question']}\n提纲：\n{plan_text}"
    )
    return {"report": response.content}
```

### Step 9：写最小 Graph

```python
from langgraph.graph import END, START, StateGraph

from deep_researcher.agents.planner import planner_node
from deep_researcher.agents.writer import writer_node
from deep_researcher.state import ResearchState


def build_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("planner", planner_node)
    builder.add_node("writer", writer_node)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "writer")
    builder.add_edge("writer", END)
    return builder.compile()


def run_research(question: str) -> ResearchState:
    graph = build_graph()
    return graph.invoke({"question": question})
```

### Step 10：写一个命令行 smoke test

可以临时创建 `scripts/smoke.py`：

```python
from deep_researcher.graph import run_research


if __name__ == "__main__":
    result = run_research("AI Agent 对软件开发流程的影响是什么？")
    print("PLAN:")
    print(result.get("plan"))
    print("\nREPORT:")
    print(result.get("report"))
```

运行：

```bash
mkdir -p scripts
# 手动创建 scripts/smoke.py 后执行
PYTHONPATH=src python scripts/smoke.py
```

如果看到 plan 和 report，Day 1 就成功了。

### Step 11：写最小 Streamlit

```python
import streamlit as st
from deep_researcher.graph import run_research

st.title("Agentic Deep Researcher")
question = st.text_area("研究问题", "AI Agent 对软件开发流程的影响是什么？")

if st.button("生成报告"):
    with st.spinner("运行中..."):
        result = run_research(question)
    st.subheader("Plan")
    st.write(result.get("plan"))
    st.subheader("Report")
    st.markdown(result.get("report", ""))
```

运行：

```bash
PYTHONPATH=src streamlit run app.py
```

### Day 1 验收标准

- `streamlit run app.py` 可以打开页面。
- 输入问题后可以生成一个简短报告。
- 项目已经有清晰目录结构。
- README 写了项目目标和本地运行方式。
- 代码已提交一次。

建议提交：

```bash
git init
git add .
git commit -m "feat: bootstrap minimal langgraph researcher"
```

---

## 15. 1-2 周开发路线

### Day 1：最小可运行版本

- 搭项目骨架。
- 跑通 LLM。
- 跑通 `planner -> writer`。
- 跑通 Streamlit 页面。

### Day 2：引入 Tavily 搜索

- 增加 `tools/search.py`。
- 增加 `researcher_node`。
- 工作流变成 `planner -> researcher -> writer`。
- 报告里出现真实来源链接。

### Day 3：网页正文抽取

- 增加 `tools/web_reader.py`。
- 搜索结果 URL 进入正文读取。
- Researcher 总结时使用网页正文，而不是只用搜索摘要。

### Day 4：Synthesizer Agent

- 增加 `synthesizer_node`。
- 工作流变成 `planner -> researcher -> synthesizer -> writer`。
- 解决多个子问题研究结果重复、杂乱的问题。

### Day 5：Critic Agent

- 增加 `critic_node`。
- 输出评分、优点、不足、建议。
- 可选：低于 7 分时让 Writer 重写一次。

### Day 6：测试与健壮性

- 给 citation、graph、planner fallback 写测试。
- 给网页读取失败做容错。
- 给 JSON 解析失败做 fallback。

### Day 7：前端增强

- Streamlit 展示执行步骤。
- 展示引用来源。
- 展示 Critic 评分。
- 支持下载 Markdown 报告。

### Day 8-9：工程化

- 写 Dockerfile。
- 补 README。
- 加示例报告。
- 加架构图。

### Day 10-14：打磨为简历项目

- 录制 1 分钟 Demo 视频。
- 部署到 HuggingFace Spaces 或 Render。
- 跑 5 个测试问题，整理评估表。
- 写简历 bullet。

---

## 16. 简历 bullet 模板

```text
多智能体深度研究助手 | Python, LangGraph, Streamlit, Tavily
- 基于 LangGraph 设计 Planner/Researcher/Synthesizer/Writer/Critic 五节点 Agent 工作流，实现从问题拆解、联网搜索、网页读取到带引用报告生成的端到端自动化。
- 封装 Tavily Search 与网页正文抽取工具，使 Agent 能基于外部实时信息生成研究结论，减少单次 LLM 调用的幻觉风险。
- 引入 Critic Agent 对报告进行结构、引用充分性与事实可靠性评审，低分报告触发自动重写，形成自我反思闭环。
- 使用 Streamlit 构建可交互 Demo，并通过 pytest/ruff/Docker 完成基础工程化，支持一键本地运行与在线展示。
```

如果你想更强一点，可以加量化：

```text
- 在 5 类开放式研究问题上测试，平均每次调用 10+ 个外部来源，生成 1500-3000 字 Markdown 报告，Critic 平均评分 8/10。
```

---

## 17. 风险与解决方案

### 风险 1：API Key 成本或不可用

解决：

- 使用 OpenAI-compatible 接口，支持切换 DeepSeek、智谱、OpenRouter、硅基流动等。
- Day 1 先用便宜模型跑通链路。

### 风险 2：网页抓取失败

解决：

- 搜索摘要作为 fallback。
- 对 httpx 请求加 timeout。
- 抓取失败时不让整个流程崩掉。

### 风险 3：LLM 输出不是 JSON

解决：

- MVP 用 try/except fallback。
- 后续用 PydanticOutputParser 或 structured output。

### 风险 4：项目做得像普通 LLM App，不像 Agent

解决：

README 和 Demo 必须突出：

- 多节点工作流。
- 工具调用。
- 中间状态。
- Critic 反思。
- 引用来源。

---

## 18. 最终交付物清单

完成后你应该有：

- GitHub 仓库。
- README。
- 架构图。
- 本地运行说明。
- Streamlit Demo。
- 至少 2 份示例报告。
- 测试用例。
- Dockerfile。
- 简历 bullet。
- 1 分钟演示视频或 GIF。

---

## 19. 推荐优先级

如果时间只有 7 天，优先级如下：

1. LangGraph 跑通完整链路。
2. 搜索 + 引用。
3. Streamlit Demo。
4. README + 架构图。
5. Critic Agent。
6. 测试和 Docker。

如果时间有 14 天，再补：

1. 并发搜索。
2. structured output。
3. 报告下载。
4. 在线部署。
5. 评估表。

---

## 20. 下一步执行建议

从 Day 1 开始，不要先追求完美架构。你第一天的唯一任务是让这个流程跑起来：

```text
用户问题 -> Planner 生成提纲 -> Writer 生成简短报告 -> Streamlit 展示
```

第二天再加搜索，第三天再加网页读取。这样最稳，也最容易坚持到完成。
