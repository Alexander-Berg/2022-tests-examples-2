# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.models.account import Account
from passport.backend.utils.time import unixtime_to_datetime


class TestTakeoutParse(unittest.TestCase):
    def test_empty(self):
        acc = Account().parse({
            'login': 'test',
        })
        ok_(not acc.takeout.extract_in_progress_since)
        ok_(not acc.takeout.archive_s3_key)
        ok_(not acc.takeout.archive_password)
        ok_(not acc.takeout.archive_created_at)
        ok_(not acc.takeout.fail_extract_at)

    def test_full(self):
        acc = Account().parse({
            'login': 'test',
            'takeout.extract_in_progress_since': '24',
            'takeout.archive_s3_key': 'key',
            'takeout.archive_password': 'password',
            'takeout.archive_created_at': 42,
            'takeout.fail_extract_at': 43,
        })
        eq_(acc.takeout.extract_in_progress_since, unixtime_to_datetime(24))
        eq_(acc.takeout.archive_s3_key, 'key')
        eq_(acc.takeout.archive_password, 'password')
        eq_(acc.takeout.archive_created_at, unixtime_to_datetime(42))
        eq_(acc.takeout.fail_extract_at, unixtime_to_datetime(43))
