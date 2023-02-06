# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.oauth import (
    OAuth,
    OAuthTemporaryError,
)
from passport.backend.core.builders.oauth.faker import (
    FakeOAuth,
    oauth_bundle_error_response,
    oauth_bundle_successful_response,
    token_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_UID = 123
TEST_USER_IP = '1.2.3.4'
TEST_CLIENT_ID = 'test_client_id'
TEST_CLIENT_SECRET = 'test_client_secret'


@with_settings(
    OAUTH_URL='http://localhost/',
    OAUTH_CONSUMER='passport',
)
class FakeOAuthTestCase(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'oauth',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.faker = FakeOAuth()
        self.faker.start()
        self.oauth = OAuth()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_token_by_session_id(self):
        self.faker.set_response_value('_token', token_response())
        eq_(
            self.oauth.token_by_sessionid(
                TEST_CLIENT_ID,
                TEST_CLIENT_SECRET,
                'test_sessionid',
                'yandex.com',
                TEST_USER_IP,
            ),
            {
                'token_type': 'bearer',
                'access_token': '1234',
                'expires_in': 30,
            },
        )

    def test_token_by_uid_id(self):
        self.faker.set_response_value('_token', token_response())
        eq_(
            self.oauth.token_by_uid(
                TEST_CLIENT_ID,
                TEST_CLIENT_SECRET,
                '123456789',
                TEST_USER_IP,
            ),
            {
                'token_type': 'bearer',
                'access_token': '1234',
                'expires_in': 30,
            },
        )

    def test_issue_authorization_code_ok(self):
        self.faker.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(code='1234', expires_in=600),
        )
        eq_(
            self.oauth.issue_authorization_code(
                TEST_CLIENT_ID,
                TEST_CLIENT_SECRET,
                {},
            ),
            {
                'status': 'ok',
                'code': '1234',
                'expires_in': 600,
            },
        )

    @raises(OAuthTemporaryError)
    def test_issue_authorization_code_error(self):
        self.faker.set_response_value(
            'issue_authorization_code',
            oauth_bundle_error_response(error='backend.failed'),
        )
        self.oauth.issue_authorization_code(
            TEST_CLIENT_ID,
            TEST_CLIENT_SECRET,
            {},
        )

    def test_device_status_ok(self):
        self.faker.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=None, device_name=None),
        )
        eq_(
            self.oauth.device_status(uid=TEST_UID),
            {
                'status': 'ok',
                'has_auth_on_device': False,
                'device_id': None,
                'device_name': None,
            },
        )

    def test_device_authorize_submit_ok(self):
        self.faker.set_response_value(
            'device_authorize_submit',
            oauth_bundle_successful_response(),
        )
        eq_(
            self.oauth.device_authorize_submit('ru', '12345', TEST_CLIENT_ID, TEST_UID),
            {'status': 'ok'},
        )

    @raises(OAuthTemporaryError)
    def test_device_authorize_submit_error(self):
        self.faker.set_response_value(
            'device_authorize_submit',
            oauth_bundle_error_response(error='backend.failed'),
        )
        self.oauth.device_authorize_submit('ru', '12345', TEST_CLIENT_ID, TEST_UID),

    def test_device_authorize_commit_ok(self):
        self.faker.set_response_value(
            'device_authorize_commit',
            oauth_bundle_successful_response(),
        )
        eq_(
            self.oauth.device_authorize_commit('ru', '12345', TEST_CLIENT_ID, TEST_UID),
            {'status': 'ok'},
        )

    @raises(OAuthTemporaryError)
    def test_device_authorize_commit_error(self):
        self.faker.set_response_value(
            'device_authorize_commit',
            oauth_bundle_error_response(error='backend.failed'),
        )
        self.oauth.device_authorize_commit('ru', '12345', TEST_CLIENT_ID, TEST_UID),
