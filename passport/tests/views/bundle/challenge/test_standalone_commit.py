# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.auth.base_test_data import (
    TEST_AUTH_ID,
    TEST_IP,
    TEST_LOGIN_ID,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_PHONE_NUMBER,
    TEST_RETPATH,
    TEST_UID,
)
from passport.backend.api.views.bundle.mixins.phone import KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG
from passport.backend.core.builders.trust_api import PAYMENT_STATUS_AUTHORIZED

from .base import (
    BaseStandaloneTestCase,
    CommonStandaloneChallengeTests,
    TEST_ANTIFRAUD_EXTERNAL_ID,
    TEST_CARD_ID,
    TEST_COOKIES_WITH_WCID,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_USER_AGENT,
)


class StandaloneCommitTestCase(BaseStandaloneTestCase, CommonStandaloneChallengeTests):
    default_url = '/1/bundle/challenge/standalone/commit/'

    def setUp(self):
        super(StandaloneCommitTestCase, self).setUp()
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        self.env.kolmogor.set_response_value('get', flag)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.retpath = TEST_RETPATH
            track.antifraud_external_id = TEST_ANTIFRAUD_EXTERNAL_ID

    @property
    def http_query_args(self):
        return dict(
            track_id=self.track_id,
            challenge='phone_confirmation',
        )

    @property
    def common_response_values(self):
        return dict(
            super(StandaloneCommitTestCase, self).common_response_values,
            retpath=TEST_RETPATH,
        )

    def expected_response(self):
        return self.common_response_values

    def assert_track_ok(self, challenge='phone_confirmation'):
        track = self.track_manager.read(self.track_id)
        eq_(track.auth_challenge_type, challenge)

    def assert_statbox_ok(self, challenge='phone_confirmation', with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry(
                'passed',
                method=challenge,
                challenge=challenge,
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
                **kwargs
            ),
        )
        self.env.statbox.assert_has_written(entries)

    def assert_statbox_failed(self, challenge='phone_confirmation', with_check_cookies=False, **kwargs):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry(
                'failed',
                method=challenge,
                challenge=challenge,
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
                **kwargs
            ),
        )
        self.env.statbox.assert_has_written(entries)

    def assert_antifraud_log_ok(self, challenge='phone_confirmation'):
        self.env.antifraud_logger.assert_has_written([
            self.env.antifraud_logger.entry(
                'base',
                status='OK',
                external_id=TEST_ANTIFRAUD_EXTERNAL_ID,
                ip=TEST_IP,
                channel='challenge',
                sub_channel='chaas',
                uid=str(TEST_UID),
                user_agent=TEST_USER_AGENT,
                yandexuid=TEST_YANDEXUID_COOKIE,
                retpath=TEST_RETPATH,
                authid=TEST_AUTH_ID,
                login_id=TEST_LOGIN_ID,
                challenge=challenge,
            )
        ])

    def test_phone_confirmation_ok(self):
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.assert_track_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_antifraud_log_ok()

    def test_phone_confirmation_by_flash_call_ok(self):
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_flash_call'

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.assert_track_ok()
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_antifraud_log_ok()

    def test_phone_confirmation_not_checked_error(self):
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            **self.expected_response()
        )
        self.assert_statbox_failed(with_check_cookies=True)

    def test_dictation_by_call_ok(self):
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_call'
            track.antifraud_tags = ['dictation']

        resp = self.make_request(query_args=dict(challenge='dictation'))
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.assert_track_ok(challenge='dictation')
        self.assert_statbox_ok(challenge='dictation', with_check_cookies=True)
        self.assert_antifraud_log_ok(challenge='dictation')

    def test_dictation_by_sms_error(self):
        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'
            track.antifraud_tags = ['dictation']

        resp = self.make_request(query_args=dict(challenge='dictation'))
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            **self.expected_response()
        )
        self.assert_statbox_failed('dictation', with_check_cookies=True)

    def test_webauthn_ok(self):
        with self.track_transaction() as track:
            track.webauthn_confirmed_secret_external_id = TEST_CREDENTIAL_EXTERNAL_ID

        resp = self.make_request(
            query_args=dict(challenge='webauthn'),
            headers={'cookie': TEST_COOKIES_WITH_WCID},
        )
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.assert_track_ok(challenge='webauthn')
        self.assert_statbox_ok(challenge='webauthn', with_check_cookies=True)
        self.assert_antifraud_log_ok(challenge='webauthn')

    def test_webauthn_wrong_credential_used(self):
        with self.track_transaction() as track:
            track.webauthn_confirmed_secret_external_id = 'some-unknown-id'

        resp = self.make_request(
            query_args=dict(challenge='webauthn'),
            headers={'cookie': TEST_COOKIES_WITH_WCID},
        )
        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            **self.expected_response()
        )

    def test_3ds_ok(self):
        with self.track_transaction() as track:
            track.paymethod_id = TEST_CARD_ID
            track.payment_status = PAYMENT_STATUS_AUTHORIZED

        resp = self.make_request(
            query_args=dict(challenge='3ds'),
            headers={'cookie': TEST_COOKIES_WITH_WCID},
        )
        self.assert_ok_response(
            resp,
            **self.expected_response()
        )
        self.assert_track_ok(challenge='3ds')
        self.assert_statbox_ok(challenge='3ds', with_check_cookies=True)
        self.assert_antifraud_log_ok(challenge='3ds')

    def test_3ds_not_passed(self):
        with self.track_transaction() as track:
            track.paymethod_id = TEST_CARD_ID

        resp = self.make_request(
            query_args=dict(challenge='3ds'),
            headers={'cookie': TEST_COOKIES_WITH_WCID},
        )

        self.assert_error_response(
            resp,
            ['challenge.not_passed'],
            **self.expected_response()
        )
        self.assert_statbox_failed('3ds', with_check_cookies=True)

    def test_no_challenges_error(self):
        self.setup_blackbox_response(has_phones=False)

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.impossible'],
            **self.expected_response()
        )

    def test_invalid_track_state_error(self):
        with self.track_transaction() as track:
            track.uid = None

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['track.invalid_state'],
        )
