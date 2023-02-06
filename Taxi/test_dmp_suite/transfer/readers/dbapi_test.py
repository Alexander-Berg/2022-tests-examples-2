import unittest
import uuid
import datetime as dt

import pytest

from dmp_suite import dbapi
from connection.pgaas import get_pgaas_connection
from dmp_suite.transfer.readers import dbapi as dbapi_readers


@pytest.mark.slow
class TestReader:
    data = (
        {'id': 1, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 0), 'value': uuid.uuid4().hex, },
        {'id': 2, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 1), 'value': uuid.uuid4().hex, },
        {'id': 3, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 2), 'value': uuid.uuid4().hex, },
        {'id': 4, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 3), 'value': uuid.uuid4().hex, },
        {'id': 5, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 3), 'value': uuid.uuid4().hex, },
        {'id': 6, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 3), 'value': uuid.uuid4().hex, },
        {'id': 7, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 4), 'value': uuid.uuid4().hex, },
        {'id': 8, 'updated_at': dt.datetime(2019, 1, 1, 0, 0, 0, 5), 'value': uuid.uuid4().hex, },
    )

    def create_table(self):
        table_name = 'table_' + uuid.uuid4().hex
        self.query_executor.execute_without_results('''
            create temporary table %s (
                id integer primary key,
                updated_at timestamp without time zone,
                value text
            ) on commit drop
        ''' % table_name)
        for row in self.data:
            self.query_executor.execute_without_results(
                'insert into %s values (%%(id)s, %%(updated_at)s, %%(value)s)' % table_name, row)
        return table_name

    @pytest.fixture(scope='class', autouse=True)
    def setup_and_teardown(self, request, slow_test_settings):
        cls = request.cls
        with slow_test_settings():
            cls.connection = get_pgaas_connection("testing", writable=True, cursor_factory=None).native_connection
            cls.transaction_ctx = dbapi.TransactionCtx(cls.connection)
            cls.query_executor = dbapi.QueryExecutor(cls.transaction_ctx)
        yield
        cls.connection.close()

    def build_increment_reader(self):
        table_name = self.create_table()
        return dbapi_readers.IncrementReader(
            filter_field='updated_at',
            transaction_ctx=self.transaction_ctx,
            table=table_name,
            sortable_uniq_index='id',
            iteration_chunk_size=1,
        )

    def test_read_all(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            table_name = self.create_table()
            reader = dbapi_readers.Reader(self.transaction_ctx, table_name)
            data = tuple(reader.read())
        assert data == self.data

    def test_iterative_read_all(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            table_name = self.create_table()
            reader = dbapi_readers.IterativeReader(
                transaction_ctx=self.transaction_ctx,
                table=table_name,
                sortable_uniq_index='id',
                iteration_chunk_size=1,
            )
            data = tuple(reader.read())
        assert data == self.data

    def test_read_increment_all(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            reader = self.build_increment_reader()
            data = tuple(reader.read())
        assert data == self.data

    def test_read_increment_filtered_from(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            reader = self.build_increment_reader()
            data = tuple(reader.read(start_value=dt.datetime(2019, 1, 1, 0, 0, 0, 3)))
        assert data == self.data[3:]

    def test_read_increment_filtered_to(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            reader = self.build_increment_reader()
            data = tuple(reader.read(end_value=dt.datetime(2019, 1, 1, 0, 0, 0, 3)))
        assert data == self.data[:3]

    def test_read_increment_filtered_between(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            reader = self.build_increment_reader()
            data = tuple(reader.read(
                start_value=dt.datetime(2019, 1, 1, 0, 0, 0, 1), end_value=dt.datetime(2019, 1, 1, 0, 0, 0, 4)))
        assert data == self.data[1:6]

    def test_read_increment_filtered_between_included_end(self):
        with self.transaction_ctx:  # execute read in single transaction since pgbouncer in transaction pooling mode
            reader = self.build_increment_reader()
            data = tuple(reader.read(
                start_value=dt.datetime(2019, 1, 1, 0, 0, 0, 1), end_value=dt.datetime(2019, 1, 1, 0, 0, 0, 3),
                include_end_value=True
            ))
        assert data == self.data[1:6]
