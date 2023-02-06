# -*- coding: utf-8 -*-

import unittest

from nose.tools import eq_
from passport.backend.core.logging_utils.loggers.phone import PhoneLogEntry
from passport.backend.core.test.time_utils.time_utils import TimeNow


class TestPhoneLogEntry(unittest.TestCase):
    def test_phone_log_entry(self):
        entry = PhoneLogEntry(test='test')

        eq_(
            entry.params,
            {
                'unixtime': TimeNow(),
                'tskv_format': 'passport-phone-log',
                'test': 'test',
            },
        )
