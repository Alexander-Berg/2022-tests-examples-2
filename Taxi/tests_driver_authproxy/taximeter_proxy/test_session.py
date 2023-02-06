import pytest

URL_PATH = 'driver/v1/auth/smth'
COOKIE_URL_PATH = 'driver/v1/cookie/smth'
UNAUTHORIZED_URL_PATH = 'driver/v1/noauth/smth'
UNAUTHORIZED_URL_PATH_PROXY_COOKIES = 'driver/v1/noauth/cookie'
PASSPORT_ONLY_URL_PATH = 'driver/v1/passport_only'
REQUEST_BODY = {'x': 'y'}
REMOTE_RESPONSE = {'sentinel': True}

HEADERS_AUTH_OK = {
    'X-Driver-Session': 'session1',
    'X-YaTaxi-Park-Id': 'db1',
    'User-Agent': 'Taximeter 9.13 (1882)',
}
HEADERS_AUTH_EXTENDED_OK = {
    'X-Driver-Session': 'session1',
    'X-YaTaxi-Park-Id': 'db1',
    'User-Agent': (
        'app:pro brand:yandex version:11.12 build:23455 '
        'build_type:beta platform:android platform_version:12.0'
    ),
}
USER_AGENT_COOKIE = 'Taximeter%209.13%20(1882)'
USER_AGENT_EXTENDED_COOKIE = (
    'app%3Apro%20brand%3Ayandex%20version%3A11.12%20build%3A23455%20'
    'build_type%3Abeta%20platform%3Aandroid%20platform_version%3A12.0'
)
HEADERS_AUTH_COOKIE_OK = {
    'Cookie': '; '.join(
        [
            'webviewdriversession=session1',
            'webviewparkid=db1',
            f'webviewuseragent={USER_AGENT_COOKIE}',
        ],
    ),
}
HEADERS_AUTH_COOKIE_UA_EXTENDED_OK = {
    'Cookie': '; '.join(
        [
            'webviewdriversession=session1',
            'webviewparkid=db1',
            f'webviewuseragent={USER_AGENT_EXTENDED_COOKIE}',
        ],
    ),
}
HEADERS_AUTH_BAD = {
    'X-Driver-Session': 'bad_session',
    'X-YaTaxi-Park-Id': 'invalid_park_id',
    'User-Agent': 'Taximeter 9.13 (1882)',
}
HEADERS_AUTH_COOKIE_BAD = {
    'Cookie': '; '.join(
        [
            'webviewdriversession=bad_session',
            'webviewparkid=invalid_park_id',
            f'webviewuseragent={USER_AGENT_COOKIE}',
        ],
    ),
}
HEADERS_NO_AUTH = {'User-Agent': 'Taximeter 9.13 (1882)'}
HEADERS_BAD_USER_AGENT = {
    'X-Driver-Session': 'session1',
    'X-YaTaxi-Park-Id': 'db1',
    'User-Agent': 'NotTaximeter',
}

PASSPORT_SESSION = {
    'park_id': 'db1',
    'session': 'session1',
    'uuid': 'uuid1',
    'yandex_uid': '123',
}
PASSPORT_TOKEN = {'uid': '123', 'scope': 'taxi-driver:all'}
PASSPORT_TOKEN_WRONG_UID = {'uid': '1', 'scope': 'taxi-driver:all'}
PASSPORT_TOKEN_WRONG_SCOPE = {'uid': '123', 'scope': 'taxi:all'}
HEADERS_AUTH_PASSPORT = {
    'X-Driver-Session': 'session1',
    'X-YaTaxi-Park-Id': 'db1',
    'Authorization': 'Bearer token1',
    'User-Agent': 'Taximeter 9.13 (1882)',
}
HEADERS_AUTH_PASSPORT_COOKIES = {
    'Cookie': '; '.join(
        [
            'webviewdriversession=session1',
            'webviewparkid=db1',
            'webviewuseragent=Taximeter%209.13%20%281882%29',
            'webviewbearertoken=token1',
        ],
    ),
}

