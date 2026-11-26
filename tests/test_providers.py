import pytest
from providers import ModelSettings, create_model

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ('LLM_PROVIDER', 'LLM_MODEL', 'LLM_BASE_URL', 'LLM_API_KEY', 'GROQ_API_KEY', 'OPENAI_API_KEY', 'OPENAI_MODEL'):
        monkeypatch.delenv(key, raising=False)

def test_groq_default_without_openai(monkeypatch):
    monkeypatch.setenv('GROQ_API_KEY', 'test-secret')
    settings = ModelSettings.from_env()
    model = create_model(settings)
    assert settings.provider == 'groq'
    assert model.model_name == 'openai/gpt-oss-20b'
    assert str(model.openai_api_base) == 'https://api.groq.com/openai/v1'
    assert 'test-secret' not in repr(settings)

def test_missing_key():
    with pytest.raises(ValueError, match='GROQ_API_KEY'):
        ModelSettings.from_env()

def test_openai_switch(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    monkeypatch.setenv('OPENAI_API_KEY', 'test')
    assert ModelSettings.from_env().model == 'gpt-4o-mini'

def test_compatible_requires_explicit_configuration(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER', 'compatible')
    monkeypatch.setenv('LLM_API_KEY', 'test')
    with pytest.raises(ValueError, match='LLM_MODEL'):
        ModelSettings.from_env()
    monkeypatch.setenv('LLM_MODEL', 'custom')
    monkeypatch.setenv('LLM_BASE_URL', 'https://example.com/v1')
    assert ModelSettings.from_env().model == 'custom'
