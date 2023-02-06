# -*- coding: utf-8 -*-
from base64 import b64encode

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_HOST
from passport.backend.api.views.bundle.account.secrets.passman_recovery_key import (
    PASSMAN_RECOVERY_KEY_GRANT,
    PASSMAN_RECOVERY_KEY_READ_SCOPE,
    PASSMAN_RECOVERY_KEY_WRITE_SCOPE,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_recovery_keys_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.counters import passman_recovery_key_counter
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


TEST_LOGIN = 'login'
TEST_UID = 1
TEST_OTHER_LOGIN = 'login2'
TEST_OTHER_UID = 2
TEST_TOKEN = '123456'
TEST_SESSIONID = 'foo'
TEST_AUTHORIZATION_HEADER = 'OAuth %s' % TEST_TOKEN
TEST_KEY_ID = 'some-\0-id'
TEST_KEY_ID_B64 = b64encode(TEST_KEY_ID)
TEST_RECOVERY_KEY = 'some-\0-key'
TEST_RECOVERY_KEY_B64 = b64encode(TEST_RECOVERY_KEY)
TEST_USER_IP = '8.8.8.8'


@nottest
@with_settings_hosts(
    BLACKBOX_URL='localhost',
    **mock_counters(PASSMAN_RECOVERY_KEY_ADD_COUNTER=(24, 3600, 1))
)
class TestSecretsPassmanRecoveryBase(BaseBundleTestViews):
    http_headers = dict(
        user_ip=TEST_USER_IP,
        authorization=TEST_AUTHORIZATION_HEADER,
    )
    statbox_action = None
    required_scope = None

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def set_grants(self):
        prefix, suffix = PASSMAN_RECOVERY_KEY_GRANT.split('.')
        self.env.grants.set_grants_return_value(mock_grants(
            grants={prefix: [suffix]},
        ))

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='account_secrets_passman_recovery_key',
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'completed',
            uid=str(TEST_UID),
        )

    def setup_blackbox_responses(self, has_key=False, password_verification_age=0):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope=self.required_scope,
                crypt_password='1:pwd',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    crypt_password='1:pwd',
                    age=password_verification_age,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                crypt_password='1:pwd',
                age=password_verification_age,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_recovery_keys',
            blackbox_get_recovery_keys_response(TEST_RECOVERY_KEY_B64 if has_key else None),
        )

    def check_db_ok(self, centraldb_query_count=0, sharddb_query_count=1,
                    key_id=TEST_KEY_ID, recovery_key=TEST_RECOVERY_KEY):

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_query_count)

        if key_id is not None and recovery_key is not None:
            self.env.db.check(
                'passman_recovery_keys',
                'recovery_key',
                recovery_key,
                key_id=key_id,
                db='passportdbshard1',
            )
        else:
            self.env.db.check_missing(
                'passman_recovery_keys',
                'recovery_key',
                db='passportdbshard1',
            )

    def assert_events_ok(self):
        expected_log_entries = {
            'action': 'passman_recovery_key',
            'consumer': 'dev',
            'info.passman_key_id': TEST_KEY_ID_B64,
        }
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def assert_events_empty(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_statbox_empty(self):
        self.env.statbox.assert_has_written([])

    def assert_statbox_ok(self):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'completed',
                action=self.statbox_action,
            ),
        ])

    def check_blackbox_calls(self, call_count=2, by_token=True, user_ip=TEST_USER_IP, uid=TEST_UID, token=TEST_TOKEN):
        eq_(len(self.env.blackbox.requests), call_count)
        if call_count >= 1:
            if by_token:
                self.env.blackbox.requests[0].assert_query_contains({
                    'method': 'oauth',
                    'oauth_token': token,
                    'userip': user_ip,
                    'format': 'json',
                })
            else:
                self.env.blackbox.requests[0].assert_query_contains({
                    'method': 'sessionid',
                    'sessionid': TEST_SESSIONID,
                    'userip': user_ip,
                    'format': 'json',
                })
        if call_count >= 2:
            self.env.blackbox.requests[1].assert_query_equals({
                'method': 'get_recovery_keys',
                'uid': str(uid),
                'key_id': TEST_KEY_ID_B64,
                'format': 'json',
            })

    def test_bad_authorization_fails(self):
        resp = self.make_request(headers=dict(authorization='not-oauth'))
        self.assert_error_response(resp, ['authorization.invalid'])

        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls(call_count=0)

    def test_account_disabled_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_DISABLED_STATUS),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['oauth_token.invalid'])

        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls(call_count=1)

    def test_blackbox_status_invalid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['oauth_token.invalid'])

        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls(call_count=1)

    def test_token_scopes_insufficient_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope='123'),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['oauth_token.invalid'])

        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls(call_count=1)

    def test_account_without_password_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=self.required_scope),
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['account.without_password'])

        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls(call_count=1)


