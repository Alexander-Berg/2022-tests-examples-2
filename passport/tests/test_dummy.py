# -*- coding: utf-8 -*-

from unittest import TestCase

from passport.backend.core.logging_utils.faker.fake_tskv_logger import DummyLoggerFaker
from passport.backend.core.logging_utils.loggers.dummy import DummyLogger


class DummyLoggerTestCase(TestCase):
    def setUp(self):
        self.dummy_logger = DummyLogger()

        self.faker = DummyLoggerFaker()
        self.faker.start()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_does_not_log(self):
        """
        Ничего не пишется в журнал.
        """
        self.dummy_logger.log(foo='foo')
        self.faker.assert_has_written([])
