# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import eq_
from passport.backend.adm_api.common.env import APIEnvironment
from passport.backend.adm_api.test.utils import with_settings
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
    ('Ya-Client-Cookie', 'key1=value1; key2=value2'),
    ('Ya-Client-User-Agent', 'Safary'),
    ('Ya-Client-Host', 'www.yandex.ru'),
    ('Ya-Client-Accept-Language', 'EN'),
    ('Ya-Client-Referer', 'http://www.yandex.ru'),
    ('Ya-Consumer-Authorization', 'OAuth 123'),
]


def make_environ(headers, **kwargs):
    make_env_key = lambda key: 'HTTP_' + key.upper().replace('-', '_')
    return dict([(make_env_key(name), value) for name, value in headers],
                **kwargs)


@with_settings()
class EnvironmentTestCase(unittest.TestCase):

    def setUp(self):
        self.request = mock.Mock()
        self.request.environ = make_environ(DEFAULT_HEADERS, REMOTE_ADDR='10.2.2.2')
        self.request.headers = Headers(DEFAULT_HEADERS)
        self.request.cookies = {
            'yandexuid': 'uid',
            'fuid00': 'f',
        }

    def test_from_request(self):
        env = APIEnvironment.from_request(self.request)
        eq_(dict(env.cookies), {})
        eq_(env.user_ip, '10.2.1.2')
        eq_(env.consumer_ip, '10.2.1.2')
        eq_(env.user_agent, 'MOZILLA')
        eq_(env.host, 'www.ya.ru')

    def test_from_request_no_real_ip(self):
        del self.request.environ['HTTP_X_REAL_IP']
        env = APIEnvironment.from_request(self.request)
        eq_(env.user_ip, '10.2.2.2')

    def test_from_request_custom_headers(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        env = APIEnvironment.from_request(self.request)
        eq_(dict(env.cookies), {'key1': 'value1', 'key2': 'value2'})
        eq_(env.consumer_ip, '10.2.1.1')
        eq_(env.user_ip, '172.1.1.1')
        eq_(env.user_agent, 'Safary')
        eq_(env.host, 'www.yandex.ru')

    def test_from_request_custom_headers_no_client_ip(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        del self.request.environ['HTTP_YA_CONSUMER_CLIENT_IP']
        env = APIEnvironment.from_request(self.request)
        eq_(env.user_ip, '10.2.1.1')

    def test_from_request_custom_headers_no_consumer_real_ip(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        del self.request.environ['HTTP_YA_CONSUMER_REAL_IP']
        env = APIEnvironment.from_request(self.request)
        eq_(env.consumer_ip, '10.2.2.2')

    def test_from_request_custom_headers_no_client_cookie(self):
        self.request.environ = make_environ(DEFAULT_CUSTOM_HEADERS, REMOTE_ADDR='10.2.2.1')
        self.request.headers = Headers(DEFAULT_CUSTOM_HEADERS)
        del self.request.environ['HTTP_YA_CONSUMER_REAL_IP']
        del self.request.environ['HTTP_YA_CLIENT_COOKIE']
        env = APIEnvironment.from_request(self.request)
        eq_(dict(env.cookies), {})
