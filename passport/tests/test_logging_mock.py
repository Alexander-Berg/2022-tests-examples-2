# encoding: utf-8

import logging
import unittest

from passport.backend.utils.logging_mock import LoggingMock


class TestLoggingMock(unittest.TestCase):
    def test_logging_mock(self):
        with LoggingMock() as log:
            logging.getLogger('test-logger-1').info('Log message #1')
            logging.getLogger('test-logger-1').info('Log message #2')
            logging.getLogger('test-logger-2').info('Log message #3')
            logging.getLogger('test-logger-2').info('Log message #4')

        self.assertListEqual(
            log.getLogger('test-logger-1').entries,
            [('Log message #1', 'INFO', None, None),
             ('Log message #2', 'INFO', None, None)]
        )
        self.assertListEqual(
            log.getLogger('test-logger-2').entries,
            [('Log message #3', 'INFO', None, None),
             ('Log message #4', 'INFO', None, None)]
        )
