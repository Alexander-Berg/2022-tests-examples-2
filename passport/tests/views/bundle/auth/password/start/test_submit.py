# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_ENCODED_ENV_FOR_PROFILE,
    TEST_FRETPATH,
    TEST_ORIGIN,
    TEST_RETPATH,
    TEST_SERVICE,
)
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.builders.oauth.faker import issue_device_code_response

from .base import (
    BaseSubmitTestCase,
    TEST_CSRF_TOKEN,
)


class SubmitTestcase(BaseSubmitTestCase):
    url = '/2/bundle/auth/password/submit/?consumer=dev'

    def get_base_query_params(self):
        return {
            'retpath': TEST_RETPATH,
            'service': TEST_SERVICE,
            'origin': TEST_ORIGIN,
            'fretpath': TEST_FRETPATH,
            'clean': 'yes',
        }

    def assert_track_ok(self, with_code=False):
        track = self.track_manager.read(self.track_id)
        ok_(track.is_allow_otp_magic)
        eq_(track.csrf_token, TEST_CSRF_TOKEN)
        eq_(track.retpath, TEST_RETPATH)
        eq_(track.service, TEST_SERVICE)
        eq_(track.origin, TEST_ORIGIN)
        eq_(track.fretpath, TEST_FRETPATH)
        eq_(track.clean, 'yes')
        eq_(track.surface, 'web_password')
        if with_code:
            eq_(track.magic_qr_device_code, 'device-code')
            eq_(track.browser_id, TEST_ENCODED_ENV_FOR_PROFILE['user_agent_info']['BrowserName'])
            eq_(track.os_family_id, TEST_ENCODED_ENV_FOR_PROFILE['user_agent_info']['OSFamily'])
            eq_(track.region_id, TEST_ENCODED_ENV_FOR_PROFILE['region_id'])

    def test_invalid_host_error(self):
        resp = self.make_request(
            headers=self.get_headers(host='google.com'),
        )
        self.assert_error_response(resp, ['host.invalid'])

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            csrf_token=TEST_CSRF_TOKEN,
            track_id=self.track_id,
        )
        self.assert_track_ok()

    def test_with_code_ok(self):
        self.env.oauth.set_response_value(
            'issue_device_code',
            issue_device_code_response(),
        )
        resp = self.make_request(with_code='1')
        self.assert_ok_response(
            resp,
            csrf_token=TEST_CSRF_TOKEN,
            track_id=self.track_id,
            user_code='user-code',
            verification_url='ver-url',
            expires_in=30,
        )
        self.assert_track_ok(with_code=True)

    def test_with_code_oauth_error(self):
        self.env.oauth.set_response_side_effect(
            'issue_device_code',
            OAuthTemporaryError(),
        )
        resp = self.make_request(with_code='1')
        self.assert_error_response(resp, ['backend.oauth_failed'])
        track = self.track_manager.read(self.track_id)
        assert not track.is_allow_otp_magic
