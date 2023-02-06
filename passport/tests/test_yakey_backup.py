# -*- coding: utf-8 -*-
import datetime
import unittest

from nose.tools import eq_
from passport.backend.core.models.yakey_backup import YaKeyBackup
from passport.backend.core.test.time_utils.time_utils import datetime_to_unixtime
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.core.undefined import Undefined


TEST_PHONE_STRING = '+79090000001'
TEST_PHONE_OBJECT = PhoneNumber.parse(TEST_PHONE_STRING)
TEST_BACKUP = 'abc123-x'
TEST_DATETIME_LONG_AGO = datetime.datetime(1970, 1, 2)
TEST_TIMESTAMP_LONG_AGO = datetime_to_unixtime(TEST_DATETIME_LONG_AGO)
TEST_DEVICE_NAME = 'my device'
TEST_UNICODE_DEVICE_NAME = u'мой девайс'


class TestYaKeyBackup(unittest.TestCase):
    def test_empty(self):
        backup = YaKeyBackup().parse({})
        eq_(backup.phone_number, Undefined)
        eq_(backup.updated, Undefined)
        eq_(backup.backup, Undefined)
        eq_(backup.device_name, Undefined)

    def test_yakey_backup_parse_with_string_phone(self):
        backup = YaKeyBackup().parse({
            'phone_number': TEST_PHONE_STRING,
            'backup': TEST_BACKUP,
            'updated': TEST_TIMESTAMP_LONG_AGO,
            'device_name': TEST_DEVICE_NAME,
        })
        eq_(backup.phone_number.e164, TEST_PHONE_STRING)
        eq_(backup.updated, TEST_DATETIME_LONG_AGO)
        eq_(backup.backup, TEST_BACKUP)
        eq_(backup.device_name, TEST_DEVICE_NAME)

    def test_yakey_backup_parse_with_object_phone(self):
        backup = YaKeyBackup().parse({
            'phone_number': TEST_PHONE_OBJECT,
            'backup': TEST_BACKUP,
            'updated': TEST_TIMESTAMP_LONG_AGO,
            'device_name': TEST_UNICODE_DEVICE_NAME,
        })
        eq_(backup.phone_number.e164, TEST_PHONE_STRING)
        eq_(backup.updated, TEST_DATETIME_LONG_AGO)
        eq_(backup.backup, TEST_BACKUP)
        eq_(backup.device_name, TEST_UNICODE_DEVICE_NAME)
