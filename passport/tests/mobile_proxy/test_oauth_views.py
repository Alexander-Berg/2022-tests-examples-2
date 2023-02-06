# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import BaseMobileProxyTestCase
from .test_base_data import (
    TEST_DISPLAY_NAME,
    TEST_HOST,
    TEST_OAUTH_TOKEN,
    TEST_SESSIONID_VALUE,
    TEST_UID,
    TEST_USER_IP,
)


TEST_LOGIN = 'test.login'
TEST_NORMALIZED_LOGIN = 'test-login'
TEST_LOGIN_ID = 'login-id'

TEST_CLIENT_ID = 'client_id'
TEST_CLIENT_SECRET = 'client_secret'
TEST_DEVICE_NAME = 'Vasja Poupkine iPhone'


@with_settings_hosts()
class OAuthViewsTestCase(BaseMobileProxyTestCase):
    def setUp(self):
        super(OAuthViewsTestCase, self).setUp()
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_response(
                uid=TEST_UID,
                login=TEST_NORMALIZED_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                login_id=TEST_LOGIN_ID,
            ),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer'
            },
        )

    def test_social_token_ok(self):
        rv = self.make_request(
            'mobileproxy/1/social_token',
            data={
                'sessionid': TEST_SESSIONID_VALUE,
                'host': TEST_HOST,
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'device_name': TEST_DEVICE_NAME,
            },
        )
        self.check_json_ok(
            rv,
            oauth={
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
                'uid': TEST_UID,
            },
            display_name={'name': TEST_DISPLAY_NAME, 'display_name_empty': False},
        )
        self.env.oauth.requests[0].assert_post_data_contains({
            'grant_type': 'passport_assertion',
            'assertion': TEST_UID,
            'password_passed': False,
            'login_id': TEST_LOGIN_ID,
        })
        self.env.oauth.requests[0].assert_query_contains({
            'user_ip': TEST_USER_IP,
            'device_name': TEST_DEVICE_NAME,
        })

    def test_social_token_params_missing(self):
        rv = self.make_request(
            'mobileproxy/1/social_token',
            data={},
        )
        self.check_xml_error(rv, 'missing parameter \'client_id\'')

    def test_social_token_session_invalid(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_response(
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/social_token',
            data={
                'sessionid': TEST_SESSIONID_VALUE,
                'host': TEST_HOST,
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
            },
        )
        self.check_json_error(
            rv,
            error='invalid_grant',
            description='Session not valid',
        )
        self.env.statbox.assert_has_written(
            [
                self.env.statbox.entry('check_cookies', ['consumer'], client_id=TEST_CLIENT_ID),
            ]
        )

    def test_social_token_client_secret_invalid(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'error': 'invalid_client',
                'error_description': 'Wrong client secret'
            },
        )
        rv = self.make_request(
            'mobileproxy/1/social_token',
            data={
                'sessionid': TEST_SESSIONID_VALUE,
                'host': TEST_HOST,
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
            },
        )
        self.check_json_error(
            rv,
            error='invalid_client',
            error_description='Wrong client secret',
        )

    def test_social_token_wrong_sessguard(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_response(
                status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/social_token',
            data={
                'sessionid': TEST_SESSIONID_VALUE,
                'host': TEST_HOST,
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
            },
        )
        self.check_json_error(
            rv,
            error='invalid_grant',
            description='Session not valid',
        )
