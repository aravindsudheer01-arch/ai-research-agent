from errors import research_error_message


def test_errors_are_specific_without_leaking_provider_body():
    for code, expected in [(400, 'format'), (401, 'access'), (429, 'usage limit'), (500, 'could not finish')]:
        error = RuntimeError('SECRET-KEY and private provider response')
        error.status_code = code
        message = research_error_message(error)
        assert expected in message
        assert 'SECRET' not in message
