from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


REQUIRED_MODULES = {
    "pytest": "pytest",
    "ruff": "ruff",
    "streamlit": "streamlit",
    "python-dotenv": "dotenv",
    "langgraph": "langgraph",
}


def status(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def is_inside_project_venv(project_root: Path) -> bool:
    executable = Path(sys.executable).resolve()
    venv_dir = (project_root / ".venv").resolve()
    return venv_dir in executable.parents


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    executable = Path(sys.executable).resolve()
    exit_code = 0

    status("OK", f"Python executable: {executable}")
    version = sys.version_info
    if version >= (3, 11):
        status("OK", f"Python version: {version.major}.{version.minor}.{version.micro}")
    else:
        status("FAIL", f"Python version: {version.major}.{version.minor}.{version.micro}; need 3.11+")
        exit_code = 1

    if is_inside_project_venv(project_root):
        status("OK", "Running inside project .venv")
    else:
        status("WARN", "Not running from project .venv")
        status("INFO", r"Use .\.venv\Scripts\python.exe scripts\doctor.py")
        if str(executable).lower().startswith(r"d:\python"):
            status("WARN", r"Detected D:\python system Python; activate .venv or use .venv python.exe")

    for label, module_name in REQUIRED_MODULES.items():
        if module_available(module_name):
            status("OK", f"{label} importable")
        else:
            status("FAIL", f"{label} not importable; run python -m pip install -r requirements.txt")
            exit_code = 1

    pythonpath = os.getenv("PYTHONPATH", "")
    pythonpath_parts = [part.strip() for part in pythonpath.split(os.pathsep) if part.strip()]
    if "src" in pythonpath_parts or str(project_root / "src") in pythonpath_parts:
        status("OK", "PYTHONPATH includes src")
    else:
        status("WARN", 'PYTHONPATH does not include src; run $env:PYTHONPATH="src"')

    env_path = project_root / ".env"
    if env_path.exists():
        status("OK", ".env exists")
    else:
        status("WARN", ".env not found; copy .env.example to .env for live API runs")

    if os.getenv("OPENAI_API_KEY"):
        status("OK", "OPENAI_API_KEY configured")
    else:
        status("WARN", "OPENAI_API_KEY not configured; app will use fallback mode")

    if os.getenv("TAVILY_API_KEY"):
        status("OK", "TAVILY_API_KEY configured")
    else:
        status("WARN", "TAVILY_API_KEY not configured; researcher will skip live search")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())