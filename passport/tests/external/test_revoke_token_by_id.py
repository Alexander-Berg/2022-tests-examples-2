# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_GRANT_TYPE,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.fake_configs import mock_grants
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


class TestRevokeTokenById(BundleApiTestCase):
    default_url = reverse_lazy('api_revoke_token_by_id')
    http_method = 'POST'

    def setUp(self):
        super(TestRevokeTokenById, self).setUp()

        self.fake_grants.set_data({
            'dev': mock_grants(grants={'api': ['revoke_token.base', 'revoke_token.any']}),
        })
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )

        self.token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        self.statbox_handle_mock.reset_mock()
        self.event_log_handle_mock.reset_mock()

    def default_params(self):
        return {
            'consumer': 'dev',
            'token_id': self.token.id
        }

    def assert_token_revoked(self):
        token = Token.by_id(self.token.id)
        eq_(token.expires, DatetimeNow())

        self.check_statbox_entries([
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'api_revoke_token',
                'status': 'ok',
                'client_id': str(self.test_client.display_id),
                'token_id': str(self.token.id),
                'has_alias': '0',
                'uid': str(TEST_UID),
                'created': TimeNow(),
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
            },
        ])
        self.check_historydb_event_entries([
            {
                'action': 'invalidate',
                'target': 'token',
                'reason': 'api_revoke_token',
                'uid': str(TEST_UID),
                'token_id': str(self.token.id),
                'client_id': self.test_client.display_id,
                'scopes': 'test:foo,test:bar',
                'has_alias': '0',
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
            },
        ])

    def assert_token_not_revoked(self):
        token = Token.by_id(self.token.id)
        ok_(token.expires is None)

        self.check_statbox_entries([])
        self.check_historydb_event_entries([])

    def test_any_grant_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        self.assert_token_revoked()

    def test_token_not_found(self):
        rv = self.make_request(token_id=123)
        self.assert_status_ok(rv)
        self.assert_token_not_revoked()

    def test_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        self.assert_token_not_revoked()

    def test_only_mailish_grant_ok(self):
        self.fake_grants.set_data({
            'dev': mock_grants(grants={'api': ['revoke_token.base', 'revoke_token.mailish']}),
        })
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={
                    'mailish': 'foo@gmail.ru',
                },
            ),
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        self.assert_token_revoked()

    def test_mailish_grant_insufficient(self):
        self.fake_grants.set_data({
            'dev': mock_grants(grants={'api': ['revoke_token.base', 'revoke_token.mailish']}),
        })
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={
                    'phonish': 'phne-foo',
                },
            ),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['grants.missing'])
