# -*- coding: utf-8 -*-
from nose.tools import ok_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.oauth.faker import token_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_TOKEN = 'a68d97976a66444496148b694802b009'
TEST_YAMBOT_CLIENT_ID = 'id'
TEST_YAMBOT_CLIENT_SECRET = 'secret'


@with_settings_hosts(
    OAUTH_URL='http://oauth.localhost',
    OAUTH_APPLICATION_YAMB={
        'client_id': TEST_YAMBOT_CLIENT_ID,
        'client_secret': TEST_YAMBOT_CLIENT_SECRET,
    },
)
class RecreateYambotTokenTestCase(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/auth/oauth/recreate_yambot_token/'
    http_method = 'POST'
    http_query_args = {
        'uid': TEST_UID,
    }
    http_headers = {
        'user_ip': TEST_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_oauth': ['recreate_yambot_token']}),
        )
        self.setup_statbox_templates()
        self.setup_blackbox_response()
        self.env.oauth.set_response_value(
            '_token',
            token_response(TEST_TOKEN),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_response(self, aliases=None):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases=aliases or {'yambot': TEST_LOGIN},
            ),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='recreate_yambot_token',
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
            'token_created',
            _inherit_from='local_base',
            action='token_created',
            client_id=TEST_YAMBOT_CLIENT_ID,
        )

    def assert_oauth_not_called(self):
        ok_(not self.env.oauth.requests)

    def assert_oauth_called(self):
        request = self.env.oauth.get_requests_by_method('_token')[0]
        request.assert_post_data_contains(
            {
                'client_id': TEST_YAMBOT_CLIENT_ID,
                'client_secret': TEST_YAMBOT_CLIENT_SECRET,
                'grant_type': 'passport_assertion',
                'assertion': TEST_UID,
                'password_passed': False,
            },
        )
        request.assert_query_equals(
            {
                'user_ip': TEST_IP,
            },
        )

    def assert_historydb_empty(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_historydb_ok(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            {
                'info.glogout': TimeNow(),
                'action': 'recreate_yambot_token',
                'consumer': 'dev',
            },
        )

    def assert_statbox_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_statbox_ok(self, token_created=True):
        events = [
            self.env.statbox.entry('account_glogout'),
        ]
        if token_created:
            events.append(
                self.env.statbox.entry('token_created'),
            )
        self.env.statbox.assert_has_written(events)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, oauth_token=TEST_TOKEN)
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

    def test_pdd_with_yambot_alias(self):
        self.setup_blackbox_response(aliases={'pdd': TEST_LOGIN, 'yambot': TEST_LOGIN})

        rv = self.make_request()
        self.assert_ok_response(rv, oauth_token=TEST_TOKEN)
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_oauth_called()

    def test_no_yambot_alias(self):
        self.setup_blackbox_response(aliases={'pdd': TEST_LOGIN})

        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_oauth_not_called()

    def test_oauth_failed(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'error': 'invalid_grant',
                'error_description': 'User does not exist',
            },
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['backend.oauth_failed'])
        self.assert_historydb_ok()
        self.assert_statbox_ok(token_created=False)
        self.assert_oauth_called()
