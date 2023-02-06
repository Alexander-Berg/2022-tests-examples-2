import pytest

from tests_cashback_authproxy import router_rules
from tests_cashback_authproxy import utils

REMOTE_PATH = '/4.0/cashback-int-api/v1/binding/create'

CONFIG = [
    router_rules.make_route_rule(
        REMOTE_PATH,
        required_scopes_alias='mango',
        auth_type='api-key-with-passport-token',
    ),
]

HEADERS = {
    'X-YaTaxi-API-Key': 'api_key',
    'X-YaTaxi-External-Service': 'mango',
    'X-Real-IP': '192.168.1.1',
}

YANDEX_UID = '100'
PASSPORT_SCOPE = 'yataxi:all'
TOKEN = {'uid': YANDEX_UID, 'scope': PASSPORT_SCOPE}
PASS_FLAGS = 'phonish,credentials=token-bearer'.split(',')


# apply to all tests by default
# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(CASHBACK_AUTHPROXY_PASSPORT_SCOPES=[PASSPORT_SCOPE]),
]


@pytest.fixture(autouse=True)
def _mocks(blackbox_service):
    pass


# invalidate token cache before every test
@pytest.fixture(scope='function', autouse=True)
async def invalidate_caches(taxi_cashback_authproxy):
    await taxi_cashback_authproxy.invalidate_caches()


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_auth_ok(do_test_ok, uapi_keys):
    remote_request = await do_test_ok(
        REMOTE_PATH, headers=HEADERS, token='user_token',
    )
    utils.assert_remote_headers(
        remote_request, YANDEX_UID, expected_pass_flags=PASS_FLAGS,
    )


@pytest.mark.passport_token(
    user_token={
        'uid': YANDEX_UID,
        'scope': PASSPORT_SCOPE,
        'has_plus_cashback': '1',
    },
)
@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_pass_flags(do_test_ok, uapi_keys):
    remote_request = await do_test_ok(
        REMOTE_PATH, token='user_token', headers=HEADERS,
    )
    utils.assert_remote_headers(
        remote_request,
        YANDEX_UID,
        expected_pass_flags=PASS_FLAGS + ['cashback-plus'],
    )


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_no_route_for_url(perform_request, mock_remote):
    not_configured_path = '/some-bad-path'
    handler = mock_remote(not_configured_path)

    response = await perform_request(
        not_configured_path, headers=HEADERS, token='user_token',
    )

    assert not handler.has_calls
    assert response.status_code == 404
    response_data = response.json()
    assert response_data['message'] == 'No route for URL'


@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_no_token(do_test_fail, uapi_keys):
    await do_test_fail(REMOTE_PATH, token=None, headers=HEADERS)


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(CASHBACK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_invalid_token(do_test_fail, uapi_keys):
    await do_test_fail(REMOTE_PATH, token='bad_token', headers=HEADERS)
