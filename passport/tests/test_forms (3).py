# -*- coding: utf-8 -*-
from passport.backend.oauth.api.api.forms import (
    ClientIdMixin,
    ClientIdsMixin,
    ClientSecretMixin,
    CodeChallengeMixin,
    DeviceInfoMixin,
    LanguageMixin,
    RedirectUriOptionalMixin,
    RedirectUrisOptionalMixin,
    RequestIdMixin,
    TokenIdMixin,
    TokenIdsMixin,
)
from passport.backend.oauth.core.test.framework import (
    FormTestCase,
    PatchesMixin,
)


class TestLanguageMixin(FormTestCase):
    form = LanguageMixin
    invalid_params = [
        ({}, {'language': ['missing']}),
        ({'language': ''}, {'language': ['missing']}),
    ]
    valid_params = [
        # честно поддерживаемые языки
        ({'language': 'ru'}, {'language': 'ru'}),
        ({'language': 'en'}, {'language': 'en'}),
        ({'language': 'tr'}, {'language': 'tr'}),
        ({'language': 'uk'}, {'language': 'uk'}),
        # нормализация
        ({'language': 'rU'}, {'language': 'ru'}),
        # фолбеки
        ({'language': 'id'}, {'language': 'en'}),
        ({'language': 'by'}, {'language': 'ru'}),
        ({'language': 'kz'}, {'language': 'ru'}),
        ({'language': 'some-weird-lang'}, {'language': 'ru'}),
    ]


class TestClientIdMixin(FormTestCase):
    form = ClientIdMixin
    invalid_params = [
        ({}, {'client_id': ['missing']}),
        ({'client_id': ''}, {'client_id': ['missing']}),
        ({'client_id': '  '}, {'client_id': ['missing']}),
        ({'client_id': 'a' * 31}, {'client_id': ['too_short']}),
        ({'client_id': 'a' * 33}, {'client_id': ['too_long']}),
    ]
    valid_params = [
        ({'client_id': 'a' * 32}, {'client_id': 'a' * 32}),
        ({'client_id': 'g' * 32}, {'client_id': 'g' * 32}),  # да, не hex тоже пока принимаем
    ]


class TestClientIdsMixin(FormTestCase):
    form = ClientIdsMixin

    invalid_params = [
        ({}, {'client_id': ['missing']}),
        ({'client_id': ' '}, {'client_id': ['missing']}),
    ]
    valid_params = [
        (
            {'client_id': '1a2b' * 8},
            {'client_id': ['1a2b' * 8]},
        ),
        (
            {'client_id': ['1a2b3c4e' * 4, '1а2б3в4г' * 4, '1#2$3&4@' * 4]},
            {'client_id': ['1a2b3c4e' * 4, '1а2б3в4г' * 4, '1#2$3&4@' * 4]},
        ),
    ]


class TestClientSecretMixin(FormTestCase):
    form = ClientSecretMixin
    invalid_params = [
        ({}, {'client_secret': ['missing']}),
        ({'client_secret': ''}, {'client_secret': ['missing']}),
        ({'client_secret': '  '}, {'client_secret': ['missing']}),
        ({'client_secret': 'a' * 31}, {'client_secret': ['too_short']}),
        ({'client_secret': 'a' * 33}, {'client_secret': ['too_long']}),
    ]
    valid_params = [
        ({'client_secret': 'a' * 32}, {'client_secret': 'a' * 32}),
        ({'client_secret': 'g' * 32}, {'client_secret': 'g' * 32}),  # да, не hex тоже пока принимаем
    ]


class TestTokenIdMixin(FormTestCase):
    form = TokenIdMixin
    invalid_params = [
        ({}, {'token_id': ['missing']}),
        ({'token_id': ''}, {'token_id': ['missing']}),
        ({'token_id': '0'}, {'token_id': ['invalid']}),
    ]
    valid_params = [
        ({'token_id': '1'}, {'token_id': 1}),
        ({'token_id': '100500'}, {'token_id': 100500}),
    ]


