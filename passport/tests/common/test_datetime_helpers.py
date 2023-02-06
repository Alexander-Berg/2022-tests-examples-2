# -*- coding: utf-8 -*-
from datetime import datetime
import os
import time

from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.oauth.core.common.utils import parse_datetime_to_unixtime
from passport.backend.oauth.core.test.framework import BaseTestCase


class TestDatetimeHelpers(BaseTestCase):
    def setUp(self):
        super(TestDatetimeHelpers, self).setUp()

        self.old_TZ = os.environ.get('TZ')
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        self.datetime = datetime(
            year=1970,
            month=1,
            day=1,
            hour=3,
            minute=0,
            second=1,
            microsecond=234567,
        )
        self.timestamp = 1.234567

    def tearDown(self):
        os.environ['TZ'] = self.old_TZ
        time.tzset()
        super(TestDatetimeHelpers, self).tearDown()

    def test_parse_datetime_to_unixtime(self):
        assert_is_none(
            parse_datetime_to_unixtime(''),
        )
        eq_(
            parse_datetime_to_unixtime('1970-01-01 03:00:01'),
            int(self.timestamp),
        )
