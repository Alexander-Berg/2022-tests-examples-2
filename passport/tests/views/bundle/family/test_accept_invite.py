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
    TEST_UID2,
    TEST_UID3,
    TEST_UID4,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.types.email.email import mask_email_for_statbox


TEST_EMAIL_MASKED_STATBOX = mask_email_for_statbox(TEST_EMAIL)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class AcceptInviteTestCase(BaseFamilyInviteTestcase):
    default_url = '/1/bundle/family/accept_invite/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(AcceptInviteTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'accept_invite',
                        'accept_invite_by_uid',
                    ],
                },
            ),
        )
        self.env.statbox.bind_entry(
            'family_accept_invite',
            consumer='dev',
            action='family_accept_invite',
            ip='1.2.3.4',
            user_agent='curl',
            mode='family',
        )

    def assert_statbox_ok(self, send_method='email', contact=TEST_EMAIL_MASKED_STATBOX, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'family_info_modification',
                family_id=TEST_FAMILY_ID,
                entity='members',
                entity_id=str(TEST_UID),
                old='-',
                attribute='members.%s.uid' % TEST_UID,
                new=str(TEST_UID),
                operation='created',
            ),
            self.env.statbox.entry(
                'family_accept_invite',
                uid=str(TEST_UID),
                family_id=TEST_FAMILY_ID,
                invite_id=TEST_FAMILY_INVITE_ID,
                send_method=send_method,
                contact=contact,
            ),
        ])
        self.env.statbox.assert_has_written(entries)

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_accept_invite',
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
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID),
                'uid': str(TEST_UID),
            },
        ]

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_ydb_exec(self, queries):
        self.env.fake_ydb.assert_queries_executed(queries)

    def assert_db_written(self, family_id=TEST_FAMILY_ID, members=None, places=None):
        members = members or [TEST_UID1, TEST_UID]
        if places is None:
            places = range(len(members))
        i_family_id = int(family_id.lstrip('f'))
        self.env.db.check_table_contents('family_info', 'passportdbcentral', [
            {
                'family_id': i_family_id,
                'admin_uid': TEST_UID1,
                'meta': '',
            },
        ])
        self.env.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': i_family_id,
                'uid': uid,
                'place': place,
            } for uid, place in zip(members, places)
        ])

    def assert_db_empty(self):
        self.env.db.check_table_contents('family_info', 'passportdbcentral', [])
        self.env.db.check_table_contents('family_members', 'passportdbcentral', [])

    def assert_db_untouched(self, family_id=TEST_FAMILY_ID, members=None):
        members = members or [TEST_UID1]
        self.assert_db_written(family_id=family_id, members=members)

    def assert_blackbox_call_ok(self):
        requests = self.env.blackbox.get_requests_by_method('family_info')
        self.assertEqual(len(requests), 1)
        requests[0].assert_query_contains({'get_place': 'yes'})

    def test_accept_ok(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(admin_uid=TEST_UID1, family_members=[TEST_UID1])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_ok_response(resp)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_db_written()
        self.assert_ydb_exec(
            self.build_ydb_select() +
            self.build_ydb_find(TEST_FAMILY_INVITE_ID) +
            self.build_ydb_delete(),
        )
        self.assert_blackbox_call_ok()

    def test_accept_ok_nearly_full(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(admin_uid=TEST_UID1, family_members=[TEST_UID1, TEST_UID2])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_invite() +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID2])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_ok_response(resp)
        self.assert_historydb_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_db_written(members=[TEST_UID1, TEST_UID2, TEST_UID])
        self.assert_ydb_exec(
            self.build_ydb_select() +
            self.build_ydb_find(TEST_FAMILY_INVITE_ID) +
            self.build_ydb_delete(),
        )
        self.assert_blackbox_call_ok()

    def test_invite_not_found_error(self):
        self.setup_bb_response(has_family=False)
        self.setup_ydb(self.build_ydb_empty())
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.invalid_invite'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_db_untouched()
        self.assert_ydb_exec(self.build_ydb_select())

    def test_family_does_not_exist_error(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(exists=False)
        self.setup_ydb(self.build_ydb_invite())
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.invalid_invite'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_empty()
        self.assert_ydb_exec(self.build_ydb_select())

    def test_already_is_member_this_error(self):
        self.setup_bb_response(has_family=True, own_family=False)
        self.setup_ydb(self.build_ydb_invite())
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.is_member_this'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_untouched()
        self.assert_ydb_exec(self.build_ydb_select())

    def test_already_is_member_other_error(self):
        self.setup_bb_response(has_family=True, own_family=False)
        self.setup_ydb(self.build_ydb_invite(family_id=TEST_FAMILY_ID1))
        self._family_to_db(TEST_FAMILY_ID1, TEST_UID1, [TEST_UID1])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.is_member_other'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_untouched(family_id=TEST_FAMILY_ID1)
        self.assert_ydb_exec(self.build_ydb_select())

    def test_family_full_mixed(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(
            admin_uid=TEST_UID1,
            family_members=[TEST_UID1, TEST_UID2, TEST_UID3],
        )
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_invite() +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID2, TEST_UID3])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.max_capacity'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_untouched(members=[TEST_UID1, TEST_UID2, TEST_UID3])
        self.assert_ydb_exec(self.build_ydb_select() + self.build_ydb_find(TEST_FAMILY_INVITE_ID))

    def test_family_full_invites(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(admin_uid=TEST_UID1, family_members=[TEST_UID1])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_invite(number=3) +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.max_capacity'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_untouched()
        self.assert_ydb_exec(self.build_ydb_select() + self.build_ydb_find(TEST_FAMILY_INVITE_ID))

    def test_family_full_members(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(admin_uid=TEST_UID1, family_members=[TEST_UID1, TEST_UID2, TEST_UID3, TEST_UID4])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID2, TEST_UID3, TEST_UID4])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.max_capacity'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_untouched(members=[TEST_UID1, TEST_UID2, TEST_UID3, TEST_UID4])
        self.assert_ydb_exec(self.build_ydb_select() + self.build_ydb_find(TEST_FAMILY_INVITE_ID))

    def test_family_capacity_race_condition(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(admin_uid=TEST_UID1, family_members=[TEST_UID1, TEST_UID2, TEST_UID3])
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1, TEST_UID2, TEST_UID3, TEST_UID4])
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['backend.database_failed'])
        self.assert_historydb_empty()
        self.assert_statbox_check_cookies()
        self.assert_db_untouched(members=[TEST_UID1, TEST_UID2, TEST_UID3, TEST_UID4])
        self.assert_ydb_exec(
            self.build_ydb_select() +
            self.build_ydb_find(TEST_FAMILY_INVITE_ID) +
            self.build_ydb_delete(),
        )

    def test_auth_by_uid__ok(self):
        self.setup_bb_response(has_family=False)
        self.setup_bb_family_response(admin_uid=TEST_UID1, family_members=[TEST_UID3])
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_userinfo_response(with_family=False)),
        )
        self.setup_ydb(
            self.build_ydb_invite() +
            self.build_ydb_empty(True) +
            self.build_ydb_empty(False),
        )
        self._family_to_db(TEST_FAMILY_ID, TEST_UID1, [TEST_UID1])
        resp = self.make_request(
            query_args=dict(
                uid=TEST_UID,
                invite_id=TEST_FAMILY_INVITE_ID,
            ),
            exclude_headers=[
                'cookie',
                'host',
            ],
        )
        self.assert_ok_response(resp)
        self.assert_historydb_ok()
        self.assert_statbox_ok()
        self.assert_db_written()
        self.assert_ydb_exec(
            self.build_ydb_select() +
            self.build_ydb_find(TEST_FAMILY_INVITE_ID) +
            self.build_ydb_delete(),
        )
        self.assert_blackbox_call_ok()
