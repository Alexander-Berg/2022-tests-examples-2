# -*- coding: utf-8 -*-
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.core.builders.oauth.faker import (
    oauth_bundle_error_response,
    oauth_bundle_successful_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_HOST = 'passport.yandex.ru'
TEST_USER_AGENT = 'curl'
TEST_COOKIE = 'Session_id=foo; sessionid2=bar'

TEST_CODE = 'abcdefgh123456'
TEST_DEFAULT_CLIENT_ID = 'cl_id'
TEST_DEFAULT_CLIENT_SECRET = 'cl_sec'
TEST_OTHER_CLIENT_ID = 'cl_id2'
TEST_OTHER_CLIENT_SECRET = 'cl_sec2'


@with_settings_hosts(
    OAUTH_URL='http://oauth.localhost',
    OAUTH_APPLICATION_AM_XTOKEN={
        'client_id': TEST_DEFAULT_CLIENT_ID,
        'client_secret': TEST_DEFAULT_CLIENT_SECRET,
    },
)
class OAuthIssueCodeTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/auth/oauth/code_for_am/?consumer=dev'
    http_method = 'POST'
    http_headers = {
        'host': TEST_HOST,
        'user_ip': TEST_IP,
        'user_agent': TEST_USER_AGENT,
        'cookie': TEST_USER_COOKIES,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_oauth': ['issue_code']})
        )

        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(code=TEST_CODE, expires_in=600),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv, code=TEST_CODE, expires_in=600)
        self.env.oauth.requests[0].assert_post_data_equals({
            'consumer': 'passport',
            'code_strength': 'long',
            'ttl': 600,
            'require_activation': '0',
            'client_id': TEST_DEFAULT_CLIENT_ID,
            'client_secret': TEST_DEFAULT_CLIENT_SECRET,
        })

    def test_ok_with_custom_client_and_uid(self):
        rv = self.make_request(
            query_args=dict(
                client_id=TEST_OTHER_CLIENT_ID,
                client_secret=TEST_OTHER_CLIENT_SECRET,
                uid=TEST_UID,
            ),
        )
        self.assert_ok_response(rv, code=TEST_CODE, expires_in=600)
        self.env.oauth.requests[0].assert_post_data_equals({
            'consumer': 'passport',
            'code_strength': 'long',
            'ttl': 600,
            'require_activation': '0',
            'client_id': TEST_OTHER_CLIENT_ID,
            'client_secret': TEST_OTHER_CLIENT_SECRET,
            'uid': str(TEST_UID),
        })

    def test_cookie_invalid(self):
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_error_response(error='sessionid.invalid'),
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['sessionid.invalid'])
