# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_PHONE_NUMBER,
    TEST_RETPATH,
    TEST_UID,
)
from passport.backend.api.views.bundle.mixins.phone import KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG

from .base import (
    BaseStandaloneTestCase,
    CommonStandaloneChallengeTests,
    TEST_CARD_ID,
    TEST_COOKIES_WITH_WCID,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_DEVICE_NAME,
    TEST_USER_AGENT_SUITABLE_FOR_WEBAUTHN,
)


class StandaloneSubmitTestcase(BaseStandaloneTestCase, CommonStandaloneChallengeTests):
    default_url = '/1/bundle/challenge/standalone/submit/'

    def setUp(self):
        super(StandaloneSubmitTestcase, self).setUp()
        flag = {
            KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0,
        }
        self.env.kolmogor.set_response_value('get', flag)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.retpath = TEST_RETPATH
            track.paymethod_id = TEST_CARD_ID

    @property
    def http_query_args(self):
        return dict(
            track_id=self.track_id,
        )

    @property
    def common_response_values(self):
        return dict(
            super(StandaloneSubmitTestcase, self).common_response_values,
            retpath=TEST_RETPATH,
        )

    def expected_response(self, phone_confirmation_challenge=True, webauthn_challenge=False, is_3ds_challened=False, dictation_challenge=False,
                          default_challenge='phone_confirmation'):
        response = dict(
            self.common_response_values,
            challenges_enabled={},
            default_challenge=default_challenge,
        )
        if phone_confirmation_challenge:
            response['challenges_enabled']['phone_confirmation'] = {
                'hint': '+7 926 ***-**-67',
                'phone_id': 1,
                'phone_number': TEST_PHONE_NUMBER.e164,
            }
        if webauthn_challenge:
            response['challenges_enabled']['webauthn'] = {
                'hint': None,
                'credentials': [
                    {
                        'device_name': TEST_DEVICE_NAME,
                        'os_family_name': 'Android',
                        'browser_name': 'ChromeMobile',
                        'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    },
                ],
            }
        if is_3ds_challened:
            response['challenges_enabled']['3ds'] = {
                'hint': None,
            }
        if dictation_challenge:
            response['challenges_enabled']['dictation'] = {
                'hint': '+7 926 ***-**-67',
                'phone_id': 1,
                'phone_number': TEST_PHONE_NUMBER.e164,
            }

        return response

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(is_3ds_challened=True)
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'shown',
                challenges='phone_confirmation,3ds',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
            ]
        )

    def test_ok_with_webauthn_via_cookie(self):
        resp = self.make_request(
            headers={'cookie': TEST_COOKIES_WITH_WCID},
        )
        self.assert_ok_response(
            resp,
            **self.expected_response(webauthn_challenge=True, is_3ds_challened=True, default_challenge='webauthn')
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'shown',
                challenges='webauthn,phone_confirmation,3ds',
                default_challenge='webauthn',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
            ]
        )

    def test_ok_with_webauthn_via_useragent(self):
        self.setup_blackbox_response(has_sms_2fa=True)
        resp = self.make_request(
            headers={'user_agent': TEST_USER_AGENT_SUITABLE_FOR_WEBAUTHN},
        )
        self.assert_ok_response(
            resp,
            **self.expected_response(webauthn_challenge=True, is_3ds_challened=True, default_challenge='webauthn')
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'shown',
                challenges='webauthn,phone_confirmation,3ds',
                default_challenge='webauthn',
                user_agent=TEST_USER_AGENT_SUITABLE_FOR_WEBAUTHN,
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
            ]
        )

    def test_ok_with_antifraud_tags(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['webauthn']

        resp = self.make_request(
            headers={'cookie': TEST_COOKIES_WITH_WCID},
        )
        self.assert_ok_response(
            resp,
            **self.expected_response(
                phone_confirmation_challenge=False,
                webauthn_challenge=True,
                default_challenge='webauthn',
            )
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'shown',
                challenges='webauthn',
                default_challenge='webauthn',
            ),
            ]
        )

    def test_ok_dictation_with_antifraud_tags(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.antifraud_tags = ['dictation']

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.expected_response(
                phone_confirmation_challenge=False,
                dictation_challenge=True,
                default_challenge='dictation',
            )
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.phone_valid_for_call, True)
        eq_(track.phone_valid_for_flash_call, False)
        eq_(track.phone_validated_for_call, TEST_PHONE_NUMBER.e164)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry(
                'shown',
                challenges='dictation',
                default_challenge='dictation',
                phone_confirmation_enabled_for_app_id='0',
                uid_in_experiment='1',
                client_can_send_sms='1',
            ),
            ]
        )

    def test_sessionid_missing(self):
        resp = self.make_request(headers={'cookie': 'foo=bar'})
        self.assert_error_response(resp, ['sessionid.invalid'], **self.common_response_values)
