# Multi-Agent Deep Researcher

## 项目亮点

- 使用 `LangGraph` 表达有状态、多节点、可扩展的 Agent 工作流，而不是把所有逻辑塞进单次链式调用。
- 采用 `Planner / Researcher / Synthesizer / Writer / Critic` 五节点分工，体现 Agent Native 架构。
- Researcher 同时使用 `Tavily Search` 和 `WebReader`，将搜索结果与网页正文转化为带来源的证据。
- 无 `OPENAI_API_KEY` 或 `TAVILY_API_KEY` 时仍能 fallback，保证 Demo、测试和 CI 不崩。
- Critic 当前作为轻量质量门禁；已支持低分触发一次 Writer 重写，后续可扩展更多自我修正策略。

## 架构设计

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
    ↓
score < 7 and rewrite_count < max_rewrites
    ↘ Writer Rewrite → Critic Recheck
```

## Agent 工作流

- `Planner`：把研究问题拆成可搜索、互补的子问题。
- `Researcher`：调用 Tavily 搜索并按配置读取网页正文；`MAX_PAGES_PER_QUERY=0` 时不会读取网页。
- `Synthesizer`：整合多个子问题发现，形成更适合成文的综合洞察。
- `Writer`：生成 Markdown 报告；若 Critic 分数过低，会结合评审意见改写一次。
- `Critic`：以 JSON 给出分数、优点、不足和建议，作为质量门禁。

## Demo

如果已真实运行并截屏，请保存到 `docs/assets/demo.png`，然后在此处展示：

```md
![Streamlit Demo](docs/assets/demo.png)
```

当前仓库仅保留 `docs/assets/.gitkeep`，不伪造运行截图。你可以先本地运行：

```powershell
$env:PYTHONPATH="src"
python -m streamlit run app.py
```

## GitHub + Streamlit Community Cloud

这是最推荐的在线 Demo 方案，因为这个项目是 Streamlit 应用，不适合直接用 GitHub Pages 托管。

1. 把当前仓库推到 GitHub。
2. 打开 Streamlit Community Cloud，新建 app。
3. 选择你的 GitHub 仓库、分支和入口文件 `app.py`。
4. 在 Streamlit Cloud 的 `Secrets` 中填写：

```toml
OPENAI_API_KEY = "your_openai_compatible_api_key"
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o-mini"
TAVILY_API_KEY = "your_tavily_api_key"
MAX_SUBQUESTIONS = "4"
MAX_SEARCH_RESULTS = "5"
MAX_PAGES_PER_QUERY = "3"
MAX_REWRITES = "1"
REQUEST_TIMEOUT_SECONDS = "15"
```

5. 点击 `Deploy`，等待应用构建完成。

说明：

- 应用现在同时支持本地 `.env` 和 Streamlit Cloud `Secrets`。
- 如果未配置 API Key，在线 Demo 仍可 fallback 运行，但不会做真实联网研究。
- `requirements.txt` 已包含 Streamlit Cloud 部署所需依赖。

## 快速开始

请不要直接运行裸命令，例如：

```powershell
pytest -q
ruff check src tests app.py
streamlit run app.py
```

推荐完整流程如下：

```powershell
cd "D:\Multi-Agent Deep Researcher"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH="src"
python scripts/doctor.py
python -m pytest -q
python -m ruff check src tests app.py
python scripts/smoke.py
python -m streamlit run app.py
```

## 完整使用方法 Windows PowerShell

如果激活环境后仍然误用系统 Python，可强制指定项目虚拟环境：

```powershell
cd "D:\Multi-Agent Deep Researcher"
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH="src"
.\.venv\Scripts\python.exe scripts\doctor.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests app.py
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## 配置说明

`.env.example` 提供以下主要配置：

```env
OPENAI_API_KEY=your_openai_compatible_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
TAVILY_API_KEY=your_tavily_api_key
MAX_SUBQUESTIONS=4
MAX_SEARCH_RESULTS=5
MAX_PAGES_PER_QUERY=3
MAX_REWRITES=1
REQUEST_TIMEOUT_SECONDS=15
```

说明：

- 未配置 `OPENAI_API_KEY`：各 Agent 进入 fallback，仍会输出计划、报告、Critic 和消息日志。
- 未配置 `TAVILY_API_KEY`：Researcher 不联网搜索，只展示 fallback 结果。
- `MAX_PAGES_PER_QUERY=0`：保留搜索摘要来源，但不读取网页正文。
- `MAX_REWRITES=1`：Critic 低分时最多触发一次 Writer 改写。
- Streamlit Community Cloud 可直接在 `Secrets` 中使用同名键，无需上传 `.env`。

## 质量验证

统一使用以下命令风格：

```powershell
$env:PYTHONPATH="src"
python scripts/doctor.py
python scripts/smoke.py
python -m pytest -q
python -m ruff check src tests app.py
```

`doctor.py` 会检查：

- 当前 Python 路径与版本
- 是否运行在项目 `.venv`
- `pytest`、`ruff`、`streamlit`、`dotenv`、`langgraph` 是否可导入
- `PYTHONPATH` 是否包含 `src`
- `.env` 是否存在
- 是否配置了 `OPENAI_API_KEY` / `TAVILY_API_KEY`（不会打印密钥值）

## 示例输出

- fallback 示例报告：`examples/sample_report.md`
- 真实联网报告占位：`examples/sample_report_real.md`

作品集评估表示例：

| Question | Mode | Subquestions | Sources | Critic Score | Notes |
|---|---|---:|---:|---:|---|
| AI Agent 工程化趋势 | fallback | 2 | 0 | 6/10 | no API key |
| 2026 年 AI Agent 工程化趋势 | live search | 4 | 10+ | TBD | after real run |

## 故障排查

### `D:\python\python.exe: No module named pytest`

通常是没有激活 `.venv`，或者当前命令使用了系统 Python。请改用：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### `D:\python\python.exe: No module named ruff`

根因通常与上面相同：没有使用项目 `.venv`。请先安装依赖，再使用：

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests app.py
```

### `ModuleNotFoundError: No module named 'dotenv'`

通常是依赖未安装，或当前 Python 不是项目 `.venv`。运行：

```powershell
python -m pip install -r requirements.txt
```

### `streamlit : 无法将“streamlit”项识别为 cmdlet`

不要直接运行裸命令 `streamlit run app.py`。请改用：

```powershell
python -m streamlit run app.py
```

### `ImportError: cannot import name 'Literal' from 'typing'`

通常说明你使用 Python 3.7 或更老版本创建了环境。请删除旧环境，并使用 Python 3.11 重建：

```powershell
py -3.11 -m venv .venv
```

## Roadmap

- 扩展 Critic 低分重写闭环，支持多轮改写和更细粒度条件边。
- 将 Planner / Critic 升级为 structured output，减少手写解析脆弱性。
- 将 `messages/findings/citations` 改为 `Annotated[..., operator.add]` reducer。
- 使用 LangGraph fan-out / map-reduce 并发处理多个子问题。
- 增加 trace summary，在 Streamlit 中展示各节点耗时、搜索次数、网页读取次数和引用数量。
