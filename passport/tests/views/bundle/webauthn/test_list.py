# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseWebauthnTestCase,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_DEVICE_NAME,
    TEST_UNIXTIME,
)


@with_settings_hosts()
class WebauthnListCredentialsTestCase(BaseWebauthnTestCase):
    default_url = '/1/bundle/webauthn/credentials/list/'
    http_method = 'GET'

    def test_ok(self):
        self.setup_blackbox_responses(has_webauthn_credentials=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            webauthn_credentials=[
                {
                    'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'device_name': TEST_DEVICE_NAME,
                    'os_family_name': 'Android',
                    'browser_name': 'ChromeMobile',
                    'is_device_mobile': True,
                    'is_device_tablet': False,
                    'created_at': TEST_UNIXTIME,
                    'is_suggested': True,
                },
            ],
        )

    def test_ok_without_optional_params(self):
        self.setup_blackbox_responses(has_webauthn_credentials=True, webautn_cred_kwargs=dict(device_name=None))
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            webauthn_credentials=[
                {
                    'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'device_name': None,
                    'os_family_name': 'Android',
                    'browser_name': 'ChromeMobile',
                    'is_device_mobile': True,
                    'is_device_tablet': False,
                    'created_at': TEST_UNIXTIME,
                    'is_suggested': True,
                },
            ],
        )

    def test_no_suggested_ok(self):
        self.setup_blackbox_responses(has_webauthn_credentials=True)
        resp = self.make_request(headers={'host': 'yandex.com'})
        self.assert_ok_response(
            resp,
            webauthn_credentials=[
                {
                    'external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'device_name': TEST_DEVICE_NAME,
                    'os_family_name': 'Android',
                    'browser_name': 'ChromeMobile',
                    'is_device_mobile': True,
                    'is_device_tablet': False,
                    'created_at': TEST_UNIXTIME,
                    'is_suggested': False,
                },
            ],
        )

    def test_no_credentials_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            webauthn_credentials=[],
        )

    def test_no_uid_in_track_error(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
        )
