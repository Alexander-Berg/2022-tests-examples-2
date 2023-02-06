# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_GRANT_TYPE,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.oauth.core.test.utils import parse_tskv_log_entry


class TestRevokeTokens(BundleApiTestCase):
    default_url = reverse_lazy('api_revoke_tokens')
    http_method = 'POST'

    def default_params(self):
        return {
            'consumer': 'dev',
            'uid': TEST_UID,
            'client_id': self.test_client.display_id,
            'client_secret': self.test_client.secret,
        }

    def test_ok(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Тестовое приложение',
            icon='http://icon',
            homepage='http://homepage',
            default_description='Test client',
        )) as other_client:
            pass
        token_from_other_client = issue_token(
            uid=TEST_UID,
            client=other_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        token_to_drop = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        alive_token = issue_token(
            uid=TEST_OTHER_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            [token for token in list_tokens_by_uid(TEST_UID) if not token.is_expired],
            [token_from_other_client],
        )
        eq_(
            [token for token in list_tokens_by_uid(TEST_OTHER_UID) if not token.is_expired],
            [alive_token],
        )

        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'api_revoke_tokens',
                'status': 'ok',
                'client_id': str(self.test_client.display_id),
                'token_id': str(token_to_drop.id),
                'has_alias': '0',
                'uid': str(TEST_UID),
                'created': TimeNow(),
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
            },
        )
        self.check_historydb_event_entry(
            {
                'action': 'invalidate',
                'target': 'token',
                'reason': 'api_revoke_tokens',
                'uid': str(TEST_UID),
                'token_id': str(token_to_drop.id),
                'client_id': self.test_client.display_id,
                'scopes': 'test:foo,test:bar',
                'has_alias': '0',
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
            },
            entry_index=-1,
        )

    def test_historydb_timestamps_equal(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id='foo',
            env=self.env,
        )
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id='bar',
            env=self.env,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)

        historydb_timestamps = [
            parse_tskv_log_entry(self.event_log_handle_mock, entry_index)['timestamp']
            for entry_index in (-1, -2)
        ]
        eq_(historydb_timestamps[0], historydb_timestamps[1])

    def test_client_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_client_secret_not_matched(self):
        rv = self.make_request(client_secret='a' * 32)
        self.assert_status_error(rv, ['client_secret.not_matched'])

    def test_no_tokens(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
