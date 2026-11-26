from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from demo_limits import reserve_request
from streamlit.testing.v1 import AppTest

def test_shared_budget_and_expiry(tmp_path):
    path = tmp_path / 'usage.sqlite3'
    for i in range(20):
        assert reserve_request(path, now=1000 + i*61)
    assert not reserve_request(path, now=3000)
    assert reserve_request(path, now=90000)

def test_atomic_reservation(tmp_path):
    path = tmp_path / 'usage.sqlite3'
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: reserve_request(path, now=1000), range(4)))
    assert sum(results) == 1

def test_demo_loads_without_credentials(monkeypatch):
    monkeypatch.delenv('GROQ_API_KEY', raising=False)
    monkeypatch.setenv('LLM_PROVIDER', 'groq')
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py', default_timeout=10).run()
    assert not app.exception
    app.text_area[0].set_value('Explain warehouse robots')
    app.button[0].click().run()
    assert not app.exception
    assert 'not configured' in app.warning[0].value

def test_demo_success_and_download(monkeypatch):
    from main import ResearchResponse
    monkeypatch.setenv('GROQ_API_KEY', 'fake')
    monkeypatch.setattr('demo_limits.reserve_request', lambda: True)
    monkeypatch.setattr('main.run_research', lambda q: ResearchResponse(topic=q,
        summary='Test summary', sources=['https://example.org'], tools_used=['web_search']))
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py', default_timeout=10).run()
    app.text_area[0].set_value('Robots')
    app.button[0].click().run()
    assert not app.exception
    assert app.text[0].value == 'Test summary'
    assert len(app.get('download_button')) == 1
