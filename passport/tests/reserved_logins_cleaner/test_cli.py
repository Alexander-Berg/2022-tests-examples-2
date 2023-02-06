# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from nose.tools import eq_
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.dbscripts.reserved_logins_cleaner.cli import clean_up_reserved_logins
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.test.consts import TEST_DATETIME_LONG_AGO


@with_settings_hosts()
class TestCleanupReservedLogins(TestCase):
    db = 'passportdbcentral'

    def serialize_login(self, login, reserved_until):
        self._db_faker.insert(
            table_name='reserved_logins',
            db=self.db,
            login=login,
            free_ts=reserved_until,
        )

    def test_nothing_to_clean(self):
        eq_(len(self._db_faker.select('reserved_logins', db=self.db)), 0)

        clean_up_reserved_logins()

        eq_(len(self._db_faker.select('reserved_logins', db=self.db)), 0)
        eq_(self._db_faker.query_count(self.db), 1)

    def test_expired_cleaned(self):
        data = (
            ('login-old', TEST_DATETIME_LONG_AGO),
            ('login-recent', datetime.now() - timedelta(seconds=1)),
            ('login-valid', datetime.now() + timedelta(seconds=1)),
        )
        for login, reserved_until in data:
            self.serialize_login(login, reserved_until)
        eq_(len(self._db_faker.select('reserved_logins', db=self.db)), 3)

        clean_up_reserved_logins()

        eq_(len(self._db_faker.select('reserved_logins', db=self.db)), 1)
        eq_(self._db_faker.query_count(self.db), 1)

        table_contents = [
            {
                'login': 'login-valid',
                'free_ts': DatetimeNow(timestamp=(datetime.now() + timedelta(seconds=1))),
            },
        ]
        self._db_faker.check_table_contents('reserved_logins', self.db, table_contents)
