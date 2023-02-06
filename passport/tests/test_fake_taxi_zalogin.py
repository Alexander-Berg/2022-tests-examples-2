# -*- coding: utf-8 -*-
from unittest import TestCase

from nose_parameterized import parameterized
from passport.backend.core.builders.taxi_zalogin import (
    EVENT_TYPE,
    TaxiZalogin,
    TaxiZaloginAuthEror,
    TaxiZaloginPermanentZaloginError,
    TaxiZaloginTemporaryZaloginError,
)
from passport.backend.core.builders.taxi_zalogin.faker import (
    FakeTaxiZalogin,
    taxi_zalogin_ok_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)


TEST_UID = 1
TEST_UID2 = 2


@with_settings(
    TAXI_ZALOGIN_URL='http://localhost/',
    TAXI_ZALOGIN_RETRIES=2,
    TAXI_ZALOGIN_TIMEOUT=1,
)
class FakeTaxiZaloginTestCase(TestCase):
    def setUp(self):
        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'taxi_zalogin',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.tvm_credentials_manager.start()

        self.faker = FakeTaxiZalogin()
        self.faker.start()

        self.taxi = TaxiZalogin()

    def tearDown(self):
        self.faker.stop()
        self.tvm_credentials_manager.stop()
        del self.faker
        del self.tvm_credentials_manager

    def test_uid_notify_ok(self):
        self.faker.set_response_value('uid_notify', taxi_zalogin_ok_response())
        self.taxi.uid_notify(TEST_UID, TEST_UID2, EVENT_TYPE.BIND)

    @parameterized.expand([
        (TaxiZaloginAuthEror,),
        (TaxiZaloginPermanentZaloginError,),
        (TaxiZaloginTemporaryZaloginError,),
    ])
    def test_uid_notify_error(self, exception):
        self.faker.set_response_side_effect('uid_notify', exception())
        self.assertRaises(exception, self.taxi.uid_notify, TEST_UID, TEST_UID2, EVENT_TYPE.BIND)
