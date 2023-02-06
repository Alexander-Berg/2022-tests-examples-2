# -*- coding: utf-8 -*-
from datetime import datetime

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_OAUTH_SCOPE,
    TEST_OAUTH_TOKEN,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_TYPE
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class AccountPhonishDisableAuthByXTokenTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/account/phonish/disable_auth_by_xtoken/'
    http_method = 'POST'
    consumer = 'dev'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
        authorization='OAuth %s' % TEST_OAUTH_TOKEN,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'phonish': ['disable_auth_by_xtoken']}),
        )
        self.setup_blackbox_response()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_response(
        self,
        uid=TEST_UID,
        alias_type='phonish',
        enabled=True,
    ):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=uid,
                enabled=enabled,
                aliases={alias_type: '_'},
                phones=[
                    {
                        'id': TEST_PHONE_ID1,
                        'number': TEST_PHONE_NUMBER.e164,
                        'created': datetime.now(),
                        'confirmed': datetime.now(),
                        'bound': datetime.now(),
                    },
                ],
                scope=TEST_OAUTH_SCOPE,
            ),
        )

    def assert_db_ok(self):
        eq_(self.env.db.query_count('passportdbcentral'), 0)
        eq_(self.env.db.query_count('passportdbshard1'), 2)

        self.env.db.check(
            'attributes',
            'account.global_logout_datetime',
            TimeNow(),
            uid=TEST_UID,
            db='passportdbshard1',
        )
        self.env.db.check(
            'extended_attributes',
            'confirmed',
            '1',
            uid=TEST_UID,
            entity_id=TEST_PHONE_ID1,
            entity_type=EXTENDED_ATTRIBUTES_PHONE_TYPE,
            db='passportdbshard1',
        )

    def assert_historydb_ok(self):
        expected_log_entries = {
            'action': 'disable_phonish_auth_by_xtoken',
            'consumer': 'dev',
            'info.glogout': TimeNow(),
            'phone.1.action': 'changed',
            'phone.1.number': TEST_PHONE_NUMBER.e164,
            'phone.1.confirmed': '1',
        }
        self.assert_events_are_logged(
            self.env.handle_mock, expected_log_entries,
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_ok_for_disabled_account(self):
        self.setup_blackbox_response(enabled=False)

        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_account_not_found_error(self):
        self.setup_blackbox_response(uid=None)

        rv = self.make_request()
        self.assert_error_response(rv, ['account.not_found'])

    def test_account_invalid_type_error(self):
        self.setup_blackbox_response(alias_type='mailish')

        rv = self.make_request()
        self.assert_error_response(rv, ['account.invalid_type'])
