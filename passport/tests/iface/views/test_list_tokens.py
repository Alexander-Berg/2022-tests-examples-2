# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from operator import itemgetter
from time import time

from django.conf import settings
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.oauth.api.api.iface.utils import token_to_response
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    CommonCookieTests,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
)
from passport.backend.oauth.core.common.utils import now
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DELETE,
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
)
from passport.backend.oauth.core.test.utils import iter_eq


class TestListTokens(BaseIfaceApiTestCase):
    default_url = reverse_lazy('iface_list_tokens')

    def setUp(self):
        super(TestListTokens, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'uid': TEST_UID,
            'language': 'ru',
        }

    def test_ok(self):
        with CREATE(Client.create(
            uid=TEST_OTHER_UID,
            scopes=[Scope.by_keyword('test:foo')],
            redirect_uris=['https://callback'],
            default_title='test_client2',
        )) as client2:
            pass

        token1 = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        token2 = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        issue_token(uid=TEST_OTHER_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            sorted(rv['tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(token1, self.test_client),
                token_to_response(token2, self.test_client),
            ], key=itemgetter('id')),
        )
        eq_(rv['expired_tokens'], [])

        token3 = issue_token(uid=TEST_UID, client=client2, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            sorted(rv['tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(token1, self.test_client),
                token_to_response(token2, self.test_client),
                token_to_response(token3, client2),
            ], key=itemgetter('id')),
        )
        eq_(rv['expired_tokens'], [])

    def test_no_clients(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['tokens'], [])
        eq_(rv['expired_tokens'], [])

    def test_user_glogouted(self):
        self.setup_blackbox_response(attributes={settings.BB_ATTR_GLOGOUT: time() + 10})
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        app_password = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id='foo',
            make_alias=True,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['tokens'], [])
        eq_(
            rv['expired_tokens'],
            [
                token_to_response(app_password, self.test_client),
            ],
        )

    def test_user_revoked_tokens(self):
        self.setup_blackbox_response(attributes={settings.BB_ATTR_REVOKER_TOKENS: time() + 10})
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        app_password = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id='foo',
            make_alias=True,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            rv['tokens'],
            [
                token_to_response(app_password, self.test_client),
            ],
        )
        eq_(
            rv['expired_tokens'],
            [],
        )

    def test_user_revoked_app_passwords(self):
        self.setup_blackbox_response(attributes={settings.BB_ATTR_REVOKER_APP_PASSWORDS: time() + 10})
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        app_password = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id='foo',
            make_alias=True,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            rv['tokens'],
            [
                token_to_response(token, self.test_client),
            ],
        )
        eq_(
            rv['expired_tokens'],
            [
                token_to_response(app_password, self.test_client),
            ],
        )

    def test_client_deleted(self):
        token = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        app_password = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id='foo',
            make_alias=True,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            sorted(rv['tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(token, self.test_client),
                token_to_response(app_password, self.test_client),
            ], key=itemgetter('id')),
        )
        eq_(rv['expired_tokens'], [])

        with DELETE(self.test_client):
            pass
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['tokens'], [])
        eq_(rv['expired_tokens'], [])

    def test_token_expired(self):
        token = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        app_password = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id='foo',
            make_alias=True,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            rv['tokens'],
            [
                token_to_response(token, self.test_client),
                token_to_response(app_password, self.test_client),
            ],
        )
        eq_(rv['expired_tokens'], [])

        with UPDATE(token):
            token.expires = datetime.now() - timedelta(seconds=10)
        with UPDATE(app_password):
            app_password.expires = datetime.now() - timedelta(seconds=10)

        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['tokens'], [])
        eq_(
            rv['expired_tokens'],
            [
                token_to_response(app_password, self.test_client),
            ],
        )

    def test_token_invalidated_by_client_glogout(self):
        token = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        app_password = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id='foo',
            make_alias=True,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            sorted(rv['tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(token, self.test_client),
                token_to_response(app_password, self.test_client),
            ], key=itemgetter('id')),
        )
        eq_(rv['expired_tokens'], [])

        with UPDATE(self.test_client) as client:
            client.glogouted = datetime.now() + timedelta(seconds=10)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['tokens'], [])
        eq_(
            rv['expired_tokens'],
            [
                token_to_response(app_password, self.test_client),
            ],
        )


