# -*- coding: utf-8 -*-
import mock
import MySQLdb
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.db.eav.dbmanager import _DBManager
from passport.backend.oauth.core.db.eav.errors import (
    DBIntegrityError,
    DBTemporaryError,
)
from passport.backend.oauth.core.db.eav.query_base import BaseQuery
from passport.backend.oauth.core.db.eav.transaction import Transaction
from passport.backend.oauth.core.test.framework import BaseTestCase
import sqlalchemy.exc
from sqlalchemy.schema import (
    Column,
    MetaData,
    Table,
)
from sqlalchemy.types import Integer


db_config = {
    'master': {
        'database': 'master_test.sqlite',
        'connect_timeout': 0.1,
        'read_timeout': 1,
        'write_timeout': 8,
        'retries': 1,
        'retry_timeout': 0.1,
        'type': 'master',
        'driver': 'sqlite',
    },
    'slave': {
        'database': 'slave_test.sqlite',
        'connect_timeout': 0.1,
        'read_timeout': 1,
        'retries': 1,
        'retry_timeout': 0.1,
        'type': 'slave',
        'driver': 'sqlite',
    },
}


testdb_metadata = MetaData()

test_table = Table(
    'test',
    testdb_metadata,
    Column('x', Integer, primary_key=True, nullable=False),
    Column('y', Integer),
    Column('z', Integer),
)


class QueryForTest(BaseQuery):
    def __init__(self, dbm, sql_query):
        super(QueryForTest, self).__init__(table=test_table)
        self._dbm = dbm
        self._sql_query = sql_query

    @property
    def dbm(self):
        return self._dbm

    def to_sql(self):
        return self._sql_query


