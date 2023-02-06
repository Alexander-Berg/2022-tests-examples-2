# -*- coding: utf-8 -*-
import base64

from django.urls import reverse_lazy
from django.utils.encoding import smart_bytes
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_REMOTE_ADDR,
    TEST_UID,
)
from passport.backend.oauth.core.test.db_utils import model_to_bb_response
from passport.backend.oauth.core.test.framework import ApiTestCase


class RevokeTokenTestCase(ApiTestCase):
    default_url = reverse_lazy('revoke_token')
    http_method = 'POST'

    def setUp(self):
        super(RevokeTokenTestCase, self).setUp()
        # выдадим токен, чтобы было что инвалидировать
        self.token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='iFridge',
            device_name='Мой холодильник',
        )
        self.setup_blackbox_response(self.token)

    def default_params(self):
        return {
            'client_id': self.test_client.display_id,
            'client_secret': self.test_client.secret,
            'access_token': self.token.access_token,
        }

    def setup_blackbox_response(self, token):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                oauth_token_info={
                    'token_attributes': model_to_bb_response(token),
                },
            ),
        )

    def assert_error(self, rv, error, error_description=None, **kwargs):
        expected = dict(error=error, **kwargs)
        if error_description is not None:
            expected['error_description'] = error_description
        eq_(rv, expected)

    def assert_ok(self, rv):
        eq_(rv, {'status': 'ok'})

    def assert_token_revoked(self):
        token = Token.by_access_token(self.token.access_token)
        ok_(token.is_expired)

    def assert_token_not_revoked(self):
        token = Token.by_access_token(self.token.access_token)
        ok_(not token.is_expired)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok(rv)
        self.assert_token_revoked()
        self.check_historydb_event_entry(
            {
                'action': 'invalidate',
                'target': 'token',
                'reason': 'api_revoke_token',
                'uid': str(TEST_UID),
                'token_id': str(self.token.id),
                'client_id': self.test_client.display_id,
                'device_id': 'iFridge',
                'device_name': 'Мой холодильник',
                'scopes': 'test:foo,test:bar',
                'has_alias': '0',
                'user_ip': TEST_REMOTE_ADDR,
                'consumer_ip': TEST_REMOTE_ADDR,
                'user_agent': 'curl',
            },
            entry_index=-1,
        )

    def test_ok_with_basic_auth(self):
        rv = self.make_request(
            exclude=['client_id', 'client_secret'],
            headers={
                'HTTP_AUTHORIZATION': 'Basic %s' % base64.b64encode(
                    smart_bytes('%s:%s' % (self.test_client.display_id, self.test_client.secret)),
                ).decode(),
            }
        )
        self.assert_ok(rv)
        self.assert_token_revoked()
        self.check_historydb_event_entry(
            {
                'action': 'invalidate',
                'target': 'token',
                'reason': 'api_revoke_token',
                'uid': str(TEST_UID),
                'token_id': str(self.token.id),
                'client_id': self.test_client.display_id,
                'device_id': 'iFridge',
                'device_name': 'Мой холодильник',
                'scopes': 'test:foo,test:bar',
                'has_alias': '0',
                'user_ip': TEST_REMOTE_ADDR,
                'consumer_ip': TEST_REMOTE_ADDR,
            },
            entry_index=-1,
        )

    def test_malformed_header(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={'HTTP_AUTHORIZATION': 'foo'},
        )
        self.assert_error(rv, error='Malformed Authorization header')
        self.assert_token_not_revoked()

    def test_bad_header(self):
        rv = self.make_request(
            expected_status=401,
            exclude=['client_id', 'client_secret'],
            headers={
                'HTTP_AUTHORIZATION': 'Basic %s' % base64.b64encode(b'foo:bar').decode(),
            },
        )
        self.assert_error(rv, error='invalid_client', error_description='Client not found')
        self.assert_token_not_revoked()

    def test_access_token_not_passed(self):
        rv = self.make_request(expected_status=400, exclude=['access_token'])
        self.assert_error(rv, error='invalid_request', error_description='access_token not in POST')
        self.assert_token_not_revoked()

    def test_token_from_other_client(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Тестовое приложение 2',
        )) as other_client:
            pass
        rv = self.make_request(
            expected_status=400,
            client_id=other_client.display_id,
            client_secret=other_client.secret,
        )
        self.assert_error(rv, error='invalid_grant', error_description='Token doesn\'t belong to client')
        self.assert_token_not_revoked()

    def test_token_empty_ok(self):
        rv = self.make_request(access_token='')
        self.assert_ok(rv)
        self.assert_token_not_revoked()

    def test_token_expired_ok(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_ok(rv)
        self.assert_token_not_revoked()

    def test_token_without_device_id(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
        )
        self.setup_blackbox_response(token)
        ok_(token.access_token != self.token.access_token)
        rv = self.make_request(expected_status=400, access_token=token.access_token)
        self.assert_error(rv, error='unsupported_token_type', error_description='Token was issued without device_id')
        self.assert_token_not_revoked()

    def test_stateless_token(self):
        stateless_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='iFridge',
            device_name='Мой холодильник',
            token_type=TOKEN_TYPE_STATELESS,
        )
        self.setup_blackbox_response(stateless_token)
        rv = self.make_request(expected_status=400, access_token=stateless_token.access_token)
        self.assert_error(rv, error='unsupported_token_type', error_description='Token is stateless')
        self.assert_token_not_revoked()
