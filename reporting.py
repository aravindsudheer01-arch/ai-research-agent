"""Reconcile claimed sources and tool usage against actual tool outputs."""

import json


def reconcile_tool_evidence(messages: list, requested_sources: list[str]) -> dict[str, list[str]]:
    """Only retain cited URLs that appeared in a web_search tool response."""
    used = set()
    known_urls = set()
    for message in messages:
        if getattr(message, "type", None) != "tool":
            continue
        name = getattr(message, "name", "")
        if name:
            used.add(name)
        if name != "web_search":
            continue
        try:
            records = json.loads(message.content)
        except (ValueError, TypeError):
            continue
        if isinstance(records, list):
            for record in records:
                if isinstance(record, dict) and isinstance(record.get("href"), str):
                    known_urls.add(record["href"])

    verified = list(dict.fromkeys(url for url in requested_sources if url in known_urls))
    return {"tools_used": sorted(used), "sources": verified}
