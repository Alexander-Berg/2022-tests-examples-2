# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core.builders.bbro_api import (
    BBroApi,
    BBroApiInvalidRequestError,
    BBroApiInvalidResponseError,
    BBroApiTemporaryError,
)
from passport.backend.core.builders.bbro_api.faker import (
    bbro_bt_counters_parsed,
    bbro_no_counters_response,
    bbro_no_response,
    bbro_response,
    bbro_segments,
    FakeBBroApi,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)


TEST_YANDEXUID = '123'
MALFORMED_TEST_YANDEXUID = 'greetings_to_your_mom'
MALFORMED_TEST_YANDEXUID2 = '2398749826438264783264328746387264783264'


@with_settings(
    BBRO_API_URL='http://bbro_api',
    BBRO_API_RETRIES=2,
    BBRO_API_TIMEOUT=1,
)
class TestBBroApi(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID): {
                    'alias': 'bbro',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_bbro_api = FakeBBroApi()
        self.fake_bbro_api.start()
        self.bbro_api = BBroApi()

    def tearDown(self):
        self.fake_bbro_api.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_bbro_api
        del self.fake_tvm_credentials_manager

    def test_ok(self):
        self.fake_bbro_api.set_response_value_without_method(json.dumps(bbro_response()))
        response = self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )
        eq_(response, bbro_bt_counters_parsed())
        self.fake_bbro_api.requests[0].assert_properties_equal(
            method='GET',
            url='http://bbro_api?operation=6&client=auth',
            cookies=dict(yandexuid=TEST_YANDEXUID),
        )

    def test_parser(self):
        bt_counters_parsed = self.bbro_api.parse_bbro_segments(
            bbro_segments(),
        )
        eq_(bt_counters_parsed, bbro_bt_counters_parsed())

    @raises(BBroApiTemporaryError)
    def test_network_error(self):
        self.fake_bbro_api.set_response_value_without_method('not a json', 400)
        self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )

    @raises(BBroApiInvalidResponseError)
    def test_invalid_json(self):
        self.fake_bbro_api.set_response_value_without_method('not a json')
        self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )

    def test_no_counters_for_yandexuid(self):
        self.fake_bbro_api.set_response_value_without_method(json.dumps(bbro_no_counters_response()))
        response = self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )
        eq_(response, {})

    def test_nonexisting_yandexuid(self):
        self.fake_bbro_api.set_response_value_without_method(json.dumps({}))
        response = self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )
        eq_(response, {})

    def test_malformed_yandexuid(self):
        with assert_raises(BBroApiInvalidRequestError):
            self.bbro_api.get_bt_counters_by_yandexuid(
                yandexuid=MALFORMED_TEST_YANDEXUID,
            )

    def test_malformed_yandexuid2(self):
        with assert_raises(BBroApiInvalidRequestError):
            self.bbro_api.get_bt_counters_by_yandexuid(
                yandexuid=MALFORMED_TEST_YANDEXUID2,
            )

    def test_no_response(self):
        self.fake_bbro_api.set_response_value_without_method(bbro_no_response())
        response = self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )
        eq_(response, {})
