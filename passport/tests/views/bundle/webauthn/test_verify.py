# -*- coding: utf-8 -*-
import base64

import mock
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.test_base_data import TEST_UID
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_webauthn_credentials_response
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)

from .base import (
    BaseWebauthnTestCase,
    TEST_AUTH_DATA,
    TEST_AUTH_DATA_BASE64,
    TEST_CHALLENGE_BASE64,
    TEST_CHALLENGE_RANDOM_BYTES,
    TEST_CLIENT_DATA_GET_BASE64,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_EXPECTED_ASSERTION_OPTIONS,
    TEST_ORIGIN,
    TEST_SIGNATURE_HEX,
    TEST_USER_AGENT,
)


TEST_RP_ID = 'passport-test.yandex.ru'


class CommonVerifyTests(object):
    def test_no_uid_error(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['uid.empty'],
        )

    def test_credential_not_found_error(self):
        resp = self.make_request(query_args=dict(credential_external_id='foo'))
        self.assert_error_response(
            resp,
            ['webauthn.credential_not_found'],
        )


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    PASSPORT_SUBDOMAIN='passport-test',
    WEBAUTHN_IS_USER_VERIFICATION_REQUIRED=True,
)
class WebauthnVerifySubmitTestCase(BaseWebauthnTestCase, CommonVerifyTests):
    default_url = '/1/bundle/webauthn/verify/submit/'
    http_query_args = {
        'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
    }

    def setUp(self):
        super(WebauthnVerifySubmitTestCase, self).setUp()
        self.urandom_mock = mock.Mock(return_value=TEST_CHALLENGE_RANDOM_BYTES)
        self.urandom_patch = mock.patch('os.urandom', self.urandom_mock)
        self.urandom_patch.start()
        self.setup_blackbox_responses(has_webauthn_credentials=True)

    def tearDown(self):
        self.urandom_patch.stop()
        super(WebauthnVerifySubmitTestCase, self).tearDown()

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            assertion_options=TEST_EXPECTED_ASSERTION_OPTIONS,
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.webauthn_challenge, TEST_CHALLENGE_BASE64)

    def test_uid_from_request_ok(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None

        resp = self.make_request(query_args=dict(uid=TEST_UID))
        self.assert_ok_response(
            resp,
            assertion_options=TEST_EXPECTED_ASSERTION_OPTIONS,
            track_id=self.track_id,
        )


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
    WEBAUTHN_IS_USER_VERIFICATION_REQUIRED=False,  # чтобы подошли тестовые данные
)
class WebauthnVerifyCommitTestCase(BaseWebauthnTestCase, CommonVerifyTests):
    default_url = '/1/bundle/webauthn/verify/commit/'
    http_query_args = {
        'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
        'origin': TEST_ORIGIN,
        'client_data': TEST_CLIENT_DATA_GET_BASE64,
        'auth_data': TEST_AUTH_DATA_BASE64,
        'signature': TEST_SIGNATURE_HEX,
    }

    def setUp(self):
        super(WebauthnVerifyCommitTestCase, self).setUp()
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.webauthn_challenge = TEST_CHALLENGE_BASE64

        self.setup_blackbox_responses(has_webauthn_credentials=True)

    def setup_blackbox_webauthn_credentials_response(self, uid=None):
        self.env.blackbox.set_blackbox_response_value(
            'webauthn_credentials',
            blackbox_webauthn_credentials_response(
                credential_external_id=TEST_CREDENTIAL_EXTERNAL_ID,
                uid=uid,
            ),
        )

    def assert_historydb_ok(self):
        expected_envents = {
            'action': 'webauthn_verify',
            'user_agent': TEST_USER_AGENT,
            'webauthn_cred.1': 'updated',
            'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
            'webauthn_cred.1.sign_count': '1',
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_envents,
        )

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_historydb_ok()

        track = self.track_manager.read(self.track_id)
        eq_(track.webauthn_confirmed_secret_external_id, TEST_CREDENTIAL_EXTERNAL_ID)

    def test_client_response_invalid(self):
        resp = self.make_request(query_args=dict(
            auth_data=base64.b64encode(b'\x00' + TEST_AUTH_DATA),
        ))
        self.assert_error_response(
            resp,
            ['webauthn.verification_rejected'],
        )

    def test_origin_mismatch(self):
        resp = self.make_request(query_args=dict(
            origin=TEST_ORIGIN + '1',
        ))
        self.assert_error_response(
            resp,
            ['webauthn.verification_rejected'],
        )

    def test_authenticator_not_trusted(self):
        with settings_context(
            WEBAUTHN_IS_USER_VERIFICATION_REQUIRED=True,
        ):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['webauthn.verification_rejected'],
        )
