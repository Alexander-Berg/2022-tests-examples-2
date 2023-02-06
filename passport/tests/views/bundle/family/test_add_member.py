# -*- coding: utf-8 -*-
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
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class AddMemberViewTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/add_member/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(AddMemberViewTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'add_member',
                        'add_member_by_uid',
                    ],
                },
            ),
        )

    def assert_statbox_ok(self, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(('check_cookies', {}))
        entries.append(
            (
                'family_info_modification',
                dict(
                    family_id='%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(TEST_UID1),
                    old='-',
                    attribute='members.%s.uid' % TEST_UID1,
                    new=str(TEST_UID1),
                    operation='created',
                ),
            ),
        )
        self.assert_statboxes(entries)

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_add_member',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID1),
                'uid': str(TEST_UID1),
            },
        ]
        expected_events += self.base_historydb_events(TEST_UID1)

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
            {
                'family_id': 1,
                'uid': TEST_UID1,
                'place': 1,
            },
        ])

    def test_add_ok(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID])
        self.set_other_userinfo_bb_response(with_family=False)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID])
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()
        self.assert_db_written()

    def test_family_does_not_exist_error(self):
        self.setup_bb_response(has_family=False)
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['family.does_not_exist'])

    def test_not_is_admin_error(self):
        self.setup_bb_response(
            has_family=True, own_family=False)
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['family.not_is_admin'])

    def test_add_himself_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.set_other_userinfo_bb_response(with_family=True)
        resp = self.make_request(query_args={'member_uid': TEST_UID})
        self.assert_error_response(resp, ['family.is_member_this'])

    def test_already_is_member_this_error(self):
        self.setup_bb_response(
            has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.set_other_userinfo_bb_response(with_family=True)
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['family.is_member_this'])

    def test_already_is_member_other_error(self):
        self.setup_bb_response(
            has_family=True, different_family_id_info=True)
        self.set_other_userinfo_bb_response(with_family=True, family_id=TEST_FAMILY_ID1)
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['family.is_member_other'])

    def test_uid_ok(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID])
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(**self.build_blackbox_family_admin_response(has_family=True)),
                blackbox_userinfo_response(**self.build_blackbox_other_userinfo_response(with_family=False)),
            ],
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID])
        resp = self.make_request(
            exclude_headers=[
                'cookie',
                'host',
            ],
            query_args={'uid': TEST_UID, 'member_uid': TEST_UID1},
        )
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok()
        self.assert_historydb_ok()
        self.assert_db_written()
