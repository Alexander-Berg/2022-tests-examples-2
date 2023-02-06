# -*- coding: utf-8 -*-
from django.http import (
    HttpRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.test.utils import override_settings
from django.urls import reverse
from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.oauth.api.api.middlewares import LocalePerDomainMiddleware
from passport.backend.oauth.core.api.middlewares import (
    HTTPSMiddleware,
    StoreEnvironmentMiddleware,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_HOST,
    TEST_INTERNAL_HOST,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework import (
    BaseTestCase,
    PatchesMixin,
)


TEST_REMOTE_ADDR = '127.0.0.1'
TEST_USER_IP = '11.11.11.11'
TEST_CONSUMER_IP = '7.7.7.7'
TEST_HOST = TEST_HOST
TEST_INTERNAL_HOST = TEST_INTERNAL_HOST


class BaseMiddlewareTestCase(BaseTestCase):
    middleware_class = None

    def process_request(self, http_method='GET', host=TEST_HOST, path='',
                        ip=TEST_REMOTE_ADDR, request_args=None, headers=None, cookies=None):
        request = HttpRequest()
        request.method = http_method
        request.META['HTTP_HOST'] = host
        request.META['REMOTE_ADDR'] = ip
        request.META.update(headers or {})
        request.COOKIES = cookies or {}
        request.REQUEST = request_args or {}
        request.path = path
        response = self.middleware_class().process_request(request)
        return request, response


@override_settings(
    REQUIRE_HTTPS=True,
    NO_HTTPS_FOR_HOSTS=[TEST_INTERNAL_HOST],
)
class HttpsTestCase(BaseMiddlewareTestCase):
    middleware_class = HTTPSMiddleware

    def test_redirect_to_https(self):
        request, response = self.process_request(path=reverse('list_clients_by_user', args=[TEST_UID]))
        ok_(isinstance(response, HttpResponseRedirect))
        eq_(response.status_code, 302)
        ok_(response['location'].startswith('https://'))

    def test_no_redirect_for_excluded_urls(self):
        request, response = self.process_request(path=reverse('ping'))
        assert_is_none(response)

    def test_no_redirect_for_excluded_hosts(self):
        request, response = self.process_request(
            host=TEST_INTERNAL_HOST,
            path=reverse('list_clients_by_user', args=[TEST_UID]),
        )
        assert_is_none(response)

    def test_no_redirect_for_post(self):
        request, response = self.process_request(
            http_method='POST',
            path=reverse('list_clients_by_user', args=[TEST_UID]),
        )
        ok_(isinstance(response, HttpResponseForbidden))
        eq_(response.content.decode(), 'Use HTTPS')

    def test_no_redirect_for_unknown_method(self):
        request, response = self.process_request(
            http_method='PATCH',
            path=reverse('list_clients_by_user', args=[TEST_UID]),
        )
        eq_(response.status_code, 405)


@override_settings(
    ENV_TYPE='production',
    INTERNAL_HOSTS=[TEST_INTERNAL_HOST],
)
class StoreEnvironmentTestCase(BaseMiddlewareTestCase, PatchesMixin):
    middleware_class = StoreEnvironmentMiddleware

    def setUp(self):
        super(StoreEnvironmentTestCase, self).setUp()
        self.patch_grants()

    def test_external_ips(self):
        request, response = self.process_request(
            request_args={'user_ip': TEST_USER_IP},
        )
        eq_(request.env.user_ip, TEST_REMOTE_ADDR)  # значение переданного параметра игнорируется
        eq_(request.env.consumer_ip, TEST_REMOTE_ADDR)

    def test_internal_ips(self):
        request, response = self.process_request(
            host=TEST_INTERNAL_HOST,
            request_args={'user_ip': TEST_USER_IP},
        )
        eq_(request.env.user_ip, TEST_USER_IP)
        eq_(request.env.consumer_ip, TEST_REMOTE_ADDR)

    def test_internal_ips_param_not_passed(self):
        request, response = self.process_request(
            host=TEST_INTERNAL_HOST,
        )
        eq_(request.env.user_ip, TEST_REMOTE_ADDR)
        eq_(request.env.consumer_ip, TEST_REMOTE_ADDR)

    def test_cookies_and_headers(self):
        request, response = self.process_request(
            headers={
                'HTTP_USER_AGENT': 'ua',
                'HTTP_X_REQUEST_ID': 'rid',
            },
            cookies={'Yandexuid': 'yu'},
        )
        eq_(request.env.cookies, {'Yandexuid': 'yu'})
        eq_(request.env.user_agent, 'ua')
        eq_(request.env.request_id, 'rid')

    def test_cookies_and_headers_empty(self):
        request, response = self.process_request(
            headers={
                'HTTP_X_REAL_IP': TEST_CONSUMER_IP,  # этот заголовок всегда выставляет nginx
            },
        )
        eq_(request.env.user_ip, TEST_CONSUMER_IP)
        eq_(request.env.consumer_ip, TEST_CONSUMER_IP)
        eq_(request.env.cookies, {})
        ok_(request.env.user_agent is None)
        ok_(request.env.request_id is None)

    def test_client_headers(self):
        request, response = self.process_request(
            host=TEST_INTERNAL_HOST,
            headers={
                'HTTP_X_REAL_IP': TEST_CONSUMER_IP,
                'HTTP_YA_CONSUMER_CLIENT_IP': '8.8.8.8',
                'HTTP_X_YPROXY_HEADER_IP': '10.10.10.10',
                'HTTP_YA_CLIENT_USER_AGENT': 'ua',
                'HTTP_YA_CLIENT_COOKIE': 'Yandexuid=yu',
                'HTTP_COOKIE': 'foo=bar',
                'HTTP_YA_CLIENT_HOST': 'oauth-rc.yandex.ru',
            },
        )
        eq_(request.env.user_ip, '8.8.8.8')
        eq_(request.env.consumer_ip, TEST_CONSUMER_IP)
        eq_(request.env.cookies, {'Yandexuid': 'yu'})
        eq_(request.env.user_agent, 'ua')
        eq_(request.env.host, 'oauth-rc.yandex.ru')

    def test_client_headers_external(self):
        request, response = self.process_request(
            headers={
                'HTTP_X_REAL_IP': TEST_CONSUMER_IP,
                'HTTP_YA_CONSUMER_CLIENT_IP': '8.8.8.8',
                'HTTP_X_YPROXY_HEADER_IP': '10.10.10.10',
                'HTTP_YA_CLIENT_USER_AGENT': 'ua',
                'HTTP_YA_CLIENT_COOKIE': 'Yandexuid=yu',
                'HTTP_COOKIE': 'foo=bar',
                'HTTP_YA_CLIENT_HOST': 'oauth-rc.yandex.ru',
            },
        )
        eq_(request.env.user_ip, TEST_CONSUMER_IP)
        eq_(request.env.consumer_ip, TEST_CONSUMER_IP)
        eq_(request.env.cookies, {'Yandexuid': 'yu'})
        ok_(request.env.user_agent is None)
        eq_(request.env.host, 'oauth.yandex.ru')

    def test_client_headers_mobileproxy(self):
        request, response = self.process_request(
            host=TEST_INTERNAL_HOST,
            headers={
                'HTTP_X_REAL_IP': TEST_CONSUMER_IP,
                'HTTP_YA_CONSUMER_CLIENT_IP': '255.255.255.255',
                'HTTP_X_YPROXY_HEADER_IP': '10.10.10.10',
                'HTTP_YA_CLIENT_USER_AGENT': 'ua',
                'HTTP_YA_CLIENT_COOKIE': 'Yandexuid=yu',
                'HTTP_YA_CLIENT_HOST': 'oauth-rc.yandex.ru',
            },
        )
        eq_(request.env.user_ip, '10.10.10.10')
        eq_(request.env.consumer_ip, TEST_CONSUMER_IP)
        eq_(request.env.cookies, {'Yandexuid': 'yu'})
        eq_(request.env.user_agent, 'ua')
        eq_(request.env.host, 'oauth-rc.yandex.ru')

    def test_client_data_invalid(self):
        request, response = self.process_request(
            host=TEST_INTERNAL_HOST,
            headers={
                'HTTP_YA_CONSUMER_CLIENT_IP': 'unparsed_ip',
                'HTTP_YA_CLIENT_COOKIE': '/=/',
            },
        )
        eq_(request.env.user_ip, 'unparsed_ip')
        eq_(request.env.cookies, {'/': '/'})


@override_settings(
    OAUTH_TLDS=('ru', 'com', 'com.tr', 'ua'),
)
class LocalePerDomainTestCase(BaseMiddlewareTestCase):
    middleware_class = LocalePerDomainMiddleware

    def check_for_tld(self, tld):
        request, response = self.process_request(host='oauth.yandex.%s' % tld)
        assert_is_none(response)
        return request.TLD, request.LANGUAGE_CODE

    def test_locales(self):
        eq_(self.check_for_tld('ru'), ('ru', 'ru'))
        eq_(self.check_for_tld('com'), ('com', 'en'))
        eq_(self.check_for_tld('com.tr'), ('com.tr', 'tr'))
        eq_(self.check_for_tld('ua'), ('ua', 'uk'))
        eq_(self.check_for_tld('de'), ('ru', 'ru'))  # для неподдерживаемых TLD - фолбек на ru-домен и ru-локаль
