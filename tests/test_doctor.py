from pathlib import Path

from scripts import doctor


def test_doctor_reports_pythonpath_and_env(monkeypatch, capsys):
    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("PYTHONPATH", "src")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.chdir(project_root)

    exit_code = doctor.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "PYTHONPATH includes src" in output
    assert "OPENAI_API_KEY not configured" in output
    assert "TAVILY_API_KEY not configured" in output
    assert "Running inside project .venv" in output or "Not running from project .venv" in output