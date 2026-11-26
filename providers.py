"""Server-side provider configuration. Never accept endpoints or keys from visitors."""
import os
from dataclasses import dataclass, field
from langchain_openai import ChatOpenAI


@dataclass(frozen=True)
class ModelSettings:
    provider: str
    model: str
    base_url: str
    api_key: str = field(repr=False)

    @classmethod
    def from_env(cls):
        provider = os.getenv('LLM_PROVIDER', 'groq').strip().lower()
        options = {
            'groq': ('openai/gpt-oss-20b', 'https://api.groq.com/openai/v1', 'GROQ_API_KEY'),
            'openai': (os.getenv('OPENAI_MODEL', 'gpt-4o-mini'), 'https://api.openai.com/v1', 'OPENAI_API_KEY'),
            'compatible': ('', os.getenv('LLM_BASE_URL', ''), 'LLM_API_KEY'),
        }
        if provider not in options:
            raise ValueError('LLM_PROVIDER must be groq, openai or compatible.')
        default_model, base_url, key_name = options[provider]
        model = os.getenv('LLM_MODEL', '').strip() or default_model
        key = os.getenv(key_name, '').strip()
        if not key:
            raise ValueError(f'Missing {key_name}. Configure it on the server, never in browser code.')
        if not model or not base_url:
            raise ValueError('Compatible providers require LLM_MODEL and LLM_BASE_URL.')
        if not base_url.startswith(('https://', 'http://localhost:', 'http://127.0.0.1:')):
            raise ValueError('Use HTTPS for remote providers or a local loopback endpoint.')
        return cls(provider, model, base_url, key)


def create_model(settings=None):
    settings = settings or ModelSettings.from_env()
    return ChatOpenAI(model=settings.model, api_key=settings.api_key,
                      base_url=settings.base_url, temperature=0,
                      max_tokens=2048, timeout=45, max_retries=0)
