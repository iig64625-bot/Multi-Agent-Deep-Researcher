# Multi-Agent Deep Researcher

基于 **Python + LangGraph + Streamlit + Tavily Search + OpenAI-compatible LLM API** 的多智能体深度研究助手。输入一个研究问题后，系统会自动规划子问题、联网搜索、读取网页正文、综合发现、生成带引用的 Markdown 报告，并由 Critic Agent 做质量评审。

## 架构

```text
User Question
    ↓
Planner Agent        拆解 3-5 个可搜索子问题
    ↓
Researcher Agent     Tavily 搜索 + WebReader 正文抽取
    ↓
Synthesizer Agent    去重、整合、保留来源编号
    ↓
Writer Agent         生成 Markdown 深度研究报告
    ↓
Critic Agent         给出评分、优点、不足、改进建议
```

## 技术亮点

- **LangGraph 工作流编排**：用状态图表达 Agent 协作流程，节点职责清晰，便于测试、调试和后续扩展条件边。
- **多 Agent 分工**：Planner 负责拆题，Researcher 负责搜索和网页读取，Synthesizer 负责去重综合，Writer 负责报告生成，Critic 负责质量评审。
- **工具调用能力**：Tavily Search 提供实时搜索结果，WebReader 抽取网页正文，Researcher 将工具结果转为可引用证据。
- **稳定 fallback**：无 `OPENAI_API_KEY` 或 `TAVILY_API_KEY` 时仍可生成计划、报告和 Critic 结果，保证 Demo 与 CI 不崩溃。
- **轻量质量门禁**：Critic Agent 输出评分、优点、不足和建议，用于发现结构、引用和事实稳健性问题。

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

启动 Streamlit：

```powershell
$env:PYTHONPATH="src"
streamlit run app.py
```

## Smoke 验证

```powershell
$env:PYTHONPATH="src"
python scripts/smoke.py
```

`smoke.py` 无 API Key 也能跑通 fallback 工作流，可快速验证 `PLAN / REPORT_HEAD / CRITIC / MESSAGES` 是否正常输出。

## 测试与 Lint

```powershell
$env:PYTHONPATH="src"
pytest -q
ruff check src tests app.py
```

## Docker

```powershell
docker build -t multi-agent-deep-researcher .
docker run --env-file .env -p 8501:8501 multi-agent-deep-researcher
```

## 示例输出

见 `examples/sample_report.md`。该文件是 fallback demo 模式下的完整示例报告结构；配置真实 API Key 后可生成带 URL 引用的真实研究报告。

## Demo

运行 `streamlit run app.py` 后，可在本地浏览器体验研究工作流。建议在正式投递简历前补充 Streamlit 截图到 `docs/assets/demo.png`。当前仓库只保留 `docs/assets/.gitkeep`，不伪造真实运行截图。

## 无 API Key 时的行为

- 未配置 `OPENAI_API_KEY`：各 Agent 使用 fallback 输出，仍能展示计划、报告和 Critic 结果。
- 未配置 `TAVILY_API_KEY`：Researcher 不联网搜索，会提示缺少实时外部资料。
- Tavily 网络异常：搜索工具返回空列表，不会导致整个 workflow 崩溃。
- `MAX_PAGES_PER_QUERY=0`：Researcher 保留搜索摘要来源，但不会调用 WebReader 读取网页正文。

## 作品集评估表示例

以下为示例数据，展示如何量化 Demo 结果；真实 API 运行后可替换为真实数据。

| Question | Subquestions | Sources | Critic Score | Mode |
|---|---:|---:|---:|---|
| AI Agent 工程化趋势 | 2 | 0 | 6/10 | fallback demo |

## Roadmap

- 实现 `critic score < 7 -> writer rewrite -> critic recheck` 闭环，并通过最大重写次数避免死循环。
- 将 `messages/findings/citations` 改为 `Annotated[..., operator.add]` reducer，更贴近 LangGraph 状态合并范式。
- 使用并发或 LangGraph fan-out/map-reduce 处理多个子问题，降低 Researcher 串行检索延迟。
- 使用 Pydantic / structured output 替代脆弱的文本解析，提高 Planner 和 Critic 输出稳定性。
- 增加 tracing 或运行日志，展示每个 Agent 的耗时和工具调用次数。

## 目录结构

```text
.
├── app.py
├── scripts/smoke.py
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
├── examples/sample_report.md
├── docs/assets/.gitkeep
├── Dockerfile
├── requirements.txt
└── PROJECT_BLUEPRINT.md
```

## 简历描述

多智能体深度研究助手 | Python, LangGraph, Streamlit, Tavily
- 基于 LangGraph 设计 Planner/Researcher/Synthesizer/Writer/Critic 五节点 Agent 工作流，实现从问题拆解、联网搜索、网页读取到带引用报告生成的端到端自动化。
- 封装 Tavily Search 与网页正文抽取工具，使 Agent 能基于外部实时信息生成研究结论，降低单次 LLM 调用的幻觉风险。
- 引入 Critic Agent 对报告结构、引用充分性与事实稳健性评分，并通过 Streamlit 展示报告、来源、执行过程和评审结果。