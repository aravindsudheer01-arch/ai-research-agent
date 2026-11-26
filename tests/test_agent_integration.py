"""Exercise the real LangChain agent with a simulated OpenAI-compatible server."""
import json
import httpx
from langchain_openai import ChatOpenAI
import main


def test_search_then_structured_report(monkeypatch):
    requests = []
    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        assert 'response_format' not in payload  # no unsupported native schema + tools
        assert payload['model'] == 'openai/gpt-oss-20b'
        if len(requests) == 1:
            name, args = 'web_search', {'query': 'robotics'}
        else:
            name, args = 'ResearchResponse', {'topic': 'robotics', 'summary': 'Robots help with automation.',
                'sources': ['https://example.com/robots', 'https://fabricated.invalid'], 'tools_used': ['fake']}
        return httpx.Response(200, json={'id': 'chatcmpl-test', 'object': 'chat.completion',
            'created': 1, 'model': 'openai/gpt-oss-20b', 'choices': [{'index': 0,
            'finish_reason': 'tool_calls', 'message': {'role': 'assistant', 'content': None,
            'tool_calls': [{'id': f'call_{len(requests)}', 'type': 'function',
                            'function': {'name': name, 'arguments': json.dumps(args)}}]}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 10, 'total_tokens': 20}})
    client = httpx.Client(transport=httpx.MockTransport(respond))
    model = ChatOpenAI(model='openai/gpt-oss-20b', api_key='fake',
                       base_url='https://api.groq.com/openai/v1', http_client=client)
    monkeypatch.setattr(main, 'create_model', lambda: model)
    monkeypatch.setattr('tools.DDGS', lambda **kw: type('Search', (), {
        'text': lambda self, *a, **k: [{'title': 'Robots', 'href': 'https://example.com/robots', 'body': 'Automation'}]})())
    result = main.run_research('robotics')
    assert result.sources == ['https://example.com/robots']
    assert result.tools_used == ['web_search']
    assert len(requests) == 2
    assert any(m['role'] == 'tool' for m in requests[1]['messages'])