class TestTokenIdsMixin(FormTestCase):
    form = TokenIdsMixin
    invalid_params = [
        ({}, {'token_id': ['missing']}),
        ({'token_id': ''}, {'token_id': ['missing']}),
        ({'token_id': 'abc'}, {'token_id': ['invalid']}),
        ({'token_id': '0'}, {'token_id': ['invalid']}),
    ]
    valid_params = [
        ({'token_id': '123'}, {'token_id': [123]}),
        ({'token_id': ['1', '2', '3']}, {'token_id': [1, 2, 3]}),
    ]


class TestRequestIdMixin(FormTestCase):
    form = RequestIdMixin
    invalid_params = [
        ({}, {'request_id': ['missing']}),
        ({'request_id': ''}, {'request_id': ['missing']}),
        ({'request_id': '  '}, {'request_id': ['missing']}),
        ({'request_id': 'a' * 31}, {'request_id': ['too_short']}),
        ({'request_id': 'a' * 33}, {'request_id': ['too_long']}),
    ]
    valid_params = [
        ({'request_id': 'a' * 32}, {'request_id': 'a' * 32}),
        ({'request_id': 'g' * 32}, {'request_id': 'g' * 32}),  # да, такое тоже пока принимаем
    ]


class TestRedirectUriOptionalMixin(FormTestCase):
    form = RedirectUriOptionalMixin
    invalid_params = [
        ({'redirect_uri': 'a' * 1025}, {'redirect_uri': ['too_long']}),
        ({'redirect_uri': 'ya.ru'}, {'redirect_uri': ['scheme_missing']}),
        ({'redirect_uri': 'http:/test'}, {'redirect_uri': ['not_absolute']}),
        ({'redirect_uri': 'javascript://alert("foo")'}, {'redirect_uri': ['scheme_forbidden']}),
        ({'redirect_uri': 'vbscript://WScript.Echo("foo")'}, {'redirect_uri': ['scheme_forbidden']}),
        ({'redirect_uri': 'data:text/html,<script>alert("foo")</script>'}, {'redirect_uri': ['scheme_forbidden']}),
        ({'redirect_uri': 'http://ya.ru?foo=bar|zar'}, {'redirect_uri': ['invalid']}),
        ({'redirect_uri': 'https://1502\u02dd\xcc\xc2\uf8ff\u201e\xcb\ufb02.\uf8ff\xd9'}, {'redirect_uri': ['invalid']}),
        ({'redirect_uri': 'http://ya.ru:foo'}, {'redirect_uri': ['invalid']}),
        ({'redirect_uri': 'http://ya.ru]'}, {'redirect_uri': ['invalid']}),
    ]
    valid_params = [
        ({}, {'redirect_uri': ''}),
        ({'redirect_uri': ''}, {'redirect_uri': ''}),
        ({'redirect_uri': '  '}, {'redirect_uri': ''}),
        ({'redirect_uri': 'http://ya.ru'}, {'redirect_uri': 'http://ya.ru'}),
        ({'redirect_uri': 'schema://callback'}, {'redirect_uri': 'schema://callback'}),
        ({'redirect_uri': 'http://окна.рф'}, {'redirect_uri': 'http://окна.рф'}),
        ({'redirect_uri': 'http://xn--80atjc.xn--p1ai'}, {'redirect_uri': 'http://xn--80atjc.xn--p1ai'}),
    ]


class TestRedirectUrisOptionalMixin(FormTestCase):
    form = RedirectUrisOptionalMixin
    invalid_params = [
        ({'redirect_uri': ['']}, {'redirect_uri': ['0.missing']}),
        ({'redirect_uri': ['', 'foo', '']}, {'redirect_uri': ['0.missing', '1.scheme_missing', '2.missing']}),
    ]
    valid_params = [
        ({}, {'redirect_uri': []}),
        ({'redirect_uri': 'http://ya.ru'}, {'redirect_uri': ['http://ya.ru']}),
        ({'redirect_uri': ['http://ya.ru', 'http://ya.com']}, {'redirect_uri': ['http://ya.ru', 'http://ya.com']}),
    ]


