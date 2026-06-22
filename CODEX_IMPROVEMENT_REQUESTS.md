# Codex 修改任务清单：Multi-Agent Deep Researcher 工程质量改进

> 面向 Codex 的执行文档。请在 `D:\Multi-Agent Deep Researcher` 项目目录下完成以下修改。
>
> 当前项目已经具备基础五节点工作流：`Planner -> Researcher -> Synthesizer -> Writer -> Critic`，并且 `pytest -q` 已通过：`8 passed`。本轮目标不是继续堆功能，而是做一次工程质量收敛，让项目更适合作为简历作品集。

---

## 0. 当前验证结果

已验证：

```bash
source .venv/Scripts/activate
export PYTHONPATH=src
pytest -q
```

结果：

```text
8 passed in 1.20s
```

未通过：

```bash
source .venv/Scripts/activate
ruff check src tests app.py
```

当前 `ruff` 报错约 10 个，主要包括：

- import 顺序未格式化
- 未使用变量 `settings`
- 行长超过 100
- 类型注解可简化

---

## 1. P0：必须优先完成

### 1.1 修复 ruff，使 lint 完全通过

执行：

```bash
source .venv/Scripts/activate
ruff check src tests app.py
```

目标：

```text
All checks passed!
```

已知问题包括但不限于：

#### `app.py`

- import 顺序未格式化。
- 可直接运行：

```bash
ruff check src tests app.py --fix
```

但注意：自动修复后仍需人工检查。

#### `src/deep_researcher/agents/critic.py`

当前有未使用变量：

```python
settings: Settings = state.get("settings") or load_settings()
```

如果后续按本文件第 1.2 节把 `settings` 显式传给 `get_llm()`，则这个变量会被使用；否则删除它。

当前还有行长超过 100 的返回语句，需要拆行。

#### `src/deep_researcher/agents/synthesizer.py`

同样存在未使用 `settings` 和行长问题。

#### `src/deep_researcher/agents/writer.py`

同样存在未使用 `settings` 和行长问题。

另有 fallback report 的长中文字符串超过 100 字符，需要拆成多行拼接。

#### `src/deep_researcher/config.py`

当前：

```python
def model_copy(self, update: dict | None = None) -> "Settings":
```

在 Python 3.11 且启用 `from __future__ import annotations` 后，可改为：

```python
def model_copy(self, update: dict | None = None) -> Settings:
```

#### `tests/test_critic.py`

测试里的 JSON 字符串太长，需要拆成多行，或使用 `json.dumps()` 构造。

完成后必须运行：

```bash
ruff check src tests app.py
pytest -q
```

---

### 1.2 修复 Agent 没有使用 UI 传入 settings 的问题

当前 `run_research()` 会把 settings 放进 state：

```python
initial_state: ResearchState = {
    "question": question,
    "settings": config,
    "messages": ["Workflow started"],
}
```

但多个 Agent 调 LLM 时是这样：

```python
get_llm(temperature=0.1).invoke(...)
```

这会导致 Streamlit 侧边栏里修改的模型、base_url 等配置不一定生效，因为 `get_llm()` 会重新从环境变量加载默认配置。

请在所有 Agent 节点中显式传入 state 中的 settings：

```python
settings: Settings = state.get("settings") or load_settings()
response = get_llm(temperature=0.1, settings=settings).invoke(...)
```

需要检查并修改：

- `src/deep_researcher/agents/planner.py`
- `src/deep_researcher/agents/researcher.py`
- `src/deep_researcher/agents/synthesizer.py`
- `src/deep_researcher/agents/writer.py`
- `src/deep_researcher/agents/critic.py`

注意：修改后 `settings` 变量就不应该再被 ruff 识别为未使用。

验收测试建议：

- 原有测试继续通过。
- 新增一个 monkeypatch 测试，验证 Agent 调用 `get_llm(..., settings=settings)` 时传入的是 state 中的 settings。

---

### 1.3 初始化 Git 仓库

当前项目目录不是 git 仓库。

