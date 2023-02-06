# -*- coding: utf-8 -*-
import base64

import mock
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_webauthn_credentials_response
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base import (
    BaseWebauthnTestCase,
    TEST_ATTESTATION_OBJECT,
    TEST_ATTESTATION_OBJECT_BASE64,
    TEST_BROWSER_ID,
    TEST_CHALLENGE_BASE64,
    TEST_CHALLENGE_RANDOM_BYTES,
    TEST_CLIENT_DATA_CREATE_BASE64,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_CREDENTIAL_PUBLIC_KEY,
    TEST_DEVICE_NAME,
    TEST_EXPECTED_MAKE_CREDENTIAL_OPTIONS,
    TEST_ORIGIN,
    TEST_OS_FAMILY_ID,
    TEST_RP_ID,
    TEST_USER_AGENT,
)


EXPECTED_WCID_COOKIE = 'wcid=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/' % TEST_CREDENTIAL_EXTERNAL_ID


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    PASSPORT_SUBDOMAIN='passport-test',
    WEBAUTHN_IS_USER_VERIFICATION_REQUIRED=False,
    WEBAUTHN_AUTHENTICATOR_ATTACHMENT='platform',
)
class WebauthnAddCredentialSubmitTestCase(BaseWebauthnTestCase):
    default_url = '/1/bundle/webauthn/credentials/add/submit/'

    def setUp(self):
        super(WebauthnAddCredentialSubmitTestCase, self).setUp()
        self.urandom_mock = mock.Mock(return_value=TEST_CHALLENGE_RANDOM_BYTES)
        self.urandom_patch = mock.patch('os.urandom', self.urandom_mock)
        self.urandom_patch.start()

    def tearDown(self):
        self.urandom_patch.stop()
        super(WebauthnAddCredentialSubmitTestCase, self).tearDown()

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            make_credential_options=TEST_EXPECTED_MAKE_CREDENTIAL_OPTIONS,
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.webauthn_challenge, TEST_CHALLENGE_BASE64)

    def test_no_uid_in_track_error(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
        )

    def test_phone_not_found_error(self):
        self.setup_blackbox_responses(has_secure_phone=False)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['phone.not_found'],
        )

    def test_phone_not_confirmed_error(self):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['phone.not_confirmed'],
        )

    def test_limit_reached_error(self):
        with settings_context(WEBAUTHN_CREDENTIALS_MAX_COUNT=0):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['webauthn.credential_limit_reached'],
        )


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
    WEBAUTHN_IS_NONE_ATTESTATION_PERMITTED=True,  # чтобы подошли тестовые данные
    WEBAUTHN_IS_USER_VERIFICATION_REQUIRED=False,  # чтобы подошли тестовые данные
)
class WebauthnAddCredentialCommitTestCase(BaseWebauthnTestCase):
    default_url = '/1/bundle/webauthn/credentials/add/commit/'
    http_query_args = {
        'origin': TEST_ORIGIN,
        'client_data': TEST_CLIENT_DATA_CREATE_BASE64,
        'attestation_object': TEST_ATTESTATION_OBJECT_BASE64,
        'device_name': TEST_DEVICE_NAME,
    }

    def setUp(self):
        super(WebauthnAddCredentialCommitTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.webauthn_challenge = TEST_CHALLENGE_BASE64

        self.setup_blackbox_webauthn_credentials_response()

    def setup_blackbox_webauthn_credentials_response(self, uid=None):
        self.env.blackbox.set_blackbox_response_value(
            'webauthn_credentials',
            blackbox_webauthn_credentials_response(
                credential_external_id=TEST_CREDENTIAL_EXTERNAL_ID,
                uid=uid,
            ),
        )

    def setup_statbox_templates(self):
        super(WebauthnAddCredentialCommitTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'add_credential',
            action='add_credential',
            credential_external_id=TEST_CREDENTIAL_EXTERNAL_ID,
            relying_party_id=TEST_RP_ID,
            device_name=TEST_DEVICE_NAME,
        )

    def assert_statbox_ok(self, with_check_cookies=False):
        entries = []
        if with_check_cookies:
            entries.append(self.env.statbox.entry('check_cookies'))
        entries.append(self.env.statbox.entry('add_credential'))
        self.env.statbox.assert_has_written(entries)

    def assert_historydb_ok(self):
        expected_envents = {
            'action': 'add_webauthn_credential',
            'user_agent': TEST_USER_AGENT,
            'webauthn_cred.1': 'created',
            'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'webauthn_cred.1.public_key': TEST_CREDENTIAL_PUBLIC_KEY,
            'webauthn_cred.1.relying_party_id': TEST_RP_ID,
            'webauthn_cred.1.device_name': TEST_DEVICE_NAME,
            'webauthn_cred.1.browser_id': str(TEST_BROWSER_ID),
            'webauthn_cred.1.os_family_id': str(TEST_OS_FAMILY_ID),
            'webauthn_cred.1.is_device_mobile': '1',
            'webauthn_cred.1.created_at': TimeNow(),
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_envents,
        )

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            cookies=[EXPECTED_WCID_COOKIE],
        )
        self.assert_statbox_ok(with_check_cookies=True)
        self.assert_historydb_ok()

    def test_credential_exists(self):
        self.setup_blackbox_webauthn_credentials_response(uid=TEST_UID)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['webauthn.credential_exists'],
        )

    def test_credential_occupied(self):
        self.setup_blackbox_webauthn_credentials_response(uid=TEST_OTHER_UID)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['webauthn.credential_occupied'],
        )

    def test_client_response_invalid(self):
        resp = self.make_request(query_args=dict(
            attestation_object=base64.b64encode(b'\x00' + TEST_ATTESTATION_OBJECT),
        ))
        self.assert_error_response(
            resp,
            ['webauthn.registration_rejected'],
        )

    def test_origin_mismatch(self):
        resp = self.make_request(query_args=dict(
            origin=TEST_ORIGIN + '1',
        ))
        self.assert_error_response(
            resp,
            ['webauthn.registration_rejected'],
        )

    def test_authenticator_not_trusted(self):
        with settings_context(
            WEBAUTHN_IS_NONE_ATTESTATION_PERMITTED=False,
            WEBAUTHN_IS_USER_VERIFICATION_REQUIRED=True,
        ):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['webauthn.registration_rejected'],
        )

    def test_limit_reached_error(self):
        with settings_context(WEBAUTHN_CREDENTIALS_MAX_COUNT=0):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['webauthn.credential_limit_reached'],
        )
