# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.api.env import APIEnvironment
from passport.backend.api.env.env import (
    _get_and_validate_host,
    _get_header,
    REQUEST_ID_ALPHABET,
    REQUEST_ID_LENGTH,
)
from passport.backend.api.exceptions import (
    InvalidHostError,
    MissingHeaderError,
)
from passport.backend.core.cookies.utils import (
    dump_cookie,
    parse_cookie,
)
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings
from werkzeug.datastructures import Headers


DEFAULT_HEADERS = [
    ('X-Real-Ip', '10.2.1.2'),
    ('User-Agent', 'MOZILLA'),
    ('Host', 'www.ya.ru'),
    ('Accept-Language', 'RU'),
    ('Referer', 'http://www.ya.ru'),
    ('Authorization', 'OAuth 123'),
]

DEFAULT_CUSTOM_HEADERS = [
    ('Ya-Consumer-Real-Ip', '10.2.1.1'),
    ('Ya-Consumer-Client-Ip', '172.1.1.1'),
    ('X-Real-Ip', '10.2.2.2'),
    ('Ya-Client-Cookie', 'key1=value1; key2=value2; key1=value3'),
    ('Ya-Client-User-Agent', 'Safary'),
    ('Ya-Client-Host', 'www.yandex.ru'),
    ('Ya-Client-Accept-Language', 'EN'),
    ('Ya-Client-Referer', 'http://www.yandex.ru'),
    ('Ya-Consumer-Authorization', 'OAuth My_Token-123'),
    ('Ya-Client-X-Request-Id', 'abc'),
    ('X-YProxy-Header-Ip', '8.8.8.8'),
]


def make_environ(headers, **kwargs):
    make_env_key = lambda key: 'HTTP_' + key.upper().replace('-', '_')
    return dict([(make_env_key(name), value) for name, value in headers],
                **kwargs)


