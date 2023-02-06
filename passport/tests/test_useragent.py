# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import contextlib
from socket import error as SocketError
from urllib import quote as urllib_quote

from mock import (
    ANY as MockAny,
    call as MockCall,
    Mock,
    patch,
)
from nose.tools import eq_
from passport.backend.core.test.test_utils.utils import iterdiff
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_ALIAS as TVM_ALIAS1,
    TEST_TICKET as TVM_TICKET1,
)
from passport.backend.core.tvm.tvm_credentials_manager import TvmCredentialsManager
from passport.backend.social.common._urllib3 import (
    _FixIssue1758ConnectionPoolMixin,
    PoolManager,
    ProxyManager,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import (
    Request,
    Response,
    UserAgent,
    ZoraUseragent,
)
import urllib3.exceptions


URL1 = 'http://www.altavista.us/'


class TestRequest(TestCase):
    def _quoted_unicode(self, value):
        return urllib_quote(value.encode('utf-8')).decode('ascii')

    def test_quoted_unicode_url(self):
        quoted_path = self._quoted_unicode('ы')
        url = 'http://www.ya.ru/%s' % quoted_path
        request = Request(method='GET', url=url)

        self.assertEqual(request.url, 'http://www.ya.ru/%s' % quoted_path)

    def test_quoted_utf8_url(self):
        quoted_path = self._quoted_unicode('ы')
        url = 'http://www.ya.ru/%s' % quoted_path
        url = url.encode('utf-8')
        request = Request(method='GET', url=url)

        self.assertEqual(request.url, 'http://www.ya.ru/%s' % quoted_path)

    def test_not_quoted_unicode_url(self):
        request = Request(method='GET', url='http://www.ya.ru/ы')

        quoted_path = self._quoted_unicode('ы')
        self.assertEqual(request.url, 'http://www.ya.ru/%s' % quoted_path)

    def test_not_quoted_utf8_url(self):
        url = 'http://www.ya.ru/ы'
        url = url.encode('utf-8')
        request = Request(method='GET', url=url)

        quoted_path = self._quoted_unicode('ы')
        self.assertEqual(request.url, 'http://www.ya.ru/%s' % quoted_path)

    def test_quoted_unicode_params(self):
        params = dict(
            quoted_key=self._quoted_unicode('а'),
            quoted_value=self._quoted_unicode('б'),
        )
        url = 'http://www.ya.ru/?%(quoted_key)s=%(quoted_value)s' % params
        request = Request(method='GET', url=url)

        self.assertEqual(
            request.url,
            'http://www.ya.ru/?%(quoted_key)s=%(quoted_value)s' % params,
        )

    def test_quoted_utf8_params(self):
        params = dict(
            quoted_key=self._quoted_unicode('а'),
            quoted_value=self._quoted_unicode('б'),
        )
        url = 'http://www.ya.ru/?%(quoted_key)s=%(quoted_value)s' % params
        url = url.encode('utf-8')
        request = Request(method='GET', url=url)

        self.assertEqual(
            request.url,
            'http://www.ya.ru/?%(quoted_key)s=%(quoted_value)s' % params,
        )

    def test_not_quoted_unicode_params(self):
        params = dict(key='а', value='б')
        url = 'http://www.ya.ru/?%(key)s=%(value)s' % params
        request = Request(method='GET', url=url, params={'в': 'г'})

        params = dict(
            quoted_key1=self._quoted_unicode('а'),
            quoted_value1=self._quoted_unicode('б'),
            quoted_key2=self._quoted_unicode('в'),
            quoted_value2=self._quoted_unicode('г'),
        )
        self.assertEqual(
            request.url,
            'http://www.ya.ru/?%(quoted_key1)s=%(quoted_value1)s&%(quoted_key2)s=%(quoted_value2)s' % params,
        )

    def test_not_quoted_utf8_params(self):
        params = dict(key='а', value='б')
        url = 'http://www.ya.ru/?%(key)s=%(value)s' % params
        url = url.encode('utf-8')
        request = Request(
            method='GET',
            url=url,
            params={'в'.encode('utf-8'): 'г'.encode('utf-8')},
        )

        params = dict(
            quoted_key1=self._quoted_unicode('а'),
            quoted_value1=self._quoted_unicode('б'),
            quoted_key2=self._quoted_unicode('в'),
            quoted_value2=self._quoted_unicode('г'),
        )
        self.assertEqual(
            request.url,
            'http://www.ya.ru/?%(quoted_key1)s=%(quoted_value1)s&%(quoted_key2)s=%(quoted_value2)s' % params,
        )

    def test_quoted_unicode_data(self):
        data = '%s=%s' % (self._quoted_unicode('а'), self._quoted_unicode('б'))
        request = Request(
            method='GET',
            url='http://www.ya.ru/',
            data=data,
        )

        self.assertEqual(request.data, data)

    def test_quoted_utf8_data(self):
        data = '%s=%s' % (self._quoted_unicode('а'), self._quoted_unicode('б'))
        data = data.encode('utf-8')
        request = Request(
            method='GET',
            url='http://www.ya.ru/',
            data=data,
        )

        self.assertEqual(request.data, data)

    def test_not_quoted_unicode_data_dict(self):
        request = Request(
            method='GET',
            url='http://www.ya.ru/',
            data={'а': 'б'},
        )

        data = '%s=%s' % (self._quoted_unicode('а'), self._quoted_unicode('б'))
        self.assertEqual(request.data, data)

    def test_not_quoted_unicode_data_string(self):
        request = Request(
            method='GET',
            url='http://www.ya.ru/',
            data='а=б',
        )

        data = '%s=%s' % (self._quoted_unicode('а'), self._quoted_unicode('б'))
        self.assertEqual(request.data, data)

    def test_not_quoted_utf8_data_dict(self):
        request = Request(
            method='GET',
            url='http://www.ya.ru/',
            data={'а'.encode('utf-8'): 'б'.encode('utf-8')},
        )

        data = '%s=%s' % (self._quoted_unicode('а'), self._quoted_unicode('б'))
        self.assertEqual(request.data, data)

    def test_not_quoted_utf8_data_string(self):
        data = 'а=б'.encode('utf-8')
        request = Request(
            method='GET',
            url='http://www.ya.ru/',
            data=data,
        )

        data = '%s=%s' % (self._quoted_unicode('а'), self._quoted_unicode('б'))
        self.assertEqual(request.data, data)

    def test_empty_params(self):
        request = Request(method='GET', url='http://www.ya.ru/?x=', params={'y': ''})
        self.assertEqual(request.url, 'http://www.ya.ru/?x=&y=')

    def test_none_params(self):
        request = Request(method='GET', url='http://www.ya.ru/', params={'x': None})
        self.assertEqual(request.url, 'http://www.ya.ru/')

    def test_empty_data(self):
        request = Request(method='POST', url='http://www.ya.ru/', data={'x': ''})
        self.assertEqual(request.data, 'x=')

    def test_empty_encoded_data(self):
        request = Request(method='POST', url='http://www.ya.ru/', data='x=')
        self.assertEqual(request.data, 'x=')

    def test_none_data(self):
        request = Request(method='POST', url='http://www.ya.ru/', data={'x': None})
        self.assertIsNone(request.data)

    def test_str(self):
        request = Request(
            method='POST',
            url='http://www.ya.ru/?oauth_token=foo',
            params={'sessionid': 'bar', 'other_param': 'value'},
            data={'access_token': 'zar', 'other_param': 'value'},
            headers={'Authorization': 'Bearer token', 'User-Agent': 'curl'},
        )
        self.assertEqual(
            str(request),
            (
                'HTTP request to http://www.ya.ru/?sessionid=%2A%2A%2A%2A%2A&oauth_token=fo%2A&other_param=value, '
                'method=POST, data=access_token=za%2A&other_param=value, '
                'headers={\'Content-Type\': \'application/x-www-form-urlencoded\', '
                'u\'Authorization\': \'*****\', u\'User-Agent\': u\'curl\'}, timeout=None, retries=1'
            ),
        )


class _BaseUseragentTestCase(TestCase):
    def setUp(self):
        super(_BaseUseragentTestCase, self).setUp()
        self._fake_pool_manager = Mock(name='pool_manager')
        self._useragent = self._build_useragent()

    def _set_response(self, response):
        if not isinstance(response, list):
            response = [response]
        self._fake_pool_manager.urlopen.side_effect = response

    def _build_useragent(self, timeout=1, retries=1):
        return UserAgent(timeout=timeout, retries=retries, pool_manager=self._fake_pool_manager)

    def _make_request(self, useragent=None, method='GET', url=URL1, **kwargs):
        useragent = useragent or self._useragent
        return useragent.request(method=method, url=url, **kwargs)

    def _assert_requests_equal(self, requests):
        expected_calls = []
        for request in requests:
            expected_calls.append(
                MockCall(
                    method=request['method'],
                    url=request['url'],
                    headers=request.get('headers'),
                    body=request.get('data'),
                    timeout=request.get('timeout', 1),
                    pool_timeout=1,
                    retries=False,
                    redirect=False,
                ),
            )
        iterdiff(eq_)(self._fake_pool_manager.urlopen.mock_calls, expected_calls)

    def _build_request_signer(self, signatures):
        call_index = [0]

        def _get_signed_request(request):
            headers = dict(request.headers)

            signature = signatures[call_index[0]]
            headers['signature'] = signature
            call_index[0] += 1

            return Request.from_request(request, headers=headers)

        signer = Mock(name='request_signer')
        signer.get_signed_request.side_effect = _get_signed_request
        return signer

    def _get_unsigned_requests_that_request_signer_signed(self, signer):
        requests = []
        for call in signer.get_signed_request.mock_calls:
            _, args, kwargs = call
            requests.append(args[0])
        return requests


class TestUseragent(_BaseUseragentTestCase):
    def test_status_200(self):
        self._set_response(Response(status_code=200, content='hello', duration=0))

        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.content, 'hello')

    def test_socket_error(self):
        self._set_response(SocketError())

        with self.assertRaises(UserAgent.request_error_class):
            self._make_request()

    def test_invalid_utf_in_response(self):
        def parse(response):
            raise RuntimeError('Error while parsing response')

        self._set_response(Response(status_code=200, content='\xe9', duration=0))
        with self.assertRaises(RuntimeError):
            self._make_request(parser=parse)

    def test_retry(self):
        useragent = self._build_useragent(retries=2)
        self._set_response([
            SocketError(),
            Response(status_code=200, content='hello', duration=0),
        ])

        rv = self._make_request(useragent=useragent)

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.content, 'hello')

    def test_get_request(self):
        self._set_response(Response(status_code=200, content='', duration=0))
        useragent = self._build_useragent(timeout=0.5)

        useragent.request(
            method='GET',
            url='http://www.ya.ru/?hello=yello',
            headers={'arg1': 'val1'},
            fields={'arg2': 'val2'},
            params={'arg3': 'val3'},
            data={'arg4': 'val4'},
        )

        self._assert_requests_equal([
            dict(
                method='GET',
                url='http://www.ya.ru/?hello=yello&arg3=val3&arg2=val2',
                headers={
                    'User-Agent': 'yandex-social-useragent/0.1',
                    'arg1': 'val1',
                },
                data='arg4=val4',
                timeout=0.5,
            ),
        ])

    def test_post_request(self):
        self._set_response(Response(status_code=200, content='', duration=0))

        self._make_request(
            method='POST',
            url='http://www.ya.ru/',
            data={'arg1': 'val1'},
        )

        self._assert_requests_equal([
            dict(
                method='POST',
                url='http://www.ya.ru/',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'yandex-social-useragent/0.1',
                },
                data='arg1=val1',
            ),
        ])

    def test_redirect(self):
        useragent = self._build_useragent(retries=2)
        self._set_response([
            Response(status_code=302, headers={'Location': 'https://www.foo.bar/?hello=yello'}, content='', duration=0),
            Response(status_code=200, content='hello', duration=0),
        ])

        rv = self._make_request(
            useragent=useragent,
            method='GET',
            url='http://www.ya.ru/?foo=bar',
            headers={'white': 'black'},
        )

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.content, 'hello')

        self._assert_requests_equal([
            dict(
                method='GET',
                url='http://www.ya.ru/?foo=bar',
                headers={
                    'white': 'black',
                    'User-Agent': 'yandex-social-useragent/0.1',
                },
            ),
            dict(
                method='GET',
                url='https://www.foo.bar/?hello=yello',
                headers={
                    'white': 'black',
                    'User-Agent': 'yandex-social-useragent/0.1',
                },
            ),
        ])

    def test_too_much_redirects(self):
        self._set_response(
            Response(
                status_code=302,
                headers={'Location': 'https://www.foo.bar/'},
                content='',
                duration=0,
            ),
        )

        with self.assertRaises(UserAgent.request_error_class):
            self._make_request(method='GET', url='http://www.ya.ru')

    def test_sign_request(self):
        request_signer = self._build_request_signer(['foo'])
        self._set_response(Response(status_code=200, content='', duration=0))

        rv = self._make_request(request_signer=request_signer)

        self.assertEqual(rv.status_code, 200)

        self._assert_requests_equal([
            dict(
                method='GET',
                url=URL1,
                headers={
                    'User-Agent': 'yandex-social-useragent/0.1',
                    'signature': 'foo',
                },
            ),
        ])

    def test_resign_request_on_redirect(self):
        useragent = self._build_useragent(retries=2)
        request_signer = self._build_request_signer(['foo', 'bar'])
        self._set_response([
            Response(status_code=302, headers={'Location': 'https://www.foo.bar/?hello=yello'}, content='', duration=0),
            Response(status_code=200, content='', duration=0),
        ])

        rv = self._make_request(useragent=useragent, request_signer=request_signer)

        self.assertEqual(rv.status_code, 200)

        self._assert_requests_equal([
            dict(
                method='GET',
                url=URL1,
                headers={
                    'User-Agent': 'yandex-social-useragent/0.1',
                    'signature': 'foo',
                },
            ),
            dict(
                method='GET',
                url='https://www.foo.bar/?hello=yello',
                headers={
                    'User-Agent': 'yandex-social-useragent/0.1',
                    'signature': 'bar',
                },
            ),
        ])

        unsigned_requests = self._get_unsigned_requests_that_request_signer_signed(request_signer)
        eq_(
            unsigned_requests,
            [
                Request(
                    method='GET',
                    url=URL1,
                    headers={'User-Agent': 'yandex-social-useragent/0.1'},
                    timeout=1,
                    retries=2,
                ),
                Request(
                    method='GET',
                    url='https://www.foo.bar/?hello=yello',
                    headers={'User-Agent': 'yandex-social-useragent/0.1'},
                    timeout=1,
                    retries=2,
                ),
            ],
        )

    def test_post_redirect(self):
        useragent = self._build_useragent(retries=2)
        response = Response(status_code=302, headers={'Location': 'https://www.foo.bar/?hello=yello'}, content='', duration=0)
        self._set_response([response] * 2)

        with self.assertRaises(UserAgent.request_error_class):
            self._make_request(
                useragent=useragent,
                method='POST',
                headers={'white': 'black'},
                url='http://www.ya.ru/?foo=bar',
                data={'arg1': 'val1'},
            )

        expected = dict(
            method='POST',
            url='http://www.ya.ru/?foo=bar',
            headers={
                'white': 'black',
                'User-Agent': 'yandex-social-useragent/0.1',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data='arg1=val1',
        )
        self._assert_requests_equal([expected] * 2)

    def test_init(self):
        ua = self._build_useragent(timeout=5, retries=2)
        eq_(ua.timeout, 5)
        eq_(ua.retries, 2)

    def test_post_args_urlencoded(self):
        self._set_response(Response(status_code=200, content='', duration=0))

        self._make_request(
            method='POST',
            url=URL1,
            data={'foo': 'bar', 'kung': 'fu'},
        )

        self._assert_requests_equal([
            dict(
                method='POST',
                url=URL1,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'yandex-social-useragent/0.1',
                },
                data='foo=bar&kung=fu',
            ),
        ])


