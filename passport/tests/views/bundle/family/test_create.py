# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_ID,
    TEST_HOST,
    TEST_UID,
    TEST_UID2,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_USER_TICKET1,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_user_ticket


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class CreateViewTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/create/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(CreateViewTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': [
                        'create',
                        'create_by_uid',
                    ],
                },
            ),
        )

    def assert_statbox_ok(self, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(('check_cookies', {}))
        entries.extend([
            (
                'family_info_modification',
                dict(
                    family_id='%s' % str(TEST_FAMILY_ID),
                    entity='admin_uid',
                    old='-',
                    new=str(TEST_UID),
                    operation='created',
                ),
            ),
            (
                'family_info_modification',
                dict(
                    family_id='%s' % str(TEST_FAMILY_ID),
                    entity='members',
                    entity_id=str(TEST_UID),
                    old='-',
                    attribute='members.%s.uid' % TEST_UID,
                    new=str(TEST_UID),
                    operation='created',
                ),
            ),
        ])
        self.assert_statboxes(entries)

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'family_create',
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.%s.family_admin' % TEST_FAMILY_ID,
                'value': str(TEST_UID),
                'uid': str(TEST_UID),
            },
            {
                'name': 'family.%s.family_member' % TEST_FAMILY_ID,
                'value': str(TEST_UID),
                'uid': str(TEST_UID),
            },
        ]
        expected_events += self.base_historydb_events(TEST_UID)

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

    def test_create_ok(self):
        self.setup_bb_response(has_family=False)
        resp = self.make_request()
        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()
        self.assert_db_written()

    def test_family_exists_error(self):
        self.setup_bb_response(has_family=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['family.already_exists'])

    def test_session_and_uid(self):
        self.setup_bb_response(has_family=False)
        resp = self.make_request(query_args=dict(uid=str(TEST_UID)))
        self.assert_error_response(resp, ['request.credentials_several_present'])

    def test_multisession_no_uid(self):
        self.setup_bb_response(has_family=False)
        resp = self.make_request(query_args=dict(multisession_uid=str(TEST_UID2)))
        self.assert_error_response(resp, ['sessionid.no_uid'])

    def test_auth_by_uid__ok(self):
        self.setup_bb_response(has_family=False)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_family_admin_response(has_family=False)),
        )

        resp = self.make_request(
            exclude_headers=[
                'cookie',
                'host',
            ],
            query_args=dict(uid=str(TEST_UID)),
        )

        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)

    def test_auth_by_user_ticket__ok(self):
        self.setup_bb_response(has_family=False)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_family_admin_response(has_family=False)),
        )
        ticket = fake_user_ticket(
            default_uid=TEST_UID,
            scopes=['bb:sessionid'],
            uids=[TEST_UID],
        )
        self.env.tvm_ticket_checker.set_check_user_ticket_side_effect([ticket])

        resp = self.make_request(
            headers=dict(
                user_ticket=TEST_USER_TICKET1,
            ),
            exclude_headers=[
                'cookie',
                'host',
            ],
        )

        self.assert_ok_response(resp, family_id=TEST_FAMILY_ID)
