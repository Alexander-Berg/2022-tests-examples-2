# -*- coding: utf-8 -*-
from datetime import datetime
import socket
import unittest

import mock
import MySQLdb
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.query import DbTransaction
from passport.backend.core.db.read_api.aliases import RemovedAliasesByUidQuery
from passport.backend.core.db.schemas import reserved_logins_table
from passport.backend.core.dbmanager.exceptions import DBDataError
from passport.backend.core.dbmanager.manager import (
    _Router,
    DBError,
    DBIntegrityError,
    get_dbm,
    safe_execute_queries,
)
from passport.backend.core.serializers.eav.query import (
    EavDeleteExtendedAttributeQuery,
    EavInsertAliasQuery,
    EavInsertAttributeQuery,
    EavInsertAttributeWithOnDuplicateKeyAppendQuery,
    EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery,
    EavInsertAttributeWithOnDuplicateKeyIncrementQuery,
    EavInsertAttributeWithOnDuplicateKeyUpdateQuery,
    EavInsertSuidQuery,
)
from passport.backend.core.serializers.query import GenericInsertQuery
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.mock_objects import _host
from passport.backend.utils.common import merge_dicts
from sqlalchemy.exc import (
    DatabaseError,
    DataError,
    IntegrityError,
    OperationalError,
)


TEST_MASTER_CONFIG = {
    'master': {
        'database': ':memory:',
        'connect_timeout': 0.1,
        'read_timeout': 1,
        'write_timeout': 8,
        'retries': 1,
        'type': 'master',
        'driver': 'sqlite',
    },
}

TEST_SLAVE_CONFIG = {
    'slave': {
        'driver': 'sqlite',
        'database': ':memory:',
        'type': 'slave',
    },
}

TEST_SLAVE_WITH_LOW_TIMEOUT_CONFIG = {
    'slave_with_low_timeout': {
        'driver': 'sqlite',
        'database': ':memory:',
        'type': 'slave',
        'has_low_timeout': True,
    },
}

TEST_HOST_WITH_DC = 'db-%(dc)s1.yandex.ru'


@with_settings(
    HOSTS=[_host(name=socket.getfqdn(), id=0x7F, dc='myt')],
    DB_DEFAULT_CONNECT_ARGS={'sqlite': {'retries': 10}},
)
class TestDBManager(unittest.TestCase):
    def setUp(self):
        self.dbm = get_dbm('test')

    def test_without_any_configs(self):
        self.dbm.configure({})
        assert_is_none(self.dbm._master)
        assert_is_none(self.dbm._slave)

        for kwargs in ({}, {'force_master': False}):
            with assert_raises(RuntimeError):
                self.dbm.get_engine(**kwargs)

    def test_with_only_slave_config(self):
        self.dbm.configure(TEST_SLAVE_CONFIG)

        assert_is_none(self.dbm._master)
        ok_(self.dbm._slave)
        eq_(len(self.dbm._slave.engines), 1)

        for kwargs in ({}, {'force_master': False, 'with_low_timeout': True}):
            with assert_raises(RuntimeError):
                self.dbm.get_engine(**kwargs)

        eq_(self.dbm.get_engine(force_master=False), self.dbm._slave.engines[0])

    def test_with_multiple_slaves(self):
        self.dbm.configure(merge_dicts(TEST_SLAVE_CONFIG, TEST_SLAVE_WITH_LOW_TIMEOUT_CONFIG))

        assert_is_none(self.dbm._master)
        ok_(self.dbm._slave)
        eq_(len(self.dbm._slave.engines), 2)

        with assert_raises(RuntimeError):
            self.dbm.get_engine()

        engine = self.dbm.get_engine(force_master=False)
        ok_(not engine.has_low_timeout)

        engine = self.dbm.get_engine(force_master=False, with_low_timeout=True)
        ok_(engine.has_low_timeout)

    def test_with_only_master_config(self):
        self.dbm.configure(TEST_MASTER_CONFIG)

        assert_is_none(self.dbm._slave)
        ok_(self.dbm._master)
        eq_(len(self.dbm._master.engines), 1)

        eq_(self.dbm.get_engine(), self.dbm._master.engines[0])
        eq_(self.dbm.get_engine(force_master=False), self.dbm._master.engines[0])

        with assert_raises(RuntimeError):
            self.dbm.get_engine(with_low_timeout=True)

    def test_with_master_and_slave_configs(self):
        self.dbm.configure(merge_dicts(TEST_SLAVE_CONFIG, TEST_MASTER_CONFIG))

        ok_(self.dbm._master)
        ok_(self.dbm._slave)
        eq_(len(self.dbm._master.engines), 1)
        eq_(len(self.dbm._slave.engines), 1)

        engine = self.dbm.get_engine()
        eq_(engine, self.dbm._master.engines[0])

        engine = self.dbm.get_engine(force_master=False)
        eq_(engine, self.dbm._slave.engines[0])

        with assert_raises(RuntimeError):
            self.dbm.get_engine(with_low_timeout=True)


