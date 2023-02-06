# -*- coding: utf-8 -*-
import datetime
import unittest

from nose.tools import raises
from passport.backend.core.db.faker.db import (
    yakey_backup_insert,
    yakey_backup_update,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import yakey_backups_table as bck
from passport.backend.core.differ import diff
from passport.backend.core.models.yakey_backup import YaKeyBackup
from passport.backend.core.serializers.eav.yakey_backup import YaKeyBackupSerializer
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_PHONE_NUMBER_1 = PhoneNumber.parse('+79090000001')
TEST_PHONE_NUMBER_2 = PhoneNumber.parse('+79090000002')
TEST_BACKUP_1 = 'abc123456def'
TEST_BACKUP_2 = 'abc654321def'
TEST_DATETIME_LONG_AGO = datetime.datetime(1970, 1, 1)
TEST_DEVICE_NAME = 'device'


class TestSerializeYaKeyBackup(unittest.TestCase):

    def test_delete(self):
        backup = YaKeyBackup()
        backup.phone_number = TEST_PHONE_NUMBER_2
        backup.backup = TEST_BACKUP_2
        backup.updated = TEST_DATETIME_LONG_AGO

        queries = YaKeyBackupSerializer().serialize(backup, None, diff(backup, None))
        eq_eav_queries(
            queries,
            [
                bck.delete().where(
                    bck.c.phone_number == int(TEST_PHONE_NUMBER_2.digital),
                ),
            ],
        )

    def test_update(self):
        backup_old = YaKeyBackup()
        backup_old.phone_number = TEST_PHONE_NUMBER_1
        backup_old.backup = TEST_BACKUP_1
        backup_old.updated = TEST_DATETIME_LONG_AGO
        backup_old.device_name = TEST_DEVICE_NAME

        backup = YaKeyBackup()
        backup.phone_number = TEST_PHONE_NUMBER_1
        backup.backup = TEST_BACKUP_2
        backup.updated = DatetimeNow()
        backup.device_name = None

        queries = YaKeyBackupSerializer().serialize(backup_old, backup, diff(backup_old, backup))
        eq_eav_queries(
            queries,
            [
                yakey_backup_update(TEST_DATETIME_LONG_AGO).values([
                    {
                        'phone_number': int(TEST_PHONE_NUMBER_1.digital),
                        'backup': TEST_BACKUP_2.encode('utf8'),
                        'device_name': None,
                        'updated': DatetimeNow(),
                    },
                ]),
            ],
        )

    def test_create(self):
        backup = YaKeyBackup()
        backup.phone_number = TEST_PHONE_NUMBER_1
        backup.backup = TEST_BACKUP_1
        backup.updated = DatetimeNow()
        backup.device_name = TEST_DEVICE_NAME

        queries = YaKeyBackupSerializer().serialize(None, backup, diff(None, backup))
        eq_eav_queries(
            queries,
            [
                yakey_backup_insert().values([
                    {
                        'phone_number': int(TEST_PHONE_NUMBER_1.digital),
                        'backup': TEST_BACKUP_1.encode('utf8'),
                        'device_name': TEST_DEVICE_NAME,
                        'updated': DatetimeNow(),
                    },
                ]),
            ],
        )

    def test_no_diff(self):
        backup_old = YaKeyBackup()
        backup_old.phone_number = TEST_PHONE_NUMBER_1
        backup_old.backup = TEST_BACKUP_1

        backup = YaKeyBackup()
        backup.phone_number = TEST_PHONE_NUMBER_1
        backup.backup = TEST_BACKUP_1

        queries = YaKeyBackupSerializer().serialize(backup_old, backup, diff(backup_old, backup))
        eq_eav_queries(queries, [])

    @raises(ValueError)
    def test_update_phone_number_forbidden(self):
        backup_old = YaKeyBackup()
        backup_old.phone_number = TEST_PHONE_NUMBER_1
        backup_old.backup = TEST_BACKUP_1
        backup_old.updated = TEST_DATETIME_LONG_AGO
        backup_old.device_name = None

        backup = YaKeyBackup()
        backup.phone_number = TEST_PHONE_NUMBER_2
        backup.backup = TEST_BACKUP_2
        backup.device_name = TEST_DEVICE_NAME

        YaKeyBackupSerializer().serialize(backup_old, backup, diff(backup_old, backup))
