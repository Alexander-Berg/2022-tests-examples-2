# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyInviteTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BLACKBOX_RESPONSE_ACCOUNT_OTHER_FAMILY_INFO,
    TEST_BLACKBOX_RESPONSE_ACCOUNT_OWN_FAMILY_INFO,
    TEST_FAMILY_ID,
    TEST_HOST,
    TEST_UID,
    TEST_UID1,
    TEST_UID4,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.test.consts import (
    TEST_KIDDISH_LOGIN1,
    TEST_LOGIN2,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.time_utils.time_utils import DatetimeNow


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class DeleteViewTestCase(BaseFamilyInviteTestcase):
    default_url = '/1/bundle/family/delete/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(DeleteViewTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'delete',
                        'delete_by_uid',
                    ],
                },
            ),
        )

    def setup_statbox_templates(self):
        super(DeleteViewTestCase, self).setup_statbox_templates()

        fake_loggers = [
            self.env.family_logger,
            self.env.statbox,
        ]
        for fake_logger in fake_loggers:
            fake_logger.bind_entry(
                'kiddish.disabled_status',
                _inherit_from=['account_modification'],
                entity='account.disabled_status',
                new='disabled_on_deletion',
                old='enabled',
                operation='updated',
                uid=str(TEST_UID4),
            )
            fake_logger.bind_entry(
                'family_admin_uid_deleted',
                _inherit_from=['family_info_modification'],
                family_id='%s' % str(TEST_FAMILY_ID),
                entity='admin_uid',
                new='-',
                old=str(TEST_UID),
                operation='deleted',
            )
            fake_logger.bind_entry(
                'base_family_member_deleted',
                _inherit_from=['family_info_modification'],
                entity='members',
                entity_id='-',
                family_id=str(TEST_FAMILY_ID),
                new='-',
                attribute='-',
                old='-',
                operation='deleted',
            )
            fake_logger.bind_entry(
                'family_member_deleted.%s' % TEST_UID,
                _inherit_from=['base_family_member_deleted'],
                entity_id=str(TEST_UID),
                attribute='members.%s.uid' % TEST_UID,
                old=str(TEST_UID),
            )
            fake_logger.bind_entry(
                'family_member_deleted.%s' % TEST_UID1,
                _inherit_from=['base_family_member_deleted'],
                entity_id=str(TEST_UID1),
                attribute='members.%s.uid' % TEST_UID1,
                old=str(TEST_UID1),
            )
            fake_logger.bind_entry(
                'family_kid_deleted',
                _inherit_from=['family_info_modification'],
                family_id=str(TEST_FAMILY_ID),
                entity='kid',
                entity_id=str(TEST_UID4),
                new='-',
                attribute='uid',
                old=str(TEST_UID4),
                operation='deleted',
            )

    def assert_statbox_ok(self, with_check_cookies=False):
        statbox_entries = list()

        def req(e):
            statbox_entries.append(self.env.statbox.entry(e))

        if with_check_cookies:
            req('check_cookies')

        req('kiddish.disabled_status')
        req('family_admin_uid_deleted')
        req('family_member_deleted.%s' % TEST_UID)
        req('family_member_deleted.%s' % TEST_UID1)
        req('family_kid_deleted')

        self.env.statbox.assert_equals(statbox_entries)

        family_entries = list()

        def req(e):
            family_entries.append(self.env.family_logger.entry(e))

        req('family_admin_uid_deleted')
        req('family_member_deleted.%s' % TEST_UID)
        req('family_member_deleted.%s' % TEST_UID1)
        req('family_kid_deleted')

        self.env.family_logger.assert_equals(family_entries)

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_delete',
                'uid': str(TEST_UID),
            },
            {
                'name': 'action',
                'value': 'family_delete',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'family.%s.family_admin' % TEST_FAMILY_ID,
                'value': '-',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': '-',
                'uid': str(TEST_UID1),
            },
        ]
        expected_events += self.base_historydb_events(TEST_UID)
        expected_events += self.base_historydb_events(TEST_UID1)

        e = EventCompositor(uid=str(TEST_UID4))
        e('info.ena', '0')
        e('info.disabled_status', '2')
        e('deletion_operation', 'created')
        e('action', 'start_kiddish_deletion')
        e('consumer', 'dev')
        e('user_agent', TEST_USER_AGENT)

        with e.context(prefix='family.%s.' % TEST_FAMILY_ID):
            e('family_kid', '-')
        e('action', 'family_delete')
        e('consumer', 'dev')
        e('user_agent', 'curl')

        expected_events += e.to_lines()

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def assert_db_written(self):
        self.env.db.check_table_contents('family_info', 'passportdbcentral', [])
        self.env.db.check_table_contents('family_members', 'passportdbcentral', [])

        del_ops = self.env.db.select('account_deletion_operations', uid=TEST_UID4, db='passportdbshard1')
        self.assertEqual(len(del_ops), 1)
        self.assertEqual(del_ops[0]['started_at'], DatetimeNow())

        self.env.db.check_db_attr(TEST_UID4, 'account.is_disabled', str(ACCOUNT_DISABLED_ON_DELETION))

    def setup_bb_response(self, with_admin_userinfo=False, **kwargs):
        super(DeleteViewTestCase, self).setup_bb_response(**kwargs)

        if kwargs.get('has_family'):
            if kwargs.get('own_family'):
                acc_family_info = TEST_BLACKBOX_RESPONSE_ACCOUNT_OWN_FAMILY_INFO
            else:
                acc_family_info = TEST_BLACKBOX_RESPONSE_ACCOUNT_OTHER_FAMILY_INFO

            userinfo_responses = []
            if with_admin_userinfo:
                userinfo_responses.append(
                    blackbox_userinfo_response(**self.build_blackbox_family_admin_response(has_family=kwargs.get('has_family'))),
                )
            userinfo_response = blackbox_userinfo_response(
                family_info=acc_family_info,
                aliases=dict(kiddish=TEST_KIDDISH_LOGIN1),
                login=TEST_KIDDISH_LOGIN1,
                uid=TEST_UID4,
            )
            userinfo_responses.append(userinfo_response)
            self.env.blackbox.set_response_side_effect('userinfo', userinfo_responses)
            self.env.db.serialize(userinfo_response)

    def test_delete_ok(self):
        self.setup_bb_response(has_family=True, family_members=[TEST_UID, TEST_UID1])
        self.setup_ydb(self.build_ydb_empty())
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()
        self.assert_db_written()
        self.assert_ydb_exec(self.build_ydb_delete_all())

    def test_family_does_not_exist_error(self):
        self.setup_bb_response(has_family=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.does_not_exist'])

    def test_not_is_admin_error(self):
        self.setup_bb_response(has_family=True, own_family=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.not_is_admin'])

    def test_race_phantom_kid(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )

        userinfo_response = blackbox_userinfo_response(
            uid=None,
            id=TEST_UID4,
        )
        self.env.blackbox.set_response_side_effect('userinfo', [userinfo_response])

        resp = self.make_request()

        self.assert_error_response(resp, ['internal.temporary'])

    def test_race_kid_grown_up_and_left_family(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )

        userinfo_response = blackbox_userinfo_response(
            aliases=dict(portal=TEST_LOGIN2),
            family_info=TEST_BLACKBOX_RESPONSE_ACCOUNT_OTHER_FAMILY_INFO,
            login=TEST_LOGIN2,
            uid=TEST_UID4,
        )
        self.env.blackbox.set_response_side_effect('userinfo', [userinfo_response])

        resp = self.make_request()

        self.assert_error_response(resp, ['internal.temporary'])

    def test_race_kid_grown_up_and_stayed_in_family(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )

        userinfo_response = blackbox_userinfo_response(
            aliases=dict(portal=TEST_LOGIN2),
            family_info=TEST_BLACKBOX_RESPONSE_ACCOUNT_OWN_FAMILY_INFO,
            login=TEST_LOGIN2,
            uid=TEST_UID4,
        )
        self.env.blackbox.set_response_side_effect('userinfo', [userinfo_response])

        resp = self.make_request()

        self.assert_error_response(resp, ['internal.temporary'])

    def test_uid(self):
        self.setup_bb_response(has_family=True, own_family=True, family_members=[TEST_UID, TEST_UID1], with_admin_userinfo=True)
        self.setup_ydb(self.build_ydb_empty())
        self._family_to_db(TEST_FAMILY_ID, TEST_UID, [TEST_UID, TEST_UID1])

        resp = self.make_request(
            exclude_headers=[
                'cookie',
                'host',
            ],
            query_args=dict(uid=str(TEST_UID)),
        )

        self.assert_ok_response(resp)
        self.assert_statbox_ok()
        self.assert_historydb_ok()
        self.assert_db_written()
        self.assert_ydb_exec(self.build_ydb_delete_all())
