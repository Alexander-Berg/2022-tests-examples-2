# -*- coding: utf-8 -*-
from datetime import datetime

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_ID,
    TEST_FAMILY_ID1,
    TEST_HOST,
    TEST_UID,
    TEST_UID1,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


class DeleteChildViewTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/delete_child/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )
    http_query_args = dict(
        child_uid=TEST_UID1,
    )

    def setUp(self):
        super(DeleteChildViewTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'delete_child',
                        'delete_child_by_uid',
                    ],
                },
            ),
        )

    def setup_statbox_templates(self):
        super(DeleteChildViewTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'disabled_status',
            _inherit_from='account_modification',
            entity='account.disabled_status',
            old='enabled',
            new='disabled_on_deletion',
            operation='updated',
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'global_logout',
            _inherit_from='account_modification',
            entity='account.global_logout_datetime',
            operation='updated',
            old=str(datetime.fromtimestamp(1)),
            new=DatetimeNow(convert_to_datetime=True),
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'last_child_family',
            _inherit_from='account_modification',
            entity='account.last_child_family',
            operation='created',
            old='-',
            new=TEST_FAMILY_ID,
            uid=str(TEST_UID1),
        )

    def assert_statbox_ok(self, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry('global_logout'),
            self.env.statbox.entry('disabled_status'),
            self.env.statbox.entry('last_child_family'),
            self.env.statbox.entry(
                'family_info_modification',
                family_id='%s' % str(TEST_FAMILY_ID),
                entity='members',
                entity_id=str(TEST_UID1),
                old=str(TEST_UID1),
                attribute='members.%s.uid' % TEST_UID1,
                new='-',
                operation='deleted',
            ),
        ])
        self.env.statbox.assert_equals(entries)

    def asset_family_logger_ok(self):
        self.env.family_logger.assert_equals([
            self.env.family_logger.entry(
                'family_info_modification',
                family_id='%s' % str(TEST_FAMILY_ID),
                entity='members',
                entity_id=str(TEST_UID1),
                old=str(TEST_UID1),
                attribute='members.%s.uid' % TEST_UID1,
                new='-',
                operation='deleted',
            ),
        ])

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'account_delete',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'action',
                'value': 'family_member_account_delete',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'account.last_child_family',
                'value': TEST_FAMILY_ID,
                'uid': str(TEST_UID1),
            },
            {
                'name': 'info.glogout',
                'value': TimeNow(),
                'uid': str(TEST_UID1),
            },
            {
                'name': 'info.disabled_status',
                'value': str(ACCOUNT_DISABLED_ON_DELETION),
                'uid': str(TEST_UID1),
            },
            {
                'name': 'info.ena',
                'value': '0',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'deletion_operation',
                'value': 'created',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'uid': str(TEST_UID1),
            },
        ]

        # 2 раза потому что вызывается 2 апдейта на разные сущности (один на семью, второй на аккаунт)
        expected_events += self.base_historydb_events(TEST_UID1) * 2

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_db_written(self):
        self.env.db.check_table_contents('family_info', 'passportdbcentral', [
            {
                'family_id': 1,
                'admin_uid': TEST_UID,
                'meta': '',
            },
        ])
        self.env.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': 1,
                'uid': TEST_UID,
                'place': 0,
            },
        ])
        del_ops = self.env.db.select('account_deletion_operations', uid=TEST_UID1, db='passportdbshard1')
        self.assertEqual(len(del_ops), 1)
        self.assertEqual(del_ops[0]['started_at'], DatetimeNow())

        self.env.db.check_db_attr(TEST_UID1, 'account.is_disabled', str(ACCOUNT_DISABLED_ON_DELETION))
        self.env.db.check_db_attr(TEST_UID1, 'account.last_child_family', TEST_FAMILY_ID)

    def test_ok(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()
        self.assert_db_written()

    def test_delete_not_a_family_member_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.set_other_userinfo_bb_response(with_family=False, is_child=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.is_not_a_member'])

    def test_delete_another_family_member_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID])
        self.set_other_userinfo_bb_response(with_family=True, is_child=True, family_id=TEST_FAMILY_ID1)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.is_not_a_member'])

    def test_not_is_admin_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1], own_family=False)
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.not_is_admin'])

    def test_not_is_child_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.set_other_userinfo_bb_response(with_family=True, is_child=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_child_want_delete_child_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1], is_child=True)
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