@with_settings(
    HOSTS=[_host(name=socket.getfqdn(), id=0x7F, dc='myt')],
    DB_DEFAULT_CONNECT_ARGS={'sqlite': {'retries': 10}},
)
class TestRouter(unittest.TestCase):
    def setUp(self):
        self.uc = TEST_MASTER_CONFIG['master']

    def test_given_config_overrides_default(self):
        """Заданная конфигурация переписывает встроенную конфигурацию."""
        router = _Router([self.uc])
        config = router.get_configs()[0]
        eq_(config['database'], self.uc['database'])
        eq_(config['retries'], self.uc['retries'])
        eq_(config['driver'], self.uc['driver'])

    def test_router_sets_up_engines(self):
        """Маршрутизатор конфигурирует движки с помощью известной ему
        конфигурации."""
        create_engine = mock.Mock()
        with mock.patch('passport.backend.core.dbmanager.manager.create_engine', create_engine):
            _Router([self.uc])
            assert create_engine.called
            eq_(
                create_engine.call_args[1]['connect_args'],
                {'retries': 1},
            )

    def test_router_formats_dc_in_host(self):
        """Роутер понимает, что в хост БД может быть нужно подставить имя датацентра текущего хоста"""
        create_engine_mock = mock.Mock()
        with mock.patch('passport.backend.core.dbmanager.manager.create_engine', create_engine_mock):
            _Router([dict(self.uc, host=TEST_HOST_WITH_DC)])

        eq_(create_engine_mock.call_args[0][0].host, TEST_HOST_WITH_DC % {'dc': 'myt'})


class SpecialException(Exception):
    pass


