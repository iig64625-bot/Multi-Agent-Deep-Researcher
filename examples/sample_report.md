# 示例报告：AI Agent 工程化趋势

## 运行信息

| Item | Value |
|---|---|
| Model | OpenAI-compatible API，示例未实际调用远程模型 |
| Tavily Search | 未启用 |
| Subquestions | 2 |
| Sources | 0 |
| Critic Score | 6/10 |
| Mode | fallback demo |

本示例未启用实时 Tavily 搜索，仅用于展示报告结构。真实运行时将生成带 URL 的外部引用。

## 摘要

AI Agent 工程化的核心不只是调用一次 LLM，而是把任务拆解、工具调用、状态流转、质量评审和用户可见结果组织成可维护的系统。Multi-Agent Deep Researcher 使用 LangGraph 将研究流程拆为 Planner、Researcher、Synthesizer、Writer、Critic 五个节点，即使在无 API Key 的 fallback demo 模式下，也能展示完整的端到端工作流。

## 研究计划

1. AI Agent 工程化的关键技术趋势是什么？
2. AI Agent 工程化落地时有哪些风险、限制与行动建议？

## 关键发现

### 1. 工作流编排是 Agent 工程化的核心

LangGraph 将研究任务表达为有状态图，每个节点只负责一个清晰职责：Planner 拆题，Researcher 搜索与读取资料，Synthesizer 综合，Writer 写报告，Critic 评审。这种结构比单次 LLM 调用更容易测试、调试和扩展。

### 2. 工具调用降低信息陈旧和幻觉风险

Researcher 通过 Tavily Search 获取实时搜索结果，并使用 WebReader 抽取网页正文。真实运行时，报告中的结论会尽量附带来源编号，例如 `[1]`，帮助用户追溯证据。

### 3. fallback 机制提升 Demo 稳定性

当未配置 `OPENAI_API_KEY` 或 `TAVILY_API_KEY` 时，系统不会直接崩溃，而是返回可解释的降级结果。这让项目在面试演示、CI 或无外网环境中仍能验证工作流结构。

## 风险与限制

- 本示例未启用 Tavily，因此没有真实 URL 引用。
- fallback 报告只适合展示结构，不应当作为事实研究结论。
- Planner 和 Critic 目前仍使用文本解析，未来可升级为 structured output。
- Researcher 当前串行处理子问题，未来可用 LangGraph fan-out 或 map-reduce 并发优化。

## 行动建议

1. 在正式演示前配置 `.env` 中的 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL` 和 `TAVILY_API_KEY`。
2. 使用 `python scripts/smoke.py` 快速验证 fallback 工作流。
3. 使用 `pytest -q` 和 `ruff check src tests app.py` 保证工程质量。
4. 真实运行 2-3 个问题后，把高质量输出补充到 `examples/` 目录。
5. 后续实现 `critic score < 7 -> writer rewrite -> critic recheck` 闭环。

## 参考来源

本示例没有实时外部来源。真实运行时，该部分会列出 Tavily Search 与 WebReader 收集到的 URL 来源。

## Critic 评审摘要

- Score：6/10
- Strengths：结构完整，展示了多 Agent 工作流和 fallback 行为。
- Weaknesses：缺少真实外部引用，事实密度有限。
- Suggestions：配置真实 API Key 后重新运行，并补充来源 URL 与更细粒度证据。