# -*- coding: utf-8 -*-
import unittest

import mock
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.s3.faker.fake_s3 import FakeS3Client
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
    TEST_TICKET_DATA,
)
from passport.backend.takeout.api.app import create_app
from passport.backend.takeout.test_utils.fake_redis import FakeRedis
from passport.backend.takeout.test_utils.touch import FakeTouchFiles
from passport.backend.utils.warnings import enable_strict_bytes_mode


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        enable_strict_bytes_mode()

    def setUp(self):
        self.tvm_faker = FakeTvmCredentialsManager()
        ticket_data = dict(TEST_TICKET_DATA)
        ticket_data.update(**{
            str(TEST_CLIENT_ID): {
                'alias': 'blackbox',
                'ticket': TEST_TICKET,
            },
        })
        self.tvm_faker.set_data(fake_tvm_credentials_data(ticket_data=ticket_data))
        self.s3_faker = FakeS3Client()
        self.grants_faker = FakeGrants()
        self.fake_redis = FakeRedis()
        self.touch_faker = FakeTouchFiles(self.s3_faker, self.fake_redis)
        self.request_id = mock.Mock(name='get_request_id', return_value='@request_id')

        # FIXME Разобраться в этом месте
        # GrantsConfig.config должен быть пустым словарём, чтобы инициализация
        # грантов не сломалась на iteritems в GrantsConfig.postprocess
        self.grants_faker._mock.return_value = {}

        self.patches = [
            self.tvm_faker,
            self.s3_faker,
            self.grants_faker,
            mock.patch(
                'passport.backend.core.logging_utils.request_id.RequestIdManager.get_request_id',
                self.request_id,
            ),
            self.fake_redis,
        ]

        for patch in self.patches:
            patch.start()

        self.flask_app = create_app()
        self.client = self.flask_app.test_client()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.tvm_faker
        del self.s3_faker
        del self.grants_faker
        del self.fake_redis
        del self.flask_app
        del self.client

    @property
    def tvm_headers(self):
        return {
            'X-Ya-Service-Ticket': TEST_TICKET,
        }
