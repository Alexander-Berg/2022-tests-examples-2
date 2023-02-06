# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

from django.conf import settings
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    CommonCookieTests,
)
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
    TEST_GRANT_TYPE,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.utils import iter_eq


class TestRevokeToken(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_revoke_token')
    http_method = 'POST'

    def setUp(self):
        super(TestRevokeToken, self).setUp()
        self.setup_blackbox_response(age=100)

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'token_id': 123,
        }

    def _check_statbox_ok(self, token_to_drop, has_alias='0'):
        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'iface_revoke_token',
                'status': 'ok',
                'client_id': str(self.test_client.display_id),
                'token_id': str(token_to_drop.id),
                'has_alias': has_alias,
                'uid': str(TEST_UID),
                'created': TimeNow(),
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
        )

    def _check_historydb_ok(self, token_to_drop, has_alias='0'):
        self.check_historydb_event_entry(
            {
                'action': 'invalidate',
                'target': 'token',
                'reason': 'iface_revoke_token',
                'uid': str(TEST_UID),
                'token_id': str(token_to_drop.id),
                'client_id': self.test_client.display_id,
                'scopes': 'test:foo,test:bar',
                'has_alias': has_alias,
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
            entry_index=-1,
        )

    def test_ok_single_token(self):
        token_to_drop = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        alive_token = issue_token(uid=TEST_OTHER_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)

        rv = self.make_request(uid=TEST_UID, token_id=token_to_drop.id)

        self.assert_status_ok(rv)
        eq_(list_tokens_by_uid(TEST_UID), [])
        eq_(list_tokens_by_uid(TEST_OTHER_UID), [alive_token])
        self._check_statbox_ok(token_to_drop)
        self._check_historydb_ok(token_to_drop)

    def test_ok_single_token_user_has_no_password(self):
        self.setup_blackbox_response(have_password=False, age=-1)
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

        self.setup_blackbox_response(have_password=False, age=-1)
        rv = self.make_request(uid=TEST_UID, token_id=token_to_drop.id)

        self.assert_status_ok(rv)
        eq_(list_tokens_by_uid(TEST_UID), [])
        eq_(list_tokens_by_uid(TEST_OTHER_UID), [alive_token])
        self._check_statbox_ok(token_to_drop)
        self._check_historydb_ok(token_to_drop)

    def test_ok_many_tokens(self):
        token_to_drop = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        another_token_to_drop = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id='foo',
            env=self.env,
        )
        alive_token = issue_token(
            uid=TEST_OTHER_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )

        rv = self.make_request(uid=TEST_UID, token_id=[token_to_drop.id, another_token_to_drop.id])

        self.assert_status_ok(rv)
        eq_(list_tokens_by_uid(TEST_UID), [])
        eq_(list_tokens_by_uid(TEST_OTHER_UID), [alive_token])

    def test_ok_app_password(self):
        token_to_drop = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            make_alias=True,
        )

        rv = self.make_request(uid=TEST_UID, token_id=token_to_drop.id)

        self.assert_status_ok(rv)
        eq_(list_tokens_by_uid(TEST_UID), [])
        self._check_statbox_ok(token_to_drop, has_alias='1')
        self._check_historydb_ok(token_to_drop, has_alias='1')

    def test_token_not_found(self):
        rv = self.make_request(uid=TEST_UID, token_id=100500)
        self.assert_status_ok(rv)
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
        ])
        self.check_historydb_event_entries([])

    def test_not_owner(self):
        token_to_drop = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request(uid=TEST_OTHER_UID, token_id=token_to_drop.id)
        self.assert_status_error(rv, ['token.owner_required'])

    def test_password_not_entered(self):
        self.setup_blackbox_response(age=-1)
        rv = self.make_request()
        self.assert_status_error(rv, ['password.required'])

    def test_password_not_entered_recently(self):
        self.setup_blackbox_response(age=100500)
        rv = self.make_request()
        self.assert_status_error(rv, ['password.required'])


class TestDeleteDeviceTokens(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_revoke_device_tokens')
    http_method = 'POST'

    def setUp(self):
        super(TestDeleteDeviceTokens, self).setUp()
        self.setup_blackbox_response()

    def create_client(self):
        with CREATE(Client.create(
            uid=TEST_OTHER_UID,
            scopes=[Scope.by_keyword('test:foo')],
            redirect_uris=['https://callback'],
            default_title='test_client2',
        )) as client:
            pass
        return client

    def issue_token_by_client(self, client=None, expired=False,
                              is_app_password=False, device_id='foo-foo'):
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

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'device_id': 'foo-foo',
        }

    def assert_logs_ok(self, token_id, client=None):
        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'token',
                'reason': 'iface_revoke_device_tokens',
                'status': 'ok',
                'client_id': str((client or self.test_client).display_id),
                'device_id': 'foo-foo',
                'token_id': str(token_id),
                'has_alias': '0',
                'uid': str(TEST_UID),
                'created': TimeNow(),
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
        )
        self.check_historydb_event_entry(
            {
                'action': 'invalidate',
                'target': 'token',
                'reason': 'iface_revoke_device_tokens',
                'uid': str(TEST_UID),
                'token_id': str(token_id),
                'client_id': str((client or self.test_client).display_id),
                'scopes': 'test:foo,test:bar',
                'has_alias': '0',
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
                'device_id': 'foo-foo',
            },
        )

    def test_ok(self):
        client2 = self.create_client()
        token1 = self.issue_token_by_client()
        token2 = self.issue_token_by_client(is_app_password=True, client=client2, device_id='qdaxefw')
        token3 = self.issue_token_by_client(device_id='bar-bar')

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
        client2 = self.create_client()
        token1 = self.issue_token_by_client(expired=True)
        token2 = self.issue_token_by_client(is_app_password=True, client=client2, expired=True)
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token1, token2])

        rv = self.make_request()
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        iter_eq(tokens, [token1, token2])

    def test_already_revoked(self):
        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_REVOKER_TOKENS: int(time() + 5)},
        )
        client2 = self.create_client()

        token1 = self.issue_token_by_client()
        token2 = self.issue_token_by_client(is_app_password=True, client=client2, device_id='random')
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token1, token2])

        rv = self.make_request()
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        iter_eq(tokens, [token1, token2])

    def test_user_glogouted_ok(self):
        self.setup_blackbox_response(attributes={settings.BB_ATTR_GLOGOUT: time() + 10})
        token = self.issue_token_by_client()
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

        rv = self.make_request()
        self.assert_response_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

    def test_client_glogouted_ok(self):
        token = self.issue_token_by_client()
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
        rv = self.make_request(device_id='foo-bar')
        self.assert_response_ok(rv)
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(tokens, [])

    def test_password_not_entered(self):
        self.setup_blackbox_response(age=-1)
        rv = self.make_request()
        self.assert_status_error(rv, ['password.required'])

    def test_password_not_entered_recently(self):
        self.setup_blackbox_response(age=200000)
        rv = self.make_request()
        self.assert_status_error(rv, ['password.required'])

    def test_no_password(self):
        self.setup_blackbox_response(
            age=-1,
            have_password=False,
        )
        token = self.issue_token_by_client()
        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        eq_(tokens, [token])

        rv = self.make_request()
        self.assert_response_ok(rv)

        eq_(list_tokens_by_uid(TEST_UID), list())
