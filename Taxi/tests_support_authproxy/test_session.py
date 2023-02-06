import dateutil.parser
import pytest

from testsuite import utils

HEADERS_FILE = 'headers.json'

NOW = '2018-01-22T00:00:00Z'

URL_AUTH = 'support/v1/auth'
URL_NOAUTH = 'support/v1/noauth'

REMOTE_RESPONSE = {'sentinel': True}


async def do_test_ok(
        mock_remote,
        request_support_authproxy,
        url_path,
        headers,
        method='post',
):
    handler = mock_remote(url_path=url_path)
    response = await request_support_authproxy(
        url_path=url_path, headers=headers, method=method,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


async def do_test_fail(
        mock_remote, request_support_authproxy, url_path, headers,
):
    handler = mock_remote(url_path=url_path)
    response = await request_support_authproxy(
        url_path=url_path, headers=headers,
    )

    assert not handler.has_calls
    assert response.status_code == 401
    assert not response.cookies


async def do_test_fail_csrf(
        mock_remote, request_support_authproxy, url_path, headers,
):
    handler = mock_remote(url_path=url_path)
    response = await request_support_authproxy(
        url_path=url_path, headers=headers,
    )

    assert not handler.has_calls
    assert response.status_code == 401
    assert not response.cookies
    assert response.json()['code'] == 'INVALID_CSRF_TOKEN'


@pytest.mark.now(NOW)
@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_session_ok(
        mock_remote, request_support_authproxy, load_json, blackbox_service,
):
    headers = load_json(HEADERS_FILE)['SESSION']
    await do_test_ok(mock_remote, request_support_authproxy, URL_AUTH, headers)


@pytest.mark.now(NOW)
async def test_session_fail(
        mock_remote, request_support_authproxy, load_json, blackbox_service,
):
    headers = load_json(HEADERS_FILE)['SESSION']
    await do_test_fail(
        mock_remote, request_support_authproxy, URL_AUTH, headers,
    )


@pytest.mark.now(NOW)
@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_csrf_token_noyandexuid(
        taxi_support_authproxy, blackbox_service,
):
    response = await taxi_support_authproxy.post(
        'csrf_token_noauth', headers={'origin': 'localhost'},
    )
    assert response.status_code == 200
    assert 'yandexuid' in response.cookies

    body = response.json()
    assert 'sk' in body


@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_csrf_token(
        mock_remote,
        request_support_authproxy,
        taxi_support_authproxy,
        mocked_time,
        load_json,
        blackbox_service,
):
    now = utils.to_utc(dateutil.parser.parse(NOW))
    mocked_time.set(now)

    headers = load_json(HEADERS_FILE)['SESSION']
    csrf_token = headers.pop('X-CSRF-Token')

    await do_test_fail_csrf(
        mock_remote, request_support_authproxy, URL_AUTH, headers,
    )

    await do_test_ok(
        mock_remote,
        request_support_authproxy,
        URL_AUTH,
        headers,
        method='get',
    )

    response = await taxi_support_authproxy.post('csrf_token', headers=headers)
    assert response.status_code == 200
    assert response.json() == {'sk': csrf_token, 'max-age-seconds': 600}
    resp_headers = response.headers
    assert resp_headers['Content-Type'] == 'application/json; charset=utf-8'
    assert resp_headers['X-Content-Type-Options'] == 'nosniff'
    assert resp_headers['X-Frame-Options'] == 'SAMEORIGIN'
    assert resp_headers['x-dns-prefetch-control'] == 'off'

    headers['X-CSRF-Token'] = csrf_token
    await do_test_ok(mock_remote, request_support_authproxy, URL_AUTH, headers)

    mocked_time.sleep(-1)
    await do_test_ok(mock_remote, request_support_authproxy, URL_AUTH, headers)

    mocked_time.sleep(-20)
    await do_test_fail_csrf(
        mock_remote, request_support_authproxy, URL_AUTH, headers,
    )

    mocked_time.set(now)
    mocked_time.sleep(10)
    await do_test_ok(mock_remote, request_support_authproxy, URL_AUTH, headers)

    mocked_time.sleep(589)
    await do_test_ok(mock_remote, request_support_authproxy, URL_AUTH, headers)

    mocked_time.sleep(2)
    await do_test_fail_csrf(
        mock_remote, request_support_authproxy, URL_AUTH, headers,
    )


@pytest.mark.now(NOW)
async def test_noauth_ok(
        mock_remote, request_support_authproxy, load_json, blackbox_service,
):
    handler = mock_remote(url_path=URL_NOAUTH)
    headers = load_json(HEADERS_FILE)['EMPTY']
    response = await request_support_authproxy(
        url_path=URL_NOAUTH, headers=headers,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers

    assert 'X-Yandex-UID' not in response_headers
    assert 'X-Yandex-Login' not in response_headers

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.now(NOW)
async def test_noauth_fail(
        mock_remote, request_support_authproxy, load_json, blackbox_service,
):
    headers = load_json(HEADERS_FILE)['EMPTY']
    await do_test_fail(
        mock_remote, request_support_authproxy, URL_AUTH, headers,
    )
