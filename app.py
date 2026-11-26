"""Portfolio demo. Provider keys stay on the server."""
import os
from urllib.parse import urlsplit
import streamlit as st
from dotenv import load_dotenv
from demo_limits import reserve_request
from main import run_research
from providers import ModelSettings

load_dotenv()
st.set_page_config(page_title='Research Desk | Aravind Sudheer', page_icon='🔎')
st.title('Research Desk')
st.caption('A web research assistant by Aravind Sudheer')
st.write('Ask a focused question. Get a short research summary with links to the search results used.')
st.info('Portfolio demo: summaries use search snippets, not full-page verification. Check the sources before relying on an answer.')
st.caption('Your question is sent to the configured AI provider and search service. Avoid personal or confidential information.')
# Streamlit Community Cloud secrets are loaded on the server only.
try:
    for key in ('GROQ_API_KEY', 'OPENAI_API_KEY', 'LLM_API_KEY', 'LLM_PROVIDER', 'LLM_MODEL', 'LLM_BASE_URL'):
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except FileNotFoundError:
    pass

with st.form('research'):
    query = st.text_area('What would you like to research?', max_chars=500,
                         placeholder='What are the trade-offs between LiDAR and cameras for mobile robots?')
    submitted = st.form_submit_button('Research', type='primary')

if submitted:
    st.session_state.pop('report', None)
    if not query.strip():
        st.warning('Enter a research question first.')
    else:
        try:
            ModelSettings.from_env()
        except ValueError:
            st.warning('Live research is not configured yet. Please try again later.')
        else:
            if not reserve_request():
                st.warning('The shared demo allowance is temporarily exhausted. Allow one minute between requests; the demo supports 20 requests per rolling day.')
            else:
                try:
                    with st.spinner('Searching and preparing your report…'):
                        st.session_state.report = run_research(query)
                except Exception:
                    st.error('Research could not finish. The provider may be rate-limited or search may be unavailable. Please try later.')

if 'report' in st.session_state:
    report = st.session_state.report
    st.subheader(report.topic)
    st.text(report.summary)
    st.subheader('Sources')
    for url in report.sources:
        parsed = urlsplit(url)
        if parsed.scheme in ('https', 'http') and parsed.netloc:
            st.link_button(parsed.netloc, url)
    st.download_button('Download report', report.model_dump_json(indent=2),
                       file_name='research-report.json', mime='application/json')
    st.caption('Source links are checked against observed search results; this does not verify every claim in the summary.')
