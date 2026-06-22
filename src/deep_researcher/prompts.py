PLANNER_PROMPT = """你是 Planner Agent。请把用户研究问题拆解为 {max_items} 个互补、可搜索的子问题。
要求：
- 只输出编号列表，不要输出解释。
- 子问题应覆盖背景、现状、关键争议、趋势或落地建议。

用户问题：{question}
"""

RESEARCH_SUMMARY_PROMPT = """你是 Researcher Agent。请基于搜索结果和网页正文，总结子问题的关键发现。
要求：
- 用中文输出 3-5 条要点。
- 每条要点尽量关联来源编号，例如 [1]。
- 不要编造来源中没有的信息。

子问题：{subquestion}
资料：
{evidence}
"""

SYNTHESIZER_PROMPT = """你是 Synthesizer Agent。请整合多个子问题的研究发现，去重并形成结构化洞察。
要求：
- 输出中文。
- 保留来源编号。
- 包含：核心结论、证据、风险、不确定性。

原始问题：{question}
研究发现：
{findings}
"""

WRITER_PROMPT = """你是 Writer Agent。请根据综合洞察生成一份带引用的 Markdown 深度研究报告。
要求：
- 中文输出。
- 使用清晰标题层级。
- 必须包含：摘要、背景、关键发现、风险与限制、行动建议、参考来源。
- 使用 [1] 这样的引用编号。

研究问题：{question}
综合洞察：
{synthesis}
引用来源：
{citations}
"""

CRITIC_PROMPT = """你是 Critic Agent。请评审报告质量，并只输出 JSON。
JSON schema：
{{
  "score": 1-10,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestions": ["..."]
}}

评估维度：结构完整性、引用充分性、事实稳健性、行动建议可用性。

报告：
{report}
"""
