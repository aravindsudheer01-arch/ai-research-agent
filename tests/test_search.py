import json
from unittest.mock import Mock
from tools import web_search


def test_transient_search_failure_recovers(monkeypatch):
    client = Mock()
    client.text.side_effect = [RuntimeError('temporary failure'), [
        {'href':'https://example.org','title':'Example','body':'a'*2000}]]
    monkeypatch.setattr('tools.DDGS', lambda **kw: client)
    result = json.loads(web_search.invoke({'query':'test'}))
    assert len(result[0]['body']) == 1200
    assert client.text.call_count == 2


def test_search_failure_is_bounded_and_private(monkeypatch):
    client = Mock()
    client.text.side_effect = RuntimeError('private internal information')
    monkeypatch.setattr('tools.DDGS', lambda **kw: client)
    result = web_search.invoke({'query':'test'})
    assert 'error' in json.loads(result)
    assert 'private' not in result
    assert client.text.call_count == 2