class TestSafeExecute(unittest.TestCase):
    INSERT_ATTRIBUTE_QUERY = EavInsertAttributeQuery(1, [(10, 'value')])
    DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY = EavDeleteExtendedAttributeQuery(
        1,
        [{'entity_type': 20, 'entity_id': 100, 'type': 2}],
    )

    def setUp(self):
        self.db = FakeDB()
        self.db.start()

    def tearDown(self):
        self.db.stop()
        del self.db

    @staticmethod
    def _query_generator():
        for query in [
            TestSafeExecute.INSERT_ATTRIBUTE_QUERY,
            TestSafeExecute.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
        ]:
            yield query

    def test_nested_transaction_fails(self):
        inner_transaction_container = DbTransaction(self._query_generator)()
        transaction_container = DbTransaction(
            lambda: [self.INSERT_ATTRIBUTE_QUERY, inner_transaction_container],
        )()

        with assert_raises(ValueError):
            safe_execute_queries([transaction_container], transaction_retries=2)

    def test_begin_fails_retry_ok(self):
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            begin=[DatabaseError('BEGIN', None, None), None],
        )

        transaction_container = DbTransaction(self._query_generator)()

        safe_execute_queries([transaction_container], transaction_retries=2)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'COMMIT',
            ],
            db='passportdbshard1',
        )

    def test_begin_completely_fails_transaction_not_retries(self):
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            begin=DatabaseError('BEGIN', None, None),
        )
        transaction_container = DbTransaction(self._query_generator)()

        with assert_raises(DBError):
            safe_execute_queries([transaction_container], transaction_retries=2)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                'BEGIN',
            ],
            db='passportdbshard1',
        )

    def test_begin_fails_with_unhandled_exception_transaction_not_retries(self):
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            begin=[SpecialException, None],
        )

        transaction_container = DbTransaction(self._query_generator)()

        with assert_raises(SpecialException):
            safe_execute_queries([transaction_container], transaction_retries=2)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
            ],
            db='passportdbshard1',
        )

    def test_commit_fails_no_retries(self):
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            commit=[DatabaseError('COMMIT', '', ''), None, None],
        )
        transaction_container = DbTransaction(self._query_generator)()

        with assert_raises(DBError):
            safe_execute_queries([transaction_container], transaction_retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'COMMIT',
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])

    def test_commit_fails_and_rollback_fails_no_retries(self):
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            commit=[DatabaseError('COMMIT', '', ''), None, None],
            rollback=[DatabaseError('ROLLBACK', '', ''), None, None],
        )
        transaction_container = DbTransaction(self._query_generator)()

        with assert_raises(DBError):
            safe_execute_queries([transaction_container], transaction_retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'COMMIT',
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])

    def test_query_fails_and_retries_within_single_transaction(self):
        FAILING_QUERY = EavInsertAliasQuery(1, [(7, 'alias', 7)])
        transaction_container = DbTransaction(
            lambda: [
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                # Запрос будет падать т.к. нет такой таблицы в passportdbshard1
                FAILING_QUERY,
            ],
        )()

        with assert_raises(DBError):
            safe_execute_queries([transaction_container], transaction_retries=2, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                FAILING_QUERY,
                'ROLLBACK',
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                FAILING_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 6)

    def test_query_fails_with_connection_invalidated_transaction_retries(self):
        transaction_container = DbTransaction(
            lambda: [
                self.INSERT_ATTRIBUTE_QUERY,
            ],
        )()
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            [DatabaseError('', None, None, connection_invalidated=True), mock.DEFAULT],
        )

        safe_execute_queries([transaction_container], transaction_retries=3, retries=2)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,  # этот запрос "упал", ретраи внутри транзакции невозможны
                'ROLLBACK',
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                'COMMIT',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [{'type': 10, 'uid': 1, 'value': 'value'}])
        eq_(self.db.query_count('passportdbshard1'), 2)

    def test_query_fails_with_operational_error_transaction_fails_without_retries(self):
        transaction_container = DbTransaction(self._query_generator)()
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            # первый запрос выполнился, следующий упал
            [mock.DEFAULT, OperationalError(None, None, MySQLdb.OperationalError(1048, None))],
        )

        with assert_raises(DBIntegrityError):
            safe_execute_queries([transaction_container], transaction_retries=3, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 2)

    def test_query_fails_with_operational_error_transaction_fails_retries(self):
        transaction_container = DbTransaction(self._query_generator)()
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            # первый запрос выполнился, следующий упал
            [mock.DEFAULT, OperationalError(None, None, MySQLdb.OperationalError(1000, None)), mock.DEFAULT, mock.DEFAULT],
        )

        safe_execute_queries([transaction_container], transaction_retries=3, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'ROLLBACK',
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'COMMIT',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [{'type': 10, 'uid': 1, 'value': 'value'}])
        eq_(self.db.query_count('passportdbshard1'), 4)

    def test_query_fails_with_integrity_error_transaction_fails_without_retries(self):
        transaction_container = DbTransaction(self._query_generator)()
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            # первый запрос выполнился, следующий упал
            [mock.DEFAULT, IntegrityError('', None, None)],
        )

        with assert_raises(DBIntegrityError):
            safe_execute_queries([transaction_container], transaction_retries=3, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 2)

    def test_query_fails_with_data_error_transaction_fails_without_retries(self):
        transaction_container = DbTransaction(self._query_generator)()
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            # первый запрос выполнился, следующий упал
            [mock.DEFAULT, DataError('', None, None)],
        )

        with assert_raises(DBDataError):
            safe_execute_queries([transaction_container], transaction_retries=3, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 2)

    def test_serialization_fails_with_unhandled_exception_transaction_rollbacks_and_fails_without_retries(self):
        def _serializer():
            yield (self.INSERT_ATTRIBUTE_QUERY, lambda *args: None)
            raise SpecialException()

        transaction_container = DbTransaction(_serializer)()

        with assert_raises(SpecialException):
            safe_execute_queries([transaction_container], transaction_retries=2, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 1)

    def test_unhandled_exception_in_callback_transaction_rollbacks_and_fails_without_retries(self):
        def _serializer():
            def _bad_callback(*args):
                raise SpecialException()
            yield (self.INSERT_ATTRIBUTE_QUERY, _bad_callback)

        transaction_container = DbTransaction(_serializer)()

        with assert_raises(SpecialException):
            safe_execute_queries([transaction_container], transaction_retries=2, retries=3)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 1)

    def test_serialization_fails_before_transaction_started(self):
        def _serializer():
            raise SpecialException()

        transaction_container = DbTransaction(_serializer)()

        with assert_raises(SpecialException):
            safe_execute_queries([transaction_container], transaction_retries=2, retries=3)

        self.db.assert_executed_queries_equal(
            [],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 0)

    def test_empty_serializer_transaction_not_executed(self):
        transaction_container = DbTransaction(lambda: (_ for _ in []))()

        safe_execute_queries([transaction_container], transaction_retries=2, retries=3)

        self.db.assert_executed_queries_equal(
            [],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [])
        eq_(self.db.query_count('passportdbshard1'), 0)

    def test_query_fails_rollback_fails_transaction_retry_ok(self):
        transaction_container = DbTransaction(
            lambda: [
                self.INSERT_ATTRIBUTE_QUERY,
            ],
        )()
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            [DatabaseError('', None, None), mock.DEFAULT],
        )
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            rollback=[DatabaseError('ROLLBACK', None, None), None],
        )

        safe_execute_queries([transaction_container], transaction_retries=2, retries=1)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                'ROLLBACK',
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                'COMMIT',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [{'type': 10, 'uid': 1, 'value': 'value'}])
        eq_(self.db.query_count('passportdbshard1'), 2)

    def test_mixed_query_and_transaction_with_retries(self):
        INSERT_ALIAS_QUERY = EavInsertAliasQuery(1, [(7, 'alias', 7)])
        transaction_container = DbTransaction(self._query_generator)()
        queries = [
            INSERT_ALIAS_QUERY,
            transaction_container,
        ]
        self.db.set_side_effect_for_db(
            'passportdbcentral',
            [MySQLdb.InterfaceError, mock.DEFAULT],
        )
        # в транзакции сначала падает BEGIN
        self.db.set_side_effect_for_transaction(
            'passportdbshard1',
            begin=[DatabaseError('BEGIN', None, None), None, None],
        )
        # затем падает запрос, ретраится в пределах транзакции, и то же самое происходит со вторым запросом
        self.db.set_side_effect_for_db(
            'passportdbshard1',
            [
                DatabaseError('', None, None, connection_invalidated=False),
                mock.DEFAULT,
                DatabaseError('', None, None, connection_invalidated=False),
                mock.DEFAULT,
            ],
        )

        safe_execute_queries(queries, transaction_retries=3, retries=2)

        self.db.assert_executed_queries_equal(
            [
                INSERT_ALIAS_QUERY,
                INSERT_ALIAS_QUERY,
            ],
            db='passportdbcentral',
        )
        self.db.check_table_contents(
            'aliases',
            'passportdbcentral',
            [{'type': 7, 'value': 'alias', 'surrogate_type': '7', 'uid': 1}],
        )
        eq_(self.db.query_count('passportdbcentral'), 2)
        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                'BEGIN',
                self.INSERT_ATTRIBUTE_QUERY,
                self.INSERT_ATTRIBUTE_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                self.DELETE_FROM_EXTENDED_ATTRIBUTES_QUERY,
                'COMMIT',
            ],
            db='passportdbshard1',
        )
        self.db.check_table_contents('attributes', 'passportdbshard1', [{'type': 10, 'uid': 1, 'value': 'value'}])
        eq_(self.db.query_count('passportdbshard1'), 4)

    def test_query_fails_with_ignore_errors_set(self):
        self.db.set_side_effect_for_db(
            'passportdbcentral',
            MySQLdb.InterfaceError,
        )
        FAILING_QUERY = EavInsertAliasQuery(1, [(7, 'alias', 7)])
        FAILING_QUERY._IGNORE_ERRORS = True

        safe_execute_queries([FAILING_QUERY], retries=10)

        self.db.check_table_contents('aliases', 'passportdbcentral', [])
        eq_(self.db.query_count('passportdbcentral'), 10)

    def test_selectable_query_passed_to_master(self):
        safe_execute_queries([RemovedAliasesByUidQuery(1)])

        self.db.assert_executed_queries_equal(
            [
                RemovedAliasesByUidQuery(1),
            ],
        )


