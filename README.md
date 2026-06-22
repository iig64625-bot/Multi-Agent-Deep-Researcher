# Multi-Agent Deep Researcher

基于 **Python + LangGraph + Streamlit + Tavily Search + OpenAI-compatible LLM API** 的多智能体深度研究助手。输入一个研究问题后，系统会自动规划子问题、联网搜索、读取网页正文、综合发现、生成带引用的 Markdown 报告，并由 Critic Agent 做质量评审。

## 架构

```text
User Question
    ↓
Planner Agent        拆解 3-5 个可搜索子问题
    ↓
Researcher Agent     Tavily 搜索 + Web Reader 正文抽取
    ↓
Synthesizer Agent    去重、整合、保留来源编号
    ↓
Writer Agent         生成 Markdown 深度研究报告
    ↓
Critic Agent         给出评分、优点、不足、改进建议
```

## 功能

- Planner：将研究问题拆解成多个子问题。
- Researcher：对每个子问题调用 Tavily Search，并抓取搜索结果网页正文。
- Synthesizer：整合多个子问题的发现，减少重复信息。
- Writer：输出结构化 Markdown 报告，包含引用编号。
- Critic：以 JSON 返回评分、优点、不足和建议。
- Streamlit：展示报告、来源、执行过程和评审结果，并支持下载 Markdown。

## 快速开始

```powershell
cd "D:\Multi-Agent Deep Researcher"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`：

```env
OPENAI_API_KEY=your_openai_compatible_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key
```

启动：

```powershell
$env:PYTHONPATH="src"
streamlit run app.py
```

## 测试

```powershell
$env:PYTHONPATH="src"
pytest -q
ruff check .
```

## 无 API Key 时的行为

- 未配置 `OPENAI_API_KEY`：各 Agent 会使用 fallback 输出，保证工作流可跑通。
- 未配置 `TAVILY_API_KEY`：Researcher 不会联网搜索，会提示缺少实时外部资料。

## 目录结构

```text
.
├── app.py
├── src/deep_researcher/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── synthesizer.py
│   │   ├── writer.py
│   │   └── critic.py
│   ├── tools/
│   │   ├── search.py
│   │   └── web_reader.py
│   ├── config.py
│   ├── graph.py
│   ├── llm.py
│   ├── prompts.py
│   └── state.py
├── tests/
├── examples/
├── Dockerfile
├── requirements.txt
└── PROJECT_BLUEPRINT.md
```

## 简历描述

多智能体深度研究助手 | Python, LangGraph, Streamlit, Tavily
- 基于 LangGraph 设计 Planner/Researcher/Synthesizer/Writer/Critic 五节点 Agent 工作流，实现从问题拆解、联网搜索、网页读取到带引用报告生成的端到端自动化。
- 封装 Tavily Search 与网页正文抽取工具，使 Agent 能基于外部实时信息生成研究结论，降低单次 LLM 调用的幻觉风险。
- 引入 Critic Agent 对报告结构、引用充分性与事实稳健性评分，并通过 Streamlit 展示报告、来源、执行过程和评审结果。
