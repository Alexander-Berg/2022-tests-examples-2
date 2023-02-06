import pytest


RULES = [
    {
        'input': {'http-path-prefix': '/auth'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {},
    },
    {
        'input': {'http-path-prefix': '/noauth'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
        'proxy': {'proxy-401': True},
    },
]
TEST_TOKEN = 'token'
PASSPORT_TOKEN = {'uid': '100', 'login': 'login', 'scope': 'eats_restapp:all'}


@pytest.mark.passport_token(token=PASSPORT_TOKEN)
@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=RULES)
async def test_token(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
):
    await taxi_eats_restapp_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await request_proxy(token=TEST_TOKEN)

    assert handler.has_calls
    assert response.status_code == 200


@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=RULES)
async def test_invalid_token(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
):
    await taxi_eats_restapp_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await request_proxy(token='invalidtoken')

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.passport_token(token=PASSPORT_TOKEN)
@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=RULES)
async def test_no_token(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
):
    await taxi_eats_restapp_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await request_proxy()

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=RULES)
async def test_proxy401(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
):
    await taxi_eats_restapp_authproxy.invalidate_caches()

    url = '/noauth'
    handler = mock_remote(url=url)

    response = await request_proxy(url=url)

    assert handler.has_calls
    assert response.status_code == 200


@pytest.mark.passport_token(token={'uid': '100', 'scope': 'bad-scope'})
@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=RULES)
async def test_bad_token_scope(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
):
    await taxi_eats_restapp_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await request_proxy(token=TEST_TOKEN)

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.passport_token(token=PASSPORT_TOKEN)
@pytest.mark.config(EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=RULES)
async def test_proxy_headers(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
):
    await taxi_eats_restapp_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await request_proxy(token=TEST_TOKEN)

    assert handler.has_calls
    request_headers = handler.next_call()['request'].headers
    assert request_headers['X-Yandex-UID'] == '100'
    assert request_headers['X-Yandex-Login'] == 'login'
    assert not request_headers.get('Authorization')

    assert response.status_code == 200


@pytest.mark.passport_token(token=PASSPORT_TOKEN)
@pytest.mark.config(
    EATS_RESTAPP_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/auth1'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {'additional-headers-to-proxy': ['Authorization']},
        },
        {
            'input': {'http-path-prefix': '/auth2'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {},
        },
        {
            'input': {'http-path-prefix': '/auth3'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {'additional-headers-to-proxy': ['Not-Existing-Header']},
        },
    ],
)
@pytest.mark.parametrize(
    'url',
    [
        pytest.param('/auth1', id='existing, proxy'),
        pytest.param('/auth2', id='existing, no proxy'),
        pytest.param('/auth3', id='not existing'),
    ],
)
async def test_add_proxy_headers(
        taxi_eats_restapp_authproxy,
        request_proxy,
        mock_remote,
        blackbox_service,
        url,
):
    if url in ('/auth1', '/auth2'):
        add_headers = [{'Authorization': f'Bearer {TEST_TOKEN}'}]
    else:
        add_headers = [{'Not-Existing-Header': '123'}]

    await taxi_eats_restapp_authproxy.invalidate_caches()
    handler = mock_remote(url=url)

    response = await request_proxy(url=url, token=TEST_TOKEN)

    assert handler.has_calls
    request_headers = handler.next_call()['request'].headers
    assert request_headers['X-Yandex-UID'] == '100'
    assert request_headers['X-Yandex-Login'] == 'login'

    for header in add_headers:
        for key in header:
            if url == '/auth1':
                assert request_headers[key] == header[key]
            else:
                assert not request_headers.get(key)

    assert response.status_code == 200
