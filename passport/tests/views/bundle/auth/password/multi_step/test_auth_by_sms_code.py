# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_TRACK_ID,
    TEST_UID,
)
from passport.backend.core.test.test_utils import with_settings

from .base import BaseMultiStepTestcase


@with_settings(
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    ALLOW_PROFILE_CHECK_FOR_WEB=False,
)
class CommitSmsCodeTestcase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/commit_sms_code/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
    }
    statbox_type = 'multi_step_sms_code'

    def setUp(self):
        super(CommitSmsCodeTestcase, self).setUp()
        _, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.uid = TEST_UID
            track.allowed_auth_methods = ['password', 'sms_code']
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.setup_blackbox_responses(with_phonenumber_alias=True)

    def setup_statbox_templates(self):
        super(CommitSmsCodeTestcase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'passed',
            _exclude=['origin'],
            action='passed',
            uid=str(TEST_UID),
            login=TEST_LOGIN,
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        eq_(track.auth_method, 'sms_code')
        eq_(track.human_readable_login, TEST_LOGIN)
        ok_(track.allow_set_xtoken_trusted)

    def test_invalid_track_type(self):
        _, track_id = self.env.track_manager.get_manager_and_trackid('register')
        resp = self.make_request(query_args={'track_id': track_id})
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_invalid_track_state(self):
        with self.track_transaction(self.track_id) as track:
            track.allowed_auth_methods = ['password']
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_phone_not_confirmed(self):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'], track_id=self.track_id)

    @parameterized.expand([
        ('by_call',),
        ('by_flash_call',),
    ])
    def test_phone_confirmed_insecurely(self, phone_confirmation_method):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_method = phone_confirmation_method
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'], track_id=self.track_id)

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.session_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'], track_id=self.track_id)

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.assert_track_ok()
        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry('passed'),
            ],
            offset=-1,
        )
        eq_(len(self.env.antifraud_api.requests), 0)