@with_settings
class EnvironmentTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_grants = FakeGrants()
        self.fake_grants.set_grants_return_value({})
        self.fake_grants.start()

        self.request = mock.Mock()
        self.request.environ = make_environ(DEFAULT_HEADERS, REMOTE_ADDR='10.2.2.2')
        self.request.headers = Headers(DEFAULT_HEADERS)
        self.request.cookies = {
            'yandexuid': 'uid',
            'fuid00': 'f',
        }

    def tearDown(self):
        self.fake_grants.stop()
        del self.fake_grants
        del self.request

    def test_from_request(self):
        env = APIEnvironment.from_request(self.request)
        eq_(env.cookies, {})
        eq_(env.user_ip, '10.2.1.2')
        eq_(env.consumer_ip, '10.2.1.2')
        eq_(env.user_agent, 'MOZILLA')
        eq_(env.host, 'www.ya.ru')
        eq_(env.accept_language, 'RU')
        eq_(env.referer, 'http://www.ya.ru')
        eq_(env.authorization, 'OAuth 123')

    def test_from_request_no_real_ip(self):
        del self.request.environ['HTTP_X_REAL_IP']
        env = APIEnvironment.from_request(self.request)
        eq_(env.user_ip, '10.2.2.2')

    def test_from_request_custom_headers(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        env = APIEnvironment.from_request(self.request)
        eq_(env.cookies, {'key1': 'value1', 'key2': 'value2'})
        eq_(env.cookies_all, {'key1': ['value3', 'value1'], 'key2': ['value2']})
        eq_(env.consumer_ip, '10.2.2.2')
        eq_(env.user_ip, '172.1.1.1')
        eq_(env.user_agent, 'Safary')
        eq_(env.host, 'www.yandex.ru')
        eq_(env.accept_language, 'EN')
        eq_(env.referer, 'http://www.yandex.ru')
        eq_(env.authorization, 'OAuth My_Token-123')

    def test_from_request_custom_headers_no_client_ip(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        del self.request.environ['HTTP_YA_CONSUMER_CLIENT_IP']
        env = APIEnvironment.from_request(self.request)
        eq_(env.user_ip, '10.2.2.2')

    def test_from_request_client_ip_from_proxy(self):
        self.fake_grants.set_grants_return_value(
            mock_grants(
                consumer='mobileproxy_substitute_ip',
                grants=[],
                networks=['172.1.1.1'],
            ),
        )
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        env = APIEnvironment.from_request(self.request)
        eq_(env.user_ip, '8.8.8.8')

    def test_from_request_consumer_ip_from_proxy(self):
        self.fake_grants.set_grants_return_value(
            mock_grants(
                consumer='allow_ya_consumer_real_ip',
                grants=[],
                networks=['10.2.2.2'],
            ),
        )
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        env = APIEnvironment.from_request(self.request)
        eq_(env.consumer_ip, '10.2.1.1')

    def test_from_request_custom_headers_no_client_cookie(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        del self.request.environ['HTTP_YA_CLIENT_COOKIE']
        env = APIEnvironment.from_request(self.request)
        eq_(env.cookies, {})

    def test_from_request_custom_headers_invalid_client_cookie(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        self.request.environ['HTTP_YA_CLIENT_COOKIE'] = '$key0=value0;key1=value1;$key2=value2; $key3=value3'
        env = APIEnvironment.from_request(self.request)
        eq_(
            env.cookies,
            {
                '$key0': 'value0',
                'key1': 'value1',
                '$key2': 'value2',
                '$key3': 'value3',
            },
        )

    def test_from_request_custom_headers_unicode_cookie(self):
        """Проверяем, что можем распарсить значение куки, содержащее не-ASCII текст"""
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        self.request.environ['HTTP_YA_CLIENT_COOKIE'] = u'yandex_login=login@закодированный.домен; test="тест"'.encode('utf-8')
        env = APIEnvironment.from_request(self.request)
        eq_(
            env.cookies,
            {
                'yandex_login': u'login@закодированный.домен',
                'test': u'тест',
            },
        )

    def test_from_request_invalid_chars_in_user_agent(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        self.request.environ['HTTP_YA_CLIENT_USER_AGENT'] = 'Mozilla/5.0 (Linux; Android 4.2.2; Samsung\xfdgalaxy\xfdtab5 Build/JDQ39)'
        env = APIEnvironment.from_request(self.request)
        eq_(env.user_agent, 'Mozilla/5.0 (Linux; Android 4.2.2; Samsunggalaxytab5 Build/JDQ39)')

    def test_nginx_request_id(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1', )
        env = APIEnvironment.from_request(self.request)
        eq_(env.request_id, 'abc')

        del self.request.environ['HTTP_YA_CLIENT_X_REQUEST_ID']
        self.request.environ['HTTP_X_REQUEST_ID'] = 'fff'
        env = APIEnvironment.from_request(self.request)
        eq_(env.request_id, 'fff')

    def test_generated_request_id(self):
        self.request.environ = make_environ({}, REMOTE_ADDR='10.2.2.1')
        env = APIEnvironment.from_request(self.request)
        eq_(len(env.request_id), REQUEST_ID_LENGTH)
        ok_(env.request_id.startswith('g-'))
        ok_(set(env.request_id).issubset(set(REQUEST_ID_ALPHABET + '-')))

    def test_request_path(self):
        self.request.path = '/1/2'

        env = APIEnvironment.from_request(self.request)

        assert env.request_path == self.request.path

    @raises(MissingHeaderError)
    def test_get_header_missing_error(self):
        _get_header({}, 'header', 'alt_header', True)

    @raises(InvalidHostError)
    def test_get_and_validate_host_error(self):
        _get_and_validate_host({'HTTP_YA_CLIENT_HOST': 'foo.com?retpath=yandex.com'})

    @raises(InvalidHostError)
    def test_get_and_validate_host_with_auth_data_error(self):
        _get_and_validate_host({'HTTP_YA_CLIENT_HOST': 'login:password@foo.com'})

    def test_get_and_validate_host_ok(self):
        test_valid_hosts = ['foo.com', 'foo.com:1234']
        for host in test_valid_hosts:
            eq_(host, _get_and_validate_host({'HTTP_YA_CLIENT_HOST': host}))


def test_cookie_dump_and_parse():
    values = (
        ('key', 'value', 'key=value; Path=/'),
        ('key', u'value@тестовыйдомен', u'key=value@тестовыйдомен; Path=/'.encode('utf-8')),
    )

    for cookie_key, cookie_value, expected_serialized_value in values:
        serialized_value = dump_cookie(cookie_key, cookie_value)
        eq_(expected_serialized_value, serialized_value)
        eq_({cookie_key: cookie_value}, parse_cookie(serialized_value))


def test_parse_several_cookies():
    """Проверяем, что при наличии нескольких кук с одним именем мы возьмём первое значение"""
    cookies = parse_cookie(
        'Session_id=new; yandexuid=yu; Session_id=old',
    )
    eq_(cookies, {'Session_id': 'new', 'yandexuid': 'yu'})
