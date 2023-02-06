# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json

from django.test.utils import override_settings
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import issue_token
from passport.backend.oauth.core.test.base_test_data import (
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_GRANT_TYPE,
)
from passport.backend.oauth.core.test.framework import ApiTestCase
from passport.backend.oauth.core.test.utils import iter_eq


TEST_UID = 42
TEST_UNIXTIME = 123456789
TEST_AVATARS_BASE_URL = 'https://mds.ru'


@override_settings(
    AVATARS_READ_URL=TEST_AVATARS_BASE_URL,
)
class TestTakeoutUserInfo(ApiTestCase):
    default_url = reverse_lazy('api_takeout_user_info')
    http_method = 'POST'

    def setUp(self):
        super(TestTakeoutUserInfo, self).setUp()
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )

    def default_params(self):
        return {
            'consumer': 'dev',
            'uid': TEST_UID,
            'unixtime': TEST_UNIXTIME,
        }

    def assert_status_error(self, rv, errors):
        eq_(
            rv,
            {
                'status': 'error',
                'error': ', '.join(sorted(errors)),
            },
            msg=rv,
        )

    def test_no_grants_error(self):
        self.fake_grants.set_data({})
        rv = self.make_request()
        self.assert_status_error(rv, ['grants.missing'])

    def test_blackbox_failed_error(self):
        self.fake_blackbox.set_response_side_effect(
            'userinfo',
            BlackboxTemporaryError,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['backend.failed'])

    def test_user_not_found_ok(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        rv = self.make_request()
        eq_(
            rv,
            {
                'status': 'no_data',
            },
        )

    def test_no_data_ok(self):
        rv = self.make_request()
        eq_(
            rv,
            {
                'status': 'no_data',
            },
        )

    def test_tokens_only_ok(self):
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],  # подмножество скоупов приложения
        )
        rv = self.make_request()

        eq_(set(rv.keys()), {'status', 'data'})
        eq_(rv['status'], 'ok')
        iter_eq(
            set(rv['data'].keys()),
            {'authorized_devices.json'},
        )
        iter_eq(
            json.loads(rv['data']['authorized_devices.json']),
            {
                'other': [
                    {
                        'client_id': self.test_client.display_id,
                        'client_title': self.test_client.default_title,
                        'scope': ['test:foo'],
                        'issued': TimeNow(),
                    },
                ],
            },
        )

    def test_full_ok(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:ttl')],
            redirect_uris=['https://callback2'],
            default_title='Тестовое приложение 2',
            icon='http://icon2',
            icon_id='gid/client_id-abc2',
            homepage='http://homepage2',
            default_description='Test client 2',
        )) as client:
            client.ios_default_app_id = 'app-id'
            client.ios_appstore_url = 'https://itunes.apple.com/some-stuff'
            client.android_default_package_name = 'package-name'
            client.android_cert_fingerprints = ['fingerprint']
            client.android_appstore_url = 'https://play.google.com/some-stuff'
            client.is_yandex = True
            self.other_client = client

        # ПП
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id='app_password',
            device_name='Mail app',
            env=self.env,
            make_alias=True,
        )
        # токен без устройства
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            scopes=[Scope.by_keyword('test:foo')],  # подмножество скоупов приложения
        )
        # токены на одном устройстве
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            env=self.env,
        )
        old_token = issue_token(
            uid=TEST_UID,
            client=self.other_client,
            grant_type=TEST_GRANT_TYPE,
            device_id=TEST_DEVICE_ID,
            device_name='foooo',
            env=self.env,
        )
        with UPDATE(old_token):
            old_token.issued = datetime.now() - timedelta(seconds=30)

        rv = self.make_request()

        eq_(set(rv.keys()), {'status', 'data'})
        eq_(rv['status'], 'ok')
        iter_eq(
            set(rv['data'].keys()),
            {
                'registered_clients.json',
                'authorized_devices.json',
                'app_passwords.json',
            },
        )
        iter_eq(
            json.loads(rv['data']['registered_clients.json']),
            [
                {
                    'id': self.other_client.display_id,
                    'title': 'Тестовое приложение 2',
                    'description': 'Test client 2',
                    'homepage': 'http://homepage2',
                    'icon_url': 'https://mds.ru/get-oauth/gid/client_id-abc2/normal',
                    'platforms': {
                        'web': {
                            'redirect_uris': ['https://callback2'],
                        },
                        'android': {
                            'package_names': ['package-name'],
                            'cert_fingerprints': ['fingerprint'],
                            'appstore_url': 'https://play.google.com/some-stuff',
                        },
                        'ios': {
                            'app_ids': ['app-id'],
                            'appstore_url': 'https://itunes.apple.com/some-stuff',
                        },
                    },
                    'created': TimeNow(),
                    'is_yandex': True,
                },
            ],
        )
        iter_eq(
            json.loads(rv['data']['authorized_devices.json']),
            {
                'devices': [
                    {
                        'device_id': TEST_DEVICE_ID,
                        'device_name': TEST_DEVICE_NAME,
                        'app_platform': 'unknown',
                        'tokens': [
                            {
                                'client_id': self.test_client.display_id,
                                'client_title': self.test_client.default_title,
                                'scope': ['test:bar', 'test:foo'],
                                'issued': TimeNow(),
                            },
                            {
                                'client_id': self.other_client.display_id,
                                'client_title': self.other_client.default_title,
                                'scope': ['test:ttl'],
                                'issued': TimeNow(offset=-30),
                            },
                        ],
                    },
                ],
                'other': [
                    {
                        'client_id': self.test_client.display_id,
                        'client_title': self.test_client.default_title,
                        'scope': ['test:foo'],
                        'issued': TimeNow(),
                    },
                ],
            },
        )
        iter_eq(
            json.loads(rv['data']['app_passwords.json']),
            [
                {
                    'name': 'Mail app',
                    'scope': ['test:bar', 'test:foo'],
                    'issued': TimeNow(),
                },
            ],
        )
