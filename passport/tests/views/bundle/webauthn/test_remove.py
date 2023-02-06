# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseWebauthnTestCase,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_USER_AGENT,
)


EXPECTED_EMPTY_WCID_COOKIE = 'wcid=; Domain=.passport-test.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/'


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
)
class WebauthnRemoveCredentialTestCase(BaseWebauthnTestCase):
    default_url = '/1/bundle/webauthn/credentials/remove/'
    http_query_args = {
        'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
    }

    def assert_historydb_ok(self):
        expected_envents = {
            'action': 'remove_webauthn_credential',
            'user_agent': TEST_USER_AGENT,
            'webauthn_cred.1': 'deleted',
            'webauthn_cred.1.external_id': TEST_CREDENTIAL_EXTERNAL_ID,
        }
        self.assert_events_are_logged(
            self.env.handle_mock,
            expected_envents,
        )

    def test_ok(self):
        self.setup_blackbox_responses(has_webauthn_credentials=True)
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_historydb_ok()

    def test_ok_with_cookie(self):
        self.setup_blackbox_responses(has_webauthn_credentials=True)
        resp = self.make_request(headers={'cookie': 'Session_id=foo; wcid=%s' % TEST_CREDENTIAL_EXTERNAL_ID})
        self.assert_ok_response(
            resp,
            cookies=[EXPECTED_EMPTY_WCID_COOKIE],
        )
        self.assert_historydb_ok()

    def test_no_credential_error(self):
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.impossible'],
        )

    def test_no_uid_in_track_error(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
        )
