# -*- coding: utf-8 -*-
import json
from sqlite3 import Cursor

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.infra.daemons.yasmsapi.db.config import (
    DB_QUEUE,
    DB_VALIDATOR,
)
from passport.infra.daemons.yasmsapi.db.connection import DBConnection
from passport.infra.daemons.yasmsapi.db.queries import METADATA_TO_DB_NAME
from passport.infra.daemons.yasmsapi.db.schemas import (
    sms_queue_table,
    TABLE_NAME_TO_TABLE,
)
from sqlalchemy import (
    delete,
    insert,
    select,
)

from .test_data import INITIAL_TEST_DB_DATA


class FakeYasmsDB(object):
    test_config = dict.fromkeys(
        [
            DB_VALIDATOR,
            DB_QUEUE,
        ],
        {
            'database': ':memory:',
            'driver': 'sqlite',
        },
    )

    def __init__(self):
        self.db = DBConnection(configs=self.test_config)

    def start(self):
        self.db.configure()
        for metadata, db_name in METADATA_TO_DB_NAME.iteritems():
            engine = self.db.get_engine(db_name)
            metadata.create_all(engine)

        self.db_mock = mock.Mock(return_value=self.db)
        self.db_patch = mock.patch('passport.infra.daemons.yasmsapi.db.queries.get_db_connection', self.db_mock)
        self.db_patch.start()

    def stop(self):
        self.db_patch.stop()
        for metadata, db_name in METADATA_TO_DB_NAME.iteritems():
            engine = self.db.get_engine(db_name)
            metadata.drop_all(engine)

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
                db_name = METADATA_TO_DB_NAME[db_table.metadata]
                self.db.execute(db_name, insert(db_table).values(row))

    def drop_tables(self, tables):
        for table in tables:
            db_table = TABLE_NAME_TO_TABLE[table]
            db_name = METADATA_TO_DB_NAME[db_table.metadata]
            self.db.execute(db_name, delete(db_table))

    def assert_enqueued(self, values):
        db_name = METADATA_TO_DB_NAME[sms_queue_table.metadata]
        result = self.db.execute(db_name, select([sms_queue_table])).fetchall()
        eq_(len(result), 1)
        result = result[0]
        for k, v in values.iteritems():
            r = result[k]
            if isinstance(v, dict) or isinstance(v, list):
                r = json.loads(r)
            eq_(v, r, 'Key differ %s != %s in %s' % (r, v, k))

    def assert_empty(self):
        db_name = METADATA_TO_DB_NAME[sms_queue_table.metadata]
        result = self.db.execute(db_name, select([sms_queue_table])).fetchall()
        ok_(not len(result))
