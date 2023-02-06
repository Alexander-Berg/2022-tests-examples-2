import pytest

from tests_cashback_authproxy import router_rules
from tests_cashback_authproxy import utils

REMOTE_PATH = '/4.0/cashback-int-api/v1/binding/create'

CONFIG = [
    router_rules.make_route_rule(
        REMOTE_PATH, required_scopes_alias='none', auth_type='api-key-only',
    ),
]

HEADERS = {
    'X-YaTaxi-API-Key': 'api_key',
    'X-YaTaxi-External-Service': 'mango',
    'X-Real-IP': '192.168.1.1',
}


@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_api_key_auth_ok(do_test_ok, uapi_keys):
    remote_request = await do_test_ok(REMOTE_PATH, headers=HEADERS)
    utils.assert_remote_headers(remote_request)


@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_api_key_auth_uapi_keys_400(do_test_fail, mockserver):
    @mockserver.handler('/uapi-keys/v2/authorization')
    def _mock_submit(request):
        return utils.ApiKeyResponse(400).make_response(mockserver)

    await do_test_fail(REMOTE_PATH, headers=HEADERS, expected_code=500)


@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_api_key_auth_uapi_keys_403(do_test_fail, mockserver):
    @mockserver.handler('/uapi-keys/v2/authorization')
    def _mock_submit(request):
        return utils.ApiKeyResponse(403).make_response(mockserver)

    await do_test_fail(REMOTE_PATH, headers=HEADERS, expected_code=401)


@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_api_key_auth_uapi_keys_500(do_test_fail, mockserver):
    @mockserver.handler('/uapi-keys/v2/authorization')
    def _mock_submit(request):
        return utils.ApiKeyResponse(500).make_response(mockserver)

    await do_test_fail(REMOTE_PATH, headers=HEADERS, expected_code=500)


@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_no_route_for_url(perform_request, mock_remote):
    not_configured_path = '/some-bad-path'
    handler = mock_remote(not_configured_path)

    response = await perform_request(not_configured_path, headers=HEADERS)

    assert not handler.has_calls
    assert response.status_code == 404
    response_data = response.json()
    assert response_data['message'] == 'No route for URL'
