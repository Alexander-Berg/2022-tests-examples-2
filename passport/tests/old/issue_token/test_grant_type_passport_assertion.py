# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.api.tests.old.issue_token.base import CommonRateLimitsTests
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import Token
from passport.backend.oauth.core.test.base_test_data import (
    TEST_LOGIN_ID,
    TEST_NORMALIZED_LOGIN,
    TEST_UID,
)
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry

from .test_grant_type_assertion import TestIssueTokenByAssertion


class TestIssueTokenByPassportAssertion(TestIssueTokenByAssertion, CommonRateLimitsTests):
    grant_type = 'passport_assertion'

    def setUp(self):
        super(TestIssueTokenByPassportAssertion, self).setUp()
        self.fake_grants.set_data({})

    def test_account_type_forbidden__special_client(self):
        pass  # тест родителя неприменим

    def test_ok_with_password_passed(self):
        rv = self.make_request(password_passed='1')
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv, password_passed=True)
        self.assert_statbox_ok()
        self.assert_antifraud_log_ok(password_passed=True)

    def test_ok_with_login_id(self):
        rv = self.make_request(login_id=TEST_LOGIN_ID)
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.login_id, TEST_LOGIN_ID)
        self.assert_antifraud_log_ok(login_id=TEST_LOGIN_ID, previous_login_id=TEST_LOGIN_ID)

    def test_ok_with_extra_log_params(self):
        rv = self.make_request(cloud_token='cl-xxx', passport_track_id='track-id')
        self.assert_token_response_ok(rv)
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(cloud_token='cl-xxx', passport_track_id='track-id'),
        )
        self.assert_antifraud_log_ok(external_id='track-track-id')
        self.assert_credentials_log_ok(track_id='track-id', login=TEST_NORMALIZED_LOGIN)

    def test_rate_limit_exceeded_uid(self):
        self.fake_kolmogor.set_response_value('get', '3')
        with self.override_rate_limit_settings():
            rv = self.make_request(expected_status=429)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='Too many requests',
        )
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(
                reason='rate_limit_exceeded',
                status='error',
                key='grant_type:%s:uid:%s' % (self.grant_type, TEST_UID),
                value='3',
                limit='2',
                uid=str(TEST_UID),
                client_id=self.test_client.display_id,
            ),
        )
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)

    def test_default_not_set_is_xtoken_trusted(self):
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        self.assertEqual(token.is_xtoken_trusted, False)

    def test_set_auth_source_sessionid(self):
        rv = self.make_request(auth_source='sessionid')
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_statbox_ok()
        self.assert_antifraud_log_ok(auth_source='sessionid')

    def test_set_is_xtoken_trusted(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:xtoken')])
        rv = self.make_request(set_is_xtoken_trusted=True)
        self.assert_token_response_ok(rv)
        self.assert_blackbox_ok()
        self.assert_historydb_ok(rv, scopes='test:xtoken')
        self.assert_statbox_ok()
        self.assert_antifraud_log_ok()
        token = Token.by_access_token(rv['access_token'])
        self.assertEqual(token.is_xtoken_trusted, True)

    def test_set_is_xtoken_trusted_non_xtoken_error(self):
        rv = self.make_request(set_is_xtoken_trusted=True, expected_status=400)
        self.assert_error(rv, 'invalid_request', 'Cannot set is_xtoken_trusted for non-xtoken')

    def test_set_is_xtoken_trusted_force_db_write(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:xtoken')])
        rv = self.make_request()
        self.assert_token_response_ok(rv)

        rv = self.make_request(set_is_xtoken_trusted=True)
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        self.assertEqual(token.is_xtoken_trusted, True)

    def test_set_is_xtoken_trusted_no_downgrade(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:xtoken')])
        rv = self.make_request(set_is_xtoken_trusted=True)
        self.assert_token_response_ok(rv)

        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        self.assertEqual(token.is_xtoken_trusted, True)
