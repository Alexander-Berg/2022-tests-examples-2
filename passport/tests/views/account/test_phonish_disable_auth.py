# -*- coding: utf-8 -*-
from datetime import datetime

from nose.tools import eq_
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_TYPE
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts()
class AccountPhonishDisableAuthTestCase(BaseViewTestCase):
    path = '/1/account/phonish/disable_auth/'
    query_params = dict(
        uid=TEST_UID,
    )

    def setUp(self):
        super(AccountPhonishDisableAuthTestCase, self).setUp()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
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

    def assert_historydb_ok(self, comment=None):
        expected_log_entries = {
            'action': 'disable_phonish_auth',
            'info.glogout': TimeNow(),
            'phone.1.action': 'changed',
            'phone.1.number': TEST_PHONE_NUMBER.e164,
            'phone.1.confirmed': '1',
            'admin': 'admin',
            'user_agent': 'curl',
        }
        if comment:
            expected_log_entries['comment'] = comment
        self.assert_events_are_logged(self.env.event_handle_mock, expected_log_entries)

    def test_ok(self):
        rv = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(rv)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_ok_with_comment(self):
        rv = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, comment='comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(rv)
        self.assert_db_ok()
        self.assert_historydb_ok(comment='comment')

    def test_ok_for_disabled_account(self):
        self.setup_blackbox_response(enabled=False)

        rv = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(rv)
        self.assert_db_ok()
        self.assert_historydb_ok()

    def test_account_not_found_error(self):
        self.setup_blackbox_response(uid=None)

        rv = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_error(rv, ['account.not_found'])

    def test_account_invalid_type_error(self):
        self.setup_blackbox_response(alias_type='mailish')

        rv = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_error(rv, ['account.invalid_type'])

    def test_no_uid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])
