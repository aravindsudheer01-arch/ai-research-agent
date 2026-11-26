from unittest.mock import Mock
import pytest
import main


def test_research_reconciles_evidence(monkeypatch):
    report = main.ResearchResponse(topic='test', summary='Answer',
        sources=['https://example.com', 'https://invented.invalid'], tools_used=['imaginary'])
    monkeypatch.setattr(main, 'web_search', Mock(invoke=Mock(return_value='[{"href":"https://example.com"}]')))
    model = Mock()
    model.with_structured_output.return_value.invoke.return_value = report
    monkeypatch.setattr(main, 'create_model', lambda: model)
    result = main.run_research('test')
    assert result.sources == ['https://example.com']
    assert result.tools_used == ['web_search']
    model.with_structured_output.return_value.invoke.assert_called_once()


@pytest.mark.parametrize('query', ['', ' ', 'x' * 501])
def test_invalid_query_never_calls_model(monkeypatch, query):
    build = Mock()
    monkeypatch.setattr(main, 'create_model', build)
    with pytest.raises(ValueError):
        main.run_research(query)
    build.assert_not_called()
