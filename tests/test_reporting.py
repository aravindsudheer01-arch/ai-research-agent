import json
from types import SimpleNamespace

from reporting import reconcile_tool_evidence


def test_only_observed_sources_and_tools_are_reported():
    messages = [
        SimpleNamespace(
            type="tool", name="web_search",
            content=json.dumps([{"href": "https://example.org/article", "title": "Example"}]),
        ),
        SimpleNamespace(type="ai", name="", content="ignored"),
    ]
    result = reconcile_tool_evidence(
        messages, ["https://fake.example", "https://example.org/article", "https://example.org/article"]
    )
    assert result == {"tools_used": ["web_search"], "sources": ["https://example.org/article"]}


def test_malformed_tool_response_does_not_crash():
    messages = [SimpleNamespace(type="tool", name="web_search", content="Search unavailable")]
    assert reconcile_tool_evidence(messages, ["https://made-up.example"]) == {
        "tools_used": ["web_search"], "sources": []
    }
