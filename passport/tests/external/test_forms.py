# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from passport.backend.oauth.api.api.external.forms import (
    CreateClientExternalForm,
    CreateClientForTurboappForm,
    EditClientExternalForm,
    IssueAuthorizationCodeForm,
    IssueDeviceCodeForm,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.framework import (
    FormTestCase,
    PatchesMixin,
)


class TestIssueAuthorizationCodeForm(FormTestCase):
    form = IssueAuthorizationCodeForm
    invalid_params = [
        (
            {},
            {
                'client_id': ['missing'],
                'client_secret': ['missing'],
                'code_strength': ['missing'],
            },
        ),
        (
            {
                'code_strength': 'foo',
                'ttl': 'bar',
                'uid': 'zar',
                'client_id': 'abc',
                'client_secret': 'def',
            },
            {
                'uid': ['invalid'],
                'client_id': ['too_short'],
                'client_secret': ['too_short'],
                'code_strength': ['invalid'],
                'ttl': ['invalid'],
            },
        ),
        (
            {
                'code_strength': 'medium',
                'ttl': '90000',
                'uid': '1',
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
            },
            {
                'ttl': ['invalid'],
            },
        ),
        (
            {
                'code_strength': 'medium',
                'ttl': '9',
                'uid': '1',
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
            },
            {
                'ttl': ['invalid'],
            },
        ),
    ]
    valid_params = [
        (
            {
                'code_strength': 'medium',
                'uid': '1',
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
            },
            {
                'code_strength': 1,
                'uid': 1,
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
                'ttl': None,
                'device_id': '',
                'device_name': '',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
                'require_activation': True,
                'code_challenge': '',
                'code_challenge_method': 0,
                'by_uid': False,
            },
        ),
        (
            {
                'code_strength': 'medium',
                'uid': '1',
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
                'require_activation': 'true',
                'by_uid': 'true',
            },
            {
                'code_strength': 1,
                'uid': 1,
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
                'ttl': None,
                'device_id': '',
                'device_name': '',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
                'require_activation': True,
                'code_challenge': '',
                'code_challenge_method': 0,
                'by_uid': True,
            },
        ),
        (
            {
                'code_strength': 'long',
                'uid': '1',
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
                'ttl': '42',
                'device_id': 'deviceid',
                'device_name': 'name',
                'require_activation': 'false',
                'by_uid': 'false',
            },
            {
                'code_strength': 2,
                'uid': 1,
                'client_id': 'a' * 32,
                'client_secret': 'b' * 32,
                'ttl': 42,
                'device_id': 'deviceid',
                'device_name': 'name',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
                'require_activation': False,
                'code_challenge': '',
                'code_challenge_method': 0,
                'by_uid': False,
            },
        ),
    ]


class TestIssueDeviceCodeForm(FormTestCase):
    form = IssueDeviceCodeForm
    invalid_params = [
        (
            {},
            {
                'client_id': ['missing'],
                'code_strength': ['missing'],
            },
        ),
        (
            {
                'code_strength': 'foo',
                'client_id': 'bar',
            },
            {
                'client_id': ['too_short'],
                'code_strength': ['invalid'],
            },
        ),
    ]
    valid_params = [
        (
            {
                'code_strength': 'below_medium',
                'client_id': 'a' * 32,
            },
            {
                'code_strength': 3,
                'client_id': 'a' * 32,
                'device_id': '',
                'device_name': '',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
                'client_bound': True,
            },
        ),
        (
            {
                'code_strength': 'medium_with_crc',
                'client_id': 'a' * 32,
                'device_id': 'deviceid',
                'device_name': 'name',
                'client_bound': 'false',
            },
            {
                'code_strength': 5,
                'client_id': 'a' * 32,
                'device_id': 'deviceid',
                'device_name': 'name',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
                'client_bound': False,
            },
        ),
    ]


@override_settings(AVATARS_READ_URL='https://avatars.mdst.yandex.net')
class TestCreateClientForTurboappForm(FormTestCase):
    form = CreateClientForTurboappForm
    invalid_params = [
        (
            {},
            {
                'title': ['missing'],
                'description': ['missing'],
                'icon_url': ['missing'],
                'turboapp_base_url': ['missing'],
            },
        ),
        (
            {
                'title': '',
                'description': '',
                'icon_url': '',
                'turboapp_base_url': '',
            },
            {
                'title': ['missing'],
                'description': ['missing'],
                'icon_url': ['missing'],
                'turboapp_base_url': ['missing'],
            },
        ),
        (
            {
                'title': 'a' * 101,
                'description': 'a' * 251,
                'icon_url': 'foo',
                'turboapp_base_url': 'foo',
            },
            {
                'title': ['too_long'],
                'description': ['too_long'],
                'icon_url': ['scheme_missing'],
                'turboapp_base_url': ['scheme_missing'],
            },
        ),
        (
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'https://ozon.ru/smth',
                'turboapp_base_url': 'https://ozon.ru',
            },
            {
                'icon_url': ['invalid'],
            },
        ),
        (
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'http://avatars.mdst.yandex.net/smth',  # http
                'turboapp_base_url': 'https://ozon.ru',
            },
            {
                'icon_url': ['invalid'],
            },
        ),
        (
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'https://avatars.mdst.yandex.net/smth?redirect=google.com',
                'turboapp_base_url': 'https://ozon.ru',
            },
            {
                'icon_url': ['invalid'],
            },
        ),
    ]
    valid_params = [
        (
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'https://avatars.mdst.yandex.net/smth',
                'turboapp_base_url': 'https://ozon.ru',
            },
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'https://avatars.mdst.yandex.net/smth',
                'turboapp_base_url': 'https://ozon.ru',
                'uid': None,
            },
        ),
        (
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'https://avatars.mdst.yandex.net/smth',
                'turboapp_base_url': 'https://ozon.ru',
                'uid': '1',
            },
            {
                'title': 'test-title',
                'description': 'test-description',
                'icon_url': 'https://avatars.mdst.yandex.net/smth',
                'turboapp_base_url': 'https://ozon.ru',
                'uid': 1,
            },
        ),
    ]


