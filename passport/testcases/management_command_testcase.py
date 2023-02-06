# -*- coding: utf-8 -*-
import logging

from passport.backend.oauth.core.test.fake_logs import FakeLoggingHandler
from passport.backend.oauth.core.test.framework.testcases.api_testcase import ApiTestCase
from passport.backend.utils.lock import lock_mock


class ManagementCommandTestCase(ApiTestCase):
    command_class = None
    default_command_kwargs = {}  # это словарь, который возвращает парсер аргументов
    logger_name = 'console'

    def setUp(self):
        super(ManagementCommandTestCase, self).setUp()

        logger = logging.getLogger(self.logger_name)
        self._fake_log_handler = FakeLoggingHandler()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.addHandler(self._fake_log_handler)

        self.command = self.command_class()

    def tearDown(self):
        super(ManagementCommandTestCase, self).setUp()

    def run_command(self, **kwargs):
        actual_kwargs = dict(self.default_command_kwargs, **kwargs)
        with lock_mock():
            self.command.handle(**actual_kwargs)

    def assert_log(self, message, level='error'):
        self._fake_log_handler.assert_written(message, level)

    def log_messages(self, level=None):
        return self._fake_log_handler.messages(level)