class TestDBManager(BaseTestCase):
    def create_table(self, engine, values):
        testdb_metadata.drop_all(bind=engine)
        testdb_metadata.create_all(bind=engine)
        query = test_table.insert(values)
        engine.execute(query)

    def setUp(self):
        super(TestDBManager, self).setUp()
        self.master_values = {'x': 4, 'y': 5, 'z': 6}
        self.slave_values = {'x': 1, 'y': 2, 'z': 3}
        ok_(self.master_values != self.slave_values)
        self.dbm = _DBManager()
        self.dbm.configure(db_config)
        self.create_table(self.dbm._master.select_engine(), self.master_values)
        self.create_table(self.dbm._slave.select_engine(), self.slave_values)

    def tearDown(self):
        del self.master_values
        del self.slave_values
        del self.dbm
        super(TestDBManager, self).tearDown()

    def test_empty_configs(self):
        dbm = _DBManager()
        dbm.configure({})
        ok_(dbm._master is None)
        ok_(dbm._slave is None)

    def test_master_slave(self):
        eq_(self.dbm._slave.select_engine().url.database, 'slave_test.sqlite')
        eq_(self.dbm._master.select_engine().url.database, 'master_test.sqlite')

    def test_fetchone(self):
        res = QueryForTest(self.dbm, test_table.select().limit(1)).execute().fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.slave_values)

        res = QueryForTest(self.dbm, test_table.select().limit(1)).execute(force_master=True).fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.master_values)

    def test_fetchone_via_transaction(self):
        res = Transaction(queries=[
            QueryForTest(self.dbm, test_table.select().limit(1)),
        ]).execute()[0].fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.slave_values)

        res = Transaction(queries=[
            QueryForTest(self.dbm, test_table.select().limit(1)),
        ]).execute(force_master=True)[0].fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.master_values)

    def test_insert(self):
        values = {'x': 7, 'y': 8, 'z': 9}
        values1 = {'x': 10, 'y': 11, 'z': 12}
        values2 = {'x': 13, 'y': 14, 'z': 15}

        # Insert всегда идет в мастер.
        QueryForTest(self.dbm, test_table.insert(values)).execute()
        QueryForTest(self.dbm, test_table.insert(values1)).execute()
        QueryForTest(self.dbm, test_table.insert(values2)).execute()

        res = QueryForTest(self.dbm, test_table.select()).execute().fetchall()
        eq_(len(res), 1)

        res = QueryForTest(self.dbm, test_table.select()).execute(force_master=True).fetchall()
        eq_(len(res), 4)

        # Тестирование идет на sqlite. Порядок результатов будет определяться
        # порядком вставки.
        eq_(res[1], (values['x'], values['y'], values['z']))
        eq_(res[2], (values1['x'], values1['y'], values1['z']))
        eq_(res[3], (values2['x'], values2['y'], values2['z']))

    def test_update(self):
        values = {'y': 8, 'z': 9}

        # Update должен уйти в мастер.
        QueryForTest(
            self.dbm,
            test_table.update().where(test_table.c.x == self.master_values['x']).values(values),
        ).execute()

        # Поэтому в слейве, куда должны уходить только Select-запросы, не
        # должно ничего поменяться.
        res = QueryForTest(self.dbm, test_table.select()).execute().fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.slave_values)

        # А вот в мастере должно поменяться.
        res = QueryForTest(self.dbm, test_table.select()).execute(force_master=True).fetchall()
        eq_(len(res), 1)
        res = res[0]
        eq_(
            {'x': res[0], 'y': res[1], 'z': res[2]},
            dict(x=self.master_values['x'], **values),
        )

    def test_update_via_transaction(self):
        values = {'y': 8, 'z': 9}

        # Update должен уйти в мастер.
        Transaction(queries=[
            QueryForTest(
                self.dbm,
                test_table.update().where(test_table.c.x == self.master_values['x']).values(values),
            ),
        ]).execute()

        # Поэтому в слейве, куда должны уходить только Select-запросы, не
        # должно ничего поменяться.
        res = QueryForTest(self.dbm, test_table.select()).execute().fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.slave_values)

        # А вот в мастере должно поменяться.
        res = QueryForTest(self.dbm, test_table.select()).execute(force_master=True).fetchall()
        eq_(len(res), 1)
        res = res[0]
        eq_(
            {'x': res[0], 'y': res[1], 'z': res[2]},
            dict(x=self.master_values['x'], **values),
        )

    def test_delete(self):
        QueryForTest(self.dbm, test_table.delete()).execute()

        res = QueryForTest(self.dbm, test_table.select()).execute().fetchone()
        eq_({'x': res[0], 'y': res[1], 'z': res[2]}, self.slave_values)

        res = QueryForTest(self.dbm, test_table.select()).execute(force_master=True).fetchone()
        eq_(res, None)

    def _dbmanager_with_patched_engine(self, assertion, reconnect_retries, fail_retries, side_effect=None):
        def custom_side_effect(query=None, counter=[0], **kwargs):
            counter[0] += 1
            if counter[0] < fail_retries:
                raise sqlalchemy.exc.DatabaseError('', '', '')
            return mock.Mock()

        engine_mock = mock.Mock()
        engine_mock.connect.side_effect = side_effect or custom_side_effect
        engine_mock.execute.side_effect = side_effect or custom_side_effect
        engine_mock.reconnect_retries = reconnect_retries
        engine_mock.reconnect_timeout = 0

        select_engine_mock = mock.Mock()
        select_engine_mock.return_value = engine_mock
        with mock.patch('passport.backend.oauth.core.db.eav.dbmanager._SlaveRouter.select_engine', select_engine_mock):
            with mock.patch('passport.backend.oauth.core.db.eav.dbmanager._MasterRouter.select_engine', select_engine_mock):
                assertion(engine_mock)

    def test_retries(self):
        def assertion(engine_mock):
            dbm = _DBManager()
            dbm.configure(db_config)
            QueryForTest(self.dbm, test_table.select()).execute()
            eq_(engine_mock.execute.call_count, 3)

        self._dbmanager_with_patched_engine(assertion=assertion, reconnect_retries=5, fail_retries=3)

    @raises(DBTemporaryError)
    def test_dberror(self):
        def assertion(engine_mock):
            dbm = _DBManager()
            dbm.configure(db_config)
            QueryForTest(self.dbm, test_table.select()).execute()

        self._dbmanager_with_patched_engine(assertion=assertion, reconnect_retries=2, fail_retries=3)

    @raises(DBTemporaryError)
    def test_mysql_dberror(self):
        def assertion(engine_mock):
            dbm = _DBManager()
            dbm.configure(db_config)
            QueryForTest(self.dbm, test_table.select()).execute()

        self._dbmanager_with_patched_engine(
            assertion=assertion,
            reconnect_retries=5,
            fail_retries=3,
            side_effect=MySQLdb.OperationalError('', ''),
        )

    @raises(DBIntegrityError)
    def test_integrity_error(self):
        def assertion(engine_mock):
            dbm = _DBManager()
            dbm.configure(db_config)
            QueryForTest(self.dbm, test_table.select()).execute()

        self._dbmanager_with_patched_engine(
            assertion=assertion,
            reconnect_retries=5,
            fail_retries=3,
            side_effect=sqlalchemy.exc.IntegrityError('', '', ''),
        )

    @raises(DBTemporaryError)
    def test_ping_failed(self):
        def assertion(engine_mock):
            dbm = _DBManager()
            dbm.configure(db_config)
            self.dbm.ping()

        self._dbmanager_with_patched_engine(assertion=assertion, reconnect_retries=2, fail_retries=3)