class TestCreateClientExternalForm(FormTestCase, PatchesMixin):
    form = CreateClientExternalForm
    form_args = [{'test:foo': 'Foo', 'test:bar': 'Bar'}]

    def setUp(self):
        super(TestCreateClientExternalForm, self).setUp()
        self.patch_scopes()
        self.patch_login_to_uid_mapping()

        self.invalid_params = [
            (
                {},
                {
                    'title': ['missing'],
                    'owner_login': ['missing'],
                    'scopes': ['missing'],
                    'redirect_uris': ['missing'],
                },
            ),
            (
                {
                    'title': 'a' * 101,
                    'owner_login': 'a' * 101,
                    'scopes': ['test:abacaba'],
                    'description': 'a' * 251,
                    'homepage': 'abacaba',
                    'redirect_uris': ['abacaba', None],
                    'files': {'icon_file': 'abacaba'},
                },
                {
                    'title': ['too_long'],
                    'owner_login': ['too_long'],
                    'scopes': ['invalid'],
                    'description': ['too_long'],
                    'homepage': ['invalid'],
                    'redirect_uris': ['0.scheme_missing', '1.missing'],
                },
            ),
            (
                {
                    'homepage': 'a' * 1025,
                    'redirect_uris': ['abacaba'] * 21,
                },
                {
                    'title': ['missing'],
                    'owner_login': ['missing'],
                    'scopes': ['missing'],
                    'homepage': ['invalid', 'too_long'],
                    'redirect_uris': ['too_many'],
                },
            ),
        ]

        self.valid_params = [
            (
                {
                    'title': 'test_title',
                    'owner_login': 'test_owner_login',
                    'scopes': ['test:foo', 'test:bar'],
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                },
                {
                    'title': 'test_title',
                    'owner_login': 'test_owner_login',
                    'scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                    'description': '',
                    'homepage': '',
                    'icon_file': None,
                },
            ),
            (
                {
                    'title': 'test_title',
                    'owner_login': 'test_owner_login',
                    'scopes': ['test:foo', 'test:bar'],
                    'login': 'test_login',
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                    'description': 'test_description',
                    'homepage': 'test.ru',
                },
                {
                    'title': 'test_title',
                    'owner_login': 'test_owner_login',
                    'scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                    'description': 'test_description',
                    'homepage': 'http://test.ru',
                    'icon_file': None,
                },
            ),
        ]


class TestEditClientExternalForm(FormTestCase, PatchesMixin):
    form = EditClientExternalForm
    form_args = [{'test:foo': 'Foo', 'test:bar': 'Bar'}]

    def setUp(self):
        super(TestEditClientExternalForm, self).setUp()
        self.patch_scopes()
        self.patch_login_to_uid_mapping()

        self.invalid_params = [
            (
                {},
                {
                    'title': ['missing'],
                    'client_id': ['missing'],
                    'scopes': ['missing'],
                    'redirect_uris': ['missing'],
                },
            ),
            (
                {
                    'title': 'a' * 101,
                    'client_id': 'abacaba',
                    'scopes': ['test:abacaba'],
                    'description': 'a' * 251,
                    'homepage': 'abacaba',
                    'redirect_uris': ['abacaba', None],
                    'files': {'icon_file': 'abacaba'},
                },
                {
                    'title': ['too_long'],
                    'client_id': ['too_short'],
                    'scopes': ['invalid'],
                    'description': ['too_long'],
                    'homepage': ['invalid'],
                    'redirect_uris': ['0.scheme_missing', '1.missing'],
                },
            ),
            (
                {
                    'homepage': 'a' * 1025,
                    'redirect_uris': ['abacaba'] * 21,
                },
                {
                    'title': ['missing'],
                    'client_id': ['missing'],
                    'scopes': ['missing'],
                    'homepage': ['invalid', 'too_long'],
                    'redirect_uris': ['too_many'],
                },
            ),
        ]

        self.valid_params = [
            (
                {
                    'title': 'test_title',
                    'client_id': 'a' * 32,
                    'scopes': ['test:foo', 'test:bar'],
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                },
                {
                    'title': 'test_title',
                    'client_id': 'a' * 32,
                    'scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                    'description': '',
                    'homepage': '',
                    'icon_file': None,
                },
            ),
            (
                {
                    'title': 'test_title',
                    'client_id': 'a' * 32,
                    'scopes': ['test:foo', 'test:bar'],
                    'login': 'test_login',
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                    'description': 'test_description',
                    'homepage': 'test.ru',
                },
                {
                    'title': 'test_title',
                    'client_id': 'a' * 32,
                    'scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'redirect_uris': ['http://test1.ru', 'http://test2.ru'],
                    'description': 'test_description',
                    'homepage': 'http://test.ru',
                    'icon_file': None,
                },
            ),
        ]
