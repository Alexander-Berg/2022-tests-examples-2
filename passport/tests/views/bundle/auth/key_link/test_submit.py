# -*- coding: utf-8 -*-
import json
import time

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_track_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.persistent_track import TRACK_TYPE_AUTH_BY_KEY_LINK
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator

from .base_test_data import *


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    FRODO_URL='http://localhost/',
)
class SubmitKeyLinkTestCase(BaseBundleTestViews):
    statbox_mode = 'key_auth'
    track_type = 'authorize'
    default_url = '/1/bundle/auth/key_link/submit/'

    def setUp(self):
        super(SubmitKeyLinkTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                dbfields={
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_UID,
                TEST_PERSISTENT_TRACK_ID,
                created=TEST_AUTH_BY_KEY_LINK_CREATE_TIMESTAMP,
                expired=int(time.time() + 60),
                content={
                    'type': TRACK_TYPE_AUTH_BY_KEY_LINK,
                },
            ),
        )

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_key': ['base']}),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.patches = [
            self.track_id_generator,
        ]
        for p in self.patches:
            p.start()
        self.setup_statbox_templates()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        super(SubmitKeyLinkTestCase, self).tearDown()

    def get_headers(self, host=None, user_ip=None, cookie=None,
                    user_agent=None):
        return mock_headers(
            host=host or TEST_HOST,
            user_agent=user_agent or TEST_USER_AGENT,
            cookie=cookie or 'yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            user_ip=user_ip or TEST_IP,
        )

    def make_request(self, data, headers=None):

        if 'track_id' not in data:
            data.update(track_id=self.track_id)

        return self.env.client.post(
            self.default_url + '?consumer=dev',
            headers=headers or self.get_headers(),
            data=data,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            yandexuid=TEST_YANDEXUID_COOKIE,
            track_id=self.track_id,
            ip=TEST_IP,
            host=TEST_HOST,
            uid=str(int(TEST_UID, 16)),
            user_agent=TEST_USER_AGENT,
            consumer='dev',
            mode=self.statbox_mode,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            action='submitted',
            type='key',
            does_key_exist='1',
            is_key_expired='0',
            key_type=str(TRACK_TYPE_AUTH_BY_KEY_LINK),
        )
        self.env.statbox.bind_entry(
            'failed',
            _inherit_from='local_base',
            action='finished_with_error',
        )

    def test_complete_autoregistered_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                dbfields={
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                },
            ),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        expected = {
            'state': 'complete_autoregistered',
            'track_id': self.track_id,
        }
        self.assert_ok_response(response, **expected)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                state='complete_autoregistered',
            ),
        ])
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            eq_(track.track_type, 'authorize')
            ok_(track.is_complete_autoregistered)
            eq_(track.uid, TEST_UID)
            eq_(track.login, TEST_LOGIN)

    def test_complete_social_with_portal_alias_without_password_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                aliases={
                    'portal': TEST_LOGIN,
                    'social': TEST_SOCIAL_ALIAS,
                },
            ),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        expected = {
            'state': 'complete_social',
            'track_id': self.track_id,
        }
        self.assert_ok_response(response, **expected)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'submitted',
                state='complete_social',
            ),
        ])
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            eq_(track.track_type, 'complete')
            ok_(not track.is_complete_autoregistered)
            eq_(track.uid, TEST_UID)
            ok_(track.is_key_auth_passed)

    def test_empty_secret_key(self):
        response = self.make_request(
            data=dict(secret_key=''),
        )

        self.assert_error_response(response, ['secret_key.empty'])
        self.env.statbox.assert_has_written([])

    def test_persistent_track_expired(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_UID,
                TEST_PERSISTENT_TRACK_ID,
                created=TEST_AUTH_BY_KEY_LINK_CREATE_TIMESTAMP,
                expired=int(time.time() - 60),
                content={
                    'type': TRACK_TYPE_AUTH_BY_KEY_LINK,
                },
            ),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        self.assert_error_response(response, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed',
                error='secret_key.invalid',
                does_key_exist='1',
                is_key_expired='1',
                key_type=str(TRACK_TYPE_AUTH_BY_KEY_LINK),
            ),
        ])

    def test_persistent_track_not_exists(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_UID,
                TEST_PERSISTENT_TRACK_ID,
                is_found=False,
            ),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        self.assert_error_response(response, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed',
                error='secret_key.invalid',
                does_key_exist='0',
            ),
        ])

    def test_persistent_track_wrong_type(self):
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_UID,
                TEST_PERSISTENT_TRACK_ID,
                created=TEST_AUTH_BY_KEY_LINK_CREATE_TIMESTAMP,
                expired=int(time.time() + 60),
                content={
                    'type': -1,
                },
            ),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        self.assert_error_response(response, ['secret_key.invalid'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed',
                error='secret_key.invalid',
                does_key_exist='1',
                is_key_expired='0',
                key_type='-1',
            ),
        ])

    def test_persistent_track_created_before_logout(self):
        """
        Персистентный трек создан до логаута
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                attributes={
                    'revoker.web_sessions': int(time.time()),
                },
                dbfields={
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                },
            ),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        self.assert_error_response(response, ['account.global_logout'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed',
                error='account.global_logout',
                does_key_exist='1',
                is_key_expired='0',
                key_type=str(TRACK_TYPE_AUTH_BY_KEY_LINK),
            ),
        ])

    def base_action_impossible_case(self, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**kwargs),
        )

        response = self.make_request(
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        self.assert_error_response(response, ['action.impossible'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'failed',
                error='action.impossible',
                does_key_exist='1',
                is_key_expired='0',
                key_type=str(TRACK_TYPE_AUTH_BY_KEY_LINK),
            ),
        ])

    def test_action_impossible_for_usual_account(self):
        self.base_action_impossible_case()

    def test_action_impossible_for_social_with_password(self):
        self.base_action_impossible_case(
            aliases={
                'portal': TEST_LOGIN,
                'social': TEST_SOCIAL_ALIAS,
            },
            crypt_password='1:123',
        )

    def test_action_impossible_for_pdd_with_password_creating_required(self):
        self.base_action_impossible_case(
            aliases={
                'pdd': TEST_LOGIN,
            },
            dbfields={
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            },
        )
