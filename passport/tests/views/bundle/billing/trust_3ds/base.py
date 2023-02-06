# -*- coding: utf-8 -*-
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth.faker import token_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_IP = '127.0.0.1'
TEST_UID = 123
TEST_HOST = 'yandex.ru'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID = '1234123412341234'
TEST_SESSIONID_VALUE = 'foo'
TEST_COOKIE = 'Session_id=%s;sessionid2=bar;yandexuid=%s' % (TEST_SESSIONID_VALUE, TEST_YANDEXUID)
TEST_RETPATH = 'https://www.yandex.ru'

TEST_CARD_ID = 'card-xxx'
TEST_SERVICE_TICKET = 'service-ticket'

TEST_AUTH_ID = '123:1422501443:126'
TEST_LOGIN_ID = 'login-id'
TEST_LOGIN = 'test-user'

TEST_ACCESS_TOKEN = 'access-token'

TEST_TRUST_BINDINGS_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5i+9gXgNJbAKus8ltkwf
Bi33a/KwVvxsiILsrtoY/OQo2MJqBJZs0zJABGGGfEnQ3W1BP16nFeRwnTLBOOH8
D6fGHqjSFkwI9b95YsbjPe58UcAUkhKj5j3+gVywTzKkvDtURrFIrF7FjQY8ucfH
gA49N1Dac/5r436dmDrnbUGNtxkCWW9mlvnbaWfN9kMf/xK7JzAzDbJz9myZNTAi
r+y97vVxrXFPbyo5EKbWrtXYMwYsu0yjJckeYcG4SkGD3xvjgJs16mbq6KJM5HMo
KRuBWVoJ61+RLHJJ5DhqiPKvMa7s+7i17kyrJu91ZfOWZ0WRFHJOAx3PfK/TgVbA
8wIDAQAB
-----END PUBLIC KEY-----
"""


@with_settings_hosts(
    TRUST_BINDINGS_URL='http://localhost/',
    TRUST_BINDINGS_RETRIES=1,
    TRUST_BINDINGS_TIMEOUT=1,
    TRUST_BINDINGS_PUBLIC_KEY=TEST_TRUST_BINDINGS_PUBLIC_KEY,
)
class BaseTrust3DSTestCase(BaseBundleTestViews):
    track_type = 'authorize'
    http_method = 'POST'
    http_headers = {
        'cookie': TEST_COOKIE,
        'user_agent': TEST_USER_AGENT,
        'host': TEST_HOST,
        'user_ip': TEST_IP,
    }
    http_query_args = {}
    mode = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'billing': ['trust_3ds']}))

        self.setup_blackbox_responses()
        self.env.oauth.set_response_value('_token', token_response(access_token=TEST_ACCESS_TOKEN))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        self.http_query_args.update(track_id=self.track_id)

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()

        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'payment_started',
            mode='3ds_start_payment',
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID,
            consumer='dev',
            uid=str(TEST_UID),
            track_id=self.track_id,
        )

    def assert_statbox_log(self, with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))
        entries.append(self.env.statbox.entry('payment_started', **kwargs))
        self.env.statbox.assert_equals(entries)

    def setup_blackbox_responses(self, alias=TEST_LOGIN, alias_type='portal', has_trusted_xtokens=False):
        bb_kwargs = {
            'uid': TEST_UID,
            'login': alias,
            'aliases': {alias_type: alias},
            'attributes': {},
            'dbfields': {},
        }

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**bb_kwargs),
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                authid=TEST_AUTH_ID,
                login_id=TEST_LOGIN_ID,
                **bb_kwargs
            ),
        )
