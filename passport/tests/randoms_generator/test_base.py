# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.dbscripts.randoms_generator import settings as local_settings
from passport.backend.dbscripts.randoms_generator.cli import run
from passport.backend.dbscripts.randoms_generator.db import get_randoms_table
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.utils.string import smart_bytes


TEST_KEYSPACES_AND_TABLES = (
    ('oauth', 'randoms_oauth'),
    ('yandex_ru', 'randoms'),
    ('yandex_com', 'randoms_com'),
    ('cookiel', 'lrandoms'),
)

TEST_OLD_KEYBODY = 'old_key'
TEST_OLD_EXPIRED_KEYBODY = 'old_expired_key'
TEST_CREATE_TIME = datetime(2000, 1, 1)


@with_settings_hosts(
    KEYSPACES_AND_TABLES_TO_PROCESS={},
    KEYSPACE_SETTINGS=local_settings.KEYSPACE_SETTINGS,
    DEFAULT_KEYSPACE_SETTINGS=local_settings.DEFAULT_KEYSPACE_SETTINGS,
    MAX_TIME_DISCREPANCY=0,
)
class TestBase(TestCase):
    def setUp(self):
        # проинициализируем таблицы, чтобы они создались
        for _, table_name in TEST_KEYSPACES_AND_TABLES:
            get_randoms_table(table_name)
        super(TestBase, self).setUp()

        for keyspace, table_name in TEST_KEYSPACES_AND_TABLES:
            self._db_faker.insert(
                'keyspaces',
                db='passportdbcentral',
                domainsuff=keyspace,
                tablename=table_name,
            )
            self._db_faker.insert(
                table_name,
                db='passportdbcentral',
                keybody=TEST_OLD_KEYBODY.encode('utf-8'),
                start=TEST_CREATE_TIME,
                valid=datetime.now() + timedelta(days=1),
            )
            self._db_faker.insert(
                table_name,
                db='passportdbcentral',
                keybody=TEST_OLD_EXPIRED_KEYBODY.encode('utf-8'),
                start=TEST_CREATE_TIME,
                valid=datetime.now() - timedelta(days=1),
            )

    def _get_keys(self, table_name):
        rows = self._db_faker.select(table_name, db='passportdbcentral')
        return [row[1] for row in rows]

    def assert_table_updated(self, table_name):
        keys = self._get_keys(table_name)
        eq_(len(keys), 2)
        ok_(smart_bytes(TEST_OLD_KEYBODY) in keys)
        ok_(smart_bytes(TEST_OLD_EXPIRED_KEYBODY) not in keys)

    def assert_table_not_updated(self, table_name):
        keys = self._get_keys(table_name)
        eq_(len(keys), 2)
        ok_(smart_bytes(TEST_OLD_KEYBODY) in keys)
        ok_(smart_bytes(TEST_OLD_EXPIRED_KEYBODY) in keys)

    def test_randoms_ok(self):
        run(process_randoms=True, process_lrandoms=False)
        eq_(self._db_faker.query_count('passportdbcentral'), 7)  # 1 читающий, 3*2 пишущих
        self.assert_table_updated('randoms')
        self.assert_table_updated('randoms_com')
        self.assert_table_updated('randoms_oauth')
        self.assert_table_not_updated('lrandoms')

    def test_lrandoms_ok(self):
        run(process_randoms=False, process_lrandoms=True)
        eq_(self._db_faker.query_count('passportdbcentral'), 3)  # 1 читающий, 2 пишущих
        self.assert_table_not_updated('randoms')
        self.assert_table_not_updated('randoms_com')
        self.assert_table_not_updated('randoms_oauth')
        self.assert_table_updated('lrandoms')

    def test_all_ok(self):
        run(process_randoms=True, process_lrandoms=True)
        eq_(self._db_faker.query_count('passportdbcentral'), 9)  # 1 читающий, 4*2 пишущих
        self.assert_table_updated('randoms')
        self.assert_table_updated('randoms_com')
        self.assert_table_updated('randoms_oauth')
        self.assert_table_updated('lrandoms')

    def test_custom_ok(self):
        with settings_context(
            KEYSPACES_AND_TABLES_TO_PROCESS={
                'oauth': 'randoms_oauth',
            },
            KEYSPACE_SETTINGS=local_settings.KEYSPACE_SETTINGS,
            DEFAULT_KEYSPACE_SETTINGS=local_settings.DEFAULT_KEYSPACE_SETTINGS,
            MAX_TIME_DISCREPANCY=0,
        ):
            run(process_randoms=True, process_lrandoms=True)
        eq_(self._db_faker.query_count('passportdbcentral'), 2)  # 0 читающих, 2 пишущих
        self.assert_table_not_updated('randoms')
        self.assert_table_not_updated('randoms_com')
        self.assert_table_updated('randoms_oauth')
        self.assert_table_not_updated('lrandoms')

    def test_nothing_to_do(self):
        run(process_randoms=False, process_lrandoms=False)
        eq_(self._db_faker.query_count('passportdbcentral'), 0)
        self.assert_table_not_updated('randoms')
        self.assert_table_not_updated('randoms_com')
        self.assert_table_not_updated('randoms_oauth')
        self.assert_table_not_updated('lrandoms')
