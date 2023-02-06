# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import eq_
from passport.backend.core.builders.tvm import TVM
from passport.backend.core.builders.tvm.faker import FakeTVM
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


TEST_CLIENT_ID = 12
TEST_CLIENT_SECRET = 'secret'


@with_settings(
    TVM_URL='http://localhost/',
    TVM_TIMEOUT=1,
    TVM_RETRIES=2,
)
class FakeTVMTestCase(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.start()

        self.fake_tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {
                        'alias': 'tvm_api',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.faker = FakeTVM()
        self.faker.start()
        self.tvm = TVM()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_verify_ssh(self):
        self.faker.set_response_value('verify_ssh', {'status': 'OK', 'fingerprint': 'fp'})
        eq_(
            self.tvm.verify_ssh('foo', 'bar', uid=1),
            {'status': 'OK', 'fingerprint': 'fp'},
        )