class TestCountAppPasswords(BaseIfaceApiTestCase):
    default_url = reverse_lazy('iface_app_passwords_count')

    def setUp(self):
        super(TestCountAppPasswords, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
        }

    def issue_token_by_client(self, count=1, client=None, outdated=False,
                              is_app_password=False, device_id='foo'):
        for _ in range(count):
            app_password = issue_token(
                uid=TEST_UID,
                client=client or self.test_client,
                grant_type=TEST_GRANT_TYPE,
                env=self.env,
                device_id=device_id,
                make_alias=is_app_password,
            )
            if outdated:
                with UPDATE(app_password):
                    app_password.expires = datetime.now() - timedelta(seconds=10)

    def test_ok(self):
        self.issue_token_by_client(device_id=None)
        self.issue_token_by_client(is_app_password=True)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['app_passwords_count'], 1)

    def test_no_app_passwords(self):
        self.issue_token_by_client(count=2, device_id=None)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['app_passwords_count'], 0)

    def test_no_valid_app_passwords(self):
        self.issue_token_by_client()
        self.issue_token_by_client(outdated=True, is_app_password=True)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['app_passwords_count'], 0)

    def test_user_glogouted(self):
        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_GLOGOUT: int(time() + 5)},
        )
        self.issue_token_by_client(count=2, is_app_password=True)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['app_passwords_count'], 0)

    def test_user_revoked_app_passwords(self):
        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_REVOKER_APP_PASSWORDS: int(time() + 5)},
        )
        self.issue_token_by_client(count=2, is_app_password=True)
        rv = self.make_request(user_app_passwords_revoke_time=int(time() + 10))
        self.assert_status_ok(rv)
        eq_(rv['app_passwords_count'], 0)

    def test_glogouted_by_client(self):
        self.issue_token_by_client(count=2, is_app_password=True)
        with UPDATE(self.test_client) as client:
            client.glogouted = datetime.now() + timedelta(seconds=10)
        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(rv['app_passwords_count'], 0)


