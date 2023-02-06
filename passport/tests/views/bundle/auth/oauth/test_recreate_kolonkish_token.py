# -*- coding: utf-8 -*-
from nose.tools import ok_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_error_response,
    oauth_bundle_successful_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_KOLONKA_CLIENT_ID = 'id'
TEST_KOLONKA_CLIENT_SECRET = 'secret'

TEST_LOGIN = 'kolonkish-123'

TEST_CREATOR_UID = TEST_UID * 2
TEST_CREATOR_LOGIN = 'vasya.pupkin'


TEST_DEVICE_ID = 'device-id'
TEST_DEVICE_NAME = 'device-name'

TEST_CODE = 'code' * 4
TEST_SCOPE = 'kolonka:scope'


@with_settings_hosts(
    OAUTH_URL='http://oauth.localhost',
    OAUTH_KOLONKA_KOLONKISH_SCOPE=TEST_SCOPE,
    OAUTH_KOLONKA_CODE_TTL=600,
    OAUTH_APPLICATION_KOLONKA={
        'client_id': TEST_KOLONKA_CLIENT_ID,
        'client_secret': TEST_KOLONKA_CLIENT_SECRET,
    },
)
class RecreateKolonkishTokenTestCase(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/auth/oauth/recreate_kolonkish_token/'
    http_method = 'POST'
    http_query_args = {
        'uid': TEST_UID,
        'device_id': TEST_DEVICE_ID,
        'device_name': TEST_DEVICE_NAME,
    }
    http_headers = {
        'user_ip': TEST_IP,
        'authorization': TEST_AUTH_HEADER,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_oauth': ['recreate_kolonkish_token']}),
        )
        self.setup_statbox_templates()
        self.setup_blackbox_response()
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(code=TEST_CODE, expires_in=600),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_CREATOR_UID, login=TEST_CREATOR_LOGIN, scope=TEST_SCOPE),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_CREATOR_UID, login=TEST_CREATOR_LOGIN),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_response(self, alias_type='kolonkish', creator_uid=TEST_CREATOR_UID):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    alias_type: TEST_LOGIN,
                },
                attributes={
                    'account.creator_uid': str(creator_uid),
                },
            ),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='recreate_kolonkish_token',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'account_glogout',
            _inherit_from='local_base',
            _exclude=['mode'],
            event='account_modification',
            uid=str(TEST_UID),
            consumer='dev',
            ip=TEST_IP,
            user_agent='-',
            operation='updated',
            entity='account.global_logout_datetime',
            new=DatetimeNow(convert_to_datetime=True),
            old=TEST_GLOBAL_LOGOUT_DATETIME,
        )
        self.env.statbox.bind_entry(
            'oauth_code_issued',
            _inherit_from='local_base',
            action='oauth_code_issued',
            uid=str(TEST_UID),
            client_id=TEST_KOLONKA_CLIENT_ID,
        )

    def assert_oauth_not_called(self):
        ok_(not self.env.oauth.requests)

    def assert_oauth_called(self, with_extra_params=True):
        expected_post = {
            'consumer': 'passport',
            'code_strength': 'long',
            'ttl': 600,
            'require_activation': '0',
            'uid': str(TEST_UID),
            'by_uid': '1',
            'client_id': TEST_KOLONKA_CLIENT_ID,
            'client_secret': TEST_KOLONKA_CLIENT_SECRET,
        }
        expected_query = {'user_ip': TEST_IP}
        if with_extra_params:
            expected_query['device_id'] = TEST_DEVICE_ID
            expected_query['device_name'] = TEST_DEVICE_NAME

        self.env.oauth.requests[0].assert_post_data_equals(expected_post)
        self.env.oauth.requests[0].assert_query_equals(expected_query)

    def assert_historydb_empty(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_historydb_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'info.glogout': TimeNow(),
                'action': 'recreate_kolonkish_token',
                'consumer': 'dev',
            },
        )

    def assert_statbox_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_statbox_ok(self, token_created=True, with_extra_params=True, with_check_cookies=False):
        events = []
        if with_check_cookies:
            events.append(self.env.statbox.entry('check_cookies'))
        events.append(self.env.statbox.entry('account_glogout'))
        if token_created:
            if with_extra_params:
                events.append(
                    self.env.statbox.entry(
                        'oauth_code_issued',
                        device_id=TEST_DEVICE_ID,
                        device_name=TEST_DEVICE_NAME,
                    ),
                )
            else:
                events.append(
                    self.env.statbox.entry('oauth_code_issued'),
                )
        self.env.statbox.assert_has_written(events)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, code=TEST_CODE)
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

    def test_ok_with_cookie(self):
        rv = self.make_request(
            exclude_headers=['authorization'],
            headers={'cookie': 'Session_id=foo;', 'host': TEST_HOST},
        )
        self.assert_ok_response(rv, code=TEST_CODE)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_oauth_called()

    def test_kolonkish_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['account.not_found'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()

    def test_invalid_account_type(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_CREATOR_UID,
                login=TEST_CREATOR_LOGIN,
                scope=TEST_SCOPE,
                aliases={
                    'phonish': 'phne-123',
                },
            ),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()

    def test_kolonkish_disabled(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(enabled=False),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['account.disabled'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()

    def test_ok_no_device_id_and_name(self):
        rv = self.make_request(
            exclude_args=[
                'device_id',
                'device_name',
            ],
        )
        self.assert_ok_response(rv, code=TEST_CODE)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_extra_params=False)
        self.assert_oauth_called(with_extra_params=False)

    def test_not_kolonkish(self):
        self.setup_blackbox_response(alias_type='pdd')

        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()

    def test_oauth_failed(self):
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_error_response('backend.failed'),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['backend.oauth_failed'])
        self.assert_historydb_ok()
        self.assert_statbox_ok(token_created=False)
        self.assert_oauth_called()

    def test_uid_mismatch(self):
        self.setup_blackbox_response(creator_uid=TEST_CREATOR_UID * 2)
        rv = self.make_request()
        self.assert_error_response(rv, ['account.uid_mismatch'])