HEADERS_ONLY_PASSPORT_OK = {
    'Authorization': 'Bearer token1',
    'User-Agent': 'Taximeter 9.13 (1882)',
}
HEADERS_ONLY_PASSPORT_EMPTY = {'User-Agent': 'Taximeter 9.13 (1882)'}
HEADERS_ONLY_PASSPORT_BAD = {
    'Authorization': 'Bearer token_bad',
    'User-Agent': 'Taximeter 9.13 (1882)',
}


@pytest.mark.parametrize('extended_ua', [False, True])
@pytest.mark.parametrize(
    'eats_courier_id',
    [
        pytest.param(
            None,
            marks=[
                pytest.mark.driver_session(
                    park_id='db1', session='session1', uuid='uuid1',
                ),
            ],
        ),
        pytest.param(
            '1122',
            marks=[
                pytest.mark.driver_session(
                    park_id='db1',
                    session='session1',
                    uuid='uuid1',
                    eats_courier_id='1122',
                ),
            ],
        ),
    ],
)
async def test_session_ok(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        extended_ua,
        eats_courier_id,
):
    handler = mock_remote()
    response = await request_post(
        headers=(HEADERS_AUTH_EXTENDED_OK if extended_ua else HEADERS_AUTH_OK),
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert 'X-Driver-Session' not in response_headers
    assert response_headers['X-YaTaxi-Park-Id'] == 'db1'
    assert response_headers['X-YaTaxi-Driver-Profile-Id'] == 'uuid1'
    assert response_headers['X-Request-Application'] == 'taximeter'
    assert response_headers['X-Request-Platform'] == 'android'
    assert response_headers['X-Request-Version-Type'] == (
        'beta' if extended_ua else ''
    )
    assert response_headers['X-Request-Application-Brand'] == 'yandex'
    assert response_headers.get('X-Request-Application-Build-Type') == (
        'beta' if extended_ua else None
    )
    assert response_headers.get('X-Request-Platform-Version') == (
        '12.0.0' if extended_ua else None
    )
    assert response_headers.get('X-YaEda-CourierId') == eats_courier_id
    assert 'X-Yandex-Uid' not in response_headers

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.driver_session(**PASSPORT_SESSION)
async def test_session_with_uid_no_token(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        blackbox_service,
):
    handler = mock_remote()
    response = await request_post(headers=HEADERS_AUTH_OK)

    assert not handler.has_calls
    assert response.status_code == 401
    assert response.json()


@pytest.mark.passport_token(token1=PASSPORT_TOKEN)
@pytest.mark.driver_session(**PASSPORT_SESSION)
async def test_session_with_uid(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        blackbox_service,
):
    handler = mock_remote(ya_uid=True)
    response = await request_post(headers=HEADERS_AUTH_PASSPORT)

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert 'X-Driver-Session' not in response_headers
    assert response_headers['X-YaTaxi-Park-Id'] == 'db1'
    assert response_headers['X-YaTaxi-Driver-Profile-Id'] == 'uuid1'
    assert response_headers['X-Request-Application'] == 'taximeter'
    assert response_headers['X-Request-Platform'] == 'android'
    assert response_headers['X-Yandex-Uid'] == '123'

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


@pytest.mark.passport_token(token_wrong_uid=PASSPORT_TOKEN_WRONG_UID)
@pytest.mark.passport_token(token_wrong_scope=PASSPORT_TOKEN_WRONG_SCOPE)
@pytest.mark.driver_session(**PASSPORT_SESSION)
@pytest.mark.parametrize(
    'token', ['token_wrong_uid', 'token_wrong_scope', 'token_invalid'],
)
async def test_session_passport_bad(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        token,
        blackbox_service,
):
    headers = HEADERS_AUTH_PASSPORT.copy()
    headers['Authorization'] = 'Bearer ' + token

    handler = mock_remote()
    response = await request_post(headers=headers)

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.driver_session(park_id='db1', session='session1', uuid='uuid1')
@pytest.mark.parametrize(
    'query_params',
    [
        {'session': 'session1', 'park_id': 'db1'},
        {'session': 'session1', 'db': 'db1'},
    ],
)
async def test_session_with_query_params(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        query_params,
):
    handler = mock_remote()
    response = await request_post(
        headers={'User-Agent': 'Taximeter 9.13 (1882)'}, params=query_params,
    )

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert 'X-Driver-Session' not in response_headers
    assert response_headers['X-YaTaxi-Park-Id'] == 'db1'
    assert response_headers['X-YaTaxi-Driver-Profile-Id'] == 'uuid1'
    assert response_headers['X-Request-Application'] == 'taximeter'
    assert response_headers['X-Request-Platform'] == 'android'

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


async def test_no_session_no_pass(
        driver_authorizer, mock_remote, request_post, taxi_taximeter_proxy,
):
    handler = mock_remote()
    response = await request_post()

    assert not handler.has_calls
    assert not response.cookies
    assert response.status_code == 401


@pytest.mark.driver_session(park_id='db1', session='session1', uuid='uuid1')
async def test_cookie_disabled(
        driver_authorizer, mock_remote, request_post, taxi_taximeter_proxy,
):
    handler = mock_remote()
    response = await request_post(headers=HEADERS_AUTH_COOKIE_OK)

    assert not handler.has_calls
    assert not response.cookies
    assert response.status_code == 400


@pytest.mark.parametrize(
    'url, headers, expect_upstream_cookies',
    [
        (UNAUTHORIZED_URL_PATH, HEADERS_AUTH_BAD, {}),
        (
            UNAUTHORIZED_URL_PATH_PROXY_COOKIES,
            HEADERS_AUTH_BAD,
            {'foobarcookie': 'foobarvalue'},
        ),
        (
            UNAUTHORIZED_URL_PATH_PROXY_COOKIES,
            HEADERS_AUTH_COOKIE_BAD,
            {'foobarcookie': 'foobarvalue'},
        ),
    ],
)
async def test_no_session_pass(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        url,
        headers,
        expect_upstream_cookies,
):
    handler = mock_remote(url_path=url, authorized=False)
    headers['Cookie'] = 'foobarcookie=foobarvalue;' + headers.get('Cookie', '')
    response = await request_post(url_path=url, headers=headers)

    assert handler.has_calls
    upstream_request = handler.next_call()['request']
    assert 'X-Driver-Session' not in upstream_request.headers
    assert 'X-YaTaxi-Park-Id' not in upstream_request.headers
    assert 'X-YaTaxi-Driver-Profile-Id' not in upstream_request.headers
    assert upstream_request.cookies == expect_upstream_cookies

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


def _check_response_cookies(response, expected_cookies):
    for key, expected_cookie in expected_cookies.items():
        assert key in response.cookies
        value, attributes = expected_cookie
        cookie = response.cookies[key]
        assert cookie.value == value
        for attr_key, attr_val in attributes.items():
            assert cookie[attr_key] == attr_val


@pytest.mark.parametrize(
    'headers, expected_upstream_cookies, extended_ua',
    [
        (HEADERS_AUTH_OK, {'foobarcookie': 'foobarvalue'}, False),
        (HEADERS_AUTH_COOKIE_OK, {'foobarcookie': 'foobarvalue'}, False),
        (
            HEADERS_AUTH_COOKIE_UA_EXTENDED_OK,
            {'foobarcookie': 'foobarvalue'},
            True,
        ),
    ],
)
@pytest.mark.driver_session(park_id='db1', session='session1', uuid='uuid1')
async def test_cookie_ok(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        headers,
        expected_upstream_cookies,
        extended_ua,
):
    handler = mock_remote(url_path=COOKIE_URL_PATH, taximeter=True)
    headers['Cookie'] = 'foobarcookie=foobarvalue;' + headers.get('Cookie', '')
    response = await request_post(url_path=COOKIE_URL_PATH, headers=headers)

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    _check_response_cookies(
        response,
        {
            'webviewdriversession': ('session1', {}),
            'webviewparkid': ('db1', {}),
            'webviewuseragent': (
                USER_AGENT_EXTENDED_COOKIE
                if extended_ua
                else USER_AGENT_COOKIE,
                {},
            ),
        },
    )

    assert handler.has_calls
    upstream_request = handler.next_call()['request']
    upstream_headers = upstream_request.headers
    assert 'X-Driver-Session' not in upstream_headers
    assert upstream_headers['X-YaTaxi-Park-Id'] == 'db1'
    assert upstream_headers['X-YaTaxi-Driver-Profile-Id'] == 'uuid1'
    assert upstream_headers['X-Request-Application'] == 'taximeter'
    assert upstream_headers['X-Request-Platform'] == 'android'
    assert upstream_headers['X-Request-Version-Type'] == (
        'beta' if extended_ua else ''
    )
    assert upstream_headers['X-Request-Application-Brand'] == 'yandex'
    assert upstream_headers.get('X-Request-Application-Build-Type') == (
        'beta' if extended_ua else None
    )
    assert upstream_headers.get('X-Request-Platform-Version') == (
        '12.0.0' if extended_ua else None
    )
    assert upstream_request.cookies == expected_upstream_cookies


@pytest.mark.parametrize(
    'headers', [HEADERS_AUTH_PASSPORT, HEADERS_AUTH_PASSPORT_COOKIES],
)
@pytest.mark.passport_token(token1=PASSPORT_TOKEN)
@pytest.mark.driver_session(**PASSPORT_SESSION)
async def test_cookie_passport(
        driver_authorizer,
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        headers,
        blackbox_service,
):
    handler = mock_remote(
        url_path=COOKIE_URL_PATH, taximeter=True, ya_uid=True,
    )
    response = await request_post(url_path=COOKIE_URL_PATH, headers=headers)

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    _check_response_cookies(
        response,
        {
            'webviewdriversession': ('session1', {}),
            'webviewparkid': ('db1', {}),
            'webviewuseragent': (USER_AGENT_COOKIE, {}),
            'webviewbearertoken': ('token1', {}),
        },
    )

    assert handler.has_calls
    response = handler.next_call()['request']
    assert 'X-Driver-Session' not in response.headers
    assert response.headers['X-YaTaxi-Park-Id'] == 'db1'
    assert response.headers['X-YaTaxi-Driver-Profile-Id'] == 'uuid1'
    assert response.headers['X-Request-Application'] == 'taximeter'
    assert response.headers['X-Request-Platform'] == 'android'
    assert response.headers['X-Yandex-Uid'] == '123'


async def test_cookie_no_session_no_pass(
        driver_authorizer, mock_remote, request_post, taxi_taximeter_proxy,
):
    handler = mock_remote(url_path=COOKIE_URL_PATH, taximeter=False)
    response = await request_post(
        url_path=COOKIE_URL_PATH, headers=HEADERS_NO_AUTH,
    )

    assert not handler.has_calls
    assert not response.cookies
    assert response.status_code == 401


@pytest.mark.driver_session(park_id='db1', session='session1', uuid='uuid1')
async def test_bad_user_agent(
        driver_authorizer, mock_remote, request_post, taxi_taximeter_proxy,
):
    handler = mock_remote()
    response = await request_post(headers=HEADERS_BAD_USER_AGENT)

    assert not handler.has_calls
    assert response.status_code == 400


@pytest.mark.passport_token(token1=PASSPORT_TOKEN)
@pytest.mark.parametrize(
    'headers, has_calls, status_code, ya_uid',
    [
        (HEADERS_ONLY_PASSPORT_OK, True, 200, True),
        (HEADERS_ONLY_PASSPORT_EMPTY, True, 200, False),
        (HEADERS_ONLY_PASSPORT_BAD, False, 401, False),
    ],
)
async def test_passport_token_only(
        mock_remote,
        request_post,
        taxi_taximeter_proxy,
        blackbox_service,
        headers,
        has_calls,
        status_code,
        ya_uid,
):

    handler = mock_remote(
        url_path=PASSPORT_ONLY_URL_PATH, authorized=False, ya_uid=ya_uid,
    )
    response = await request_post(
        url_path=PASSPORT_ONLY_URL_PATH, headers=headers,
    )

    assert handler.has_calls == has_calls
    assert response.status_code == status_code
