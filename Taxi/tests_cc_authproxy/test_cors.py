# pylint: disable=import-error
import pytest

from client_blackbox import mock_blackbox  # noqa: F403 F401, I100, I202


ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/cc/'},
        'proxy': {'auth': 'token', 'server-hosts': ['*']},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]
TOKEN = {
    'uid': '100',
    'scope': 'taxi-cc:all',
    'emails': [mock_blackbox.make_email('smth@drvrc.com')],
}
CORS = {
    'allowed-origins': ['localhost', 'example.com'],
    'allowed-headers': ['a', 'b'],
    'exposed-headers': ['c', 'd'],
    'cache-max-age-seconds': 66,
}


def validate_cors_headers(response):
    origin = response.headers['Access-Control-Allow-Origin']
    assert origin == 'localhost'
    assert response.headers['Access-Control-Allow-Headers'] == 'a, b'
    assert response.headers['Access-Control-Expose-Headers'] == 'c, d'
    methods = set(response.headers['Access-Control-Allow-Methods'].split(', '))
    assert methods == set(
        ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'],
    )
    assert response.headers['Access-Control-Max-Age'] == '66'


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES, CC_AUTHPROXY_CORS=CORS,
)
async def test_cors(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request(token='token1')

    assert handler.has_calls
    assert response.status_code == 200
    validate_cors_headers(response)


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_cors_other_origin(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request(
        token='token1', headers={'Origin': 'example.com'},
    )

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_cors_no_origin(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request(token='token1', headers={'Origin': None})

    assert handler.has_calls
    assert response.status_code == 200
    assert 'Access-Control-Allow-Origin' not in response.headers


@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES, CC_AUTHPROXY_CORS=CORS,
)
async def test_cors_options(
        taxi_cc_authproxy, mock_remote, default_url, blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    # No token is passed
    response = await taxi_cc_authproxy.options(
        default_url, headers={'origin': 'localhost'},
    )

    assert not handler.has_calls
    assert response.status_code == 204
    validate_cors_headers(response)
