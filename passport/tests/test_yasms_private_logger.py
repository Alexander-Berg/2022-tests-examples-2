# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.logging_utils.faker.fake_tskv_logger import YasmsPrivateLoggerFaker
from passport.backend.core.logging_utils.loggers.statbox import (
    YasmsPrivateLogEntry,
    YasmsPrivateLogger,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow


def test_params():
    entry = YasmsPrivateLogEntry(foo='bar')

    eq_(
        entry.params,
        {
            'foo': 'bar',
            'unixtime': TimeNow(),
            'unixtimef': TimeNow(),
            'sender': 'passport',
            'sms': '1',
        },
    )


class TestYasmsPrivateLogger(unittest.TestCase):
    def setUp(self):
        self._yasms_private_log_faker = YasmsPrivateLoggerFaker()
        self._yasms_private_log_faker.start()

    def tearDown(self):
        self._yasms_private_log_faker.stop()
        del self._yasms_private_log_faker

    def test_log(self):
        logger = YasmsPrivateLogger()
        logger.bind(hello='world')
        logger.log(foo='bar', a='b=c', global_smsid='global-sms-id')

        self._yasms_private_log_faker.assert_has_written(
            [
                {
                    'foo': 'bar',
                    'hello': 'world',
                    'a': 'b=c',
                    'global_smsid': 'global-sms-id',
                    'sender': 'passport',
                    'unixtime': TimeNow(),
                    'unixtimef': TimeNow(),
                    'sms': '1',
                },
            ],
        )

    def test_log_missing_global_smsid(self):
        logger = YasmsPrivateLogger()
        logger.bind(hello='world')
        with self.assertRaises(ValueError):
            logger.log(foo='bar')

        self._yasms_private_log_faker.assert_equals([])
