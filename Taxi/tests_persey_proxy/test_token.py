import pytest

ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/persey/v1/'},
        'proxy': {'server-hosts': ['*'], 'auth': 'token'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]

ROUTE_RULES_401 = [
    {
        'input': {'http-path-prefix': '/persey/v1/'},
        'proxy': {'server-hosts': ['*'], 'proxy-401': True, 'auth': 'token'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]

TOKEN = {'uid': '100', 'scope': 'persey:smth'}
REMOTE_RESPONSE = {'sentinel': True}


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(
    PERSEY_PROXY_ROUTE_RULES=ROUTE_RULES,
    PERSEY_PROXY_PASSPORT_SCOPES=['persey:smth'],
)
async def test_token(
        taxi_persey_proxy, request_post, mock_remote, blackbox_service,
):
    await taxi_persey_proxy.invalidate_caches()
    handler = mock_remote()

    response = await request_post(token='token1')

    assert handler.has_calls
    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE

    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=ROUTE_RULES)
async def test_wrong_scope(
        taxi_persey_proxy, request_post, mock_remote, blackbox_service,
):
    await taxi_persey_proxy.invalidate_caches()
    handler = mock_remote()

    response = await request_post(token='token1')

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=ROUTE_RULES)
async def test_invalid_token(
        taxi_persey_proxy, request_post, mock_remote, blackbox_service,
):
    await taxi_persey_proxy.invalidate_caches()
    handler = mock_remote()

    response = await request_post(token='token1')

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=ROUTE_RULES)
async def test_notoken(
        taxi_persey_proxy, request_post, mock_remote, blackbox_service,
):
    await taxi_persey_proxy.invalidate_caches()
    handler = mock_remote()

    response = await request_post()

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.config(PERSEY_PROXY_ROUTE_RULES=ROUTE_RULES_401)
async def test_proxy401(
        taxi_persey_proxy, request_post, mock_remote, blackbox_service,
):
    await taxi_persey_proxy.invalidate_caches()
    handler = mock_remote()

    response = await request_post()

    assert handler.has_calls
    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
