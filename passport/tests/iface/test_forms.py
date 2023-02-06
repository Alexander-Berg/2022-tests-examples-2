# -*- coding: utf-8 -*-

from passport.backend.oauth.api.api.iface.forms import (
    AuthorizeCommitForm,
    AuthorizeSubmitForm,
    EditClientForm,
    IssueAppPasswordForm,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.framework import (
    FormTestCase,
    PatchesMixin,
)


TEST_REQUEST_ID = 'a' * 32
TEST_ANDROID_FINGERPRINT = 'a' * 95
TEST_OTHER_ANDROID_FINGERPRINT = 'b' * 95


class TestAuthorizeSubmitForm(FormTestCase, PatchesMixin):
    form = AuthorizeSubmitForm
    form_args = [{'test:foo': 'Foo', 'test:bar': 'Bar'}]

    def setUp(self):
        super(TestAuthorizeSubmitForm, self).setUp()
        self.patch_scopes()
        self.patch_login_to_uid_mapping()

        # Валидные и невалидные примеры данных задаём тут, а не на уровне класса,
        # так как нам нужен работающий патч конфига скоупов
        self.invalid_params = [
            (
                {},
                {
                    'client_id': ['missing'], 'response_type': ['missing'], 'language': ['missing'],
                },
            ),
            (
                {
                    'uid': '1', 'client_id': 'a' * 32, 'response_type': 'unknown', 'language': 'ru',
                },
                {'response_type': ['invalid']},
            ),

        ]
        self.valid_params = [
            (
                {
                    'client_id': 'a' * 32, 'response_type': 'code',
                    'language': 'ru',
                },
                {
                    'uid': None, 'client_id': 'a' * 32, 'response_type': 'code',
                    'redirect_uri': '', 'state': '', 'language': 'ru', 'device_id': '', 'device_name': '',
                    'requested_scopes': set(), 'code_challenge': '', 'code_challenge_method': 0,
                    'payment_auth_scheme': '', 'fingerprint': '',
                    'uuid': '', 'app_id': '', 'app_platform': '', 'manufacturer': '', 'model': '',
                    'app_version': '', 'am_version': '',
                },
            ),
            (
                {
                    'uid': '1', 'client_id': 'a' * 32, 'response_type': 'token',
                    'language': 'ru', 'requested_scopes': ['test:foo'],
                },
                {
                    'uid': 1, 'client_id': 'a' * 32, 'response_type': 'token',
                    'redirect_uri': '', 'state': '', 'language': 'ru', 'device_id': '', 'device_name': '',
                    'requested_scopes': {Scope.by_keyword('test:foo')},
                    'code_challenge': '', 'code_challenge_method': 0, 'payment_auth_scheme': '', 'fingerprint': '',
                    'uuid': '', 'app_id': '', 'app_platform': '', 'manufacturer': '', 'model': '',
                    'app_version': '', 'am_version': '',
                },
            ),
            (
                {
                    'uid': '1', 'client_id': 'a' * 32, 'response_type': 'code',
                    'language': 'ru', 'redirect_uri': 'http://ya.ru', 'state': '42',
                    'requested_scopes': ['test:foo', 'test:bar', 'test:foo'],
                    'payment_auth_scheme': 'yandex1',
                },
                {
                    'uid': 1, 'client_id': 'a' * 32, 'response_type': 'code',
                    'redirect_uri': 'http://ya.ru', 'state': '42', 'language': 'ru', 'device_id': '', 'device_name': '',
                    'requested_scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'code_challenge': '', 'code_challenge_method': 0, 'payment_auth_scheme': 'yandex1',
                    'uuid': '', 'app_id': '', 'app_platform': '', 'manufacturer': '', 'model': '',
                    'app_version': '', 'am_version': '', 'fingerprint': '',
                },
            ),
            (
                {
                    'uid': '1', 'client_id': 'a' * 32, 'response_type': 'code',
                    'language': 'ru', 'redirect_uri': 'http://ya.ru', 'state': '42', 'payment_auth_scheme': '',
                    'app_platform': 'Android', 'fingerprint': 'fp',
                },
                {
                    'uid': 1, 'client_id': 'a' * 32, 'response_type': 'code',
                    'redirect_uri': 'http://ya.ru', 'state': '42', 'language': 'ru', 'device_id': '', 'device_name': '',
                    'requested_scopes': set(), 'code_challenge': '', 'code_challenge_method': 0,
                    'payment_auth_scheme': '', 'fingerprint': 'fp',
                    'uuid': '', 'app_id': '', 'app_platform': 'Android', 'manufacturer': '', 'model': '',
                    'app_version': '', 'am_version': '',
                },
            ),
        ]


class TestAuthorizeCommitForm(FormTestCase, PatchesMixin):
    form = AuthorizeCommitForm
    form_args = [{'test:foo': 'Foo', 'test:bar': 'Bar'}]

    def setUp(self):
        super(TestAuthorizeCommitForm, self).setUp()
        self.patch_scopes()
        self.patch_login_to_uid_mapping()

        # Валидные и невалидные примеры данных задаём тут, а не на уровне класса,
        # так как нам нужен работающий патч конфига скоупов
        self.invalid_params = [
            (
                {},
                {
                    'request_id': ['missing'],
                },
            ),
            (
                {
                    'request_id': 'foo',
                    'granted_scopes': ['not-a-scope'],
                    'payment_auth_retpath': 'not-an-url',
                },
                {
                    'request_id': ['too_short'],
                    'granted_scopes': ['invalid'],
                    'payment_auth_retpath': ['scheme_missing'],
                },
            ),

        ]
        self.valid_params = [
            (
                {
                    'request_id': TEST_REQUEST_ID,
                },
                {
                    'uid': None,
                    'request_id': TEST_REQUEST_ID,
                    'granted_scopes': set(),
                    'payment_auth_retpath': '',
                },
            ),
            (
                {
                    'uid': '1',
                    'request_id': TEST_REQUEST_ID,
                    'granted_scopes': ['test:foo', 'test:bar'],
                    'payment_auth_retpath': 'http://ya.ru',
                },
                {
                    'uid': 1,
                    'request_id': TEST_REQUEST_ID,
                    'granted_scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'payment_auth_retpath': 'http://ya.ru',
                },
            ),
        ]


class TestEditClientForm(FormTestCase, PatchesMixin):
    form = EditClientForm
    form_args = [{'test:foo': 'Foo', 'test:bar': 'Bar'}]

    def setUp(self):
        super(TestEditClientForm, self).setUp()
        self.patch_scopes()
        self.patch_login_to_uid_mapping()

        # Валидные и невалидные примеры данных задаём тут, а не на уровне класса,
        # так как нам нужен работающий патч конфига скоупов
        self.invalid_params = [
            ({}, {'title': ['missing'], 'scopes': ['missing']}),
            ({'title': '   '}, {'title': ['missing'], 'scopes': ['missing']}),
            (
                # невалидные значения разных полей
                {
                    'title': 'a' * 101,
                    'icon_id': 'no_slash',
                    'scopes': ['test:ttl'],
                    'ios_app_id': 'foo.bar',
                    'android_package_name': 'foo-bar',
                    'android_cert_fingerprints': ['', 'foo'],
                    'turboapp_base_url': 'foo',
                    'owner_uids': ['foo'],
                    'owner_groups': ['foo'],
                    'platforms': ['foo'],
                    'contact_email': 'not_an_email',
                },
                {
                    'title': ['too_long'],
                    'icon_id': ['invalid'],
                    'scopes': ['invalid'],
                    'ios_app_id': ['0.invalid'],
                    'android_package_name': ['0.invalid'],
                    'android_cert_fingerprints': ['0.missing', '1.invalid'],
                    'turboapp_base_url': ['scheme_missing'],
                    'owner_uids': ['0.invalid'],
                    'owner_groups': ['0.invalid'],
                    'platforms': ['invalid'],
                    'contact_email': ['invalid'],
                },
            ),
            (
                # невалидные или слишком длинные значения разных полей
                {
                    'title': 'client',
                    'description': 'Test client',
                    'scopes': ['test:foo'],
                    'icon': 'http://home.ru/%s' % ('a' * 1010),
                    'icon_id': 'b/' + 'a' * 99,
                    'homepage': 'http://home.ru/%s' % ('a' * 1010),
                    'redirect_uri': 'http://home.ru/%s' % ('a' * 1010),
                    'android_package_name': 'a' * 101,
                    'android_cert_fingerprints': [TEST_ANDROID_FINGERPRINT],
                    'turboapp_base_url': 'http://home.ru/%s' % ('a' * 1010),
                    'owner_groups': ['staff:foo', 'st:bar', 'jira:zar'],
                },
                {
                    'icon': ['too_long'],
                    'icon_id': ['too_long'],
                    'homepage': ['too_long'],
                    'redirect_uri': ['0.too_long'],
                    'android_package_name': ['0.too_long'],
                    'turboapp_base_url': ['too_long'],
                    'owner_groups': ['1.prefix_invalid', '2.prefix_invalid'],
                },
            ),
            (
                # слишком много значений для collection-полей
                {
                    'title': 'client', 'scopes': ['test:foo'], 'is_yandex': 'true',
                    'redirect_uri': ['https://ya_%s.ru' % i for i in range(21)],
                    'owner_uids': list(range(1, 7)), 'owner_groups': ['staff:%s' % i for i in range(6)],
                    'android_package_name': ['packagename-%s' % i for i in range(6)],
                    'ios_app_id': ['app-id-%s' % i for i in range(6)],
                },
                {
                    'icon': ['required'], 'redirect_uri': ['too_many'], 'owner_uids': ['too_many'],
                    'owner_groups': ['too_many'], 'android_package_name': ['too_many'], 'ios_app_id': ['too_many'],
                },
            ),
            (
                # есть платформы - нужно задать все их поля
                {
                    'title': 'client', 'scopes': ['test:foo'], 'platforms': ['ios', 'android', 'turboapp', 'web'],
                },
                {
                    'ios_app_id': ['required'], 'turboapp_base_url': ['required'], 'android_package_name': ['required'],
                    'android_cert_fingerprints': ['required'], 'redirect_uri': ['required'],
                },
            ),
            (
                # есть платформы - пустые значения их полей не подойдут
                {
                    'title': 'client', 'scopes': ['test:foo'], 'platforms': ['ios', 'android', 'turboapp', 'web'],
                    'turboapp_base_url': '', 'redirect_uri': '', 'ios_app_id': '',
                    'android_package_name': '', 'android_cert_fingerprints': '',
                },
                {
                    'turboapp_base_url': ['required'], 'redirect_uri': ['0.missing'], 'ios_app_id': ['0.missing'],
                    'android_package_name': ['0.missing'], 'android_cert_fingerprints': ['0.missing'],
                },
            ),
            (
                # есть require_platform и нет platforms
                {
                    'title': 'client', 'scopes': ['test:foo'], 'require_platform': True,
                },
                {
                    'platforms': ['required'],
                },
            ),
        ]
        self.valid_params = [
            (
                # минимальный набор полей
                {
                    'title': 'client', 'scopes': ['test:foo'],
                },
                {
                    'uid': None, 'title': 'client', 'description': '', 'scopes': {Scope.by_keyword('test:foo')},
                    'icon_file': None, 'icon': '', 'icon_id': '', 'homepage': '', 'redirect_uri': [],
                    'is_yandex': False, 'ios_app_id': [], 'ios_appstore_url': '', 'turboapp_base_url': '',
                    'android_package_name': [], 'android_cert_fingerprints': [], 'android_appstore_url': '',
                    'owner_uids': [], 'owner_groups': [], 'platforms': [], 'require_platform': False,
                    'contact_email': '',
                },
            ),
            (
                # минимальный набор полей; поля платформ не учитываются, если платформы не выбраны
                {
                    'title': 'client', 'scopes': ['test:foo'], 'redirect_uri': 'http://test',
                    'is_yandex': False, 'ios_app_id': ' 1234567890.foo ', 'ios_appstore_url': 'https://ios.com',
                    'turboapp_base_url': 'https://ozon.ru', 'android_package_name': ' package_name ',
                    'android_cert_fingerprints': [TEST_ANDROID_FINGERPRINT, TEST_OTHER_ANDROID_FINGERPRINT],
                    'android_appstore_url': 'https://android.com',
                },
                {
                    'uid': None, 'title': 'client', 'description': '', 'scopes': {Scope.by_keyword('test:foo')},
                    'icon_file': None, 'icon': '', 'icon_id': '', 'homepage': '', 'redirect_uri': [],
                    'is_yandex': False, 'ios_app_id': [], 'ios_appstore_url': '', 'turboapp_base_url': '',
                    'android_package_name': [], 'android_cert_fingerprints': [], 'android_appstore_url': '',
                    'owner_uids': [], 'owner_groups': [], 'platforms': [], 'require_platform': False,
                    'contact_email': '',
                },
            ),
            (
                # полный набор полей
                {
                    'uid': '1', 'title': 'client', 'scopes': ['test:foo'], 'redirect_uri': 'http://test', 'icon_id': ' a/b ',
                    'is_yandex': 'false', 'ios_app_id': '1234567890.foo', 'android_package_name': 'package_name.foo',
                    'android_cert_fingerprints': [TEST_ANDROID_FINGERPRINT], 'turboapp_base_url': 'https://ozon.ru', 'owner_uids': [1],
                    'owner_groups': ['staff:foo'], 'platforms': ['ios', 'android', 'turboapp', 'web'],
                    'require_platform': True, 'contact_email': 'test@test.test',
                },
                {
                    'uid': 1, 'title': 'client', 'description': '', 'scopes': {Scope.by_keyword('test:foo')},
                    'icon_file': None, 'icon': '', 'icon_id': 'a/b', 'homepage': '', 'redirect_uri': ['http://test'],
                    'is_yandex': False, 'ios_app_id': ['1234567890.foo'], 'ios_appstore_url': '',
                    'android_package_name': ['package_name.foo'], 'android_cert_fingerprints': [TEST_ANDROID_FINGERPRINT],
                    'android_appstore_url': '', 'turboapp_base_url': 'https://ozon.ru', 'owner_uids': [1], 'owner_groups': ['staff:foo'],
                    'platforms': ['ios', 'android', 'turboapp', 'web'], 'require_platform': True,
                    'contact_email': 'test@test.test',
                },
            ),
            (
                # полный набор полей с множественными значениями для collection-полей
                {
                    'uid': '1', 'title': 'client', 'description': 'Test client', 'scopes': ['test:foo', 'test:bar', 'test:foo'],
                    'icon': 'http://home.ru/icon', 'icon_id': 'b/' + 'a' * 65, 'homepage': 'http://home.ru',
                    'redirect_uri': ['http://test', 'https://prod'], 'is_user_corporate': 'true',
                    'is_yandex': 'true', 'ios_app_id': [' 1234567890.foo ', '1234567890.bar'], 'ios_appstore_url': 'https://ios.com',
                    'turboapp_base_url': 'https://ozon.ru', 'android_package_name': [' package_name_1 ', 'package_name_2'],
                    'android_cert_fingerprints': [TEST_ANDROID_FINGERPRINT, TEST_OTHER_ANDROID_FINGERPRINT],
                    'android_appstore_url': 'https://android.com', 'owner_uids': [1, 2],
                    'owner_groups': ['staff:foo', 'staff:bar'], 'platforms': ['ios', 'android', 'turboapp', 'web'],
                    'require_platform': True, 'contact_email': 'test@test.test',
                },
                {
                    'uid': 1, 'title': 'client', 'description': 'Test client',
                    'scopes': {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')},
                    'icon_file': None, 'icon': 'http://home.ru/icon', 'icon_id': 'b/' + 'a' * 65,
                    'homepage': 'http://home.ru', 'redirect_uri': ['http://test', 'https://prod'],
                    'is_yandex': True, 'ios_app_id': ['1234567890.foo', '1234567890.bar'], 'ios_appstore_url': 'https://ios.com',
                    'turboapp_base_url': 'https://ozon.ru', 'android_package_name': ['package_name_1', 'package_name_2'],
                    'android_cert_fingerprints': [TEST_ANDROID_FINGERPRINT, TEST_OTHER_ANDROID_FINGERPRINT],
                    'android_appstore_url': 'https://android.com', 'owner_uids': [1, 2],
                    'owner_groups': ['staff:foo', 'staff:bar'], 'platforms': ['ios', 'android', 'turboapp', 'web'],
                    'require_platform': True, 'contact_email': 'test@test.test',
                },
            ),
        ]


class TestIssueAppPasswordForm(FormTestCase):
    form = IssueAppPasswordForm
    base_params = {
        'client_id': 'a' * 32,
        'device_id': 'a' * 6,
        'device_name': 'a',
        'language': 'ru',
        'uuid': '',
        'app_id': '',
        'app_platform': '',
        'manufacturer': '',
        'model': '',
        'app_version': '',
        'am_version': '',
    }
    base_expected_params = dict(
        base_params,
        uid=None,
    )
    valid_params = [
        (
            base_params,
            base_expected_params,
        ),
        (
            dict(base_params, device_name=''),
            dict(base_expected_params, device_name=''),
        ),
        (
            dict(base_params, uid='1'),
            dict(base_expected_params, uid=1),
        ),
    ]