class TestZoraUseragent(_BaseUseragentTestCase):
    def setUp(self):
        super(TestZoraUseragent, self).setUp()
        self._fake_pool_manager.proxy_headers = dict()
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data())
        self._fake_tvm_credentials_manager.start()

    def tearDown(self):
        self._fake_tvm_credentials_manager.stop()
        super(TestZoraUseragent, self).tearDown()

    def _make_request(self, useragent=None, method='POST', url=URL1, **kwargs):
        useragent = useragent or self._useragent
        return useragent.request(method=method, url=url, **kwargs)

    def _build_useragent(self, timeout=1, retries=1):
        tvm_credentials_manager = TvmCredentialsManager()
        return ZoraUseragent(
            tvm_credentials_manager=tvm_credentials_manager,
            timeout=timeout,
            retries=retries,
            zora_connection_pool=self._fake_pool_manager,
            zora_tvm_client_alias=TVM_ALIAS1,
        )

    def _build_response(self, status_code, content, headers=None):
        return Response(
            status_code=status_code,
            content=content,
            duration=0,
            headers=headers,
        )

    def _build_zora_error_response(self, error_code, error_description=''):
        return Response(
            status_code=599,
            content='',
            duration=0,
            headers={
                'X-Yandex-GoZora-Error-Code': str(error_code),
                'X-Yandex-Gozora-Error-Description': error_description,
            },
        )

    def _build_headers(self, headers=None):
        headers = headers or dict()

        defaults = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'yandex-social-useragent/0.1',
            'X-Ya-Client-Id': 'socialism',
            'X-Yandex-Socialism-Salt': MockAny,
        }
        headers = dict(headers)
        for key in defaults:
            headers.setdefault(key, defaults[key])
        return headers

    def test_status_200(self):
        self._set_response(self._build_response(status_code=200, content='hello'))

        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.content, 'hello')

        self.assertEqual(self._fake_pool_manager.proxy_headers, {'X-Ya-Service-Ticket': TVM_TICKET1})

    def test_socket_error(self):
        self._set_response(SocketError())

        with self.assertRaises(UserAgent.request_error_class):
            self._make_request()

    def test_retry(self):
        useragent = self._build_useragent(retries=2)
        self._set_response([
            SocketError(),
            self._build_response(status_code=200, content='hello')
        ])

        rv = self._make_request(useragent=useragent)

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.content, 'hello')

    def test_get_request(self):
        with self.assertRaises(NotImplementedError) as assertion:
            self._make_request(method='GET')

        self.assertEqual(
            str(assertion.exception),
            'GET requests through Zora are forbidden',
        )

    def test_post_request(self):
        self._set_response(self._build_response(status_code=200, content=''))
        useragent = self._build_useragent(timeout=0.5)

        useragent.request(
            method='POST',
            url='http://www.ya.ru/',
            data={'arg1': 'val1'},
        )

        self._assert_requests_equal([
            dict(
                method='POST',
                url='http://www.ya.ru/',
                headers=self._build_headers(),
                data='arg1=val1',
                timeout=0.5,
            ),
        ])

    def test_https_request(self):
        self._set_response(self._build_response(status_code=200, content=''))

        self._make_request(url='https://www.ya.ru/')

        self._assert_requests_equal([
            dict(
                method='POST',
                url='https://www.ya.ru/',
                headers=self._build_headers(),
            ),
        ])

    def test_sign_request(self):
        request_signer = self._build_request_signer(['foo'])
        self._set_response(self._build_response(status_code=200, content=''))

        rv = self._make_request(request_signer=request_signer)

        self.assertEqual(rv.status_code, 200)

        self._assert_requests_equal([
            dict(
                method='POST',
                url=URL1,
                headers=self._build_headers({'signature': 'foo'}),
            ),
        ])

        unsigned_requests = self._get_unsigned_requests_that_request_signer_signed(request_signer)
        self.assertEqual(
            unsigned_requests,
            [
                Request(
                    method='POST',
                    url=URL1,
                    headers=self._build_headers(),
                    timeout=1,
                    retries=1,
                ),
            ],
        )

    def test_zora_error(self):
        self._set_response(self._build_zora_error_response(error_code=1000, error_description='ololo'))

        with self.assertRaises(UserAgent.request_error_class) as assertion:
            self._make_request()

        self.assertEqual(str(assertion.exception), 'Zora failed: 1000 ololo')

    def test_dns_failure(self):
        self._set_response(
            urllib3.exceptions.ProxyError(
                'Cannot connect to proxy.',
                SocketError('Tunnel connection failed: 502 resolving failed'),
            ),
        )

        with self.assertRaises(UserAgent.request_error_class) as assertion:
            self._make_request()

        self.assertEqual(str(assertion.exception), 'Zora failed: 10001 Dns failure')

    def test_zora_not_numeric_error(self):
        self._set_response(self._build_zora_error_response(error_code='!', error_description='ololo'))

        with self.assertRaises(UserAgent.request_error_class) as assertion:
            self._make_request()

        self.assertEqual(str(assertion.exception), 'Zora failed: 10000 Unexpected Zora response')

    def test_post_redirect(self):
        useragent = self._build_useragent(retries=2)
        response = self._build_response(
            status_code=302,
            headers={'Location': 'https://www.foo.bar/?hello=yello'},
            content='',
        )
        self._set_response([response] * 2)

        with self.assertRaises(UserAgent.request_error_class) as assertion:
            self._make_request(
                useragent=useragent,
                method='POST',
                headers={'white': 'black'},
                url='http://www.ya.ru/?foo=bar',
                data={'arg1': 'val1'},
            )

        self.assertEqual(str(assertion.exception), 'Redirect to https://www.foo.bar/?hello=yello')

        expected = dict(
            method='POST',
            url='http://www.ya.ru/?foo=bar',
            headers=self._build_headers(
                {
                    'white': 'black',
                    'User-Agent': 'yandex-social-useragent/0.1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            ),
            data='arg1=val1',
        )
        self._assert_requests_equal([expected] * 2)

    def test_init(self):
        ua = self._build_useragent(timeout=5, retries=2)
        eq_(ua.timeout, 5)
        eq_(ua.retries, 2)

    def test_post_args_urlencoded(self):
        self._set_response(self._build_response(status_code=200, content=''))
        useragent = self._build_useragent(timeout=0.5)

        useragent.request(
            method='POST',
            url=URL1,
            data={'foo': 'bar', 'kung': 'fu'},
        )

        self._assert_requests_equal([
            dict(
                method='POST',
                url=URL1,
                headers=self._build_headers(),
                data='foo=bar&kung=fu',
                timeout=0.5,
            ),
        ])


class TestFixIssue1758ConnectionPoolMixinApplied(TestCase):
    def do_request(self, schema, manager):
        url = '%s://tramonta.na/' % schema
        try:
            manager.request('GET', url, retries=False)
        except urllib3.exceptions.HTTPError:
            pass

    def build_proxy_manager(self):
        return ProxyManager(proxy_url=URL1)

    def test_http_get_conn(self):
        patches = [
            patch('passport.backend.social.common._urllib3._HTTPConnectionPool._make_request', side_effect=SocketError()),
            patch('passport.backend.social.common._urllib3._FixIssue1758ConnectionPoolMixin._get_conn'),
        ]
        with contextlib.nested(*patches):
            self.do_request('http', PoolManager())
            _FixIssue1758ConnectionPoolMixin._get_conn.assert_called_once()

        with contextlib.nested(*patches):
            self.do_request('http', self.build_proxy_manager())
            _FixIssue1758ConnectionPoolMixin._get_conn.assert_called_once()

    def test_http_urlopen(self):
        with patch('passport.backend.social.common._urllib3._FixIssue1758ConnectionPoolMixin.urlopen'):
            self.do_request('http', PoolManager())
            _FixIssue1758ConnectionPoolMixin.urlopen.assert_called_once()

        with patch('passport.backend.social.common._urllib3._FixIssue1758ConnectionPoolMixin.urlopen'):
            self.do_request('http', self.build_proxy_manager())
            _FixIssue1758ConnectionPoolMixin.urlopen.assert_called_once()

    def test_https_get_conn(self):
        patches = [
            patch('passport.backend.social.common._urllib3._HTTPSConnectionPool._make_request', side_effect=SocketError()),
            patch('passport.backend.social.common._urllib3._FixIssue1758ConnectionPoolMixin._get_conn'),
        ]
        with contextlib.nested(*patches):
            self.do_request('https', PoolManager())
            _FixIssue1758ConnectionPoolMixin._get_conn.assert_called_once()

        with contextlib.nested(*patches):
            self.do_request('https', self.build_proxy_manager())
            _FixIssue1758ConnectionPoolMixin._get_conn.assert_called_once()

    def test_https_urlopen(self):
        with patch('passport.backend.social.common._urllib3._FixIssue1758ConnectionPoolMixin.urlopen'):
            self.do_request('https', PoolManager())
            _FixIssue1758ConnectionPoolMixin.urlopen.assert_called_once()

        with patch('passport.backend.social.common._urllib3._FixIssue1758ConnectionPoolMixin.urlopen'):
            self.do_request('https', self.build_proxy_manager())
            _FixIssue1758ConnectionPoolMixin.urlopen.assert_called_once()


class TestUserAgentWithMocks(TestCase):
    def create_ua_mock(self):
        ua = UserAgent(retries=1, timeout=2)
        ua.http = Mock()
        ua.http.urlopen.return_value = FakeResponse('', status_code=200)
        return ua

    def setUp(self):
        super(TestUserAgentWithMocks, self).setUp()
        self.ua = self.create_ua_mock()

        self.ua_logger = Mock()
        self.ua_logger.debug = Mock()

    def test_default_disabled_allow_redirects(self):
        self.ua.get(URL1)
        eq_(self.ua.http.urlopen.call_args[1]['redirect'], False)

    def test_request_error(self):
        for error in [urllib3.exceptions.TimeoutError]:
            self.ua.http.urlopen.side_effect = error

            with self.assertRaises(UserAgent.request_error_class):
                self.ua.get('http://ya.ru')

            eq_(self.ua.http.urlopen.call_count, 1)
            self.ua.http.urlopen.reset_mock()

    def test_request_retries(self):
        self.ua.http.urlopen.side_effect = urllib3.exceptions.TimeoutError
        with self.assertRaises(UserAgent.request_error_class):
            self.ua.get('http://ya.ru', retries=10)
        eq_(self.ua.http.urlopen.call_count, 10)
        self.ua.http.urlopen.reset_mock()

    def test_request(self):
        self.ua.get('http://ya.ru')
        eq_(self.ua.http.urlopen.call_count, 1)

    def test_request_methods(self):
        mock_request = Mock()
        with patch('passport.backend.social.common.useragent.UserAgent.request', mock_request):
            ua = UserAgent()
            for method, name in [(ua.get, 'get'),
                                 (ua.post, 'post'),
                                 (ua.head, 'head'),
                                 (ua.put, 'put'),
                                 (ua.delete, 'delete')]:
                method(URL1)
                eq_(mock_request.call_args[0], (name, URL1))

    def test_global_pool(self):
        pool_manager = Mock(name='pool_manager')
        ua = UserAgent(pool_manager=pool_manager)
        self.assertIs(ua.http, pool_manager)

    def test_local_pool(self):
        pool_manager = Mock(name='pool_manager')
        with patch('passport.backend.social.common.useragent.build_http_pool_manager', return_value=pool_manager):
            ua = UserAgent()
            self.assertIs(ua.http, pool_manager)
