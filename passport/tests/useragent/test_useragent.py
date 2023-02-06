# -*- coding: utf-8 -*-

from mock import (
    Mock,
    patch,
)
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.common.exception import ProviderCommunicationProxylibError
from passport.backend.social.common.test.fake_useragent import FakeUseragent
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.test.types import FakeResponse
from passport.backend.social.common.useragent import (
    build_http_pool_manager,
    RequestError,
)
from passport.backend.social.proxylib.useragent import execute_request


class TestMisc(TestCase):
    def setUp(self):
        super(TestMisc, self).setUp()
        self._fake_useragent = FakeUseragent().start()
        LazyLoader.register('http_pool_manager', build_http_pool_manager)

    def tearDown(self):
        self._fake_useragent.stop()
        LazyLoader.flush()
        super(TestMisc, self).tearDown()

    def test_execute_request_ok(self):
        response = FakeResponse('some response', 200)
        self._fake_useragent.set_response_value(response)
        eq_(execute_request(method='get', url='http://someurl.ru').decoded_data, 'some response')

    @raises(ProviderCommunicationProxylibError)
    def test_execute_request_error(self):
        response = Mock(side_effect=RequestError())
        with patch('passport.backend.social.proxylib.useragent.UserAgent.request', response):
            execute_request(method='get', url='http://someurl.ru')

    def test_execute_request_non_ascii_response(self):
        response = FakeResponse(b'\xd1\x8f\xd1\x8f\xd1\x8f', 200)
        self._fake_useragent.set_response_value(response)
        response = execute_request(method='get', url='http://someurl.ru')

        ok_(isinstance(response.data, str), type(response.data))
        ok_(isinstance(response.decoded_data, unicode), type(response.decoded_data))
        eq_(response.decoded_data, u'яяя', response.decoded_data)
