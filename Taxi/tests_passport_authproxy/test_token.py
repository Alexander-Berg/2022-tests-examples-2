import pytest

from tests_passport_authproxy import router_rules
from tests_passport_authproxy import utils

REMOTE_PATH = '/pap/stories'

CONFIG = [
    router_rules.make_route_rule(REMOTE_PATH, required_scopes_alias='drive'),
]

YANDEX_UID = '100'
PASSPORT_SCOPE = 'taxi-drive:all'
TOKEN = {'uid': YANDEX_UID, 'scope': PASSPORT_SCOPE}
PASS_FLAGS = 'phonish,credentials=token-bearer'.split(',')


# apply to all tests by default
# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        PASSPORT_AUTHPROXY_PASSPORT_SCOPES_BY_ALIAS={
            'none': [],
            'drive': [PASSPORT_SCOPE],
            'alias-for-fail': ['this-scope-would-be-never-used:all'],
        },
    ),
]


@pytest.fixture(autouse=True)
def _mocks(blackbox_service):
    pass


# invalidate token cache before every test
@pytest.fixture(scope='function', autouse=True)
async def invalidate_caches(taxi_passport_authproxy):
    await taxi_passport_authproxy.invalidate_caches()


# begin tests
@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_happy_path(do_test_ok):
    remote_request = await do_test_ok(REMOTE_PATH, token='user_token')
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
@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_pass_flags(do_test_ok):
    remote_request = await do_test_ok(REMOTE_PATH, token='user_token')
    utils.assert_remote_headers(
        remote_request,
        YANDEX_UID,
        expected_pass_flags=PASS_FLAGS + ['cashback-plus'],
    )


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_no_route_for_url(perform_request, mock_remote):
    not_configured_path = '/some-bad-path'
    handler = mock_remote(not_configured_path)

    response = await perform_request(not_configured_path, token='user_token')

    assert not handler.has_calls
    assert response.status_code == 404
    response_data = response.json()
    assert response_data['message'] == 'No route for URL'


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(
    PASSPORT_AUTHPROXY_ROUTE_RULES=[
        router_rules.make_route_rule(REMOTE_PATH, 'missing'),
    ],
)
async def test_alias_is_not_found_in_config(do_test_fail):
    await do_test_fail(REMOTE_PATH, token='user_token', expected_code=500)


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(
    PASSPORT_AUTHPROXY_ROUTE_RULES=[
        router_rules.make_route_rule(REMOTE_PATH, 'alias-for-fail'),
    ],
)
async def test_wrong_scope(do_test_fail):
    await do_test_fail(REMOTE_PATH, token='user_token')


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_invalid_token(do_test_fail):
    await do_test_fail(REMOTE_PATH, token='bad_token')


@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_no_token(do_test_fail):
    await do_test_fail(REMOTE_PATH, token=None)


# NOTE: no passport_token
@pytest.mark.config(
    PASSPORT_AUTHPROXY_ROUTE_RULES=[
        router_rules.make_route_rule(
            REMOTE_PATH, 'drive', authorization_required=False,
        ),
    ],
)
async def test_proxy401(do_test_ok):
    remote_request = await do_test_ok(REMOTE_PATH, token=None)
    utils.assert_remote_headers(remote_request)


# NOTE: no passport_token
@pytest.mark.config(
    PASSPORT_AUTHPROXY_ROUTE_RULES=[
        router_rules.make_route_rule(
            REMOTE_PATH, 'none', authorization_required=False,
        ),
    ],
)
async def test_proxy401_with_empty_required_scopes(do_test_ok):
    remote_request = await do_test_ok(REMOTE_PATH, token=None)
    utils.assert_remote_headers(remote_request)


@pytest.mark.passport_token(user_token=TOKEN)
@pytest.mark.config(
    PASSPORT_AUTHPROXY_ROUTE_RULES=[
        router_rules.make_route_rule(REMOTE_PATH, 'none'),
    ],
)
async def test_empty_required_scopes_valid_token(do_test_ok):
    remote_request = await do_test_ok(REMOTE_PATH, token='user_token')
    utils.assert_remote_headers(remote_request, YANDEX_UID)
