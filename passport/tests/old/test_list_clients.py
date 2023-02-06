# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

from django.conf import settings
from django.urls import (
    reverse,
    reverse_lazy,
)
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.core.db.eav import (
    DELETE,
    UPDATE,
)
from passport.backend.oauth.core.db.token import issue_token
from passport.backend.oauth.core.test.framework import ApiTestCase


TEST_UID = 1
TEST_OTHER_UID = 123


class ListClientsByUserTestCase(ApiTestCase):
    default_url = reverse_lazy('list_clients_by_user', args=[TEST_OTHER_UID])
    http_method = 'GET'

    def setUp(self):
        super(ListClientsByUserTestCase, self).setUp()
        self.token = issue_token(
            uid=TEST_OTHER_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='iFridge',
        )

    def default_params(self):
        return {
            'scope': 'test:foo',
        }

    def test_ok(self):
        rv = self.make_request()
        eq_(rv, [self.test_client.display_id])

    def test_scope_missing(self):
        rv = self.make_request(expected_status=400, exclude=['scope'])
        eq_(rv['error'], 'Required parameter is missing: scope')

    def test_scope_not_matched(self):
        rv = self.make_request(scope='test:ttl')
        eq_(rv, [])

    def test_no_clients(self):
        rv = self.make_request(url=reverse('list_clients_by_user', args=[TEST_UID]))
        eq_(rv, [])

    def test_client_deleted(self):
        with DELETE(self.test_client):
            pass
        rv = self.make_request()
        eq_(rv, [])

    def test_token_expired(self):
        with UPDATE(self.token) as token:
            token.expires = datetime.now() - timedelta(10)
        rv = self.make_request()
        eq_(rv, [])

    def test_token_invalidated_by_client_glogout(self):
        with UPDATE(self.test_client) as client:
            client.glogouted = datetime.now() + timedelta(10)
        rv = self.make_request()
        eq_(rv, [])

    def test_token_invalidated_by_user_glogout(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
            ),
        )
        rv = self.make_request()
        eq_(rv, [])

    def test_user_revoked_all_tokens(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={settings.BB_ATTR_REVOKER_TOKENS: time() + 10},
            ),
        )
        rv = self.make_request()
        eq_(rv, [])

    def test_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request()
        eq_(rv, [])

    def test_bad_uid(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request()
        eq_(rv, [])

    def test_no_grants(self):
        self.fake_grants.set_data({})
        rv = self.make_request(decode_response=False, expected_status=403)
        eq_(rv, 'No grants')


class ListClientsByCreatorTestCase(ApiTestCase):
    default_url = reverse_lazy('list_clients_by_creator', args=[TEST_UID])
    http_method = 'GET'

    def default_params(self):
        return {
            'scope': 'test:foo',
        }

    def test_ok(self):
        rv = self.make_request()
        eq_(rv, [self.test_client.display_id])

    def test_scope_missing(self):
        rv = self.make_request(expected_status=400, exclude=['scope'])
        eq_(rv['error'], 'Required parameter is missing: scope')

    def test_scope_not_matched(self):
        rv = self.make_request(scope='test:ttl')
        eq_(rv, [])

    def test_no_clients(self):
        rv = self.make_request(url=reverse('list_clients_by_creator', args=[TEST_OTHER_UID]))
        eq_(rv, [])

    def test_no_grants(self):
        self.fake_grants.set_data({})
        rv = self.make_request(decode_response=False, expected_status=403)
        eq_(rv, 'No grants')


class ClientInfoTestCase(ApiTestCase):
    http_method = 'GET'

    def setUp(self):
        super(ClientInfoTestCase, self).setUp()
        self.default_url = reverse_lazy('client_info_api', args=[self.test_client.display_id])

    def default_params(self):
        return {
            'scope': 'test:foo',
        }

    def test_ok(self):
        rv = self.make_request()
        eq_(rv['id'], self.test_client.display_id)
        eq_(rv['callback'], 'https://callback')
        eq_(rv['name'], 'Тестовое приложение')
        eq_(set(rv['scope']), set(['test:foo', 'test:bar']))
        eq_(set(rv['localized_scope']), set(['фу', 'бар']))
        ok_(
            all(field not in rv for field in ['requires_approval', 'approval_status', 'blocked', 'creator_uid']),
        )
        ok_(not rv['is_yandex'])

    def test_ok_custom_locale(self):
        rv = self.make_request(locale='en')
        eq_(rv['id'], self.test_client.display_id)
        eq_(rv['callback'], 'https://callback')
        eq_(rv['name'], 'Тестовое приложение')
        eq_(set(rv['scope']), set(['test:foo', 'test:bar']))
        eq_(set(rv['localized_scope']), set(['foo', 'bar']))
        ok_(
            all(field not in rv for field in ['requires_approval', 'approval_status', 'blocked', 'creator_uid']),
        )

    def test_ok_with_unsupported_locale(self):
        rv = self.make_request(locale='clingon')
        eq_(rv['id'], self.test_client.display_id)
        eq_(rv['callback'], 'https://callback')
        eq_(rv['name'], 'Тестовое приложение')
        eq_(set(rv['scope']), set(['test:foo', 'test:bar']))
        eq_(set(rv['localized_scope']), set(['фу', 'бар']))
        ok_(
            all(field not in rv for field in ['requires_approval', 'approval_status', 'blocked', 'creator_uid']),
        )

    def test_yandex_client(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request()
        eq_(rv['id'], self.test_client.display_id)
        ok_(rv['is_yandex'])

    def test_client_not_found(self):
        rv = self.make_request(expected_status=403, url=reverse('client_info_api', args=['foo']))
        eq_(rv['error'], 'invalid_client')
        eq_(rv['error_description'], 'Client not found')

    def test_no_grants(self):
        self.fake_grants.set_data({})
        rv = self.make_request(decode_response=False, expected_status=403)
        eq_(rv, 'No grants')
