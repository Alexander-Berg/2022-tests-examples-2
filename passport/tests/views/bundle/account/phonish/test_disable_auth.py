# -*- coding: utf-8 -*-
from datetime import datetime

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_HOST,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_TYPE
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class AccountPhonishDisableAuthTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/account/phonish/disable_auth/'
    http_method = 'POST'
    consumer = 'dev'
    http_query_args = dict(
        uid=TEST_UID,
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        host=TEST_HOST,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'phonish': ['disable_auth'],
        }))
        self.setup_blackbox_response()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_blackbox_response(self, uid=TEST_UID, alias_type='phonish', enabled=True):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                enabled=enabled,
                aliases={alias_type: '_'},
                phones=[{
                    'id': TEST_PHONE_ID1,
                    'number': TEST_PHONE_NUMBER.e164,
                    'created': datetime.now(),
                    'confirmed': datetime.now(),
                    'bound': datetime.now(),
                }],
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

    def assert_historydb_ok(self, admin_name=None, comment=None):
        expected_log_entries = {
            'action': 'disable_phonish_auth',
            'consumer': 'dev',
            'info.glogout': TimeNow(),
            'phone.1.action': 'changed',
            'phone.1.number': TEST_PHONE_NUMBER.e164,
            'phone.1.confirmed': '1',
        }
        if admin_name and comment:
            expected_log_entries['admin'] = admin_name
            expected_log_entries['comment'] = comment
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_ok_with_admin_comment(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'admin': ['log_action'],
            'phonish': ['disable_auth'],
        }))

        rv = self.make_request(query_args=dict(admin_name='admin', comment='comment'))
        self.assert_ok_response(rv)
        self.assert_db_ok()
        self.assert_historydb_ok(admin_name='admin', comment='comment')

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
