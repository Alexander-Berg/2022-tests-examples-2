# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_yakey_backup_response
from passport.backend.core.models.yakey_backup import YaKeyBackup
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.dbscripts.test.base_phone_harvester import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_BACKUP_1,
    TEST_BACKUP_2,
    TEST_BACKUP_3,
    TEST_DATETIME_LONG_AGO,
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_PHONE_NUMBER3,
)
from passport.backend.dbscripts.yakey_backups_cleaner.cli import clean_up_expired_backups
from passport.backend.utils.time import datetime_to_integer_unixtime


@with_settings_hosts()
class TestCleanupYakeyBackups(TestCase):
    db = 'passportdbcentral'

    def serialize_backup(self, phone_number, backup, updated):
        bb_response = json.loads(blackbox_yakey_backup_response(
            phone_number=phone_number,
            backup=backup,
            updated=updated,
        ))
        backup = YaKeyBackup().parse(bb_response['yakey_backups'][0])
        self._db_faker._serialize_to_eav(backup)

    def assert_db_no_backup_for_number(self, phone_number, queries=None):
        self._db_faker.check_missing(
            'yakey_backups',
            attr='phone_number',
            phone_number=int(phone_number),
            db=self.db,
        )
        if queries is not None:
            self._db_faker.assert_executed_queries_equal(queries, db=self.db)

    def test_no_backups(self):
        clean_up_expired_backups(offset=timedelta(seconds=1))

        ok_(not self._db_faker.select('yakey_backups', db=self.db))
        eq_(self._db_faker.query_count(self.db), 1)

    def test_expired_cleaned(self):
        bck_2_last_updated = (datetime.now() - timedelta(seconds=600)).replace(microsecond=0)

        data = (
            (TEST_PHONE_NUMBER1, TEST_BACKUP_1, TEST_DATETIME_LONG_AGO),
            (TEST_PHONE_NUMBER2, TEST_BACKUP_2, bck_2_last_updated),
        )
        for phone, backup, updated in data:
            self.serialize_backup(
                phone_number=phone.digital,
                backup=backup,
                updated=datetime_to_integer_unixtime(updated),
            )
        eq_(len(self._db_faker.select('yakey_backups', db=self.db)), 2)

        clean_up_expired_backups(offset=timedelta(seconds=700))

        eq_(len(self._db_faker.select('yakey_backups', db=self.db)), 1)
        eq_(self._db_faker.query_count(self.db), 1)

        self.assert_db_no_backup_for_number(TEST_PHONE_NUMBER1.digital)

        table_contents = [
            {
                'phone_number': int(TEST_PHONE_NUMBER2.digital),
                'backup': TEST_BACKUP_2,
                'updated': bck_2_last_updated,
                'device_name': None,
            },
        ]
        self._db_faker.check_table_contents('yakey_backups', self.db, table_contents)

    def test_with_phone_numbers(self):
        bck_2_last_updated = (datetime.now() - timedelta(seconds=600)).replace(microsecond=0)
        phone_numbers = [int(TEST_PHONE_NUMBER1.digital), int(TEST_PHONE_NUMBER2.digital)]

        data = (
            (TEST_PHONE_NUMBER1, TEST_BACKUP_1, TEST_DATETIME_LONG_AGO),
            (TEST_PHONE_NUMBER2, TEST_BACKUP_2, bck_2_last_updated),
            (TEST_PHONE_NUMBER3, TEST_BACKUP_3, TEST_DATETIME_LONG_AGO),
        )
        for phone, backup, updated in data:
            self.serialize_backup(
                phone_number=phone.digital,
                backup=backup,
                updated=datetime_to_integer_unixtime(updated),
            )
        eq_(len(self._db_faker.select('yakey_backups', db=self.db)), 3)

        clean_up_expired_backups(offset=timedelta(seconds=700), phone_numbers=phone_numbers)

        eq_(len(self._db_faker.select('yakey_backups', db=self.db)), 2)
        eq_(self._db_faker.query_count(self.db), 1)

        self.assert_db_no_backup_for_number(TEST_PHONE_NUMBER1.digital)

        table_contents = [
            {
                'phone_number': int(TEST_PHONE_NUMBER2.digital),
                'backup': TEST_BACKUP_2,
                'updated': bck_2_last_updated,
                'device_name': None,
            },
            {
                'phone_number': int(TEST_PHONE_NUMBER3.digital),
                'backup': TEST_BACKUP_3,
                'updated': TEST_DATETIME_LONG_AGO,
                'device_name': None,
            },
        ]
        self._db_faker.check_table_contents('yakey_backups', self.db, table_contents)
