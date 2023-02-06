# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyInviteTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_EMAIL,
    TEST_FAMILY_ID,
    TEST_FAMILY_ID1,
    TEST_FAMILY_INVITE_ID,
    TEST_HOST,
    TEST_UID,
    TEST_UID1,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.types.email.email import mask_email_for_statbox


TEST_STATBOX_EMAIL = mask_email_for_statbox(TEST_EMAIL)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class RevokeInviteTestCase(BaseFamilyInviteTestcase):
    default_url = '/1/bundle/family/revoke_invite/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(RevokeInviteTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': ['revoke_invite'],
                },
            ),
        )
        self.env.statbox.bind_entry(
            'family_revoke_invite',
            consumer='dev',
            action='family_revoke_invite',
            ip='1.2.3.4',
            user_agent='curl',
            mode='family',
        )

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_revoke_invite',
                'uid': str(TEST_UID),
            },
            {
                'name': 'contact',
                'value': TEST_EMAIL,
                'uid': str(TEST_UID),
            },
            {
                'name': 'family_id',
                'value': TEST_FAMILY_ID,
                'uid': str(TEST_UID),
            },
            {
                'name': 'invite_id',
                'value': TEST_FAMILY_INVITE_ID,
                'uid': str(TEST_UID),
            },
            {
                'name': 'send_method',
                'value': 'email',
                'uid': str(TEST_UID),
            },
            {
                'name': 'user_agent',
                'value': 'curl',
                'uid': str(TEST_UID),
            },
            {
                'name': 'consumer',
                'value': 'dev',
                'uid': str(TEST_UID),
            },
        ]

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_statbox_ok(self, send_method='email', contact=TEST_STATBOX_EMAIL, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry(
                'family_revoke_invite',
                uid=str(TEST_UID),
                family_id=TEST_FAMILY_ID,
                invite_id=TEST_FAMILY_INVITE_ID,
                send_method=send_method,
                contact=contact,
            ),
        )
        self.env.statbox.assert_has_written(entries)

    def test_revoke_ok(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.setup_ydb(self.build_ydb_invite() + self.build_ydb_empty(False))

        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_ok_response(resp)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_ydb_exec(self.build_ydb_select() + self.build_ydb_delete())

    def test_family_does_not_exist_error(self):
        self.setup_bb_response(has_family=False)
        self.setup_ydb(self.build_ydb_invite() + self.build_ydb_empty(False))
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.does_not_exist'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec([])

    def test_not_is_admin_error(self):
        self.setup_bb_response(has_family=True, own_family=False)
        self.setup_ydb(self.build_ydb_invite() + self.build_ydb_empty(False))
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.not_is_admin'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec([])

    def test_invite_not_found_error(self):
        self.setup_bb_response(has_family=True, own_family=True)
        self.setup_ydb(self.build_ydb_empty())
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.invalid_invite'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec(self.build_ydb_select())

    def test_invite_other_family_error(self):
        self.setup_bb_response(has_family=True, own_family=True)
        self.setup_ydb(self.build_ydb_invite(family_id=TEST_FAMILY_ID1) + self.build_ydb_empty())
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.invalid_invite'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_ydb_exec(self.build_ydb_select())
