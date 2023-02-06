# -*- coding: utf-8 -*-

from unittest import TestCase as _TestCase

from passport.backend.core.builders.blackbox.blackbox import Blackbox as BlackboxBuilder
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.logging_utils.faker.fake_tskv_logger import StatboxLoggerFaker
from passport.backend.core.logging_utils.loggers import StatboxLogger
from passport.backend.core.mailer.faker import FakeMailer
from passport.backend.core.models.phones.faker import PhoneIdGeneratorFaker
from passport.backend.core.test.events import EventLoggerFaker
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


class TestCase(_TestCase):
    def setUp(self):
        self._fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self._fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self._blackbox_builder_faker = FakeBlackbox()
        self._statbox_faker = StatboxLoggerFaker()
        self._db_faker = FakeDB()
        self._event_log_faker = EventLoggerFaker()
        self._mailer_faker = FakeMailer()
        self._phone_id_generator_faker = PhoneIdGeneratorFaker()

        self._patches = [
            self._blackbox_builder_faker,
            self._db_faker,
            self._event_log_faker,
            self._fake_tvm_credentials_manager,
            self._mailer_faker,
            self._phone_id_generator_faker,
            self._statbox_faker,
        ]
        for patch in self._patches:
            patch.start()

        self._blackbox_builder = BlackboxBuilder()
        self._statbox = StatboxLogger()

    def tearDown(self):
        for patch in reversed(self._patches):
            patch.stop()
        del self._patches
        del self._fake_tvm_credentials_manager
        del self._blackbox_builder_faker
        del self._statbox_faker
        del self._db_faker
        del self._event_log_faker
        del self._mailer_faker
