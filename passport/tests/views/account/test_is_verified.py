# -*- coding: utf-8 -*-
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.base_test_data import *
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.models.account import Account


@with_settings_hosts()
class SetIsVerifiedViewTestCase(BaseViewTestCase):
    path = '/1/account/set_is_verified/'
    query_params = {
        'uid': TEST_UID,
        'is_verified': 'true',
    }

    def setUp(self):
        super(SetIsVerifiedViewTestCase, self).setUp()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))

        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            display_name=dict(name='display_name'),
        )
        self.env.blackbox.set_response_value('userinfo', userinfo)
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                userinfo,
            ),
        )
        self.env.db._serialize_to_eav(self.account)

    def check_db_entries(self, is_verified=True):
        if is_verified:
            self.env.db.check_db_attr(
                TEST_UID,
                'account.is_verified',
                '1',
            )
        else:
            self.env.db.check_db_attr_missing(
                TEST_UID,
                'account.is_verified',
            )
        if is_verified:
            self.env.db.check_db_attr(
                TEST_UID,
                'account.display_name',
                'p:%s' % self.account.person.display_name.public_name,
            )
        else:
            if self.account.person.display_name.name:
                self.env.db.check_db_attr(
                    TEST_UID,
                    'account.display_name',
                    'p:%s' % self.account.person.display_name.name,
                )
            else:
                self.env.db.check_db_attr_missing(
                    TEST_UID,
                    'account.display_name',
                )

    def check_historydb_entries(self, comment=None, is_verified=True):
        expected_entries = {
            'action': 'set_is_verified',
            'admin': 'admin',
            'user_agent': 'curl',
        }
        if comment:
            expected_entries['comment'] = comment
        expected_entries['info.is_verified'] = '1' if is_verified else '0'
        if is_verified and self.account.person.display_name.public_name != self.account.person.display_name.name:
            expected_entries['info.display_name'] = 'p:%s' % self.account.person.display_name.public_name
        self.assert_events_are_logged(
            self.env.event_handle_mock,
            expected_entries,
        )

    def test_ok(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries()

    def test_ok__flag_removed(self):
        snapshot = self.account.snapshot()
        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            display_name=dict(name='display_name'),
            attributes={
                'account.is_verified': '1',
            },
        )
        self.env.blackbox.set_response_value('userinfo', userinfo)
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                userinfo,
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, is_verified='false'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries(is_verified=False)
        self.check_historydb_entries(is_verified=False)

    def test_ok_with_comment(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, comment='some comment'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries(comment='some comment')

    def test_no_is_verified(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'uid': TEST_UID},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['is_verified.empty'])

    def test_no_uid(self):
        resp = self.make_request(
            method='POST',
            path=self.path,
            data={'is_verified': 'true'},
            headers=self.get_headers(),
        )
        self.check_response_error(resp, ['uid.empty'])

    def test_ok__display_name_was_empty(self):
        snapshot = self.account.snapshot()
        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            is_display_name_empty=True,
            public_name='public_name',
        )
        self.env.blackbox.set_response_value('userinfo', userinfo)
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                userinfo,
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request(
            method='POST',
            path=self.path,
            data=self.query_params,
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries()
        self.check_historydb_entries()

    def test_ok__display_name_was_empty__flag_removed(self):
        snapshot = self.account.snapshot()
        userinfo = blackbox_userinfo_response(
            uid=TEST_UID,
            is_display_name_empty=True,
            public_name='public_name',
        )
        self.env.blackbox.set_response_value('userinfo', userinfo)
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                userinfo,
            ),
        )
        self.env.db._serialize_to_eav(self.account, snapshot)

        resp = self.make_request(
            method='POST',
            path=self.path,
            data=dict(self.query_params, is_verified='false'),
            headers=self.get_headers(),
        )
        self.check_response_ok(resp)
        self.check_db_entries(is_verified=False)
        self.check_historydb_entries(is_verified=False)
