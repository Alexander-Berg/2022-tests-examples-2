# -*- coding: utf-8 -*-
import errno
import socket
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.logging_utils.loggers import StatboxLogger
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.name import (
    DNSError,
    DNSNoNameError,
)
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)
import requests
import six
from six.moves import (
    http_client as httplib,
    urllib_parse as urlparse,
)
from urllib3 import exceptions as urllib3_exceptions


TEST_UNICODE = u'e\ufffd\x01+\ufffdl\x12E\ufffd\x11h\ufffdVjcllaD'


@with_settings
class TestUrlParsing(unittest.TestCase):
    def setUp(self):
        self.ua = UserAgent()
        self.kwargs = {}

    def test_url_parse(self):
        url = self.ua._process_url('http://a:b@ya.ru', self.kwargs)

        eq_(url.hostname, b'ya.ru')
        eq_(self.kwargs['headers'][b'Host'], b'ya.ru')

    def test_url_with_port_parse(self):
        url = self.ua._process_url('http://a:b@ya.ru:8080', self.kwargs)

        eq_(url.hostname, b'ya.ru')
        eq_(self.kwargs['headers'][b'Host'], b'ya.ru:8080')

    def test_doesnt_overwrite_explicit_host(self):
        self.kwargs['headers'] = {'Host': 'yandex.ru'}
        url = self.ua._process_url('http://a:b@ya.ru:8080', self.kwargs)

        eq_(url.hostname, b'ya.ru')
        eq_(self.kwargs['headers'][b'Host'], b'yandex.ru')

    def test_ip_parse(self):
        url = self.ua._process_url('http://a:b@127.0.0.1/', self.kwargs)

        eq_(url.hostname, b'127.0.0.1')
        eq_(self.kwargs['headers'][b'Host'], b'127.0.0.1')

    def test_url_ip_with_port_parse(self):
        url = self.ua._process_url('http://a:b@127.0.0.1:8080/', self.kwargs)

        eq_(url.hostname, b'127.0.0.1')
        eq_(self.kwargs['headers'][b'Host'], b'127.0.0.1:8080')

    def test_encode_headers(self):
        self.kwargs['headers'] = {
            'Ya-Client-User-Agent': TEST_UNICODE,
            'Host': 'ya.ru',
            TEST_UNICODE: 'test',
        }
        self.ua._process_url('http://ya.ru', self.kwargs)

        expected = {
            b'Ya-Client-User-Agent': TEST_UNICODE.encode('utf-8'),
            b'Host': b'ya.ru',
            TEST_UNICODE.encode('utf-8'): b'test',
        }
        assert self.kwargs['headers'] == expected

    def test_encode_cookies(self):
        self.kwargs['cookies'] = {
            '__utmz': TEST_UNICODE,
            TEST_UNICODE: 'такие дела',
        }
        self.ua._process_url('http://ya.ru', self.kwargs)

        expected_value = 'такие дела'
        if six.PY3:
            expected_value = expected_value.encode('utf-8')

        expected = {
            b'__utmz': TEST_UNICODE.encode('utf-8'),
            TEST_UNICODE.encode('utf-8'): expected_value,
        }
        assert self.kwargs['cookies'] == expected


@with_settings
class TestUrlGeneration(unittest.TestCase):
    def setUp(self):
        self.ua = UserAgent()

    def test_host(self):
        split_url = urlparse.urlsplit(b'http://ya.ru/')
        url = self.ua._generate_url(split_url, '127.0.0.1')

        eq_(url, b'http://127.0.0.1/')

        split_url = urlparse.urlsplit(b'http://ya.ru')
        url = self.ua._generate_url(split_url, '127.0.0.1')

        eq_(url, b'http://127.0.0.1')

    def test_ipv6(self):
        split_url = urlparse.urlsplit(b'http://www.yandex.com/')
        url = self.ua._generate_url(split_url, '2a02:6b8::11:11')

        eq_(url, b'http://[2a02:6b8::11:11]/')

        split_url = urlparse.urlsplit(b'http://www.yandex.com')
        url = self.ua._generate_url(split_url, '2a02:6b8::11:11')

        eq_(url, b'http://[2a02:6b8::11:11]')

    def test_host_port(self):
        split_url = urlparse.urlsplit(b'http://ya.ru:8080/')
        url = self.ua._generate_url(split_url, '127.0.0.1')

        eq_(url, b'http://127.0.0.1:8080/')

    def test_username_host_port(self):
        split_url = urlparse.urlsplit(b'http://user@ya.ru:8080/')
        url = self.ua._generate_url(split_url, '127.0.0.1')

        eq_(url, b'http://user@127.0.0.1:8080/')

    def test_username_password_host_port(self):
        split_url = urlparse.urlsplit(b'http://user:pass@ya.ru:8080/')
        url = self.ua._generate_url(split_url, '127.0.0.1')

        eq_(url, b'http://user:pass@127.0.0.1:8080/')


