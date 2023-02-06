import pytest

EXISTING_HEADERS = {
    'access-token': 'Some',
    'client': 'Some',
    'expiry': 'Some',
    'token-type': 'Bearer',
    'uid': 'uid@uid.uid',
    'X-Auth-User-Id': '1',
    'X-Auth-User-Role': 'admin',
    'X-Auth-Original': 'uid@uid.uid,Some,Some,Some,Bearer',
    'X-Auth-Organization-Id': '1',
}
PATH_LEGACY_200 = '/legacy'
PATH_LEGACY_401 = '/legacy401'
PATH_LEGACY_SIGN_IN = '/legacy/login'


@pytest.mark.parametrize(
    'exams_response_code, request_proxied',
    [(200, True), (400, False), (401, False)],
)
async def test_legacy_auth(
        load_json,
        _request_exams_authproxy,
        _mock_exams_training,
        _mock_remote,
        exams_response_code,
        request_proxied,
):
    exams_handler = _mock_exams_training(exams_response_code)

    handler = _mock_remote(PATH_LEGACY_200, existing_headers=EXISTING_HEADERS)
    response = await _request_exams_authproxy(
        PATH_LEGACY_200, headers=load_json('headers.json'),
    )

    assert exams_handler.has_calls
    assert handler.has_calls is request_proxied
    assert not response.cookies


@pytest.mark.parametrize(
    'route, proxied', [('/bad/legacy/login', False), ('/legacy/login', True)],
)
async def test_no_auth(
        load_json,
        _request_exams_authproxy,
        _mock_exams_training,
        _mock_remote,
        route,
        proxied,
):
    request_body = load_json('sign_in.json')
    handler = _mock_remote(
        route,
        request_body=request_body,
        existing_headers={
            'X-Forwarded-Host': 'education.adm.tst.training.yandex',
            'Host': 'education.adm.tst.training.yandex',
        },
    )
    response = await _request_exams_authproxy(
        route,
        request_body=request_body,
        headers={
            'Content-type': 'application/json',
            'Host': 'education.adm.tst.training.yandex',
        },
    )
    assert handler.has_calls is proxied
    assert not response.cookies
    if proxied:
        assert response.headers


@pytest.mark.config(EXAMS_AUTHPROXY_PROXY_ALL_TO_EXAMS_TRAINING=True)
async def test_proxy_all(
        load_json,
        _request_exams_authproxy,
        _mock_exams_training,
        _mock_remote,
):
    handler = _mock_remote(
        '/proxy-all',
        existing_headers={
            'X-Forwarded-Host': 'education.tst.training.yandex',
            'Host': 'education.tst.training.yandex',
        },
    )
    response = await _request_exams_authproxy(
        '/proxy-all', headers=load_json('headers.json'),
    )
    assert handler.has_calls is True
    assert not response.cookies
