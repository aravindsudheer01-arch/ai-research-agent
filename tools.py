"""Web research tool. No credentials are stored in this source file."""
import json
from ddgs import DDGS
from langchain.tools import tool


@tool
def web_search(query: str) -> str:
    """Search for relevant titles, URLs and short snippets about a research question."""
    # Search backends can fail transiently. Retry once, with bounded time/results.
    for attempt in range(2):
        try:
            matches = DDGS(timeout=10).text(query[:500], max_results=3)
            results = [
                {'title': str(item.get('title', ''))[:300],
                 'href': item['href'], 'body': str(item.get('body', ''))[:1200]}
                for item in matches
                if isinstance(item, dict) and isinstance(item.get('href'), str)
                and item['href'].startswith(('https://', 'http://'))
            ]
            if results:
                return json.dumps(results, ensure_ascii=False)
        except Exception:
            pass
    return json.dumps({'error': 'Search unavailable after two attempts; no evidence retrieved.'})