class TestListTokenGroups(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_list_token_groups')
    http_method = 'GET'

    def setUp(self):
        super(TestListTokenGroups, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'language': 'ru',
        }

    @property
    def empty_response(self):
        return {
            'app_passwords': [],
            'device_tokens': [],
            'other_tokens': [],
        }

    def create_client(self, is_yandex=False, scopes=None):
        with CREATE(Client.create(
            uid=TEST_OTHER_UID,
            scopes=scopes or [Scope.by_keyword('test:foo')],
            redirect_uris=['https://callback'],
            default_title='test_client2',
        )) as new_client:
            new_client.is_yandex = is_yandex
        return new_client

    def issue_token_by_client(self, client=None, expired=False,
                              is_app_password=False, device_id='foo-foo', device_name='bzz', **kwargs):
        token = issue_token(
            uid=TEST_UID,
            client=client or self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id=device_id,
            device_name=device_name,
            make_alias=is_app_password,
            **kwargs
        )
        if expired:
            with UPDATE(token):
                token.expires = datetime.now() - timedelta(seconds=10)
        return token

    def test_full_house(self):
        client2 = self.create_client()
        client_ya = self.create_client(is_yandex=True)
        # device_id & device_name
        token1 = self.issue_token_by_client()
        # device_id & device_name
        token2 = self.issue_token_by_client(client=client2, app_platform='Android X')
        # diff device_id & device_name
        token3 = self.issue_token_by_client(client=client2, device_id='bar-bar', app_platform='iPhone')
        # diff device_id & device_name yandex
        token4 = self.issue_token_by_client(device_id='ya-foo-foo', client=client_ya)
        # no device_id & device_name no yandex
        token5 = self.issue_token_by_client(device_id=None)
        # no device_id yandex
        token6 = self.issue_token_by_client(device_id=None, client=client_ya)
        # app password
        token7 = self.issue_token_by_client(client=client2, is_app_password=True, device_id='random')
        # app password expired
        self.issue_token_by_client(client=client2, is_app_password=True, expired=True, device_id='zzz')
        # token expired
        self.issue_token_by_client(client=client2, expired=True, device_id='exp')

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 9)

        rv = self.make_request()
        self.assert_status_ok(rv)

        iter_eq(
            sorted(rv['device_tokens'], key=itemgetter('device_id')),
            sorted([
                {
                    'device_id': 'foo-foo',
                    'device_name': 'bzz',
                    'app_platform': 'unknown',
                    'has_xtoken': False,
                    'tokens': [
                        token_to_response(token1, self.test_client),
                        token_to_response(token2, client2),
                    ],
                },
                {
                    'device_id': 'bar-bar',
                    'device_name': 'bzz',
                    'app_platform': 'unknown',
                    'has_xtoken': False,
                    'tokens': [
                        token_to_response(token3, client2),
                    ],
                },
                {
                    'device_id': 'ya-foo-foo',
                    'device_name': 'bzz',
                    'app_platform': 'unknown',
                    'has_xtoken': False,
                    'tokens': [
                        token_to_response(token4, client_ya),
                    ],
                },
            ], key=itemgetter('device_id')),
        )

        iter_eq(
            sorted(rv['other_tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(token5, self.test_client),
                token_to_response(token6, client_ya),
            ], key=itemgetter('id')),
        )

        iter_eq(
            rv['app_passwords'],
            [token_to_response(token7, client2)],
        )

    def test_hide_yandex_device_tokens(self):
        yandex_client = self.create_client(is_yandex=True)
        x_token_client = self.create_client(is_yandex=True, scopes=[Scope.by_keyword('test:xtoken')])

        external_token_wo_device_id = self.issue_token_by_client(
            device_id=None,
            device_name=None,
        )
        yandex_token_wo_device_id = self.issue_token_by_client(
            yandex_client,
            device_id=None,
            device_name=None,
        )

        x_token_with_device_id = self.issue_token_by_client(
            x_token_client,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )
        yandex_token_with_device_id = self.issue_token_by_client(
            yandex_client,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            x_token_id=x_token_with_device_id.id,
        )
        external_token_with_device_id = self.issue_token_by_client(
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )

        yandex_token_with_other_device_id = self.issue_token_by_client(
            yandex_client,
            device_id='other-device-id',
            device_name='other-device-name',
        )

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(
            set(tokens),
            {
                external_token_wo_device_id,
                yandex_token_wo_device_id,

                x_token_with_device_id,
                yandex_token_with_device_id,
                external_token_with_device_id,

                yandex_token_with_other_device_id,
            },
        )

        rv = self.make_request(hide_yandex_device_tokens=True)
        self.assert_status_ok(rv)

        iter_eq(
            sorted(rv['device_tokens'], key=itemgetter('device_id')),
            sorted([
                {
                    'device_id': TEST_DEVICE_ID,
                    'device_name': TEST_DEVICE_NAME,
                    'app_platform': 'unknown',
                    'has_xtoken': True,
                    'tokens': [
                        token_to_response(external_token_with_device_id, self.test_client),
                        # yandex_token_with_device_id нет, так как его мы скрыли
                        # x_token_with_device_id нет, так как это х-токен
                    ],
                },
                {
                    'device_id': 'other-device-id',
                    'device_name': 'other-device-name',
                    'app_platform': 'unknown',
                    'has_xtoken': False,
                    'tokens': [
                        token_to_response(yandex_token_with_other_device_id, yandex_client),
                    ],
                },
            ], key=itemgetter('device_id')),
        )

        iter_eq(
            sorted(rv['other_tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(external_token_wo_device_id, self.test_client),
                token_to_response(yandex_token_wo_device_id, yandex_client),
            ], key=itemgetter('id')),
        )

        iter_eq(
            rv['app_passwords'],
            [],
        )

    def test_latest_device_name(self):
        client2 = self.create_client()
        client_ya = self.create_client(is_yandex=True)
        token1 = self.issue_token_by_client()
        token2 = self.issue_token_by_client(device_name='vzyk', client=client2)
        token3 = self.issue_token_by_client(client=client_ya, device_name=None)

        with UPDATE(token1) as token:
            token.issued = now() - timedelta(seconds=10)

        with UPDATE(token3) as token:
            token.issued = now() + timedelta(seconds=10)

        rv = self.make_request()
        self.assert_status_ok(rv)

        eq_(rv['device_tokens'][0]['device_id'], 'foo-foo')
        eq_(rv['device_tokens'][0]['device_name'], 'vzyk')

        iter_eq(
            sorted(rv['device_tokens'][0]['tokens'], key=itemgetter('id')),
            sorted([
                token_to_response(token1, self.test_client),
                token_to_response(token2, client2),
                token_to_response(token3, client_ya),
            ], key=itemgetter('id')),
        )
        eq_(rv['app_passwords'], [])
        eq_(rv['other_tokens'], [])

    def test_tokens_revoked(self):
        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_REVOKER_TOKENS: int(time() + 5)},
        )
        client2 = self.create_client()
        self.issue_token_by_client()
        self.issue_token_by_client(client=client2, device_id=None)

        rv = self.make_request()
        self.assert_response_ok(rv, **self.empty_response)

    def test_client_glogouted(self):
        self.issue_token_by_client(device_id='aaa')
        self.issue_token_by_client(device_id='bbb', is_app_password=True)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 2)
        with UPDATE(self.test_client) as client:
            client.glogouted = datetime.now() + timedelta(seconds=10)

        rv = self.make_request()
        self.assert_response_ok(rv, **self.empty_response)

    def test_user_glogouted(self):
        self.setup_blackbox_response(attributes={settings.BB_ATTR_GLOGOUT: time() + 10})
        client2 = self.create_client()
        self.issue_token_by_client(device_id='aaa')
        self.issue_token_by_client(device_id='bbb', is_app_password=True)
        self.issue_token_by_client(device_id='ccc', client=client2)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 3)

        rv = self.make_request()
        self.assert_response_ok(rv, **self.empty_response)

    def test_has_xtoken(self):
        client2 = self.create_client(
            scopes=[
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:xtoken'),
            ],
        )
        token1 = self.issue_token_by_client()
        self.issue_token_by_client(client=client2, app_platform='Android 100500')

        rv = self.make_request()
        self.assert_status_ok(rv)

        iter_eq(
            rv['device_tokens'],
            [
                {
                    'device_id': 'foo-foo',
                    'device_name': 'bzz',
                    'app_platform': 'android',
                    'has_xtoken': True,
                    'tokens': [
                        token_to_response(token1, self.test_client),
                    ],
                },
            ]
        )
        eq_(rv['app_passwords'], [])
        eq_(rv['other_tokens'], [])

    def test_device_with_only_xtokens(self):
        client = self.create_client(
            scopes=[
                Scope.by_keyword('test:xtoken'),
            ],
        )
        self.issue_token_by_client(client=client, app_platform='iPhone')
        token2 = self.issue_token_by_client(client=client, device_id=None)

        rv = self.make_request()
        self.assert_status_ok(rv)

        iter_eq(
            rv['device_tokens'],
            [
                {
                    'device_id': 'foo-foo',
                    'device_name': 'bzz',
                    'app_platform': 'ios',
                    'has_xtoken': True,
                    'tokens': [],
                },
            ]
        )
        eq_(rv['app_passwords'], [])
        eq_(rv['other_tokens'], [token_to_response(token2, client)])
