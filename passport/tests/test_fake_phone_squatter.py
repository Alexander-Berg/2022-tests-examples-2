# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.core.builders.phone_squatter.faker import (
    FakePhoneSquatter,
    phone_squatter_get_change_status_response,
    phone_squatter_start_tracking_response,
)
from passport.backend.core.builders.phone_squatter.phone_squatter import PhoneSquatter
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_PHONE_NUMBER = '+78001234567'
TEST_REQUEST_ID = 'req-id'


@with_settings(
    PHONE_SQUATTER_URL='http://localhost/',
    PHONE_SQUATTER_TIMEOUT=1,
    PHONE_SQUATTER_RETRIES=2,
)
class FakePhoneSquatterTestCase(PassportTestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'phone_squatter',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.faker = FakePhoneSquatter()
        self.faker.start()
        self.phone_squatter = PhoneSquatter()

    def tearDown(self):
        self.faker.stop()
        self.fake_tvm_credentials_manager.stop()

    def test_get_change_status(self):
        self.faker.set_response_value('get_change_status', phone_squatter_get_change_status_response())
        eq_(
            self.phone_squatter.get_change_status(TEST_PHONE_NUMBER, TEST_REQUEST_ID),
            json.loads(phone_squatter_get_change_status_response()),
        )

    def test_start_tracking(self):
        self.faker.set_response_value('start_tracking', phone_squatter_start_tracking_response())
        eq_(
            self.phone_squatter.start_tracking(TEST_PHONE_NUMBER, TEST_REQUEST_ID),
            json.loads(phone_squatter_start_tracking_response()),
        )
