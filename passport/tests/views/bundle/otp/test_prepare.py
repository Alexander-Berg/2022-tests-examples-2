# -*- coding: utf-8 -*-
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.conf import settings
from passport.backend.core.redis_manager.redis_manager import (
    RedisError,
    RedisWatchError,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


TEST_LOGIN = 'user1'
TEST_OTP = '12345678'
TEST_USER_IP = '127.0.0.1'
TEST_OAUTH_X_TOKEN = 'x-token'


@with_settings_hosts()
class TestTotpPrepare(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/auth/otp/prepare/'
    http_method = 'POST'
    http_query_args = {
        'otp': TEST_OTP,
        'login': TEST_LOGIN,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['app']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args.update(track_id=self.track_id)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = True
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_USER_IP,
            track_id=self.track_id,
        )
        for action in (
            'otp_auth_started',
            'otp_auth_prepared',
        ):
            self.env.statbox.bind_entry(
                action,
                action=action,
            )

    def test_params_empty_error(self):
        for param in ['login', 'track_id', 'otp']:
            rv = self.make_request(query_args=dict(**{param: ''}))
            self.assert_error_response(rv, ['%s.empty' % param])

    def test_track_id_invalid_error(self):
        rv = self.make_request(query_args=dict(track_id='123'))
        self.assert_error_response(rv, ['track_id.invalid'])

    def test_track_not_found_error(self):
        rv = self.make_request(
            query_args=dict(
                track_id='0a' * settings.TRACK_RANDOM_BYTES_COUNT + '00',
            ),
        )
        self.assert_error_response(rv, ['track.not_found'])

    def test_invalid_track_state_permanent_error(self):
        """Пришли не с "магическим" треком."""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = False

        rv = self.make_request()
        self.assert_error_response(rv, ['internal.permanent'])

        track = self.track_manager.read(self.track_id)
        ok_(track.otp is None)
        ok_(track.login is None)
        ok_(not track.cred_status)

    def test_redis_error(self):
        """Пришли, а редис сломался."""
        with mock.patch.object(
            self.env.track_manager.get_redis(),
            'pipeline',
            mock.Mock(side_effect=RedisError()),
        ):
            rv = self.make_request()
            self.assert_error_response(rv, ['internal.temporary'])
        track = self.track_manager.read(self.track_id)
        ok_(track.otp is None)
        ok_(track.login is None)
        ok_(not track.cred_status)

    def test_redis_watch_error(self):
        """Гонки при записи в Redis"""
        with mock.patch.object(
            self.env.track_manager.get_redis(),
            'pipeline',
            mock.Mock(side_effect=RedisWatchError()),
        ):
            rv = self.make_request()
            self.assert_error_response(rv, ['internal.temporary'])
        track = self.track_manager.read(self.track_id)
        ok_(track.otp is None)
        ok_(track.login is None)
        ok_(not track.cred_status)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            server_time=TimeNow(),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.otp, TEST_OTP)
        eq_(track.login, TEST_LOGIN)
        eq_(track.blackbox_password_status, '')
        eq_(track.blackbox_login_status, '')
        ok_(track.cred_status is None)
        ok_(track.uid is None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('otp_auth_prepared'),
        ])

    def test_malformed_otp_ok(self):
        rv = self.make_request(query_args=dict(otp='bad'))
        self.assert_ok_response(
            rv,
            server_time=TimeNow(),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.otp, 'bad')
        eq_(track.login, TEST_LOGIN)
        eq_(track.blackbox_password_status, '')
        eq_(track.blackbox_login_status, '')
        ok_(track.cred_status is None)
        ok_(track.uid is None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('otp_auth_prepared'),
        ])

    def test_ok_ensure_blackbox_cached_response_cleared(self):
        """
        Удостоверимся, что при успехе ручка сбрасывает
        состояние похода в ЧЯ.
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.blackbox_login_status = 'VALID'
            track.blackbox_password_status = 'BAD'

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            server_time=TimeNow(),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.otp, TEST_OTP)
        eq_(track.login, TEST_LOGIN)
        eq_(track.blackbox_password_status, '')
        eq_(track.blackbox_login_status, '')
        ok_(not track.allow_authorization)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('otp_auth_prepared'),
        ])

    def test_ok_after_x_token(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = 1

        rv = self.make_request()
        self.assert_ok_response(
            rv,
            server_time=TimeNow(),
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.otp, TEST_OTP)
        eq_(track.login, TEST_LOGIN)
        eq_(track.blackbox_password_status, '')
        eq_(track.blackbox_login_status, '')
        ok_(track.cred_status is None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('otp_auth_prepared'),
        ])

    def test_invalid_track_type(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')

        rv = self.make_request(query_args=dict(track_id=self.track_id))
        self.assert_error_response(rv, ['internal.permanent'])

    def test_with_2fa_pictures__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = int(time() + 60)

        rv = self.make_request(query_args=dict(selected_2fa_picture=42))
        self.assert_ok_response(
            rv,
            server_time=TimeNow(),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.otp, TEST_OTP)
        eq_(track.login, TEST_LOGIN)
        eq_(track.blackbox_password_status, '')
        eq_(track.blackbox_login_status, '')
        ok_(track.cred_status is None)
        ok_(track.uid is None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('otp_auth_prepared'),
        ])

    def test_with_2fa_pictures__wrong_picture(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = int(time() + 60)

        rv = self.make_request(query_args=dict(selected_2fa_picture=43))
        self.assert_error_response(rv, ['2fa_picture.invalid'])

        track = self.track_manager.read(self.track_id)
        eq_(track.correct_2fa_picture_expires_at, TimeNow())

    def test_with_2fa_pictures__expired(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = int(time() - 60)

        rv = self.make_request(query_args=dict(selected_2fa_picture=42))
        self.assert_error_response(rv, ['2fa_picture.expired'])

    def test_with_2fa_pictures__bad_track(self):
        rv = self.make_request(query_args=dict(selected_2fa_picture=42))
        self.assert_error_response(rv, ['internal.permanent'])
