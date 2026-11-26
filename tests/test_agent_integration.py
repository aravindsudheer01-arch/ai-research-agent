"""Real LangChain workflow against a simulated Groq-compatible HTTP server."""
import json
import httpx
from langchain_openai import ChatOpenAI
import main


def test_search_then_single_json_report(monkeypatch):
    requests = []
    def respond(request):
        payload = json.loads(request.content)
        requests.append(payload)
        assert payload.get('tool_choice') not in ('required', 'any')
        assert payload['model'] == 'openai/gpt-oss-20b'
        message = {'role': 'assistant', 'content': 'Robots help with automation.'}
        finish = 'stop'
        assert not payload.get('tools')
        assert payload['response_format'] == {'type': 'json_object'}
        message['content'] = json.dumps({'topic':'robotics', 'summary':'Robots help with automation.',
            'sources':['https://example.com/robots','https://fabricated.invalid'], 'tools_used':['fake']})
        return httpx.Response(200, json={'id':'chatcmpl-test', 'object':'chat.completion',
            'created':1, 'model':'openai/gpt-oss-20b', 'choices':[{'index':0,
            'finish_reason':finish, 'message':message}],
            'usage':{'prompt_tokens':10, 'completion_tokens':10, 'total_tokens':20}})
    client = httpx.Client(transport=httpx.MockTransport(respond))
    model = ChatOpenAI(model='openai/gpt-oss-20b', api_key='fake',
                       base_url='https://api.groq.com/openai/v1', http_client=client)
    monkeypatch.setattr(main, 'create_model', lambda: model)
    monkeypatch.setattr('tools.DDGS', lambda **kw: type('Search', (), {
        'text': lambda self, *a, **k: [{'title':'Robots','href':'https://example.com/robots','body':'Automation'}]})())
    result = main.run_research('robotics')
    assert result.sources == ['https://example.com/robots']
    assert result.tools_used == ['web_search']
    assert len(requests) == 1
