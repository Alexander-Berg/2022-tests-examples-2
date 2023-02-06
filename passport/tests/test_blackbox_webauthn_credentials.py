# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from six.moves.urllib.parse import urlparse

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


TEST_CRED_ID = 'cred-id'
TEST_UID = 1234


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxWebauthnCredentials(BaseBlackboxRequestTestCase):
    def test_ok(self):
        self.set_blackbox_response_value('''
            {
              "%s": {
                "uid": "%s"
              }
            }
        ''' % (TEST_CRED_ID, TEST_UID))

        response = self.blackbox.webauthn_credentials(TEST_CRED_ID)
        eq_(
            response,
            {
                TEST_CRED_ID: {'uid': TEST_UID}
            }
        )

    def test_not_found(self):
        self.set_blackbox_response_value('''
            {
              "%s": {
                "uid": ""
              }
            }
        ''' % TEST_CRED_ID)

        response = self.blackbox.webauthn_credentials(TEST_CRED_ID)
        eq_(
            response,
            {
                TEST_CRED_ID: {'uid': None}
            }
        )


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxWebauthnCredentialsUrl(BaseBlackboxTestCase):
    def test_ok(self):
        request_info = Blackbox().build_webauthn_credentials_request(TEST_CRED_ID)
        url = urlparse(request_info.url)
        eq_(url.netloc, 'localhost')

        check_all_url_params_match(
            request_info.url,
            {
                'method': 'webauthn_credentials',
                'format': 'json',
                'credential_id': TEST_CRED_ID,
            },
        )
