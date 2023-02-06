# -*- coding: utf-8 -*-
import json

from django.test.utils import override_settings
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox.blackbox import parse_blackbox_userinfo_response
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.api.api.iface.utils import (
    account_to_response,
    client_to_response,
    remove_param_from_url,
    token_to_response,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import issue_token
from passport.backend.oauth.core.test.base_test_data import (
    TEST_AVATAR_ID,
    TEST_DISPLAY_NAME,
    TEST_GRANT_TYPE,
    TEST_GROUP,
    TEST_LOGIN,
    TEST_NORMALIZED_LOGIN,
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework import BaseTestCase
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.oauth.core.test.utils import iter_eq
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_AVATARS_BASE_URL = 'https://avatars.ru'
TEST_ICON_URL = TEST_AVATARS_BASE_URL + '/get-oauth/gid/client_id-abc/normal'


@override_settings(AVATARS_READ_URL=TEST_AVATARS_BASE_URL)
class TestClientToResponse(BundleApiTestCase):
    def test_ok(self):
        iter_eq(
            client_to_response(self.test_client, for_creator=True),
            {
                'id': self.test_client.display_id,
                'title': 'Тестовое приложение',
                'description': 'Test client',
                'icon': 'http://icon',
                'icon_id': 'gid/client_id-abc',
                'icon_url': TEST_ICON_URL,
                'homepage': 'http://homepage',
                'callback': 'https://callback',
                'redirect_uris': ['https://callback'],
                'scopes': {
                    'Тестирование OAuth': {
                        'test:foo': {
                            'title': 'фу',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                        'test:bar': {
                            'title': 'бар',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                    },
                },
                'platforms': {
                    'web': {
                        'redirect_uris': ['https://callback'],
                    },
                },
                'create_time': datetime_to_integer_unixtime(self.test_client.created),
                'is_yandex': False,
                'is_deleted': False,

                'secret': self.test_client.secret,
                'approval_status': self.test_client.approval_status,
                'blocked': self.test_client.is_blocked,
                'owners': [],
                'owner_groups': [],
                'contact_email': None,
            },
        )

    def test_not_creator(self):
        iter_eq(
            client_to_response(self.test_client),
            {
                'id': self.test_client.display_id,
                'title': 'Тестовое приложение',
                'description': 'Test client',
                'icon': 'http://icon',
                'icon_id': 'gid/client_id-abc',
                'icon_url': TEST_ICON_URL,
                'homepage': 'http://homepage',
                'callback': 'https://callback',
                'redirect_uris': ['https://callback'],
                'scopes': {
                    'Тестирование OAuth': {
                        'test:foo': {
                            'title': 'фу',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                        'test:bar': {
                            'title': 'бар',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                    },
                },
                'platforms': {
                    'web': {
                        'redirect_uris': ['https://callback'],
                    },
                },
                'create_time': datetime_to_integer_unixtime(self.test_client.created),
                'is_yandex': False,
                'is_deleted': False,
            },
        )

    def test_full(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, login=TEST_LOGIN),
        )
        with UPDATE(self.test_client) as client:
            client.ios_default_app_id = 'app-id'
            client.ios_extra_app_ids = ['app-id-2']
            client.ios_appstore_url = 'https://itunes.apple.com/some-stuff'
            client.android_default_package_name = 'package-name'
            client.android_extra_package_names = ['package-name-2']
            client.android_cert_fingerprints = ['fingerprint']
            client.android_appstore_url = 'https://play.google.com/some-stuff'
            client.turboapp_base_url = 'https://ozon.ru'
            client.owner_uids = [TEST_UID]
            client.owner_groups = [TEST_GROUP]
            client.contact_email = 'abacaba@test.ru'

        iter_eq(
            client_to_response(self.test_client, for_creator=True),
            {
                'id': self.test_client.display_id,
                'title': 'Тестовое приложение',
                'description': 'Test client',
                'icon': 'http://icon',
                'icon_id': 'gid/client_id-abc',
                'icon_url': TEST_ICON_URL,
                'homepage': 'http://homepage',
                'callback': 'https://callback',
                'redirect_uris': ['https://callback'],
                'scopes': {
                    'Тестирование OAuth': {
                        'test:foo': {
                            'title': 'фу',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                        'test:bar': {
                            'title': 'бар',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                    },
                },
                'platforms': {
                    'web': {
                        'redirect_uris': ['https://callback'],
                    },
                    'ios': {
                        'app_ids': ['app-id', 'app-id-2'],
                        'appstore_url': 'https://itunes.apple.com/some-stuff',
                        'universal_link_domains': [
                            'https://yx%s.oauth.yandex.ru' % self.test_client.display_id,
                            'https://yx%s.oauth.yandex.com' % self.test_client.display_id,
                        ],
                        'custom_urlschemes': [
                            'yx%s' % self.test_client.display_id,
                        ],
                    },
                    'android': {
                        'package_names': ['package-name', 'package-name-2'],
                        'cert_fingerprints': ['fingerprint'],
                        'appstore_url': 'https://play.google.com/some-stuff',
                        'custom_urlschemes': [
                            'yx%s' % self.test_client.display_id,
                        ],
                    },
                    'turboapp': {
                        'base_url': 'https://ozon.ru',
                    },
                },
                'create_time': datetime_to_integer_unixtime(self.test_client.created),
                'is_yandex': False,
                'is_deleted': False,

                'secret': self.test_client.secret,
                'approval_status': self.test_client.approval_status,
                'blocked': self.test_client.is_blocked,
                'owners': [
                    {
                        'uid': TEST_UID,
                        'login': TEST_LOGIN,
                    },
                ],
                'owner_groups': [TEST_GROUP],
                'contact_email': 'abacaba@test.ru'
            },
        )


@override_settings(AVATARS_READ_URL=TEST_AVATARS_BASE_URL)
class TestTokenToResponse(BundleApiTestCase):
    def setUp(self):
        super(TestTokenToResponse, self).setUp()
        self.test_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )

    def test_ok(self):
        eq_(
            token_to_response(self.test_token, self.test_client),
            {
                'id': self.test_token.id,
                'scopes': {
                    'Тестирование OAuth': {
                        'test:foo': {
                            'title': 'фу',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                        'test:bar': {
                            'title': 'бар',
                            'requires_approval': False,
                            'ttl': None,
                            'is_ttl_refreshable': False,
                        },
                    },
                },
                'client': client_to_response(self.test_client),
                'device_id': None,
                'device_name': None,
                'create_time': datetime_to_integer_unixtime(self.test_token.created),
                'issue_time': datetime_to_integer_unixtime(self.test_token.issued),
                'is_app_password': False,
            },
        )

    @raises(ValueError)
    def test_token_not_belongs_to_client(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='Тестовое приложение 2',
            icon='http://icon',
            homepage='http://homepage',
            default_description='Test client',
        )) as other_client:
            pass
        token_to_response(self.test_token, other_client)


class TestAccountToResponse(BundleApiTestCase):
    def make_bb_response(self, **kwargs):
        return parse_blackbox_userinfo_response(json.loads(blackbox_userinfo_response(**kwargs)))

    def test_ok(self):
        eq_(
            account_to_response(self.make_bb_response()),
            {
                'uid': 1,
                'login': 'test',
                'display_login': 'test',
                'display_name': '',
                'default_avatar_id': None,
                'is_avatar_empty': True,
            },
        )

    def test_full_ok(self):
        eq_(
            account_to_response(self.make_bb_response(
                uid=TEST_OTHER_UID,
                login=TEST_NORMALIZED_LOGIN,
                display_login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME,
                default_avatar_key=TEST_AVATAR_ID,
                is_avatar_empty=False,
            )),
            {
                'uid': TEST_OTHER_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )


class TestRemoveParamFromURL(BaseTestCase):
    def test_remove_param_from_url(self):
        param = 'code'
        for from_, to_ in (
            ('https://yandex.ru?code=123', 'https://yandex.ru'),
            ('https://yandex.ru?code=123&code=456', 'https://yandex.ru'),
            ('https://yandex.ru?code=123&test=123', 'https://yandex.ru?test=123'),
            ('https://yandex.ru?code=123&test=123&test=456', 'https://yandex.ru?test=123&test=456'),
            ('https://yandex.ru?test=123', 'https://yandex.ru?test=123'),
            ('https://yandex.ru', 'https://yandex.ru'),
            ('https://yandex.ru?test=123&code=123&test=456&code=456', 'https://yandex.ru?test=123&test=456'),
        ):
            eq_(remove_param_from_url(from_, param), to_)
