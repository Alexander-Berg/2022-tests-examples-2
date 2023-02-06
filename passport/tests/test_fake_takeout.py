# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from passport.backend.core.builders.takeout import Takeout
from passport.backend.core.builders.takeout.faker import (
    FakeTakeout,
    takeout_ok_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)


TEST_UID = 1
TEST_UNIXTIME = 1000


@with_settings(
    TAKEOUT_URL='http://localhost/',
    TAKEOUT_CONSUMER='passport',
    TAKEOUT_RETRIES=2,
    TAKEOUT_TIMEOUT=1,
)
class FakeTakeoutTestCase(TestCase):
    def setUp(self):
        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'takeout',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.tvm_credentials_manager.start()

        self.faker = FakeTakeout()
        self.faker.start()

        self.takeout = Takeout()

    def tearDown(self):
        self.faker.stop()
        self.tvm_credentials_manager.stop()
        del self.faker
        del self.tvm_credentials_manager

    def test_prepare_archive_ok(self):
        self.faker.set_response_value(
            'prepare_archive',
            json.dumps(takeout_ok_response()).encode('utf8'),
        )
        self.takeout.prepare_archive(TEST_UID, TEST_UNIXTIME)
