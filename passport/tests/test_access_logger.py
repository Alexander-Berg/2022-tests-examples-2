# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.logging_utils.faker.fake_tskv_logger import AccessLoggerFaker
from passport.backend.core.logging_utils.loggers.access import (
    AccessLogEntry,
    AccessLogger,
)


def test_params():
    entry = AccessLogEntry(foo='bar')

    eq_(
        entry.params,
        {
            'tskv_format': 'passport-api-access-log',
            'foo': 'bar',
        },
    )


class TestAccessLogger(unittest.TestCase):
    def setUp(self):
        self._access_log_faker = AccessLoggerFaker()
        self._access_log_faker.start()

    def tearDown(self):
        self._access_log_faker.stop()
        del self._access_log_faker

    def test_log(self):
        logger = AccessLogger()
        logger.bind(hello='world')
        logger.log(foo='bar', a='b=c')

        self._access_log_faker.assert_has_written(
            [
                {
                    'tskv_format': 'passport-api-access-log',
                    'foo': 'bar',
                    'hello': 'world',
                    'a': 'b=c',
                },
            ],
        )
