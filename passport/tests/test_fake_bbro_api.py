# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.bbro_api import BBroApi
from passport.backend.core.builders.bbro_api.exceptions import BBroApiInvalidResponseError
from passport.backend.core.builders.bbro_api.faker import (
    bbro_bt_counters_parsed,
    bbro_response,
    FakeBBroApi,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)


TEST_YANDEXUID = 123


@with_settings(
    BBRO_API_URL='http://bbro_api/',
    BBRO_API_RETRIES=2,
    BBRO_API_TIMEOUT=1,
)
class FakeBBroApiTestCase(TestCase):
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

    def test_set_register_response_value(self):
        ok_(not self.fake_bbro_api._mock.request.called)
        self.fake_bbro_api.set_bbro_api_response_value(
            bbro_response(),
        )
        result = self.bbro_api.get_bt_counters_by_yandexuid(
            yandexuid=TEST_YANDEXUID,
        )
        ok_(self.fake_bbro_api._mock.request.called)
        eq_(result, bbro_bt_counters_parsed())

    def test_set_response_side_effect(self):
        ok_(not self.fake_bbro_api._mock.request.called)
        self.fake_bbro_api.set_bbro_api_response_side_effect(
            BBroApiInvalidResponseError('fake_message'),
        )
        with assert_raises(BBroApiInvalidResponseError):
            self.bbro_api.get_bt_counters_by_yandexuid(
                yandexuid=TEST_YANDEXUID,
            )