class BaseUserAgentWithMocksTestCase(unittest.TestCase):
    def create_ua_mock(self):
        ua = UserAgent()
        ua.dns = mock.Mock()
        ua.session = mock.Mock()
        return ua

    def setUp(self):
        self.ua = self.create_ua_mock()
        self.ua_logger = mock.Mock()
        self.ua_logger.debug = mock.Mock()

        self.statbox_patch = mock.patch(
            'passport.backend.core.logging_utils.loggers.statbox.StatboxLogger.get_default_logger',
            mock.Mock(return_value=self.ua_logger),
        )
        self.statbox_patch.start()
        self.statbox = StatboxLogger(action='test')

    def tearDown(self):
        self.statbox_patch.stop()
        del self.statbox_patch
        del self.statbox
        del self.ua
        del self.ua_logger


@with_settings
class TestUserAgentWithMocks(BaseUserAgentWithMocksTestCase):
    def test_default_disabled_allow_redirects(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.get('http://ya.ru')
        eq_(self.ua.session.request.call_args[1]['allow_redirects'], False)

    def test_dns_error(self):
        self.ua.dns.query.side_effect = DNSError

        with assert_raises(RequestError) as context:
            self.ua.get('http://ya.ru')

        eq_(str(context.exception), 'DNS returned no IPs for ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 0)

    def test_dns_returned_nothing_error(self):
        self.ua.dns.query.return_value = []

        with assert_raises(RequestError) as context:
            self.ua.get('http://ya.ru')

        eq_(str(context.exception), 'DNS returned no IPs for ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 0)

    def test_dns_retries(self):
        self.ua.dns.query.side_effect = DNSError

        with assert_raises(RequestError):
            self.ua.get('http://ya.ru', retries=20)

        eq_(self.ua.dns.query.call_count, 20)
        eq_(self.ua.session.request.call_count, 0)

    def test_timeout_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.Timeout

        log_mock = mock.Mock()
        with assert_raises(RequestError):
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_read_timeout_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.ReadTimeout

        log_mock = mock.Mock()
        with assert_raises(RequestError):
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_connect_timeout_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.ConnectTimeout

        log_mock = mock.Mock()
        with assert_raises(RequestError):
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_request_empty_status_line_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.ConnectionError(
            urllib3_exceptions.ProtocolError(
                'Connection aborted',
                httplib.BadStatusLine(''),
            ),
        )

        log_mock = mock.Mock()
        with assert_raises(RequestError) as context:
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        expected_message = 'Socket was closed while requesting http://127.0.0.1'
        eq_(str(context.exception), expected_message)
        eq_(log_mock.debug.call_args, mock.call(expected_message))

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_request_permission_denied_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']

        socket_error = socket.error('Permission denied')
        socket_error.errno = errno.EACCES
        self.ua.session.request.side_effect = requests.ConnectionError(
            urllib3_exceptions.ProtocolError(
                'Connection aborted',
                socket_error,
            ),
        )

        log_mock = mock.Mock()
        with assert_raises(RequestError) as context:
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        expected_message = 'Permission denied while requesting http://127.0.0.1'
        eq_(str(context.exception), expected_message)
        eq_(log_mock.error.call_args[0], (expected_message, ))

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_request_connection_reset_by_peer_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        socket_error = socket.error('Connection reset by peer')
        socket_error.errno = errno.ECONNRESET
        self.ua.session.request.side_effect = socket_error

        log_mock = mock.Mock()
        with assert_raises(RequestError) as context:
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        expected_message = 'Socket was closed while reading response from http://127.0.0.1'
        eq_(str(context.exception), expected_message)
        eq_(log_mock.debug.call_args, mock.call(expected_message))

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_request_chunked_encoding_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.exceptions.ChunkedEncodingError

        log_mock = mock.Mock()
        with assert_raises(RequestError) as context:
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        expected_message = 'Connection reset by peer while reading response from http://127.0.0.1'
        eq_(str(context.exception), expected_message)
        eq_(log_mock.warning.call_args[0], (expected_message, ))

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_request_ssl_error(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.exceptions.SSLError

        log_mock = mock.Mock()
        with assert_raises(RequestError) as context:
            with mock.patch('passport.backend.core.useragent.sync.log', log_mock):
                self.ua.get('http://ya.ru')

        expected_message = 'SSL problem while requesting ya.ru'
        eq_(str(context.exception), expected_message)
        eq_(log_mock.error.call_args[0], (expected_message, ))

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        self.ua.dns.query.reset_mock()
        self.ua.session.request.reset_mock()

    def test_request_error_with_tskv(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.Timeout

        with assert_raises(RequestError):
            self.ua.get('http://ya.ru', statbox_logger=self.statbox)

        eq_(self.ua_logger.debug.call_count, 1)
        log_entry = self.ua_logger.debug.call_args[0][0]
        ok_('http_code=0' in log_entry)
        ok_('network_error=1' in log_entry)
        ok_('action=test' in log_entry)
        # Проверяем, что записалась длительность вызова
        duration_record = [token for token in log_entry.split('\t') if token.startswith('duration')][0]
        ok_(float(duration_record.split('=')[1]) < 1)

    def test_request_retries(self):
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.session.request.side_effect = requests.Timeout

        with assert_raises(RequestError):
            self.ua.get('http://ya.ru', retries=10)

        eq_(self.ua.dns.query.call_count, 10)
        eq_(self.ua.session.request.call_count, 10)

    def test_dns_several_ips(self):
        self.ua.dns.query.return_value = ['127.0.0.1', '127.0.0.2', '127.0.0.3']
        self.ua.session.request.side_effect = requests.Timeout

        with assert_raises(RequestError):
            self.ua.get('http://ya.ru', retries=10)

        eq_(self.ua.dns.query.call_count, 10)
        eq_(self.ua.session.request.call_count, 30)

    def test_request(self):
        self.ua.dns.query.return_value = ['127.0.0.1']

        self.ua.get('http://ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        eq_(self.ua_logger.debug.call_count, 0)

    def test_request_with_tskv(self):
        ua = self.create_ua_mock()
        ua.dns.query.return_value = ['127.0.0.1']
        ua.session.request.return_value = mock.Mock()
        ua.session.request.return_value.status_code = 200

        ua.get('http://ya.ru', statbox_logger=self.statbox)
        eq_(self.ua_logger.debug.call_count, 1)
        log_entry = self.ua_logger.debug.call_args[0][0]
        ok_('http_code=200' in log_entry)
        ok_('network_error=0' in log_entry)
        ok_('action=test' in log_entry)
        # Проверяем, что записалась длительность вызова
        duration_record = [token for token in log_entry.split('\t') if token.startswith('duration')][0]
        ok_(float(duration_record.split('=')[1]) < 1)

    def test_request_gets_host_headers(self):
        self.ua.dns.query.return_value = ['127.0.0.1']

        self.ua.get('http://ya.ru')

        eq_(self.ua.dns.query.call_count, 1)
        eq_(self.ua.session.request.call_count, 1)
        eq_(self.ua.session.request.call_args[1]['headers'], {b'Host': b'ya.ru'})

    def test_request_methods(self):
        url = 'http://ya.ru'
        mock_request = mock.Mock()
        with mock.patch('passport.backend.core.useragent.sync.UserAgent.request', mock_request):
            ua = UserAgent()
            for method, name in [(ua.get, 'get'),
                                 (ua.post, 'post'),
                                 (ua.head, 'head'),
                                 (ua.put, 'put'),
                                 (ua.delete, 'delete')]:
                method(url)
                eq_(mock_request.call_args[0], (name, url))

    def test_request_with_files(self):
        self.ua.dns.query.return_value = ['127.0.0.1']

        fileMock = mock.Mock()
        self.ua.post('http://ya.ru', files={'name': fileMock})
        self.ua.post('http://ya.ru', files={'name': ('filename.txt', fileMock)})
        eq_(fileMock.seek.call_count, 2)
        eq_(fileMock.seek.call_args_list[0][0][0], 0)
        eq_(fileMock.seek.call_args_list[1][0][0], 0)


@with_settings(USE_GLOBAL_DNS_CACHE=False)
class TestUserAgent(unittest.TestCase):
    def setUp(self):
        self.ua = UserAgent()

    def test_init(self):
        ua = UserAgent(max_pool_size=5)
        eq_(ua.max_pool_size, 5)

    def test_negative_timeout_is_ok(self):
        with assert_raises(RequestError):
            self.ua.get('http://213.180.193.3', timeout=0)

        with assert_raises(RequestError):
            self.ua.get('http://213.180.193.3', timeout=-1)

    @raises(requests.RequestException)
    def test_request_exception(self):
        self.ua.requests_adapter.send = mock.Mock(side_effect=requests.RequestException)
        self.ua.get('http://213.180.193.3/', timeout=0.0005)

    @raises(RequestError)
    def test_timeout(self):
        self.ua.get('http://213.180.193.3/', timeout=0.0005)

    @raises(RequestError)
    def test_dns_noname(self):
        mock_dnsresover_query = mock.Mock(side_effect=DNSNoNameError)
        with mock.patch('passport.backend.core.useragent.name.DNSResolver.query', mock_dnsresover_query):
            self.ua.get('http://ya.ru', timeout=0.1)

    def test_dns_retries(self):
        mock_dnsresover_query = mock.Mock(side_effect=DNSError)
        with mock.patch('passport.backend.core.useragent.name.DNSResolver.query', mock_dnsresover_query):
            with assert_raises(RequestError):
                self.ua.get('http://ya.ru/', timeout=0.1, retries=5)

    def test_request_with_reconnect(self):
        with assert_raises(RequestError):
            self.ua.get('http://213.180.193.3', timeout=0.0005)

        pool = self.ua.requests_adapter.poolmanager.pools

        old_pool = [(hash(x), id(pool[x])) for x in pool.keys()]
        self.assertEqual(len(old_pool), 1)

        with self.assertRaises(RequestError):
            self.ua.get('http://213.180.193.3', timeout=0.0005)

        mid_pool = [(hash(x), id(pool[x])) for x in pool.keys()]
        self.assertEqual(len(mid_pool), 1)
        self.assertListEqual(old_pool, mid_pool)

        with self.assertRaises(RequestError):
            self.ua.get('http://213.180.193.3', reconnect=True, timeout=0.0005)

        new_pool = [(hash(x), id(pool[x])) for x in pool.keys()]
        self.assertEqual(len(new_pool), 1)
        self.assertEqual(old_pool[0][0], new_pool[0][0])
        self.assertNotEqual(old_pool[0][1], new_pool[0][1])


@with_settings
class TestUserAgentGraphiteLogger(BaseUserAgentWithMocksTestCase):
    def setUp(self):
        super(TestUserAgentGraphiteLogger, self).setUp()
        self.graphite_logger_mock = mock.Mock()
        self.ua.dns.query.return_value = ['127.0.0.1']

    def tearDown(self):
        del self.graphite_logger_mock
        super(TestUserAgentGraphiteLogger, self).tearDown()

    def test_ua_reports_success_request(self):
        self.ua.session.request.return_value = mock.Mock(status_code=200)
        self.ua.get('http://ya.ru', graphite_logger=self.graphite_logger_mock)

        self.graphite_logger_mock.log.assert_called_with(
            http_code='200',
            duration=mock.ANY,
            response='success',
            network_error=False,
            srv_hostname='ya.ru',
            srv_ipaddress='127.0.0.1',
        )

    def test_ua_reports_failed_request(self):
        self.ua.session.request.side_effect = requests.ConnectionError
        with assert_raises(RequestError):
            self.ua.get('http://ya.ru', graphite_logger=self.graphite_logger_mock)

        self.graphite_logger_mock.log.assert_called_with(
            http_code='0',
            duration=mock.ANY,
            response='failed',
            network_error=True,
            srv_hostname='ya.ru',
            srv_ipaddress='127.0.0.1',
        )

    def test_ua_reports_timeout_request(self):
        self.ua.session.request.side_effect = requests.Timeout
        with assert_raises(RequestError):
            self.ua.get('http://ya.ru', graphite_logger=self.graphite_logger_mock)

        self.graphite_logger_mock.log.assert_called_with(
            http_code='0',
            duration=mock.ANY,
            response='timeout',
            network_error=True,
            srv_hostname='ya.ru',
            srv_ipaddress='127.0.0.1',
        )


@with_settings
class TestUserAgentMaxRedirects(unittest.TestCase):
    def setUp(self):
        self.ua = UserAgent()
        self.ua.dns = mock.Mock()
        self.ua.dns.query.return_value = ['127.0.0.1']
        self.ua.requests_adapter.send = mock.Mock(
            side_effect=[
                mock.Mock(
                    url='http://some.url/{}'.format(i),
                    status_code=301,
                    headers=dict(location='http://some.url/{}'.format(i+1)),
                    history=None,
                    raw='',
                    is_redirect=True,
                ) for i in range(10)
            ] + [
                mock.Mock(
                    url='http://some.url/final',
                    status_code=200,
                    headers=dict(),
                    history=None,
                    raw='',
                    is_redirect=False,
                )
            ]
        )

    def tearDown(self):
        del self.ua

    def test_ok(self):
        self.ua.get('http://some.url/0', allow_redirects=True)
        eq_(self.ua.requests_adapter.send.call_count, 11)

    def test_ok_w_max_redirects(self):
        self.ua.get('http://some.url/0', allow_redirects=True, max_redirects=15)
        eq_(self.ua.requests_adapter.send.call_count, 11)

    def test_error_w_max_redirects(self):
        with assert_raises(requests.TooManyRedirects):
            self.ua.get('http://some.url/0', allow_redirects=True, max_redirects=5)
        eq_(self.ua.requests_adapter.send.call_count, 6)
