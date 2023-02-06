import json
import pytest

from taxi.external import translate


@pytest.mark.parametrize(
    'text,expected_request_kwargs,detected_lang',
    [
        (
            'example text',
            {
                'exponential_backoff': True,
                'log_extra': None,
                'params': {
                    'srv': 'taxi',
                    'text': 'example text',
                },
                'headers': {
                    'Content-Type': 'application/json',
                    'User-Agent': 'arequests',
                },
                'timeout': 1,
            },
            'en',
        ),
    ]
)
@pytest.inline_callbacks
def test_detect_language(mock, areq_request, text, expected_request_kwargs,
                         detected_lang):
    @mock
    @areq_request
    def arequest(method, url, **kwargs):
        assert method == 'GET'
        assert url == 'http://translate.yandex.net/api/v1/tr.json/detect'
        assert kwargs == expected_request_kwargs

        return 200, json.dumps({'lang': 'en', 'code': 200}), {}

    language = yield translate.detect_language(text)
    assert language == detected_lang
    assert arequest.call
