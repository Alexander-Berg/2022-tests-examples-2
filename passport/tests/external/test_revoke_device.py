# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

from django.conf import settings
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_DEVICE_ID,
    TEST_GRANT_TYPE,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.oauth.core.test.utils import iter_eq


class TestRevokeDevice(BundleApiTestCase):
    default_url = reverse_lazy('api_revoke_device')
    http_method = 'POST'

    def setUp(self):
        super(TestRevokeDevice, self).setUp()
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )
        with CREATE(Client.create(
            uid=TEST_OTHER_UID,
            scopes=[Scope.by_keyword('test:foo')],
            redirect_uris=['https://callback'],
            default_title='test_client2',
        )) as self.other_client:
            pass

    def default_params(self):
        return {
            'consumer': 'dev',
            'uid': TEST_UID,
            'device_id': TEST_DEVICE_ID,
        }

    def issue_token_for_client(self, client=None, expired=False, is_app_password=False, device_id=TEST_DEVICE_ID):
        token = issue_token(
            uid=TEST_UID,
            client=client or self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id=device_id,
            make_alias=is_app_password,
        )
        if expired:
            with UPDATE(token):
                token.expires = datetime.now() - timedelta(seconds=10)
        return token

    def assert_logs_ok(self, token_id, client=None):
        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'api_revoke_device_tokens',
                'status': 'ok',
                'client_id': str((client or self.test_client).display_id),
                'device_id': TEST_DEVICE_ID,
                'token_id': str(token_id),
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
                'reason': 'api_revoke_device_tokens',
                'uid': str(TEST_UID),
                'token_id': str(token_id),
                'client_id': str((client or self.test_client).display_id),
                'scopes': 'test:foo,test:bar',
                'has_alias': '0',
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'device_id': TEST_DEVICE_ID,
            },
        )

    def test_ok(self):
        token1 = self.issue_token_for_client()
        token2 = self.issue_token_for_client(is_app_password=True, client=self.other_client, device_id='qdaxefw')
        token3 = self.issue_token_for_client(device_id='some-other-stuff')

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 3)
        iter_eq(tokens, [token1, token2, token3])

        rv = self.make_request(http_method='POST')
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token2, token3])
        self.assert_logs_ok(token1.id)

    def test_expired(self):
        token1 = self.issue_token_for_client(expired=True)
        token2 = self.issue_token_for_client(is_app_password=True, client=self.other_client, expired=True)
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token1, token2])

        rv = self.make_request()
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        iter_eq(tokens, [token1, token2])

    def test_already_revoked(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={settings.BB_ATTR_REVOKER_TOKENS: int(time() + 5)},
            ),
        )

        token1 = self.issue_token_for_client()
        token2 = self.issue_token_for_client(is_app_password=True, client=self.other_client, device_id='random')
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token1, token2])

        rv = self.make_request()
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token1, token2])

    def test_user_glogouted_ok(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={settings.BB_ATTR_GLOGOUT: int(time() + 5)},
            ),
        )
        token = self.issue_token_for_client()
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

        rv = self.make_request()
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

    def test_client_glogouted_ok(self):
        token = self.issue_token_for_client()
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

        with UPDATE(self.test_client) as client:
            client.glogouted = datetime.now() + timedelta(seconds=10)

        rv = self.make_request()
        self.assert_response_ok(rv)
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

    def test_empty_ok(self):
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(tokens, [])
        rv = self.make_request()
        self.assert_response_ok(rv)
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(tokens, [])