class TestQueryJoining(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()

    def tearDown(self):
        self.db.stop()
        del self.db

    def test_all_inserts_joined(self):
        queries = [
            (EavInsertAttributeQuery(1, [(1, 2)]), None),
            (EavInsertAttributeQuery(1, [(2, 3)]), None),
            (EavInsertAttributeQuery(1, [(3, 4)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(4, 5)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(5, 6)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(6, 7)]), None),
            (EavInsertAttributeWithOnDuplicateKeyAppendQuery(1, [(7, 8)]), None),
            (EavInsertAttributeWithOnDuplicateKeyAppendQuery(1, [(8, 9)]), None),
            (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(4, (5, 6))]), None),
            (EavInsertAttributeWithOnDuplicateKeyIncrementQuery(1, [(9, 11)]), None),
            (EavInsertAttributeWithOnDuplicateKeyIncrementQuery(1, [(10, 12)]), None),
        ]

        safe_execute_queries(queries)

        expected = [
            EavInsertAttributeQuery(
                1,
                [
                    (1, 2),
                    (2, 3),
                    (3, 4),
                ]
            ),
            EavInsertAttributeWithOnDuplicateKeyUpdateQuery(
                1,
                [
                    (4, 5),
                    (5, 6),
                    (6, 7),
                ],
            ),
            EavInsertAttributeWithOnDuplicateKeyAppendQuery(
                1,
                [
                    (7, 8),
                    (8, 9),
                ],
            ),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(
                1,
                [
                    (4, (5, 6)),
                ],
            ),
            EavInsertAttributeWithOnDuplicateKeyIncrementQuery(
                1,
                [
                    (9, 11),
                    (10, 12),
                ],
            ),
        ]
        self.db.assert_executed_queries_equal(
            expected,
            db='passportdbshard1',
        )

    def test_all_inserts_joined_inside_transaction(self):
        queries = [
            DbTransaction(lambda: [
                (EavInsertAttributeQuery(1, [(1, 2)]), None),
                (EavInsertAttributeQuery(1, [(2, 3)]), None),
                (EavInsertAttributeQuery(1, [(3, 4)]), None),
                (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(4, 5)]), None),
                (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(5, 6)]), None),
                (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(6, 7)]), None),
                (EavInsertAttributeWithOnDuplicateKeyAppendQuery(1, [(7, 8)]), None),
                (EavInsertAttributeWithOnDuplicateKeyAppendQuery(1, [(8, 9)]), None),
                (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(4, (5, 6))]), None),
                (EavInsertAttributeWithOnDuplicateKeyIncrementQuery(1, [(9, 11)]), None),
                (EavInsertAttributeWithOnDuplicateKeyIncrementQuery(1, [(10, 12)]), None),
            ])(),
        ]

        safe_execute_queries(queries)

        expected = [
            'BEGIN',
            EavInsertAttributeQuery(
                1,
                [
                    (1, 2),
                    (2, 3),
                    (3, 4),
                ]
            ),
            EavInsertAttributeWithOnDuplicateKeyUpdateQuery(
                1,
                [
                    (4, 5),
                    (5, 6),
                    (6, 7),
                ],
            ),
            EavInsertAttributeWithOnDuplicateKeyAppendQuery(
                1,
                [
                    (7, 8),
                    (8, 9),
                ],
            ),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(
                1,
                [
                    (4, (5, 6)),
                ],
            ),
            EavInsertAttributeWithOnDuplicateKeyIncrementQuery(
                1,
                [
                    (9, 11),
                    (10, 12),
                ],
            ),
            'COMMIT',
        ]
        self.db.assert_executed_queries_equal(
            expected,
            db='passportdbshard1',
        )

    def test_split_by_callback(self):
        callback = mock.Mock()
        qieries = [
            (EavInsertAttributeQuery(1, [(1, 2)]), None),
            (EavInsertAttributeQuery(1, [(2, 3)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(3, 4)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(4, 5)]), None),
            (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]), None),

            (EavInsertAttributeQuery(1, [(5, 6)]), callback),
            (EavInsertAttributeQuery(1, [(6, 7)]), None),
            (EavInsertAttributeQuery(1, [(8, 9)]), None),
            (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]), None),
        ]

        safe_execute_queries(qieries)

        expected = [
            EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(3, 4), (4, 5)]),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]),
            EavInsertAttributeQuery(1, [(1, 2), (2, 3), (5, 6)]),

            EavInsertAttributeQuery(1, [(6, 7), (8, 9)]),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]),
        ]
        self.db.assert_executed_queries_equal(
            expected,
            db='passportdbshard1',
        )

    def test_split_by_transaction_boundary(self):
        qieries = [
            (EavInsertAttributeQuery(1, [(1, 2)]), None),
            (EavInsertAttributeQuery(1, [(2, 3)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(3, 4)]), None),
            (EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(4, 5)]), None),
            (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]), None),

            DbTransaction(
                lambda: [
                    (EavInsertAttributeQuery(1, [(5, 6)]), None),
                    (EavInsertAttributeQuery(1, [(6, 7)]), None),
                    (EavInsertAttributeQuery(1, [(8, 9)]), None),
                    (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]), None),
                ],
            )(),

            (EavInsertAttributeQuery(1, [(10, 11)]), None),
            (EavInsertAttributeQuery(1, [(12, 13)]), None),
        ]

        safe_execute_queries(qieries)

        expected = [
            EavInsertAttributeQuery(1, [(1, 2), (2, 3)]),
            EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(3, 4), (4, 5)]),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]),

            'BEGIN',
            EavInsertAttributeQuery(1, [(5, 6), (6, 7), (8, 9)]),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]),
            'COMMIT',

            EavInsertAttributeQuery(1, [(10, 11), (12, 13)]),
        ]
        self.db.assert_executed_queries_equal(
            expected,
            db='passportdbshard1',
        )

    def test_save_order(self):
        queries = [
            (EavInsertAttributeQuery(1, [(1, 2)]), None),
            (EavInsertSuidQuery(1, 2, 3), None),
            (EavInsertAttributeQuery(1, [(3, 4)]), None),
            (EavInsertAliasQuery(1, [(2, 3, '2')]), None),
            (EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]), None),
        ]

        safe_execute_queries(queries)

        expected = [
            EavInsertAttributeQuery(1, [(1, 2), (3, 4)]),
            EavInsertSuidQuery(1, 2, 3),
            EavInsertAliasQuery(1, [(2, 3, '2')]),
            EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [(3, (4, 5))]),
        ]
        self.db.assert_executed_queries_equal(
            expected,
        )

    def test_not_joinable(self):
        queries = [
            GenericInsertQuery(reserved_logins_table, {'login': b'test1', 'free_ts': datetime.now()}),
            GenericInsertQuery(reserved_logins_table, {'login': b'test2', 'free_ts': datetime.now()}),
        ]

        safe_execute_queries(queries)

        self.db.assert_executed_queries_equal(
            queries,
        )

    def test_not_joinable_update_if_equals(self):
        queries = [
            (
                EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [('value', ('expected', 'new-value'))]),
                None,
            ),
            (
                EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [('value', ('old', 'new'))]),
                None,
            ),
        ]

        safe_execute_queries(queries)

        self.db.assert_executed_queries_equal(
            [
                EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [('value', ('expected', 'new-value'))]),
                EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(1, [('value', ('old', 'new'))]),
            ],
        )


class TestSafeExecuteSlaveOnlyDatabase(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB(db_config=TEST_SLAVE_CONFIG)
        self.db.start()

    def tearDown(self):
        self.db.stop()
        del self.db

    def test_works_with_selectable_query(self):
        safe_execute_queries([RemovedAliasesByUidQuery(1)])

        self.db.assert_executed_queries_equal(
            [
                RemovedAliasesByUidQuery(1),
            ],
        )

    def test_fails_with_non_selectable_query(self):
        with assert_raises(RuntimeError):
            safe_execute_queries([EavInsertAttributeQuery(1, [(1, 2)])])

    def test_fails_with_no_matching_engine_in_router(self):
        with assert_raises(RuntimeError):
            safe_execute_queries([RemovedAliasesByUidQuery(1)], with_low_timeout=True)
