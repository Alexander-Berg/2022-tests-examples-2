# -*- coding: utf-8 -*-
from sqlite3 import Cursor

import mock
from nose.tools import (
    eq_,
    ok_,
)
from sqlalchemy import (
    delete,
    insert,
    select,
)

from clck_db.connection import DBConnection
from clck_db.schemas import (
    clicker_metadata,
    TABLE_NAME_TO_TABLE,
    urls_table,
)

from .test_data import INITIAL_TEST_DB_DATA


class FakeClickerDB(object):
    test_config = {
        'master': {
            'driver': 'sqlite',
        },
    }
    test_credentials = {
        'db_user': '',
        'db_password': '',
    }

    def __init__(self):
        self.db_name = ':memory:'
        self.db = DBConnection(config=self.test_config, db_credentials={self.db_name: self.test_credentials})

    def start(self):
        self.db.configure()
        assert self.db.primary_db_name == self.db_name
        engine = self.db.get_engine()
        clicker_metadata.create_all(engine)

        self.db_mock = mock.Mock(return_value=self.db)
        self.db_patch = mock.patch('clck_db.queries.get_db_connection', self.db_mock)
        self.db_patch.start()

    def stop(self):
        self.db_patch.stop()
        engine = self.db.get_engine()
        clicker_metadata.drop_all(engine)

    def set_side_effect(self, side_effect):
        self.db.execute = mock.Mock(side_effect=side_effect)

    def set_cursor_fetchall_result(self, result):
        cursor_mock = mock.MagicMock(spec=Cursor)
        cursor_mock.fetchall.return_value = result
        return cursor_mock

    def set_cursor_inserted_key_result(self, result):
        cursor_mock = mock.MagicMock(spec=Cursor)
        cursor_mock.inserted_primary_key = result
        return cursor_mock

    def assert_called(self):
        ok_(self.db_mock.call_count)

    def assert_not_called(self):
        ok_(not self.db_mock.call_count)

    def load_initial_data(self):
        for table_name, data in INITIAL_TEST_DB_DATA.iteritems():
            for row in data:
                db_table = TABLE_NAME_TO_TABLE[table_name]
                self.db.execute(insert(db_table).values(row), db_name=self.db_name)

    def drop_tables(self, tables):
        for table in tables:
            db_table = TABLE_NAME_TO_TABLE[table]
            self.db.execute(delete(db_table), db_name=self.db_name)

    def assert_db(self, total_count=2, last_url=None):
        result = self.db.execute(select([urls_table]), master=False, db_name=self.db_name).fetchall()
        eq_(len(result), total_count)
        if last_url:
            result = result[-1]
            eq_(last_url, result['url'])
