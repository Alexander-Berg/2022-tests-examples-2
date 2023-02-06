# -*- coding: utf-8 -*-

import mock
from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_ID1,
    TEST_HOST,
    TEST_UID,
    TEST_UID1,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.avatars_mds_api.faker import avatars_mds_api_upload_ok_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from six import StringIO


TEST_URL = 'http://someurl'
TEST_GROUP_ID = '1234'
TEST_AVATAR_SUBKEY = '567890'


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
)
class DeleteChildViewTestCase(BaseFamilyTestcase):
    default_url = '/1/bundle/family/change_child_avatar/'
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
                        'change_child_avatar',
                        'change_child_avatar_by_uid',
                    ],
                },
            ),
        )
        self.env.avatars_mds_api.set_response_value('upload_from_url', avatars_mds_api_upload_ok_response())
        self.env.avatars_mds_api.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response())
        self.get_avatar_mds_key_patch = mock.patch(
            'passport.backend.core.avatars.avatars.get_avatar_mds_key',
            mock.Mock(return_value=TEST_AVATAR_SUBKEY),
        )
        self.get_avatar_mds_key_patch.start()

    def tearDown(self):
        super(DeleteChildViewTestCase, self).tearDown()
        self.get_avatar_mds_key_patch.stop()
        del self.get_avatar_mds_key_patch

    def get_expected_ok_response(self, avatar_size='normal'):
        return {
            'avatar_url': 'https://localhost/get-yapic/1234/567890/%s' % avatar_size,
        }

    def assert_statbox_ok(self, action='upload_from_url', with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.extend([
            self.env.statbox.entry(
                'account_modification',
                action=action,
                mode='family',
                _exclude=['event', 'uid'],
            ),
            self.env.statbox.entry(
                'account_modification',
                entity='person.default_avatar',
                uid=str(TEST_UID1),
                old='-',
                new='1234/567890',
                operation='created',
            ),
        ])
        self.env.statbox.assert_equals(entries)

    def assert_historydb_ok(self):
        expected_events = [
            {
                'name': 'action',
                'value': 'set_default_avatar',
                'uid': str(TEST_UID1),
            },
            {
                'name': 'info.default_avatar',
                'value': '1234/567890',
                'uid': str(TEST_UID1),
            },
        ]

        expected_events += self.base_historydb_events(TEST_UID1)

        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_events,
        )

    def test_ok(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        resp = self.make_request(query_args=dict(url=TEST_URL))
        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()

    def test_send_file_ok(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        resp = self.make_request(query_args=dict(file=(StringIO('my file content'), 'test.png')))
        self.assert_ok_response(resp, **self.get_expected_ok_response())
        self.assert_statbox_ok(action='upload_from_file', with_check_cookies=True)
        self.assert_historydb_ok()

    def test_not_a_family_member_error(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )
        self.set_other_userinfo_bb_response(with_family=False, is_child=True)
        resp = self.make_request(query_args=dict(url=TEST_URL))
        self.assert_error_response(resp, ['family.is_not_a_member'])

    def test_another_family_member_error(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID],
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=True, family_id=TEST_FAMILY_ID1)
        resp = self.make_request(query_args=dict(url=TEST_URL))
        self.assert_error_response(resp, ['family.is_not_a_member'])

    def test_not_is_admin_error(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
            own_family=False,
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        resp = self.make_request(query_args=dict(url=TEST_URL))
        self.assert_error_response(resp, ['family.not_is_admin'])

    def test_not_is_child_error(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=False)
        resp = self.make_request(query_args=dict(url=TEST_URL))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_cant_edit_child_error(self):
        self.setup_bb_response(
            has_family=True,
            family_members=[TEST_UID, TEST_UID1],
            is_child=True,
        )
        self.set_other_userinfo_bb_response(with_family=True, is_child=True)
        resp = self.make_request(query_args=dict(url=TEST_URL))
        self.assert_error_response(resp, ['account.invalid_type'])