class TestDeviceInfoMixin(FormTestCase, PatchesMixin):
    form = DeviceInfoMixin
    invalid_params = [
        ({}, {'device_id': ['missing'], 'device_name': ['missing']}),
        ({'device_id': '', 'device_name': ''}, {'device_id': ['missing'], 'device_name': ['missing']}),
        ({'device_id': '', 'device_name': '   '}, {'device_id': ['missing'], 'device_name': ['missing']}),
        ({'device_id': 'a' * 5, 'device_name': ''}, {'device_id': ['too_short'], 'device_name': ['missing']}),
        ({'device_id': 'a' * 51, 'device_name': 'a' * 101}, {'device_id': ['too_long'], 'device_name': ['too_long']}),
        ({'device_id': 'привет', 'device_name': 'привет'}, {'device_id': ['invalid']}),
    ]
    valid_params = [
        (
            {'device_id': 'a' * 6, 'device_name': 'a'},
            {
                'device_id': 'a' * 6,
                'device_name': 'a',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
            },
        ),
        (
            {'device_id': 'a' * 50, 'device_name': 'a' * 100},
            {
                'device_id': 'a' * 50,
                'device_name': 'a' * 100,
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': '',
                'model': '',
                'app_version': '',
                'am_version': '',
            },
        ),
        (
            {
                'device_id': 'a_1 + b^2 % (3 / 2 + x)',
                'device_name': 'имя устройства',
                'uuid': 'UUID',
                'app_id': 'app-id',
                'app_platform': 'app-platform',
                'manufacturer': 'manufacturer',
                'model': 'model',
                'app_version': '1.2.3',
                'am_version': '4.5.6',
            },
            {
                'device_id': 'a_1 + b^2 % (3 / 2 + x)',
                'device_name': 'имя устройства',
                'uuid': 'UUID',
                'app_id': 'app-id',
                'app_platform': 'app-platform',
                'manufacturer': 'manufacturer',
                'model': 'model',
                'app_version': '1.2.3',
                'am_version': '4.5.6',
            },
        ),
        (
            {
                'deviceid': 'xxx-yyy',
                'model': 'iPhone7',
                'manufacturer': 'sony',
            },
            {
                'device_id': 'xxx-yyy',
                'device_name': 'iPhone Cheap',
                'uuid': '',
                'app_id': '',
                'app_platform': '',
                'manufacturer': 'sony',
                'model': 'iPhone7',
                'app_version': '',
                'am_version': '',
            },
        ),
    ]

    def setUp(self):
        self.patch_device_names_mapping()


class TestCodeChallengeMixin(FormTestCase):
    form = CodeChallengeMixin
    invalid_params = [
        (
            {
                'code_challenge': 'abc',
                'code_challenge_method': 'foo',
            },
            {
                'code_challenge': ['too_short'],
                'code_challenge_method': ['invalid'],
            },
        ),
        (
            {
                'code_challenge': 'a' * 201,
            },
            {
                'code_challenge': ['too_long'],
            },
        ),
    ]
    valid_params = [
        (
            {},
            {
                'code_challenge': '',
                'code_challenge_method': 0,
            },
        ),
        (
            {
                'code_challenge_method': 'plain',
            },
            {
                'code_challenge': '',
                'code_challenge_method': 0,
            },
        ),
        (
            {
                'code_challenge': 'a' * 43,
            },
            {
                'code_challenge': 'a' * 43,
                'code_challenge_method': 1,
            },
        ),
        (
            {
                'code_challenge': 'a' * 43,
                'code_challenge_method': 'plain',
            },
            {
                'code_challenge': 'a' * 43,
                'code_challenge_method': 1,
            },
        ),
        (
            {
                'code_challenge': 'a' * 128,
                'code_challenge_method': 'S256',
            },
            {
                'code_challenge': 'a' * 128,
                'code_challenge_method': 2,
            },
        ),
    ]
