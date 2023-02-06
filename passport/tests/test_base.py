# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.base.base import (
    BaseBuilder,
    RequestInfo,
)
from passport.backend.core.test.test_utils import (
    assert_call_has_kwargs,
    with_settings,
)
from passport.backend.core.useragent.sync import (
    RequestError,
    UserAgent,
)
from passport.backend.utils.common import merge_dicts
from six import StringIO
from six.moves.urllib.parse import urlencode


TEST_BASE_URL = 'http://base.url/'
TEST_TIMEOUT = 10
TEST_RETRIES = 3

TEST_METHOD = 'POST'
TEST_URL = 'http://someurl.com/'
TEST_URL_SUFFIX = 'urlsuffix/'
TEST_URL_PARAMS = {'some': 'params'}
TEST_DATA = {'some': 'data'}
TEST_HEADERS = {'Any': 'Header'}
TEST_COOKIES = {'some': 'cookie'}
TEST_FILES = {'file': StringIO('File content.')}
TEST_CA_CERT = 'ca-cert-path'
DEFAULT_CA_CERT = 'default-ca-cert-path'
TEST_SERVICE_TICKET = 'service-ticket'

TEST_RAW_RESPONSE = 'Raw response'
TEST_PARSED_RESPONSE = 'Parsed response'
TEST_PROCESSED_RESPONSE = 'Processed response'


class FakeBaseError(Exception):
    pass


class FakeTemporaryError(Exception):
    pass


