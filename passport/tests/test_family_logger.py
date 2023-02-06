# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.logging_utils.faker.fake_tskv_logger import FamilyLoggerFaker
from passport.backend.core.logging_utils.loggers.family import (
    FamilyLogEntry,
    FamilyLogger,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow


def test_params():
    entry = FamilyLogEntry(foo='bar')

    eq_(
        entry.params,
        {
            'tskv_format': 'passport-family-log',
            'unixtime': TimeNow(),
            'foo': 'bar',
        },
    )


class TestFamilyLogger(unittest.TestCase):
    def setUp(self):
        self._money_log_faker = FamilyLoggerFaker()
        self._money_log_faker.start()

    def tearDown(self):
        self._money_log_faker.stop()
        del self._money_log_faker

    def test_log(self):
        logger = FamilyLogger()
        logger.bind(hello='world')
        logger.log(foo='bar', a='b=c')

        self._money_log_faker.assert_has_written(
            [
                {
                    'tskv_format': 'passport-family-log',
                    'unixtime': TimeNow(),
                    'foo': 'bar',
                    'hello': 'world',
                    'a': 'b=c',
                },
            ],
        )
