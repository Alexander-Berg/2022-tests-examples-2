import pytest

FILE_REQUESTS = 'requests.json'
CSRF_PATH = '/csrf_token'
DATE = '2022-01-01T00:00:00Z'


@pytest.mark.now(DATE)
@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    EXAMS_AUTHPROXY_CSRF_TOKEN={
        'validation-enabled': True,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
@pytest.mark.parametrize('request_type_name', ['valid.csrf', 'invalid.csrf'])
async def test_csrf_get(
        load_json,
        _request_exams_authproxy,
        _mock_remote,
        blackbox_service,
        request_type_name,
):
    _type, _name = request_type_name.split('.')
    data = load_json(FILE_REQUESTS)[_type][_name]
    headers = data['headers']
    proxied = data['proxied']
    handler = _mock_remote(data['path'])

    get_request = await _request_exams_authproxy(
        data['path'], headers=headers, method='get',
    )
    if proxied:
        assert get_request.status_code == 200
        assert handler.has_calls is True
    else:
        assert get_request.status_code == 401
        assert handler.has_calls is False


@pytest.mark.now(DATE)
@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    EXAMS_AUTHPROXY_CSRF_TOKEN={
        'validation-enabled': True,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
@pytest.mark.parametrize('request_type_name', ['valid.csrf', 'invalid.csrf'])
async def test_csrf_post(
        load_json,
        _request_exams_authproxy,
        _mock_remote,
        blackbox_service,
        request_type_name,
):
    _type, _name = request_type_name.split('.')
    data = load_json(FILE_REQUESTS)[_type][_name]
    headers = data['headers']
    handler = _mock_remote(data['path'])

    first_attempt = await _request_exams_authproxy(
        data['path'], headers=headers,
    )
    assert first_attempt.status_code == 401
    assert first_attempt.json()['code'] == 'INVALID_CSRF_TOKEN'

    _csrf_token = await _request_exams_authproxy(
        CSRF_PATH, headers=data['headers'],
    )
    headers['X-CSRF-TOKEN'] = _csrf_token.json()['sk']

    second_attempt = await _request_exams_authproxy(
        data['path'], headers=headers,
    )

    assert second_attempt.status_code == 200 if data['proxied'] else 401
    assert handler.has_calls is data['proxied']
