# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.conf import settings
from passport.backend.core.redis_manager.redis_manager import RedisError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_OAUTH_X_TOKEN = 'x-token'
TEST_OAUTH_HEADER = 'OAuth %s' % TEST_OAUTH_X_TOKEN
TEST_OAUTH_SCOPE = X_TOKEN_OAUTH_SCOPE
TEST_LOGIN = 'login'
TEST_UID = 1
TEST_USER_IP = '127.0.0.1'


@with_settings_hosts()
class TestXTokenPrepareAuth(BaseBundleTestViews):
    default_url = '/1/bundle/auth/x_token/prepare/?consumer=dev'
    http_method = 'POST'
    http_headers = dict(
        user_ip=TEST_USER_IP,
        authorization=TEST_OAUTH_HEADER,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_by_token': ['base']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = True

        self.setup_statbox_templates()
        self.http_query_args = {
            'track_id': self.track_id,
        }

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            ip=TEST_USER_IP,
            track_id=self.track_id,
        )
        self.env.statbox.bind_entry(
            'prepared',
            action='auth_prepared_by_cred',
        )
        self.env.statbox.bind_entry(
            'error',
            action='failed',
            error='oauth_token.invalid',
        )

    def assert_track_ok(self, status='valid', uid=None):
        track = self.track_manager.read(self.track_id)
        ok_(not track.otp)
        ok_(not track.login)
        ok_(not track.blackbox_password_status)
        ok_(not track.blackbox_login_status)
        eq_(track.x_token_status, status)
        eq_(track.cred_status, status)
        if uid:
            eq_(track.uid, str(uid))
        else:
            ok_(track.uid is None)

    def assert_track_empty(self):
        track = self.track_manager.read(self.track_id)
        ok_(not track.otp)
        ok_(not track.login)
        ok_(not track.uid)
        ok_(track.x_token_status is None)
        ok_(track.cred_status is None)
        ok_(not track.blackbox_password_status)
        ok_(not track.blackbox_login_status)

    def test_track_id_invalid__error(self):
        resp = self.make_request(query_args={'track_id': '123'})
        self.assert_error_response(resp, ['track_id.invalid'])

    def test_track_not_found__error(self):
        resp = self.make_request(query_args={'track_id': '0a' * settings.TRACK_RANDOM_BYTES_COUNT + '00'})
        self.assert_error_response(resp, ['track.not_found'])

    def test_invalid_track_state__error(self):
        """Пришли не с "магическим" треком."""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = False

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_track_empty()

    def test_redis_error(self):
        """Пришли, а редис сломался."""
        with mock.patch.object(
            self.env.track_manager.get_redis(),
            'pipeline',
            mock.Mock(side_effect=RedisError()),
        ):
            resp = self.make_request()
            self.assert_error_response(resp, ['backend.redis_failed'])

        self.assert_track_empty()

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok(uid=TEST_UID)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('prepared'),
        ])

    def test_ok_with_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID, login=TEST_LOGIN),
        )
        resp = self.make_request(
            exclude_headers=['authorization'],
            headers={'cookie': 'Session_id=foo', 'host': 'yandex.ru'},
        )
        self.assert_ok_response(resp)
        self.assert_track_ok(uid=TEST_UID)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='yandex.ru'),
            self.env.statbox.entry('prepared'),
        ])

    def test_not_allowed(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login='phne-test',
                aliases={
                    'phonish': 'phne-test',
                },
                scope=TEST_OAUTH_SCOPE,
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_track_empty()

    def test_token_invalid(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['oauth_token.invalid'])
        self.assert_track_ok(status='invalid')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('error'),
        ])

    def test_invalid_scope(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope='smth:different',
            ),
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['oauth_token.invalid'])
        self.assert_track_ok(status='invalid')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('error'),
        ])

    def test_invalid_track_type(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('complete')

        resp = self.make_request(query_args={'track_id': self.track_id})
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_2fa_on__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope=TEST_OAUTH_SCOPE,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_track_ok(status=None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('error', error='account.invalid_type'),
        ])

    def test_method_disabled__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope=TEST_OAUTH_SCOPE,
                attributes={
                    'account.qr_code_login_forbidden': '1',
                },
            ),
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['account.invalid_type'])
        self.assert_track_ok(status=None)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('error', error='account.invalid_type'),
        ])
