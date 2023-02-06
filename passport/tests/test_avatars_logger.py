# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.logging_utils.faker.fake_tskv_logger import AvatarsLoggerFaker
from passport.backend.core.logging_utils.loggers.avatars import (
    AvatarsLogEntry,
    AvatarsLogger,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow


def test_params():
    entry = AvatarsLogEntry(foo='bar')

    eq_(
        entry.params,
        {
            'tskv_format': 'avatars-log',
            'unixtime': TimeNow(),
            'foo': 'bar',
        },
    )


class TestAvatarsLogger(unittest.TestCase):
    def setUp(self):
        self._log_faker = AvatarsLoggerFaker()
        self._log_faker.start()

    def tearDown(self):
        self._log_faker.stop()
        del self._log_faker

    def test_log(self):
        logger = AvatarsLogger()
        logger.bind(hello='world')
        logger.log(foo='bar', a='b=c')

        self._log_faker.assert_has_written(
            [
                {
                    'tskv_format': 'avatars-log',
                    'unixtime': TimeNow(),
                    'foo': 'bar',
                    'hello': 'world',
                    'a': 'b=c',
                },
            ],
        )
