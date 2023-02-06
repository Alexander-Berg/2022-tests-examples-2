# -*- coding: utf-8 -*-
from time import time

from nose.tools import eq_
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_TRACK_ID,
    TEST_UID,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.bot_api.faker.fake_bot_api import bot_api_response
from passport.backend.core.builders.historydb_api.faker import lastauth_response
from passport.backend.core.builders.phone_squatter import PhoneSquatterPhoneNumberNotTrackedError
from passport.backend.core.builders.phone_squatter.faker import phone_squatter_get_change_status_response
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
)

from .base import BaseMultiStepTestcase


DEFAULT_TEST_SETTINGS = dict(
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    USE_NEW_SUGGEST_BY_PHONE=True,
    USE_PHONE_SQUATTER=True,
    PHONE_SQUATTER_DRY_RUN=False,
)


@with_settings(**DEFAULT_TEST_SETTINGS)
class AuthAfterSuggestByPhoneTestcase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/after_suggest_by_phone/'
    http_query_args = {
        'track_id': TEST_TRACK_ID,
        'uid': TEST_UID,
    }
    statbox_type = 'multi_step_after_suggest_by_phone'

    def setUp(self):
        super(AuthAfterSuggestByPhoneTestcase, self).setUp()
        self.create_and_fill_track()
        self.setup_blackbox_responses(with_phonenumber_alias=True)
        self.env.historydb_api.set_response_value(
            'lastauth',
            lastauth_response(timestamp=time() - 3600),
        )
        self.env.phone_squatter.set_response_value(
            'get_change_status',
            phone_squatter_get_change_status_response(change_unixtime=0),
        )
        self.env.bot_api.set_response_value('send_message', bot_api_response())

    def setup_statbox_templates(self):
        super(AuthAfterSuggestByPhoneTestcase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'passed',
            _exclude=['origin'],
            action='passed',
            uid=str(TEST_UID),
            login=TEST_LOGIN,
        )

    def create_and_fill_track(self, track_type='authorize'):
        _, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

    def test_account_invalid_type(self):
        self.setup_blackbox_responses(has_2fa=True)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'], track_id=self.track_id)

    def test_phone_not_confirmed(self):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'], track_id=self.track_id)

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.session_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'], track_id=self.track_id)

    def test_new_suggest_disabled(self):
        self.setup_blackbox_responses(has_2fa=True)
        with settings_context(**dict(DEFAULT_TEST_SETTINGS, USE_NEW_SUGGEST_BY_PHONE=False)):
            resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'], track_id=self.track_id)

    def test_lastauth_missing(self):
        self.env.historydb_api.set_response_value(
            'lastauth',
            lastauth_response(_type=None),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'], track_id=self.track_id)

    def test_lastauth_old(self):
        self.env.historydb_api.set_response_value(
            'lastauth',
            lastauth_response(timestamp=1),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'], track_id=self.track_id)

    def test_phone_not_found_in_squatter(self):
        self.env.phone_squatter.set_response_side_effect('get_change_status', PhoneSquatterPhoneNumberNotTrackedError)
        resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'], track_id=self.track_id)

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )

        eq_(len(self.env.antifraud_api.requests), 0)

        track = self.track_manager.read(self.track_id)
        assert track.allow_authorization
        assert track.uid == str(TEST_UID)
        assert track.session_scope == 'xsession'

    def test_password_change_required(self):
        self.setup_blackbox_responses(with_phonenumber_alias=True, password_change_required=True)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='change_password',
            validation_method='captcha_and_phone',
            change_password_reason='account_hacked',
            number=dump_number(TEST_PHONE_NUMBER),
            account=self.account_response_values(),
        )

        track = self.track_manager.read(self.track_id)
        assert not track.allow_authorization
        assert track.uid == str(TEST_UID)
        assert track.session_scope == 'xsession'

    def test_phone_squatter_disabled_ok(self):
        self.env.phone_squatter.set_response_side_effect('get_change_status', PhoneSquatterPhoneNumberNotTrackedError)

        with settings_context(**dict(DEFAULT_TEST_SETTINGS, USE_PHONE_SQUATTER=False)):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        eq_(len(self.env.phone_squatter.requests), 0)

    def test_phone_squatter_dry_run_ok(self):
        self.env.phone_squatter.set_response_side_effect('get_change_status', PhoneSquatterPhoneNumberNotTrackedError)

        with settings_context(**dict(DEFAULT_TEST_SETTINGS, PHONE_SQUATTER_DRY_RUN=True)):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        eq_(len(self.env.phone_squatter.requests), 1)
