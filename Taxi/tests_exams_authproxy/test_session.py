# pylint: disable=import-error
import pytest

from client_blackbox import mock_blackbox  # noqa: F403 F401, I100, I202

DATE = '2022-01-01T00:00:00+03'
FILE_REQUESTS = 'requests.json'


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    EXAMS_AUTHPROXY_CSRF_TOKEN={
        'validation-enabled': True,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
@pytest.mark.now(DATE)
@pytest.mark.parametrize(
    'request_type_name',
    ['valid.yandex-session', 'valid.rewrite-path', 'invalid.yandex-session'],
)
async def test_session(
        load_json,
        _request_exams_authproxy,
        _mock_remote,
        blackbox_service,
        request_type_name,
):
    _type, _name = request_type_name.split('.')
    data = load_json(FILE_REQUESTS)[_type][_name]
    handler = _mock_remote(data['path'])
    request_path = data.get('request_path') or data['path']
    response = await _request_exams_authproxy(
        request_path, headers=data['headers'],
    )
    handler_has_calls = handler.has_calls
    assert handler_has_calls is data['proxied']

    if handler_has_calls:
        response_headers = handler.next_call()['request'].headers
        assert response_headers['X-Yandex-UID'] == '100'
        assert response_headers['X-Yandex-Login'] == 'login'
        assert not response.cookies
