"""Web research tool. No credentials are stored in this source file."""

import json

from ddgs import DDGS
from langchain.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for relevant titles, URLs and short snippets about a research question."""
    try:
        matches = DDGS().text(query, max_results=5)
        results = [
            {
                "title": item.get("title", ""),
                "href": item.get("href", ""),
                "body": item.get("body", ""),
            }
            for item in matches
            if item.get("href")
        ]
        return json.dumps(results, ensure_ascii=False)
    except Exception:
        # Surface a simple error without exposing network/library internals.
        return json.dumps({"error": "Search unavailable; retry or check your connection."})
