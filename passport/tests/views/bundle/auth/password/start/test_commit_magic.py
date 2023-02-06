# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import *
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.oauth import (
    OAuthDeviceCodeNotAccepted,
    OAuthDeviceCodeNotFound,
)
from passport.backend.core.builders.oauth.faker import check_device_code_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseSubmitTestCase,
    CommonContinueTests,
    TEST_CSRF_TOKEN,
    TEST_OTP,
)


OAUTH_SCOPE_CREATE_SESSION = 'passport:create_session'


class CommitMagicTestCase(BaseSubmitTestCase, CommonContinueTests):
    url = '/2/bundle/auth/password/commit_magic/?consumer=dev'
    type = 'magic'

    def setup_statbox_templates(self):
        super(CommitMagicTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'submitted',
            type=self.type,
        )

    def get_base_query_params(self):
        return {
            'track_id': self.track_id,
            'csrf_token': TEST_CSRF_TOKEN,
        }

    def setUp(self):
        super(CommitMagicTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.origin = TEST_ORIGIN
            track.service = TEST_SERVICE
            track.is_allow_otp_magic = True
            track.csrf_token = TEST_CSRF_TOKEN
            track.login = TEST_LOGIN
            track.otp = TEST_OTP

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
                attributes={'account.2fa_on': '1'},
            ),
        )

    def default_response_values(self):
        return dict(
            super(CommitMagicTestCase, self).default_response_values(),
            state='otp_auth_finished',
        )

    def check_statbox_entries_xunistater_parsed(self, total_messages=1):
        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ["auth_magic.rps"],
            {"auth_magic.rps.total_dmmm": total_messages}
        )

    def test_no_magic_track_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = False
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
            track_id=self.track_id,
        )

    def test_auth_already_passed_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '0:session'
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['account.auth_passed'],
            track_id=self.track_id,
        )

    def test_invalid_track_state_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.login = ''
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
            track_id=self.track_id,
        )

    def test_csrf_token_invalid(self):
        resp = self.make_request(csrf_token='foo')
        self.assert_error_response(
            resp,
            ['csrf_token.invalid'],
            track_id=self.track_id,
        )

    def test_auth_not_ready(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='otp_auth_not_ready',
        )

    def test_use_blackbox_status_from_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.blackbox_login_status = blackbox.BLACKBOX_LOGIN_VALID_STATUS
            track.blackbox_password_status = blackbox.BLACKBOX_PASSWORD_VALID_STATUS

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)

    def test_x_token_valid_and_no_uid__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.otp = None
            track.login = None

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_x_token_invalid_alone__error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'invalid'
            track.otp = None
            track.login = None

        resp = self.make_request()
        self.assert_error_response(resp, ['oauth_token.invalid'], track_id=self.track_id)

    def test_x_token_invalid_with_otp__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'invalid'

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        eq_(track.surface, 'web_password')

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)
        self.check_statbox_entries_xunistater_parsed()

    def test_both_choose_otp__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('login')), 1)
        self.check_statbox_entries_xunistater_parsed()

    def test_by_x_token__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID
            track.otp = ''
            track.login = ''

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        eq_(track.auth_source, 'xtoken')

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)
        self.env.statbox.assert_contains([self.env.statbox.entry('start_commit_magic', type='auth_by_x_token')])
        self.check_statbox_entries_xunistater_parsed()

    def test_with_code__ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
            track.login = ''
            # если есть этот параметр в треке, то дополнительно проверяется подтверждение кода в oauth
            track.magic_qr_device_code = 'device-code'

        self.env.oauth.set_response_value(
            'check_device_code',
            check_device_code_response(uid=TEST_UID, scopes=['scope1', OAUTH_SCOPE_CREATE_SESSION, 'scope2'])
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )

        eq_(len(self.env.ufo_api.requests), 1)  # 1 запрос для process_env_profile, а не для челленджа
        eq_(len(self.env.oauth.requests), 1)

        track = self.track_manager.read(self.track_id)
        eq_(int(track.uid), TEST_UID)

        # Повторно. Проверяем, что ручку можно дёрнуть ещё разок.

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )

        eq_(len(self.env.oauth.requests), 2)
        self.env.statbox.assert_contains([self.env.statbox.entry('start_commit_magic', type='auth_by_device_code')])
        self.check_statbox_entries_xunistater_parsed(total_messages=2)

    def test_with_code__invalid_scope_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
            track.login = ''
            # если есть этот параметр в треке, то дополнительно проверяется подтверждение кода в oauth
            track.magic_qr_device_code = 'device-code'

        self.env.oauth.set_response_value(
            'check_device_code',
            check_device_code_response(uid=TEST_UID, scopes=['invalid-scope'])
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['oauth.invalid_scope'], track_id=self.track_id)
        eq_(len(self.env.oauth.requests), 1)

    def test_with_code__another_uid_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID * 2
            track.otp = ''
            track.login = ''
            # если есть этот параметр в треке, то дополнительно проверяется подтверждение кода в oauth
            track.magic_qr_device_code = 'device-code'

        self.env.oauth.set_response_value(
            'check_device_code',
            check_device_code_response(uid=TEST_UID, scopes=[OAUTH_SCOPE_CREATE_SESSION])
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

        eq_(len(self.env.oauth.requests), 1)

        track = self.track_manager.read(self.track_id)
        eq_(int(track.uid), TEST_UID * 2)

    def test_with_code__not_accepted(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
            track.login = ''
            # если есть этот параметр в треке, то дополнительно проверяется подтверждение кода в oauth
            track.magic_qr_device_code = 'device-code'

        self.env.oauth.set_response_side_effect(
            'check_device_code',
            OAuthDeviceCodeNotAccepted(),
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='otp_auth_not_ready',
        )

        eq_(len(self.env.oauth.requests), 1)

        track = self.track_manager.read(self.track_id)
        ok_(not track.uid)

    def test_with_code__not_found(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = ''
            track.login = ''
            # если есть этот параметр в треке, то дополнительно проверяется подтверждение кода в oauth
            track.magic_qr_device_code = 'device-code'

        self.env.oauth.set_response_side_effect(
            'check_device_code',
            OAuthDeviceCodeNotFound(),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['oauth_code.not_found'], track_id=self.track_id)

        eq_(len(self.env.oauth.requests), 1)

        track = self.track_manager.read(self.track_id)
        ok_(not track.uid)

    def test_by_x_token_2fa__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID
            track.otp = ''
            track.login = ''

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['account.invalid_type'],
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.allow_authorization)

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)

    def test_by_x_token_sms_2fa__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={
                    'account.sms_2fa_on': '1',
                },
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID
            track.otp = ''
            track.login = ''

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )

    def test_challenge_not_shown(self):
        self.setup_profile_responses(ufo_items=[], estimate=TEST_PROFILE_BAD_ESTIMATE)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cred_status = 'valid'
            track.uid = TEST_UID
            track.otp = ''
            track.login = ''

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        eq_(track.auth_source, 'xtoken')

        assert len(self.env.blackbox.requests) == 1
        eq_(len(self.env.blackbox.get_requests_by_method('userinfo')), 1)


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
)
class AntifraudCommitMagicTestCase(BaseSubmitTestCase):
    url = '/2/bundle/auth/password/commit_magic/?consumer=dev'
    type = 'magic'

    def get_base_query_params(self):
        return {
            'track_id': self.track_id,
            'csrf_token': TEST_CSRF_TOKEN,
        }

    def setUp(self):
        super(AntifraudCommitMagicTestCase, self).setUp()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.retpath = TEST_RETPATH
            track.origin = TEST_ORIGIN
            track.service = TEST_SERVICE
            track.is_allow_otp_magic = True
            track.csrf_token = TEST_CSRF_TOKEN
            track.login = TEST_LOGIN
            track.otp = TEST_OTP

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:pwd',
            ),
        )

        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])

    def assert_ok_antifraud_score_request(self, request):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.default()
        params.populate_from_headers(self.get_headers())
        params.external_id = 'track-' + self.track_id
        params.uid = TEST_UID
        params.available_challenges = []
        params.surface = 'auth_by_magic'
        eq_(request_data, params.as_dict())

        request.assert_query_contains(dict(consumer='passport'))

    def test(self):
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            state='otp_auth_finished',
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)

        eq_(len(self.env.antifraud_api.requests), 1)
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0])
