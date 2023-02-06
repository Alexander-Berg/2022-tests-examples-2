# -*- coding: utf-8 -*-
from passport.backend.core.builders.blackbox import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_OAUTH_VALID_STATUS,
    BlackboxInvalidParamsError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
)
from passport.backend.perimeter.auth_api.oauth.checker import OAuthChecker
from passport.backend.perimeter.auth_api.test import BaseTestCase


TEST_LOGIN = 'vasya'
TEST_TOKEN = 'a' * 32
TEST_IP = '1.2.3.4'
TEST_SCOPE = 'mail:imap_full'


class TestOAuthChecker(BaseTestCase):
    def setUp(self):
        super(TestOAuthChecker, self).setUp()

        self.checker = OAuthChecker()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {'alias': 'blackbox', 'ticket': 'test-ticket'},
                },
            ),
        )
        self.fake_tvm_credentials_manager.start()

        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()

    def tearDown(self):
        self.fake_blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        super(TestOAuthChecker, self).tearDown()

    def setup_blackbox_response(self, status=BLACKBOX_OAUTH_VALID_STATUS, login=TEST_LOGIN, scope=TEST_SCOPE):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                status=status,
                login=login,
                scope=scope,
            ),
        )

    def assert_blackbox_called(self):
        assert len(self.fake_blackbox.requests) == 1

    def assert_blackbox_not_called(self):
        assert not self.fake_blackbox.requests

    def test_is_enabled(self):
        assert self.checker.is_enabled

    def test_check__ok(self):
        self.setup_blackbox_response()
        result = self.checker.check(TEST_LOGIN, TEST_TOKEN, TEST_IP, allowed_scopes=[TEST_SCOPE])
        assert result.is_ok, result.description
        assert result.description, 'OAuth auth successful'
        self.assert_blackbox_called()

    def test_check__ok_with_several_scopes(self):
        self.setup_blackbox_response(scope='test:foo test:bar')
        result = self.checker.check(TEST_LOGIN, TEST_TOKEN, TEST_IP, allowed_scopes=['test:bar', 'test:zar'])
        assert result.is_ok, result.description
        assert result.description, 'OAuth auth successful'
        self.assert_blackbox_called()

    def test_check__not_a_token(self):
        result = self.checker.check(TEST_LOGIN, 'smth_short', TEST_IP, allowed_scopes=[TEST_SCOPE])
        assert not result.is_ok
        assert result.description == 'OAuth not a token'
        self.assert_blackbox_not_called()

    def test_check__invalid_token(self):
        self.setup_blackbox_response(status=BLACKBOX_OAUTH_INVALID_STATUS)
        result = self.checker.check(TEST_LOGIN, TEST_TOKEN, TEST_IP, allowed_scopes=[TEST_SCOPE])
        assert not result.is_ok
        assert result.description == 'OAuth invalid token'
        self.assert_blackbox_called()

    def test_check__invalid_scope(self):
        self.setup_blackbox_response(scope='login:info')
        result = self.checker.check(TEST_LOGIN, TEST_TOKEN, TEST_IP, allowed_scopes=[TEST_SCOPE])
        assert not result.is_ok
        assert result.description == 'OAuth insufficient scope'
        self.assert_blackbox_called()

    def test_check__invalid_login(self):
        self.setup_blackbox_response(login='petya')
        result = self.checker.check(TEST_LOGIN, TEST_TOKEN, TEST_IP, allowed_scopes=[TEST_SCOPE])
        assert not result.is_ok
        assert result.description == 'OAuth token from another account'
        self.assert_blackbox_called()

    def test_check__blackbox_error(self):
        self.fake_blackbox.set_response_side_effect('oauth', BlackboxInvalidParamsError)
        result = self.checker.check(TEST_LOGIN, TEST_TOKEN, TEST_IP, allowed_scopes=[TEST_SCOPE])
        assert not result.is_ok
        assert result.description == 'OAuth blackbox error'
        self.assert_blackbox_called()
