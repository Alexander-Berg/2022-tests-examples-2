# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.zora import (
    Zora,
    ZoraInvalidUrlError,
    ZoraTemporaryError,
)
from passport.backend.core.builders.zora.faker.fake_zora import (
    FakeZora,
    zora_response,
)
from passport.backend.core.test.test_utils import (
    check_data_contains_params,
    iterdiff,
    with_settings,
)


TEST_URLS = ['https://smth_{}'.format(i) for i in range(10)]
TEST_OK_RESPONSE_RAW = b'SOME RAW BYTES'


@with_settings(
    ZORA_HOST='localhost',
    ZORA_PORT='666',
    ZORA_RETRIES=2,
    ZORA_TIMEOUT=1,
    ZORA_SOURCE='source',
)
class TestZoraCommon(unittest.TestCase):
    def setUp(self):
        self.zora = Zora()
        self.zora.useragent.request = mock.Mock()

        self.response = mock.Mock()
        self.zora.useragent.request.return_value = self.response
        self.response.content = TEST_OK_RESPONSE_RAW
        self.response.status_code = 200
        self.response.reason = ''
        self.response.headers = {}

    def tearDown(self):
        del self.zora
        del self.response

    def test_ok(self):
        self.zora.get(TEST_URLS[0])
        iterdiff(eq_)(
            self.zora.useragent.request.call_args.args,
            (
                'GET',
                'http://smth_0',
            ),
        )
        check_data_contains_params(
            self.zora.useragent.request.call_args.kwargs,
            {
                'timeout': 1,
                'verify': '/etc/ssl/certs/ca-certificates.crt',
                'headers': {
                    'X-Yandex-Fetchoptions': 'd',
                    'X-Yandex-Sourcename': 'source',
                    'X-Yandex-NoCalc': '1',
                    'X-Yandex-Response-Timeout': '1',
                    'X-Yandex-Requesttype': 'userproxy',
                    'X-Yandex-Use-Https': '1',
                },
                'reconnect': False,
                'allow_redirects': True,
                'max_redirects': 5,
                'proxies': {'http': 'http://localhost:666'},
            },
        )

    def test_zora_error(self):
        self.response.reason = 'zora'
        with assert_raises(ZoraTemporaryError):
            self.zora.get(TEST_URLS[0])

    def test_passport_default_initialization(self):
        zora = Zora()
        ok_(zora.useragent is not None)
        eq_(zora.proxies, {
            'http': 'http://localhost:666',
        })


@with_settings(
    ZORA_HOST='http://localhost',
    ZORA_PORT='666',
    ZORA_RETRIES=2,
    ZORA_TIMEOUT=1,
    ZORA_SOURCE='source',
)
class TestZoraMethods(unittest.TestCase):
    def setUp(self):
        self.faker = FakeZora()
        self.faker.start()
        self.zora = Zora()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.zora

    def test_ok(self):
        self.faker.set_response_value(TEST_URLS[0], zora_response(TEST_OK_RESPONSE_RAW))
        eq_(self.zora.get(TEST_URLS[0]), TEST_OK_RESPONSE_RAW)
        self.faker.requests[0].assert_properties_equal(
            method='GET',
            url='http://smth_0',
            headers={
                'X-Yandex-Sourcename': 'source',
                'X-Yandex-Response-Timeout': '1',
                'X-Yandex-Fetchoptions': 'd',
                'X-Yandex-NoCalc': '1',
                'X-Yandex-Requesttype': 'userproxy',
                'X-Yandex-Use-Https': '1',
            },
        )

    def test_zora_error(self):
        self.faker.set_response_value(TEST_URLS[0], zora_response(
            reason='zora',
        ))
        with assert_raises(ZoraTemporaryError):
            self.zora.get(TEST_URLS[0])
        eq_(len(self.faker.requests), 2)

    def test_get_image_empty_content(self):
        self.faker.set_response_value(TEST_URLS[0], zora_response())
        with assert_raises(ZoraInvalidUrlError):
            self.zora.get_image(TEST_URLS[0])

    def test_get_image_bad_status_coded(self):
        self.faker.set_response_value(TEST_URLS[0], zora_response(status_code=404))
        with assert_raises(ZoraInvalidUrlError):
            self.zora.get_image(TEST_URLS[0])

    def test_get_image_invalid_content_type(self):
        self.faker.set_response_value(TEST_URLS[0], zora_response(TEST_OK_RESPONSE_RAW, headers={'content-type': 'application/msword'}))
        with assert_raises(ZoraInvalidUrlError):
            self.zora.get_image(TEST_URLS[0])
