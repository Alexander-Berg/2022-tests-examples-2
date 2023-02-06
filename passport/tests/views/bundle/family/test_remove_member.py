# -*- coding: utf-8 -*-
from nose_parameterized import parameterized
from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_ID,
    TEST_FAMILY_ID1,
    TEST_HOST,
    TEST_UID,
    TEST_UID1,
    TEST_UID2,
    TEST_UID3,
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
class RemoveMemberViewTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/remove_member/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(RemoveMemberViewTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'remove_member',
                        'remove_member_by_uid',
                    ],
                },
            ),
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=False)

    def assert_statbox_ok(self, removed_uid=TEST_UID1, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(('check_cookies', {}))
        entries.append((
                'family_info_modification',
                dict(
                    family_id='%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(removed_uid),
                    new='-',
                    attribute='members.%s.uid' % removed_uid,
                    old=str(removed_uid),
                    operation='deleted',
                ),
            ),
        )
        self.assert_statboxes(entries)

    def assert_historydb_ok(self, removed_uid=TEST_UID1):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_remove_member',
                'uid': str(removed_uid),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'uid': str(removed_uid),
            },
        ]
        expected_events += self.base_historydb_events(removed_uid)

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_db_written(self, uids_remain=None, places_remain=None):
        if uids_remain is None:
            uids_remain = [TEST_UID]
        if places_remain is None:
            places_remain = range(len(uids_remain))
        assert len(places_remain) == len(uids_remain)
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
                'uid': uid,
                'place': place,
            } for uid, place in zip(uids_remain, places_remain)
        ])

    def assert_db_untouched(self, uids=None, places=None):
        if uids is None:
            uids = [TEST_UID, TEST_UID1]
        self.assert_db_written(uids_remain=uids, places_remain=places)

    @parameterized.expand(
        [
            # members, place, expected_uid, uids_remain, places_remain
            ([TEST_UID, TEST_UID1], 1, TEST_UID1, [TEST_UID], [0]),
            ([TEST_UID, TEST_UID1, TEST_UID2], 1, TEST_UID1, [TEST_UID, TEST_UID2], [0, 2]),
            ([TEST_UID, TEST_UID1, TEST_UID2], 2, TEST_UID2, [TEST_UID, TEST_UID1], [0, 1]),
            ([TEST_UID, TEST_UID1, TEST_UID2, TEST_UID3], 1, TEST_UID1, [TEST_UID, TEST_UID2, TEST_UID3], [0, 2, 3]),
            ([TEST_UID, TEST_UID1, TEST_UID2, TEST_UID3], 2, TEST_UID2, [TEST_UID, TEST_UID1, TEST_UID3], [0, 1, 3]),
            ([TEST_UID, TEST_UID1, TEST_UID2, TEST_UID3], 3, TEST_UID3, [TEST_UID, TEST_UID1, TEST_UID2], [0, 1, 2]),
        ]
    )
    def test_remove_by_place__ok(self, members, place, expected_uid, uids_remain, places_remain):
        self.setup_bb_response(has_family=True, family_members=members)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, members)
        place_id = '%s:%s' % (TEST_FAMILY_ID, place)
        resp = self.make_request(query_args={'place_id': place_id})
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok(removed_uid=expected_uid, with_check_cookies=True)
        self.assert_historydb_ok(removed_uid=expected_uid)
        self.assert_db_written(uids_remain=uids_remain, places_remain=places_remain)

    @parameterized.expand(
        [
            # members, remove_uid, uids_remain, places_remain
            ([TEST_UID, TEST_UID1], TEST_UID1, [TEST_UID], [0]),
            ([TEST_UID, TEST_UID1, TEST_UID2], TEST_UID1, [TEST_UID, TEST_UID2], [0, 2]),
            ([TEST_UID, TEST_UID1, TEST_UID2], TEST_UID2, [TEST_UID, TEST_UID1], [0, 1]),
            ([TEST_UID, TEST_UID1, TEST_UID2, TEST_UID3], TEST_UID1, [TEST_UID, TEST_UID2, TEST_UID3], [0, 2, 3]),
            ([TEST_UID, TEST_UID1, TEST_UID2, TEST_UID3], TEST_UID2, [TEST_UID, TEST_UID1, TEST_UID3], [0, 1, 3]),
            ([TEST_UID, TEST_UID1, TEST_UID2, TEST_UID3], TEST_UID3, [TEST_UID, TEST_UID1, TEST_UID2], [0, 1, 2]),
        ]
    )
    def test_remove_by_uid__ok(self, members, remove_uid, uids_remain, places_remain):
        self.setup_bb_response(has_family=True, family_members=members)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, members)
        resp = self.make_request(query_args={'member_uid': remove_uid})
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok(removed_uid=remove_uid, with_check_cookies=True)
        self.assert_historydb_ok(removed_uid=remove_uid)
        self.assert_db_written(uids_remain=uids_remain, places_remain=places_remain)

    def test_family_does_not_exist_error(self):
        self.setup_bb_response(has_family=False)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['family.does_not_exist'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_not_is_admin_error(self):
        self.setup_bb_response(has_family=True, own_family=False)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['family.not_is_admin'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_remove_himself_by_place_error(self):
        self.setup_bb_response(has_family=True, own_family=True)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'place_id': '%s:0' % TEST_FAMILY_ID})
        self.assert_error_response(resp, ['family.is_admin'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_remove_himself_by_uid_error(self):
        self.setup_bb_response(has_family=True, own_family=True)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'member_uid': TEST_UID})
        self.assert_error_response(resp, ['family.is_admin'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_remove_not_member_by_uid_error(self):
        self.setup_bb_response(has_family=True, own_family=True)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'member_uid': TEST_UID3})
        self.assert_error_response(resp, ['family.is_not_a_member'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_remove_child_by_uid_error(self):
        self.setup_bb_response(has_family=True, own_family=True, family_members=[TEST_UID1, TEST_UID])
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'member_uid': TEST_UID1})
        self.assert_error_response(resp, ['account.is_child'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_wrong_place_error(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID, TEST_UID1])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'place_id': '%s:2' % TEST_FAMILY_ID})
        self.assert_error_response(resp, ['family.invalid_place'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_wrong_family_id_error(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID, TEST_UID1])
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request(query_args={'place_id': '%s:1' % TEST_FAMILY_ID1})
        self.assert_error_response(resp, ['family.invalid_family'])
        self.assert_statbox_check_cookies()
        self.assert_historydb_empty()
        self.assert_db_untouched()

    def test_auth_by_uid__ok(self):
        members = [TEST_UID, TEST_UID1]
        remove_uid = TEST_UID1
        uids_remain = [TEST_UID]
        places_remain = [0]
        self.setup_bb_response(has_family=True, family_members=members)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_family_admin_response(has_family=True)),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, members)

        resp = self.make_request(
            exclude_headers=[
                'cookie',
                'host',
            ],
            query_args={'uid': TEST_UID, 'member_uid': remove_uid},
        )
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok(removed_uid=remove_uid)
        self.assert_historydb_ok(removed_uid=remove_uid)
        self.assert_db_written(uids_remain=uids_remain, places_remain=places_remain)
