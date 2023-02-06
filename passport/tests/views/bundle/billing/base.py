# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.billing import BaseBillingError
from passport.backend.core.builders.billing.faker.billing import FakeBillingXMLRPC
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_multi_response
from passport.backend.core.test.consts import TEST_LOGIN1
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import remove_none_values


TEST_IP = '127.0.0.1'
TEST_UID = 123
TEST_HOST = 'yandex.ru'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID = '1234123412341234'
TEST_SESSIONID_VALUE = 'foo'
TEST_COOKIE = 'Session_id=%s;sessionid2=bar;yandexuid=%s' % (TEST_SESSIONID_VALUE, TEST_YANDEXUID)
TEST_TOKEN = 'billing_token'
TEST_CARD_ID = '1'


@with_settings_hosts(
    BILLING_XMLRPC_URL='http://yandex.ru',
    BILLING_XMLRPC_RETRIES=2,
    BILLING_XMLRPC_TIMEOUT=1,
    BILLING_TOKEN=TEST_TOKEN,
)
class BaseBillingTestCase(BaseBundleTestViews):
    track_type = 'authorize'
    http_method = 'POST'
    http_headers = {
        'cookie': TEST_COOKIE,
        'user_agent': TEST_USER_AGENT,
        'host': TEST_HOST,
        'user_ip': TEST_IP,
    }
    billing_method = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'billing': [self.billing_method],
        }))
        self.fake_billing = FakeBillingXMLRPC()
        self.fake_billing.start()

        self.userinfo = dict(
            crypt_password='1:something',
            login=TEST_LOGIN1,
            uid=TEST_UID,
        )
        self.setup_blackbox()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        self.http_query_args = {
            'track_id': self.track_id,
        }
        self.setup_statbox_templates()

    def tearDown(self):
        self.fake_billing.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.fake_billing

    def setup_blackbox(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**self.userinfo),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'billing_called',
            mode='billing',
            method=self.billing_method,
            action='called',
            ip=TEST_IP,
            host=TEST_HOST,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID,
            consumer='dev',
            uid=str(TEST_UID),
        )

    def assert_statbox_log(self, with_check_cookies=False, **kwargs):
        kwargs = remove_none_values(kwargs)
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies', host='yandex.ru'))
        entries.append(self.env.statbox.entry('billing_called', **kwargs))
        self.env.statbox.assert_equals(entries)


class CommonBillingBundleTests(object):
    def test_session_invalid(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_billing_fails(self):
        self.fake_billing.set_response_side_effect(self.billing_method, BaseBillingError)

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['backend.billing_failed'],
        )

    def test_ok_without_password(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )

    def test_ok_with_password_verification_required(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                crypt_password='1:something',
                age=100500,
            ),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            billing_response=self.parsed_billing_response,
        )
