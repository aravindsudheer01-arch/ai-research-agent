import json
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
import main
from langchain.agents.structured_output import ToolStrategy

def test_agent_uses_tool_strategy(monkeypatch):
    monkeypatch.setenv('GROQ_API_KEY', 'test')
    factory = Mock()
    monkeypatch.setattr(main, 'create_agent', factory)
    main.build_agent()
    assert isinstance(factory.call_args.kwargs['response_format'], ToolStrategy)

def test_research_reconciles_evidence(monkeypatch):
    report = main.ResearchResponse(topic='test', summary='Answer',
        sources=['https://example.com', 'https://invented.invalid'], tools_used=['imaginary'])
    agent = Mock()
    agent.invoke.return_value = {'structured_response': report, 'messages': [
        SimpleNamespace(type='tool', name='web_search', content=json.dumps([{'href':'https://example.com'}]))]}
    monkeypatch.setattr(main, 'build_agent', lambda: agent)
    result = main.run_research('test')
    assert result.sources == ['https://example.com']
    assert result.tools_used == ['web_search']
    assert agent.invoke.call_args.kwargs['config']['recursion_limit'] == 6

@pytest.mark.parametrize('query', ['', ' ', 'x' * 501])
def test_invalid_query_never_calls_model(monkeypatch, query):
    build = Mock()
    monkeypatch.setattr(main, 'build_agent', build)
    with pytest.raises(ValueError):
        main.run_research(query)
    build.assert_not_called()
