# -*- coding: utf-8 -*-

from contextlib import contextmanager

import mock
from passport.backend.social.common.db.schemas import metadata
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.pool import StaticPool

from .diff import (
    build_diff,
    format_diff,
)


_engine_descriptor = None


def eq_sql_queries(queries_a, queries_b):
    queries_a = map(_ComparableSqlQuery, queries_a)
    queries_b = map(_ComparableSqlQuery, queries_b)
    assert queries_a == queries_b, format_diff(build_diff(queries_a, queries_b))


class EngineDescriptor(object):
    def __init__(self):
        self.executed_queries = []

        connect_args = dict(
            # Т.к. sqlite создаёт для каждого нового соединения новую БД в
            # памяти, придётся делиться соединением между гринлетами.
            # Правильно делиться БД, а не соединениями
            # (https://sqlite.org/sharedcache.html#inmemsharedcache), но
            # для этого нужен sqlite из Python 3.4 или пропатченный бинарный
            # python-модуль sqlite.
            check_same_thread=False,
        )

        # Включаем честный autocommit в Sqlite и выключаем имитацию autocommit
        # в Sqlalchemy, чтобы было как в MySQL.
        connect_args.update(isolation_level=None)
        execution_options = dict(autocommit=False)

        engine = create_engine(
            'sqlite://',
            connect_args=connect_args,
            execution_options=execution_options,
            poolclass=StaticPool,
        )
        engine.reconnect_retries = 1

        metadata.create_all(engine)

        self.execute_original = Connection.execute
        self.execute_mock = mock.Mock(name='execute', side_effect=self.execute_original)

        def fake_execute(conn, query, *args, **kwargs):
            self.executed_queries.append(query)
            return self.execute_mock(conn, query, *args, **kwargs)

        execute_patch = mock.patch.object(Connection, 'execute', fake_execute)
        execute_patch.start()

        self.engine = engine
        self.execute_patch = execute_patch


class FakeDb(object):
    def __init__(self):
        global _engine_descriptor

        if _engine_descriptor is None:
            _engine_descriptor = EngineDescriptor()

        def fake_create_engine(dsn, *args, **kwargs):
            return _engine_descriptor.engine

        self._patch = mock.patch('passport.backend.social.common.db.utils.sqlalchemy_create_engine', fake_create_engine)

    def start(self):
        _engine_descriptor.executed_queries = []
        _engine_descriptor.execute_mock.side_effect = _engine_descriptor.execute_original
        self._patch.start()

        with self.no_recording():
            metadata.create_all(_engine_descriptor.engine)

    def stop(self):
        _engine_descriptor.execute_mock.side_effect = _engine_descriptor.execute_original
        metadata.drop_all(_engine_descriptor.engine)
        self._patch.stop()

    @contextmanager
    def no_recording(self):
        _engine_descriptor.execute_patch.stop()
        try:
            yield self.get_engine()
        finally:
            _engine_descriptor.execute_patch.start()

    @property
    def executed_queries(self):
        return _engine_descriptor.executed_queries

    def get_engine(self):
        return _engine_descriptor.engine

    def assert_executed_queries_equal(self, queries):
        eq_sql_queries(self.executed_queries, queries)

    def set_side_effect(self, side_effect):
        _engine_descriptor.execute_mock.side_effect = side_effect


class _ComparableSqlQuery(object):
    def __init__(self, query):
        self._sql_expr, self._params = _sql_query_to_tuple(query)
        self._evaluated = _sql_query_to_str(query)

    def __eq__(self, other):
        return (self._sql_expr, self._params) == (other._sql_expr, other._params)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self._evaluated

    def __repr__(self):
        return self._evaluated


def _sql_query_to_str(query, dialect=None):
    if isinstance(query, basestring):
        return query

    sql, parameters = _sql_query_to_tuple(query, dialect)

    for i, value in enumerate(parameters):
        if isinstance(value, str):
            value = value.decode('utf-8')
        if isinstance(value, basestring):
            value = "'" + value + "'"
        else:
            value = repr(value)
        parameters[i] = value

    if parameters:
        sql = sql % tuple(parameters)
    return sql


def _sql_query_to_tuple(query, dialect=None):
    compiled = query.compile(dialect=dialect or mysql.dialect())

    parameters = []
    for param_ind in compiled.positiontup:
        value = compiled.binds[param_ind].value
        parameters.append(value)

    sql = compiled.string.replace('\n', '')
    return (sql, parameters)
