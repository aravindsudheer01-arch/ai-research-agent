"""Public-safe failure messages. Never display provider response bodies or keys."""
def research_error_message(exc):
    status = getattr(exc, 'status_code', None)
    name = type(exc).__name__.lower()
    if status == 429:
        return 'The AI provider has reached its usage limit. Wait before retrying and check your provider quota if this continues.'
    if status in (401, 403):
        return 'The AI provider rejected access. Check the server API key and model permissions.'
    if status == 400:
        return 'The model rejected the request format. Check that the configured model supports this research workflow.'
    if 'recursion' in name:
        return 'Research reached its step limit. Try a narrower question.'
    if 'timeout' in name or 'connection' in name:
        return 'The AI service could not be reached in time. Please try again shortly.'
    if 'validation' in name or 'parser' in name:
        return 'The model returned an incomplete report. Please try again with a more focused question.'
    return 'Research could not finish. Please try again; if it persists, check the server configuration.'
