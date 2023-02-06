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

ROUTE_RULES_401 = [
    {
        'input': {'http-path-prefix': '/cc/'},
        'proxy': {'auth': 'token', 'server-hosts': ['*'], 'proxy-401': True},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]

TOKEN = {
    'uid': '100',
    'scope': 'taxi-cc:all',
    'emails': [mock_blackbox.make_email('smth@drvrc.com')],
}
TOKEN_BAD_EMAIL = {
    'uid': '100',
    'scope': 'taxi-cc:all',
    'emails': [mock_blackbox.make_email('smth@example.com')],
}


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_token(
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
    assert response.json() == default_response


@pytest.mark.passport_token(token1=TOKEN_BAD_EMAIL)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_token_bad_email(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request(token='token1')

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_invalidtoken(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request(token='token1')

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_notoken(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request()

    assert not handler.has_calls
    assert response.status_code == 401


@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES_401)
async def test_proxy401(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        default_response,
        blackbox_service,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote()

    response = await cc_request()

    assert handler.has_calls
    assert response.status_code == 200
    assert response.json() == default_response


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
async def test_provider_headers(
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
    request_headers = handler.next_call()['request'].headers
    assert request_headers['X-Yandex-UID'] == '100'
    assert request_headers['X-Yandex-Login'] == 'login'
    assert request_headers['X-YaTaxi-Provider'] == 'yandex'
    assert request_headers['X-YaTaxi-ProviderUserId'] == '100'

    assert response.status_code == 200
    assert response.json() == default_response


URL_AUTH = 'cc/test2'


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
@pytest.mark.parametrize(
    ('response_code', 'response_body', 'expected_audit_request'),
    [
        pytest.param(
            200,
            {'a': 'b'},
            {
                'action': 'auth_action',
                'arguments': {
                    'data': '"123"',  # from DEFAULT_REQUEST
                    'request': {
                        'endpoint': '/' + URL_AUTH,
                        'service_name': 'mock',  # tvm-service from CONFIG
                    },
                    'response': {'a': 'b'},  # response_body
                },
                'login': '100',  # from TOKEN
                'object_id': 'b',  # from response_body
                'request_id': '122333',
                'system_name': 'cc-authproxy',  # from CC_AUTHPROXY_AUDIT_RULES
            },
            id='Audit - ok',
            marks=pytest.mark.config(
                CC_AUTHPROXY_AUDIT_RULES={
                    'enabled': True,
                    'rules': [
                        {
                            'path': '/' + URL_AUTH,
                            'method': 'POST',
                            'action': 'auth_action',
                            'object_id_retrieve_settings': {
                                'path': 'a',
                                'storage': 'response',
                            },
                        },
                    ],
                    'system_name': 'cc-authproxy',
                },
            ),
        ),
    ],
)
async def test_audit(
        mock_remote,
        mock_audit,
        cc_request,
        taxi_cc_authproxy,
        blackbox_service,
        response_code,
        response_body,
        expected_audit_request,
):
    audit_handler = mock_audit()
    remote_handler = mock_remote(
        url_path=URL_AUTH,
        response_code=response_code,
        response_body=response_body,
    )
    response = await cc_request(url_path=URL_AUTH, token='token1')

    assert remote_handler.has_calls
    assert response.status_code == response_code
    assert response.json() == response_body

    if expected_audit_request is not None:
        assert audit_handler.has_calls
        audit_request = audit_handler.next_call()['request'].json
        del audit_request['timestamp']
        assert audit_request == expected_audit_request
    else:
        assert not audit_handler.has_calls
