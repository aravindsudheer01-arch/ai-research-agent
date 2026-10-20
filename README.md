# AI Research Assistant — LangChain and OpenAI

A command-line research agent built in **Python**. It performs web searches, uses an OpenAI model to summarise retrieved results, validates the output against a **Pydantic schema**, and saves a timestamped text report.

This is a portfolio demonstration, **not** an academic research engine or a guarantee that web-search results are correct.

## What this project does

1. Accepts a question from the command line.
2. Runs a LangChain tool-calling agent with a web-search tool powered by **DDGS** (a successor to `duckduckgo-search`).
3. Requests a structured response with `topic`, `summary`, `sources`, and `tools_used`.
4. Checks listed source URLs against links actually returned by the search tool; records observed tool usage, rather than trusting the model's claim.
5. Appends the report and a UTC timestamp to `outputs/research_output.txt`.

The agent is set up to use `gpt-4o-mini` by default, or a model provided through `OPENAI_MODEL`.

## Project structure

```text
ai-research-agent/
├── main.py               # CLI and structured agent
├── tools.py              # DDGS web search tool
├── reporting.py          # Checks reported sources and tool usage
├── storage.py            # Timestamped output saving
├── requirements.txt
├── .env.example          # Safe configuration template
├── .gitignore
└── tests/
    ├── test_reporting.py
    └── test_storage.py
```

## Quick start

Requires Python 3.10+ and an **OpenAI API key** with API billing/quota available. A ChatGPT subscription alone does not supply API usage.

```bash
# Create a virtual environment (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Make a local, untracked config file
cp .env.example .env
# Open .env in your editor and replace the placeholder with your API key

python main.py
```

Example prompt: `What are the principal applications of swarm robotics?`

The report is displayed in the terminal and appended to `outputs/research_output.txt`. The output directory is excluded from Git so you won't accidentally publish personal research queries or generated content.

To run local tests (no API key or live network call required):

```bash
python -m pip install pytest
python -m pytest -q
```

## Development history

The original version used the older `create_tool_calling_agent` / `AgentExecutor` interface, a `PydanticOutputParser`, and DuckDuckGo search. This version preserves the project goal and updates the agent to LangChain's newer `create_agent(..., response_format=...)` pattern, replaces the renamed `duckduckgo-search` library with `ddgs`, and makes saving deterministic after a successful structured response. The legacy import of Wikipedia was unused and has been removed. No Anthropic model is used.

## Limitations

- Web search produces snippets and links; this app does **not** independently verify claims or read full source documents.
- A source appearing in search results does not prove it supports the generated statement.
- DDGS may be rate-limited or fail based on network conditions.
- Source filtering only confirms URLs were returned by the tool, not factual reliability.
- Live end-to-end execution requires your own API key, network connection, and available API credit; offline tests validate only deterministic helpers.
- Original example research output was **not** republished because its statistics were not independently verified.

## Safety

**Never commit** `.env`, OpenAI API keys, auth tokens or generated user-specific output. `.gitignore` excludes these local files, but secrets already tracked in Git history require separate removal and key rotation.

## Future development

Possible improvements include source-content retrieval, claim-level citation verification, error retries, research quality evaluation, and a Streamlit UI. These features are **not yet implemented**.
