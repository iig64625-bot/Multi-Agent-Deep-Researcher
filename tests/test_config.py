from deep_researcher import config


def test_build_settings_prefers_environment_over_streamlit_secrets(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_MODEL", "env-model")

    settings = config._build_settings_from_sources(
        {
            "OPENAI_API_KEY": "secret-key",
            "OPENAI_MODEL": "secret-model",
            "TAVILY_API_KEY": "secret-tavily",
        }
    )

    assert settings.openai_api_key == "env-key"
    assert settings.openai_model == "env-model"
    assert settings.tavily_api_key == "secret-tavily"


def test_build_settings_uses_streamlit_secrets_when_env_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    settings = config._build_settings_from_sources(
        {
            "OPENAI_API_KEY": "secret-key",
            "OPENAI_MODEL": "secret-model",
            "TAVILY_API_KEY": "secret-tavily",
        }
    )

    assert settings.openai_api_key == "secret-key"
    assert settings.openai_model == "secret-model"
    assert settings.tavily_api_key == "secret-tavily"