请在 `D:\Multi-Agent Deep Researcher` 下执行：

```bash
git init
git add .
git commit -m "feat: bootstrap multi-agent deep researcher"
```

注意：确保 `.gitignore` 已包含：

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.py[cod]
.streamlit/secrets.toml
```

不要把 `.env`、虚拟环境、缓存文件提交进去。

---

### 1.4 README 与实际文件保持一致

当前 README 的目录结构里写了：

```text
├── Dockerfile
```

但如果项目目录下没有 `Dockerfile`，需要二选一：

1. 补上 Dockerfile；推荐。
2. 或删除 README 中的 Dockerfile 项。

推荐补 Dockerfile，见第 2.4 节。

---

## 2. P1：建议本轮一起完成

### 2.1 增加命令行 smoke 脚本

新增：

```text
scripts/smoke.py
```

目标：无需打开 Streamlit，也可以快速验证工作流。

推荐内容：

```python
from __future__ import annotations

from deep_researcher.graph import run_research


if __name__ == "__main__":
    result = run_research("AI Agent 对软件开发流程的影响是什么？")

    print("PLAN:")
    for index, item in enumerate(result.get("plan", []), start=1):
        print(f"{index}. {item}")

    print("\nREPORT:")
    print(result.get("report", ""))

    print("\nCRITIC:")
    print(result.get("critic", {}))

    print("\nMESSAGES:")
    for message in result.get("messages", []):
        print(f"- {message}")
```

运行：

```bash
source .venv/Scripts/activate
export PYTHONPATH=src
python scripts/smoke.py
```

验收：

- 没有 API Key 时也不崩溃。
- 能输出 plan、report、critic、messages。

---

### 2.2 增加示例报告

新增：

```text
examples/sample_report.md
```

内容可以使用无 API Key fallback 的示例报告，也可以用真实 API 跑一份结果。

要求：

- Markdown 格式清晰。
- 包含标题、摘要、研究计划、关键发现、参考来源、Critic 评分。
- 如果无真实 Tavily 来源，应明确写：`示例报告未启用实时搜索，仅用于展示格式。`

README 中增加链接：

```md
## 示例输出

见 `examples/sample_report.md`。
```

---

### 2.3 补充无 API Key 的端到端测试

新增测试建议：

```text
tests/test_graph_no_api_key.py
```

目标：保证未配置 LLM 和 Tavily 时工作流仍能 fallback 跑通。

示例测试：

```python
from deep_researcher.config import Settings
from deep_researcher.graph import run_research


def test_run_research_without_api_keys_uses_fallbacks():
    settings = Settings(
        openai_api_key="",
        tavily_api_key="",
        max_subquestions=2,
        max_search_results=1,
        max_pages_per_query=0,
    )

    result = run_research("AI Agent 是什么？", settings=settings)

    assert result["question"] == "AI Agent 是什么？"
    assert result.get("plan")
    assert result.get("report")
    assert result.get("critic")
    assert result.get("messages")
```

如果当前 LangGraph 返回状态没有保留 `question`，可根据实际行为调整断言，但建议保留 `question`。

---

### 2.4 增加 Dockerfile

新增：

```text
Dockerfile
```

推荐内容：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

README 增加 Docker 运行方式：

```bash
docker build -t multi-agent-deep-researcher .
docker run --env-file .env -p 8501:8501 multi-agent-deep-researcher
```

---

## 3. P2：作品集增强项，可后续做

### 3.1 使用 LangGraph reducer 优化状态合并

当前状态里：

```python
messages: list[str]
findings: list[Finding]
citations: list[Citation]
```

各节点手动做：

```python
state.get("messages", []) + ["xxx"]
```

后续建议改成 LangGraph reducer：

```python
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class ResearchState(TypedDict, total=False):
    question: str
    plan: list[str]
    findings: Annotated[list[Finding], operator.add]
    citations: Annotated[list[Citation], operator.add]
    messages: Annotated[list[str], operator.add]
    synthesis: str
    report: str
    critic: CriticReview
    settings: Any