@istest
class TestSecretsReadPassmanRecoveryKeyView(TestSecretsPassmanRecoveryBase):

    default_url = '/1/bundle/account/secrets/passman_recovery_key/'
    http_method = 'get'
    http_query_args = dict(
        consumer='dev',
        key_id=TEST_KEY_ID_B64,
    )

    statbox_action = 'read'
    required_scope = PASSMAN_RECOVERY_KEY_READ_SCOPE

    def test_ok_by_token(self):
        self.setup_blackbox_responses(has_key=True)

        resp = self.make_request()
        self.assert_ok_response(resp, recovery_key=TEST_RECOVERY_KEY_B64)

        self.check_blackbox_calls()

    def test_ok_by_session(self):
        self.setup_blackbox_responses(has_key=True)

        resp = self.make_request(
            exclude_headers=['authorization'],
            headers={'cookie': 'Session_id=foo', 'host': TEST_HOST},
        )
        self.assert_ok_response(resp, recovery_key=TEST_RECOVERY_KEY_B64)

        self.check_blackbox_calls(by_token=False)

    def test_ok_by_session_with_other_user(self):
        self.setup_blackbox_responses(has_key=True)

        resp = self.make_request(
            exclude_headers=['authorization'],
            headers={'cookie': 'Session_id=foo', 'host': TEST_HOST},
            query_args=dict(uid=TEST_OTHER_UID),
        )
        self.assert_ok_response(resp, recovery_key=TEST_RECOVERY_KEY_B64)

        self.check_blackbox_calls(by_token=False, uid=TEST_OTHER_UID)

    def test_password_required(self):
        self.setup_blackbox_responses(has_key=True, password_verification_age=301)

        resp = self.make_request(
            exclude_headers=['authorization'],
            headers={'cookie': 'Session_id=foo', 'host': TEST_HOST},
        )
        self.assert_error_response(resp, ['password.required'])

    def test_key_missing_ok(self):
        self.setup_blackbox_responses(has_key=False)

        resp = self.make_request()
        self.assert_ok_response(resp, recovery_key=None)

        self.check_blackbox_calls()

    def test_no_authorization_fails(self):
        resp = self.make_request(exclude_headers=['authorization'])
        self.assert_error_response(resp, ['request.credentials_all_missing'])

        self.check_blackbox_calls(call_count=0)


@istest
class TestSecretsWritePassmanRecoveryKeyView(TestSecretsPassmanRecoveryBase):

    default_url = '/1/bundle/account/secrets/passman_recovery_key/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        key_id=TEST_KEY_ID_B64,
        recovery_key=TEST_RECOVERY_KEY_B64,
    )

    statbox_action = 'saved'
    required_scope = PASSMAN_RECOVERY_KEY_WRITE_SCOPE

    def assert_counter_value(self, value):
        counter = passman_recovery_key_counter.get_counter()
        eq_(counter.get(TEST_UID), value)

    def test_create_key_ok(self):
        self.setup_blackbox_responses(has_key=False)

        resp = self.make_request()
        self.assert_ok_response(resp, uid=str(TEST_UID), login=TEST_LOGIN)
        self.check_db_ok()
        self.assert_events_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()
        self.assert_counter_value(1)

    def test_update_forbidden(self):
        self.setup_blackbox_responses(has_key=True)

        resp = self.make_request()
        self.assert_error_response(resp, ['recovery_key.exists'])
        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls()
        self.assert_counter_value(0)

    def test_rate_limit_exceeded(self):
        counter = passman_recovery_key_counter.get_counter()
        counter.incr(TEST_UID)

        self.setup_blackbox_responses(has_key=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])
        self.assert_counter_value(1)

    def test_no_authorization_fails(self):
        resp = self.make_request(exclude_headers=['authorization'])
        self.assert_error_response(resp, ['authorization.empty'])

        self.check_db_ok(sharddb_query_count=0, key_id=None, recovery_key=None)
        self.assert_events_empty()
        self.assert_statbox_empty()
        self.check_blackbox_calls(call_count=0)