@with_settings(SSL_CA_CERT=DEFAULT_CA_CERT)
class BaseBuilderTest(TestCase):
    def setUp(self):
        self.useragent = UserAgent()
        self.response = mock.Mock()
        self.logger = mock.Mock()
        self.useragent.request = mock.Mock(return_value=self.response)
        self.builder = BaseBuilder(
            TEST_URL,
            useragent=self.useragent,
            timeout=TEST_TIMEOUT,
            retries=TEST_RETRIES,
            logger=self.logger,
        )

        self.builder.base_error_class = FakeBaseError
        self.builder.temporary_error_class = FakeTemporaryError

        TEST_FILES['file'].seek(0)

    def tearDown(self):
        del self.useragent
        del self.response
        del self.logger
        del self.builder

    def test_request_ok(self):
        self.useragent.request.return_value = TEST_RAW_RESPONSE

        response = self.builder._request(
            TEST_METHOD,
            TEST_URL,
            data=TEST_DATA,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        request_args, request_kwargs = self.useragent.request.call_args_list[0]

        method, url = request_args

        files = request_kwargs.get('files')
        headers = request_kwargs.get('headers')
        cookies = request_kwargs.get('cookies')
        data = request_kwargs.get('data')

        eq_(method, TEST_METHOD)
        eq_(url, TEST_URL)
        eq_(files, TEST_FILES)
        eq_(headers, TEST_HEADERS)
        eq_(cookies, TEST_COOKIES)
        eq_(data, TEST_DATA)

        eq_(response, TEST_RAW_RESPONSE)

    def test_request_with_retries_simple_ok(self):
        http_error_handler = mock.Mock()
        error_detector = mock.Mock()
        parser = mock.Mock(return_value=TEST_PARSED_RESPONSE)

        self.useragent.request.return_value = TEST_RAW_RESPONSE

        response = self.builder._request_with_retries_simple(
            error_detector,
            parser,
            http_error_handler,
            method=TEST_METHOD,
            url_suffix=TEST_URL_SUFFIX,
            params=TEST_URL_PARAMS,
            data=TEST_DATA,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        http_error_handler.assert_called_once_with(TEST_RAW_RESPONSE)
        parser.assert_called_once_with(TEST_RAW_RESPONSE)
        error_detector.assert_called_once_with(TEST_PARSED_RESPONSE, TEST_RAW_RESPONSE)

        request_args, request_kwargs = self.useragent.request.call_args_list[0]
        method, url = request_args
        files = request_kwargs.get('files')
        headers = request_kwargs.get('headers')
        cookies = request_kwargs.get('cookies')
        data = request_kwargs.get('data')

        eq_(method, TEST_METHOD)
        eq_(url, TEST_URL + TEST_URL_SUFFIX + '?' + urlencode(TEST_URL_PARAMS))
        eq_(files, TEST_FILES)
        eq_(headers, TEST_HEADERS)
        eq_(cookies, TEST_COOKIES)
        eq_(data, TEST_DATA)
        eq_(response, TEST_PARSED_RESPONSE)

    def test_request_with_retries_ok(self):
        http_error_handler = mock.Mock()
        error_detector = mock.Mock()
        parser = mock.Mock(return_value=TEST_PARSED_RESPONSE)
        response_processor = mock.Mock(return_value=TEST_PROCESSED_RESPONSE)

        self.useragent.request.return_value = TEST_RAW_RESPONSE

        response = self.builder._request_with_retries(
            TEST_METHOD,
            RequestInfo(TEST_URL, TEST_DATA, None),
            parser,
            error_detector=error_detector,
            http_error_handler=http_error_handler,
            response_processor=response_processor,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        http_error_handler.assert_called_once_with(TEST_RAW_RESPONSE)
        parser.assert_called_once_with(TEST_RAW_RESPONSE)
        error_detector.assert_called_once_with(TEST_PARSED_RESPONSE, TEST_RAW_RESPONSE)
        response_processor.assert_called_once_with(TEST_PARSED_RESPONSE)

        eq_(response, TEST_PROCESSED_RESPONSE)

    def test_request_with_n_minus_one_request_errors_ok(self):
        """ Проверяет, что при TEST_RETRIES - 1 ошибок RequestError получаем нормальный ответ"""
        parser = mock.Mock(return_value=TEST_PARSED_RESPONSE)

        self.useragent.request.side_effect = [
            RequestError,
            RequestError,
            TEST_RAW_RESPONSE,
        ]

        response = self.builder._request_with_retries(
            TEST_METHOD,
            RequestInfo(TEST_URL, TEST_DATA, None),
            parser,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        eq_(response, TEST_PARSED_RESPONSE)

    def test_request_with_n_request_errors_raises(self):
        """ Проверяет, что при TEST_RETRIES ошибок RequestError получаем temporary_error"""
        parser = mock.Mock(return_value=TEST_PARSED_RESPONSE)

        self.useragent.request.side_effect = [
            RequestError('foo'),
            RequestError('bar'),
            RequestError('zar'),
            TEST_RAW_RESPONSE,
        ]

        with assert_raises(FakeTemporaryError) as context:
            self.builder._request_with_retries(
                TEST_METHOD,
                RequestInfo(TEST_URL, TEST_DATA, None),
                parser,
                files=TEST_FILES,
                headers=TEST_HEADERS,
                cookies=TEST_COOKIES,
            )

        eq_(str(context.exception), 'zar')

    def test_ok_with_tvm(self):
        tvm_mock = mock.Mock()
        tvm_mock.get_ticket_by_alias.return_value = TEST_SERVICE_TICKET
        builder = BaseBuilder(
            TEST_URL,
            useragent=self.useragent,
            timeout=TEST_TIMEOUT,
            retries=TEST_RETRIES,
            logger=self.logger,
            tvm_dst_alias='builder',
            tvm_credentials_manager=tvm_mock,
        )

        builder._request_with_retries_simple(
            error_detector=None,
            parser=mock.Mock(return_value=TEST_PARSED_RESPONSE),
            http_error_handler=None,
            method=TEST_METHOD,
            url_suffix=TEST_URL_SUFFIX,
            params=TEST_URL_PARAMS,
            data=TEST_DATA,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )
        request_args, request_kwargs = self.useragent.request.call_args_list[0]
        headers = request_kwargs.get('headers')
        eq_(headers, merge_dicts({'X-Ya-Service-Ticket': TEST_SERVICE_TICKET}, TEST_HEADERS))

    @parameterized.expand([
        ('cert', 'key'),
        ('', None),
        (None, ''),
        ('', ''),
    ])
    def test_client_side_cert_and_key(self, cert, key):
        builder = BaseBuilder(
            TEST_URL,
            useragent=self.useragent,
            timeout=TEST_TIMEOUT,
            logger=self.logger,
            retries=TEST_RETRIES,
            client_side_cert=cert,
            client_side_key=key,
        )

        builder._request(
            TEST_METHOD,
            TEST_URL,
            data=TEST_DATA,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        if cert or key:
            assert_call_has_kwargs(self.useragent.request, cert=(cert, key))
        else:
            ok_('cert' not in self.useragent.request.call_args[1])

    @parameterized.expand([
        ('cert', None),
        (None, 'key'),
        ('cert', ''),
        ('', 'key'),
    ])
    @raises(ValueError)
    def test_client_side_only_cert_or_key(self, cert, key):
        BaseBuilder(
            TEST_URL,
            useragent=self.useragent,
            timeout=TEST_TIMEOUT,
            logger=self.logger,
            retries=TEST_RETRIES,
            client_side_cert=cert,
            client_side_key=key,
        )

    def test_ca_cert(self):
        builder = BaseBuilder(
            TEST_URL,
            useragent=self.useragent,
            timeout=TEST_TIMEOUT,
            logger=self.logger,
            retries=TEST_RETRIES,
            ca_cert=TEST_CA_CERT,
        )

        builder._request(
            TEST_METHOD,
            TEST_URL,
            data=TEST_DATA,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        assert_call_has_kwargs(self.useragent.request, verify=TEST_CA_CERT)

    def test_no_initial_ca_cert_(self):
        self.builder._request(
            TEST_METHOD,
            TEST_URL,
            data=TEST_DATA,
            files=TEST_FILES,
            headers=TEST_HEADERS,
            cookies=TEST_COOKIES,
        )

        assert_call_has_kwargs(self.useragent.request, verify=DEFAULT_CA_CERT)


class TestRequestInfo(TestCase):
    def test_query_has_none_value(self):
        rq_info = RequestInfo(
            'http://hello/',
            {'a': None, 'b': 'bar'},
            None,
        )
        eq_(rq_info.url, 'http://hello/?b=bar')

        rq_info = RequestInfo(
            'http://hello/',
            [('a', None), ('b', 'bar')],
            None,
        )
        eq_(rq_info.url, 'http://hello/?b=bar')
