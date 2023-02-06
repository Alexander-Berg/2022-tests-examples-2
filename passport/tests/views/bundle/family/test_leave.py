# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_ID,
    TEST_HOST,
    TEST_UID,
    TEST_UID1,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants


class LeaveViewTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/leave/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(LeaveViewTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'leave',
                        'leave_by_uid',
                    ],
                },
            ),
        )

    def assert_statbox_ok(self, remove_manage_child=False, with_check_cookies=False):
        lines = []
        if with_check_cookies:
            lines.append(self.env.statbox.entry('check_cookies'))

        if remove_manage_child:
            lines.append(
                self.env.statbox.entry(
                    'account_modification',
                    **{
                        'old': str(TEST_UID),
                        'entity': 'account.can_manage_children',
                        'new': '0',
                        'operation': 'updated',
                    })
            )
        lines.append(
            self.env.statbox.entry(
                'family_info_modification',
                **{
                    'entity_id': str(TEST_UID),
                    'old': str(TEST_UID),
                    'attribute': 'members.{}.uid'.format(TEST_UID),
                    'entity': 'members',
                    'family_id': TEST_FAMILY_ID,
                    'new': '-',
                    'operation': 'deleted',
                }
            )
        )
        self.env.statbox.assert_has_written(lines)

    def assert_historydb_ok(self, remove_manage_child=False):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_leave',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'uid': str(TEST_UID),
            },
        ]
        if remove_manage_child:
            remove_manage_child_events = [
                {
                    'name': 'account.can_manage_children',
                    'value': '0',
                    'uid': str(TEST_UID),
                },
                {
                    'name': 'action',
                    'value': 'family_leave',
                    'uid': str(TEST_UID),
                },
            ]
            remove_manage_child_events += self.base_historydb_events(TEST_UID)
            expected_events += remove_manage_child_events

        expected_events += self.base_historydb_events(TEST_UID)

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_db_written(self):
        self.env.db.check_table_contents('family_info', 'passportdbcentral', [
            {
                'family_id': 1,
                'admin_uid': TEST_UID1,
                'meta': '',
            },
        ])
        self.env.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': 1,
                'uid': TEST_UID1,
                'place': 0,
            },
        ])
        self.env.db.check_table_contents('attributes', 'passportdbshard1', [])

    def test_leave_ok(self):
        self.setup_bb_response(has_family=True, own_family=False, family_members=[TEST_UID1, TEST_UID])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID])
        resp = self.make_request()
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()
        self.assert_db_written()

    def test_leave_with_child_manage_ok(self):
        self.setup_bb_response(has_family=True, own_family=False, can_manage_children=True,
                               family_members=[TEST_UID1, TEST_UID])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID])
        self._attribute_to_db(TEST_UID, [225], ['1'])
        resp = self.make_request()
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_db_written()
        self.assert_statbox_ok(remove_manage_child=True, with_check_cookies=True)
        self.assert_historydb_ok(remove_manage_child=True)

    def test_family_does_not_exist_error(self):
        self.setup_bb_response(has_family=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.does_not_exist'])

    def test_is_admin_error(self):
        self.setup_bb_response(has_family=True, own_family=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.is_admin'])

    def test_is_child_error(self):
        self.setup_bb_response(has_family=True, own_family=False, is_child=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.is_child'])

    def test_auth_by_uid__ok(self):
        self.setup_bb_response(has_family=True, own_family=False, family_members=[TEST_UID1, TEST_UID])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID])
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **self.build_blackbox_userinfo_response(with_family=True, family_admin_uid=TEST_UID1)),
        )

        resp = self.make_request(
            query_args=dict(uid=TEST_UID),
            exclude_headers=[
                'cookie',
                'host',
            ],
        )
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok()
        self.assert_historydb_ok()
        self.assert_db_written()
