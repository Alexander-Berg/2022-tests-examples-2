# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_CSRF_TOKEN,
    TEST_LOGIN,
    TEST_OTP,
    TEST_PROFILE_BAD_ESTIMATE,
    TEST_TRACK_ID,
    TEST_UID,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.utils.time import get_unixtime

from .base import (
    BaseMultiStepTestcase,
    CommonAuthTests,
)


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
)
class CommitMagicTestcase(BaseMultiStepTestcase, CommonAuthTests):
    default_url = '/1/bundle/auth/password/multi_step/commit_magic/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'csrf_token': TEST_CSRF_TOKEN,
    }

    def setUp(self):
        super(CommitMagicTestcase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.login = TEST_LOGIN
            track.is_allow_otp_magic = True
            track.csrf_token = TEST_CSRF_TOKEN
            track.otp = TEST_OTP

    def tearDown(self):
        del self.track_id
        super(CommitMagicTestcase, self).tearDown()

    def default_response_values(self):
        return dict(
            super(CommitMagicTestcase, self).default_response_values(),
            state='otp_auth_finished',
        )

    def assert_track_ok(self):
        track = self.track_manager.read(TEST_TRACK_ID)
        ok_(track.allow_authorization)
        ok_(track.is_otp_magic_passed)
        eq_(track.auth_method, 'magic')

    def test_magic_not_allowed(self):
        with self.track_transaction(self.track_id) as track:
            track.is_allow_otp_magic = False
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=TEST_TRACK_ID)

    def test_csrf_token_invalid(self):
        resp = self.make_request(query_args={'csrf_token': 'not_csrf'})
        self.assert_error_response(resp, ['csrf_token.invalid'], track_id=TEST_TRACK_ID)

    def test_corrupt_track(self):
        with self.track_transaction(self.track_id) as track:
            track.login = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=TEST_TRACK_ID)

    def test_auth_not_ready(self):
        with self.track_transaction(self.track_id) as track:
            track.otp = None
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='otp_auth_not_ready',
        )

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

        assert len(self.env.blackbox.requests) == 1
        assert len(self.env.blackbox.get_requests_by_method('login')) == 1

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
        assert len(self.env.blackbox.get_requests_by_method('login')) == 1

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
        assert len(self.env.blackbox.get_requests_by_method('userinfo')) == 1

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

        eq_(len(self.env.blackbox.requests), 1)
        self.env.blackbox.requests[0].assert_post_data_contains({'method': 'userinfo'})

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
        assert len(self.env.blackbox.get_requests_by_method('userinfo')) == 1

    def test_with_2fa_picture_ok(self):
        with self.track_transaction(self.track_id) as track:
            track.otp = None
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = get_unixtime() + 60
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='otp_auth_not_ready',
            is_2fa_picture_expired=False,
        )

    def test_with_2fa_picture_expired(self):
        with self.track_transaction(self.track_id) as track:
            track.otp = None
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = get_unixtime() - 1
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='otp_auth_not_ready',
            is_2fa_picture_expired=True,
        )


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    EMAIL_CODE_CHALLENGE_ENABLED=False,
)
class AntifraudCommitMagicTestcase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/commit_magic/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'csrf_token': TEST_CSRF_TOKEN,
    }

    def setUp(self):
        super(AntifraudCommitMagicTestcase, self).setUp()

        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.login = TEST_LOGIN
            track.is_allow_otp_magic = True
            track.csrf_token = TEST_CSRF_TOKEN
            track.otp = TEST_OTP

        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])

    def tearDown(self):
        del self.track_id
        super(AntifraudCommitMagicTestcase, self).tearDown()

    def assert_ok_antifraud_score_request(self, request):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.default()
        params.populate_from_headers(mock_headers(**self.http_headers))
        params.external_id = 'track-' + self.track_id
        params.input_login = TEST_LOGIN
        params.uid = TEST_UID
        params.lah_uids = [TEST_UID]
        params.available_challenges = ['email_hint']
        params.surface = 'multi_step_magic'
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
