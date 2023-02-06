import pytest

from tests_passport_authproxy import router_rules
from tests_passport_authproxy import utils

DATE = '2018-01-22T00:00:00Z'

URL_AUTH = '/pap/need-auth'
URL_NOAUTH = '/pap/no-auth'

CONFIG = [
    router_rules.make_route_rule(
        URL_AUTH, required_scopes_alias='none', authorization_required=True,
    ),
    router_rules.make_route_rule(
        URL_NOAUTH, required_scopes_alias='none', authorization_required=False,
    ),
]


# apply to all tests by default
# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        PASSPORT_AUTHPROXY_PASSPORT_SCOPES_BY_ALIAS={'none': []},
    ),
]


YANDEX_UID = '100'
SESSION = {'uid': YANDEX_UID}
PASS_FLAGS = 'phonish,credentials=session'.split(',')
SESSION_HEADERS = {'Cookie': 'Session_id=user_session; yandexuid=123'}
EMPTY_HEADERS = {'Cookie': 'yandexuid=123'}


@pytest.fixture(autouse=True)
def _mocks(blackbox_service):
    pass


# begin tests
@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.passport_session(user_session=SESSION)
async def test_session_ok(do_test_ok):
    remote_request = await do_test_ok(URL_AUTH, headers=SESSION_HEADERS)
    utils.assert_remote_headers(
        remote_request, YANDEX_UID, expected_pass_flags=PASS_FLAGS,
    )


@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_session_fail(do_test_fail):
    await do_test_fail(URL_AUTH, headers=SESSION_HEADERS)


@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_noauth_ok(do_test_ok):
    remote_request = await do_test_ok(URL_NOAUTH, headers=EMPTY_HEADERS)
    utils.assert_remote_headers(remote_request)


@pytest.mark.config(PASSPORT_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_noauth_fail(do_test_fail):
    await do_test_fail(URL_AUTH, headers=EMPTY_HEADERS)
