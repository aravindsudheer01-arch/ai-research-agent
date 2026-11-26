# Research Desk — a configurable AI research agent

A Python research assistant with a CLI and Streamlit portfolio demo. Groq is the default provider; OpenAI and other OpenAI-compatible, tool-capable chat APIs can be selected through environment variables.

It searches the web, produces a Pydantic-validated report, and filters reported source URLs against actual search-tool results. This is a snippet-based research demonstration, not an academic research engine or claim-verification service.

## Run locally

Use **Python 3.12** (minimum 3.10). Create a free Groq account and API key at https://console.groq.com/keys.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Set GROQ_API_KEY in .env using your editor. Never commit it.
python main.py
# Or launch the portfolio interface:
streamlit run app.py
```

The default model is `openai/gpt-oss-20b`, served by **Groq**. The model's namespace does not mean it uses your OpenAI API account or credits. Model availability and free-tier quotas can change; check your Groq dashboard. Stay on the free plan if you do not want paid usage.

## Provider switching

| LLM_PROVIDER | Required key | Model configuration |
|---|---|---|
| `groq` (default) | `GROQ_API_KEY` | `LLM_MODEL`, defaults to `openai/gpt-oss-20b` |
| `openai` | `OPENAI_API_KEY` | `LLM_MODEL`, then legacy `OPENAI_MODEL`, then `gpt-4o-mini` |
| `compatible` | `LLM_API_KEY` | Set both `LLM_MODEL` and `LLM_BASE_URL` |

When switching, change both provider and model; `.env.example` explicitly sets the Groq model. Compatible providers must implement OpenAI-style chat completions and tool calling. This is an extension point, not a promise that every model/provider works. Local endpoints may use a placeholder key if their server does not require authentication. Remote endpoints must use HTTPS.

`providers.py` creates the model; `main.py` owns the research workflow. Research runs one deterministic web search, followed by one JSON-mode formatting call validated with Pydantic. This avoids forced report-tool calls that Groq can reject when the model answers in plain text. No automatic fallback to a billable provider occurs.

## Publish the portfolio demo

GitHub Pages cannot run this Python backend. Host `app.py` on **Streamlit Community Cloud**, then link to its URL from your GitHub Pages portfolio.

1. Push the reviewed code to your repository.
2. Create a Streamlit Community Cloud app pointing to the repository/branch and `app.py`; select Python 3.12.
3. Add server-side secrets in the hosting dashboard:

```toml
LLM_PROVIDER = "groq"
LLM_MODEL = "openai/gpt-oss-20b"
GROQ_API_KEY = "YOUR_KEY_HERE"
```

4. Run one live question and check the summary, source links and download before sharing the URL.

Do not put the key in GitHub Pages HTML, browser JavaScript, a screenshot, or a committed file. The app never asks visitors for credentials or allows them to select API endpoints. Local `.streamlit/secrets.toml` is ignored by Git.

### Demo limits and privacy

- Up to 500 characters per question, three search results per search and 1,200 characters per snippet.
- One model call per run, with a 2,048-token output limit, 45-second model-call timeout and no automatic API retries. Search retries once after a transient failure, with a 10-second timeout per attempt. Provider token quotas still apply.
- Shared allowance: one run per rolling minute and 20 per rolling 24 hours, reserved atomically in SQLite. Failed runs count too.
- SQLite tracks timestamps only. The web app keeps reports in the visitor's session and offers a download; it does not append them to the CLI report file.
- The limiter is for a **single deployment with shared local storage**. Ephemeral storage resets on redeploy; multiple replicas require a shared external limiter. It is not a substitute for provider limits or billing controls. Public visitors can exhaust the shared allowance.
- Questions and snippets are sent to the selected provider; search queries go to the search service. Avoid confidential inputs.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

Offline tests cover provider configuration, JSON output strategy, evidence filtering, input validation, atomic demo limits, Streamlit startup and a mocked successful report. They do not establish live model quality or account access. A live smoke test needs an actual Groq key.

## Files

- `providers.py`: provider settings and model factory
- `main.py`: bounded search-and-summary workflow and CLI
- `app.py`: Streamlit interface
- `tools.py`: DDGS search
- `reporting.py`: observed-source reconciliation
- `demo_limits.py`: atomic shared request allowance
- `storage.py`: timestamped CLI report saving

## Limitations

Search results are snippets, not full documents. A returned URL does not prove that it supports a claim. Model prose can still contain mistakes or unsupported links; only the separate sources list is reconciled. DDGS can fail or be rate-limited. Provider quotas may interrupt an otherwise valid research run. The UI reports failures without displaying raw exceptions or credentials.

Original project: Python, LangChain, OpenAI and structured web research. This revision introduces Groq, provider configuration and a portfolio interface while retaining the existing report schema and CLI output.

The original autonomous tool-calling loop has been replaced with a bounded retrieval-and-summary workflow for the free-tier demo. This avoids forced-tool-choice HTTP 400 errors and repeated-search recursion failures; the model does not autonomously plan searches.