```

然后节点只返回增量：

```python
return {"messages": ["Planner completed"]}
```

好处：

- 更符合 LangGraph 范式。
- 更适合后续并行 fan-out。
- 简历上可以强调状态图和 reducer 管理。

---

### 3.2 Researcher 并发执行

当前 Researcher 是串行：

```python
for subquestion in state.get("plan", []):
    ...
```

后续可升级为：

- `asyncio.gather`
- LangGraph map-reduce
- LangGraph Send API fan-out

简历可写：

```text
使用 LangGraph fan-out/map-reduce 模式并行执行子问题研究，将多子问题检索和总结延迟从串行 N 次调用优化为并发执行。
```

本轮不强制做，避免引入复杂度。

---

### 3.3 structured output / Pydantic 解析

当前 Planner 和 Critic 主要依赖文本解析：

- numbered list parsing
- JSON object extraction

后续可升级为：

- Pydantic 模型
- LangChain structured output
- OpenAI-compatible JSON schema 输出

目标：减少 LLM 输出格式不稳定带来的 fallback。

---

## 4. 建议新增/调整的测试清单

在原有测试基础上，建议补充：

### 4.1 Tavily 无 Key 测试

```python
from deep_researcher.config import Settings
from deep_researcher.tools.search import TavilySearchClient


def test_tavily_search_without_api_key_returns_empty_list():
    client = TavilySearchClient(Settings(tavily_api_key=""))

    assert client.search("AI Agent") == []
```

### 4.2 WebReader 网络错误测试

使用 monkeypatch 模拟 `httpx.Client.get` 抛异常，验证返回空字符串。

目标：

```python
assert reader.read("https://bad.example") == ""
```

### 4.3 Critic fenced JSON 解析测试

确认工具函数能解析：

````md
```json
{"score": 8, "strengths": [], "weaknesses": [], "suggestions": []}
```
````

### 4.4 settings 传递测试

至少对一个 Agent 做测试：

- 构造自定义 Settings，例如 `openai_model="custom-test-model"`
- monkeypatch `get_llm`
- 验证传入的 `settings.resolved_model()` 是 `custom-test-model`

---

## 5. 修改后的验收命令

Codex 完成修改后，必须在 `D:\Multi-Agent Deep Researcher` 下运行：

```bash
source .venv/Scripts/activate
export PYTHONPATH=src
pytest -q
ruff check src tests app.py
python scripts/smoke.py
```

如果新增 Dockerfile，还建议验证：

```bash
docker build -t multi-agent-deep-researcher .
```

最终期望：

```text
pytest: 全部通过
ruff: All checks passed
smoke.py: 无 API Key 也能输出 plan/report/critic/messages
README: 与实际文件一致
Git: 已初始化并完成首次 commit
```

---

## 6. 不要做的事情

本轮不要做这些，避免 scope 失控：

- 不要重构成复杂插件系统。
- 不要引入数据库。
- 不要引入用户登录。
- 不要加入向量数据库 RAG。
- 不要大幅改 UI 风格。
- 不要把 `.env` 或 `.venv` 提交到 Git。
- 不要为了通过测试而删除核心功能。

---

## 7. 推荐提交信息

完成后提交：

```bash
git add .
git commit -m "chore: harden day-one researcher project quality"
```

如果是首次提交，则使用：

```bash
git commit -m "feat: bootstrap multi-agent deep researcher"
```

---

## 8. 高级工程师审查结论

当前项目已经具备很好的作品集基础，但下一步重点不是继续加功能，而是让项目达到可展示、可验证、可维护的状态。

本轮完成后，项目应该满足：

1. 本地一键测试通过。
2. lint 通过。
3. 无 API Key 也能展示 fallback Demo。
4. 有 README、示例报告、Smoke 脚本、Dockerfile。
5. GitHub 提交历史干净。
6. 代码能体现 Agent Native 架构，而不是简单 LLM 调用。
