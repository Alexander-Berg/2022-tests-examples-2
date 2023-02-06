# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.dbmanager.manager import (
    DBError,
    get_dbm,
)
from passport.backend.core.dbmanager.transaction_manager import (
    full_transaction,
    get_transaction_manager,
    TransactionAdapter,
    TransactionManager,
)
from passport.backend.core.differ import diff
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.faker.account import default_account
from passport.backend.core.processor import run_eav
from passport.backend.core.serializers.eav.query import (
    EavInsertAliasQuery,
    EavInsertAttributeWithOnDuplicateKeyUpdateQuery,
    EavInsertExtendedAttributeWithOnDuplicateKeyQuery,
    EavInsertPhoneBindingCreatedQuery,
    EavPhoneIdIncrementQuery,
    EavUidIncrementQuery,
)
from passport.backend.utils.time import (
    unixtime_to_datetime,
    zero_datetime,
)
from sqlalchemy.exc import DatabaseError


TEST_ATTRIBUTE_QUERY = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(28, 'lastname')])
TEST_EXTENDED_ATTRIBUTE_QUERY = EavInsertExtendedAttributeWithOnDuplicateKeyQuery(
    1,
    [
        {
            'entity_type': 1,
            'entity_id': 1,
            'type': 1,
            'value': '79991231231',
        },
        {
            'entity_type': 1,
            'entity_id': 1,
            'type': 2,
            'value': 1234,
        },
    ],
)
TEST_BINDING_QUERY = EavInsertPhoneBindingCreatedQuery(
    uid=1,
    number=79991231231,
    phone_id=1,
    bound=zero_datetime,
    flags=0,
)


class SpecialException(Exception):
    pass


class TestTransactionAdapter(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()

    def tearDown(self):
        self.db.stop()
        del self.db

    def test_begin_ok(self):
        engine = get_dbm('passportdbcentral').get_engine()

        trx_adapter = TransactionAdapter()
        trx_adapter.begin(engine)

        ok_(trx_adapter.connection)
        ok_(trx_adapter.is_started)
        ok_(trx_adapter.transaction)

    def test_connection_closed_on_begin_failure(self):
        engine = get_dbm('passportdbcentral').get_engine()
        conn_mock = mock.Mock()
        conn_mock.begin.side_effect = DatabaseError('BEGIN', None, None)
        with mock.patch.object(engine, 'connect', mock.Mock(return_value=conn_mock)):
            trx_adapter = TransactionAdapter()
            with assert_raises(DatabaseError):
                trx_adapter.begin(engine)

            ok_(engine.connect.called)
            ok_(conn_mock.begin.called)
            ok_(conn_mock.close.called)
            ok_(not trx_adapter.is_started)

    def test_commit_ignored_when_transaction_not_started(self):
        trx_adapter = TransactionAdapter()
        trx_adapter.commit_and_close()

        assert_is_none(trx_adapter.transaction)
        assert_is_none(trx_adapter.connection)

    def test_commit_ok(self):
        engine = get_dbm('passportdbcentral').get_engine()
        trx_adapter = TransactionAdapter()
        trx_adapter.begin(engine)

        trx_adapter.transaction = mock.Mock(wraps=trx_adapter.transaction)
        conn_mock = mock.Mock(wraps=trx_adapter.connection)
        trx_adapter.connection = conn_mock

        trx_adapter.commit_and_close()

        ok_(trx_adapter.transaction.commit.called)
        ok_(conn_mock.close.called)
        ok_(not trx_adapter.is_started)

    def test_rollback_ok(self):
        engine = get_dbm('passportdbcentral').get_engine()
        trx_adapter = TransactionAdapter()
        trx_adapter.begin(engine)

        trx_adapter.transaction = mock.Mock(wraps=trx_adapter.transaction)
        conn_mock = mock.Mock(wraps=trx_adapter.connection)
        trx_adapter.connection = conn_mock

        trx_adapter.rollback_and_close()

        ok_(trx_adapter.transaction.rollback.called)
        ok_(conn_mock.close.called)
        ok_(not trx_adapter.is_started)

    def test_connection_closed_on_rollback_failure(self):
        engine = get_dbm('passportdbcentral').get_engine()
        trx_adapter = TransactionAdapter()
        trx_adapter.begin(engine)

        trx_adapter.transaction = mock.Mock()
        trx_adapter.transaction.rollback.side_effect = DatabaseError('ROLLBACK', None, None)
        conn_mock = mock.Mock(wraps=trx_adapter.connection)
        trx_adapter.connection = conn_mock

        with assert_raises(DatabaseError):
            trx_adapter.rollback_and_close()

        ok_(trx_adapter.transaction.rollback.called)
        ok_(conn_mock.close.called)
        ok_(not trx_adapter.is_started)


class TestTransactionManager(unittest.TestCase):

    def generate_fake_configs(self, count=1, start_id=1):
        return [
            {'database': 'db%d' % i}
            for i in range(start_id, start_id + count)
        ]

    def setUp(self):
        fake_configs = self.generate_fake_configs(2)
        self.fake_engine = mock.Mock(_configs=fake_configs)
        self.another_fake_engine = mock.Mock(_configs=fake_configs)

        self.patched_transaction = mock.patch(
            'passport.backend.core.dbmanager.transaction_manager.TransactionAdapter',
            side_effect=lambda: mock.Mock(),
        )
        self.patched_transaction.start()

        self.tm = get_transaction_manager()
        self.tm.start_full_transaction()

    def tearDown(self):
        self.patched_transaction.stop()
        LazyLoader.flush('TransactionManager')
        del self.fake_engine
        del self.another_fake_engine
        del self.patched_transaction
        del self.tm

    def test_started_flag_is_set(self):
        ok_(self.tm.started)
        eq_(self.tm._open_transactions, {})

    def test_unique_transactions(self):
        t1 = self.tm.enter_transaction(self.fake_engine)
        t2 = self.tm.enter_transaction(self.another_fake_engine)
        ok_(t1 is not t2)

    def test_same_transaction_for_same_engine(self):
        t1 = self.tm.enter_transaction(self.fake_engine)
        t2 = self.tm.enter_transaction(self.fake_engine)
        ok_(t1 is t2)

    def test_commit_all_transactions(self):
        t1 = self.tm.enter_transaction(self.fake_engine)
        t2 = self.tm.enter_transaction(self.another_fake_engine)
        self.tm.commit_all_transactions()

        eq_(t1.commit_and_close.call_count, 1)
        eq_(t2.commit_and_close.call_count, 1)
        eq_(self.tm._open_transactions, {})
        ok_(not self.tm.started)

    def test_rollback_all_transactions(self):
        t1 = self.tm.enter_transaction(self.fake_engine)
        t2 = self.tm.enter_transaction(self.another_fake_engine)
        self.tm.rollback_all_transactions()

        eq_(t1.rollback_and_close.call_count, 1)
        eq_(t2.rollback_and_close.call_count, 1)


class TestFullTransaction(unittest.TestCase):
    # FIXME: нужны тесты с походом в две базы сразу, с телефонами etc
    def setUp(self):
        self.db = FakeDB()
        self.db.start()

        tm = get_transaction_manager()
        tm.reset_state = lambda: None
        tm.commit_all_transactions = mock.Mock(wraps=tm.commit_all_transactions)
        tm.rollback_all_transactions = mock.Mock(wraps=tm.rollback_all_transactions)
        tm = mock.Mock(wraps=tm)

        # Патчим здесь, т.к. при импорте модуля мы уже успели зарегистрировать
        # нужный нам класс в реестре синглтонов.
        LazyLoader.register(
            'TransactionManager',
            mock.Mock(return_value=tm),
        )
        self.tm = get_transaction_manager()
        self.acc = default_account()

    def tearDown(self):
        self.db.stop()
        LazyLoader.register(
            'TransactionManager',
            TransactionManager,
        )
        LazyLoader.flush('TransactionManager')
        del self.db
        del self.tm

    def test_full_transaction_as_decorator__function_fails(self):
        """
        Если во время выполнения полной транзакции до нас дошло никем
        не обработанное исключение, то откатываем все задействованные транзакции.
        """
        def bad_function():
            run_eav(
                None,
                self.acc,
                diff(None, self.acc),
                retries=1,
            )
            raise ValueError('Much ado about nothing')

        with assert_raises(ValueError):
            full_transaction(bad_function)()

        eq_(self.tm.start_full_transaction.call_count, 1)

        eq_(self.tm.enter_transaction.call_count, 2)
        eq_(self.tm.rollback_all_transactions.call_count, 1)

        eq_(self.tm.commit_all_transactions.call_count, 0)

        self.db.assert_executed_queries_equal([
            'BEGIN',
            EavUidIncrementQuery(False),
            EavInsertAliasQuery(1, [(1, 'login', 1)]),
            'ROLLBACK',
        ])

    def test_full_transaction_as_decorator__function_does_not_fail(self):
        """
        Если во время выполнения полной транзакции не было выброшено никаких
        исключений, то мы должны успешно закоммитить все транзакции.
        """
        def good_function():
            run_eav(None, self.acc, diff(None, self.acc), retries=1)

        full_transaction(good_function)()

        eq_(self.tm.start_full_transaction.call_count, 1)
        eq_(self.tm.enter_transaction.call_count, 2)
        eq_(self.tm.commit_all_transactions.call_count, 1)

        eq_(self.tm.rollback_all_transactions.call_count, 0)

        self.db.assert_executed_queries_equal([
            'BEGIN',
            EavUidIncrementQuery(False),
            EavInsertAliasQuery(1, [(1, 'login', 1)]),
            'COMMIT',
        ])

    def test_full_transaction_as_context_manager__function_fails(self):
        """
        Если во время выполнения полной транзакции до нас дошло никем
        не обработанное исключение, то откатываем все задействованные транзакции.
        """
        def bad_function():
            run_eav(
                None,
                self.acc,
                diff(None, self.acc),
                retries=1,
            )
            raise ValueError('Much ado about nothing')

        with assert_raises(ValueError):
            with full_transaction():
                bad_function()

        eq_(self.tm.start_full_transaction.call_count, 1)

        eq_(self.tm.enter_transaction.call_count, 2)
        eq_(self.tm.rollback_all_transactions.call_count, 1)

        eq_(self.tm.commit_all_transactions.call_count, 0)

        self.db.assert_executed_queries_equal([
            'BEGIN',
            EavUidIncrementQuery(False),
            EavInsertAliasQuery(1, [(1, 'login', 1)]),
            'ROLLBACK',
        ])

    def test_full_transaction_as_context_manager__function_does_not_fail(self):
        """
        Если во время выполнения полной транзакции не было выброшено никаких
        исключений, то мы должны успешно закоммитить все транзакции.
        """
        def good_function():
            run_eav(None, self.acc, diff(None, self.acc), retries=1)

        with full_transaction():
            good_function()

        eq_(self.tm.start_full_transaction.call_count, 1)
        eq_(self.tm.enter_transaction.call_count, 2)
        eq_(self.tm.commit_all_transactions.call_count, 1)

        eq_(self.tm.rollback_all_transactions.call_count, 0)

        self.db.assert_executed_queries_equal([
            'BEGIN',
            EavUidIncrementQuery(False),
            EavInsertAliasQuery(1, [(1, 'login', 1)]),
            'COMMIT',
        ])

    def test_full_transaction_function_does_not_fail_commit_does(self):
        self.db.set_side_effect_for_transaction('passportdbcentral', commit=DatabaseError('', '', ''))

        def good_function():
            run_eav(None, self.acc, diff(None, self.acc), retries=1)

        with assert_raises(DBError):
            full_transaction(good_function)()

        eq_(self.tm.start_full_transaction.call_count, 1)
        eq_(self.tm.enter_transaction.call_count, 2)
        eq_(self.tm.commit_all_transactions._mock_wraps.call_count, 1)

        # В этой ситуации rollback_all_transactions вызывается
        # после commit_all_transactions
        eq_(self.tm.rollback_all_transactions._mock_wraps.call_count, 1)

        self.db.assert_executed_queries_equal([
            'BEGIN',
            EavUidIncrementQuery(False),
            EavInsertAliasQuery(1, [(1, 'login', 1)]),
            'COMMIT',
            'ROLLBACK',
        ])

    def test_with_multiple_databases_ok(self):

        def good_function():
            self.acc.uid = 1
            snapshot = self.acc.snapshot()

            self.acc.person.lastname = 'lastname'
            self.acc.phones.create(number='+79991231231', created=unixtime_to_datetime(1234))

            run_eav(snapshot, self.acc, diff(snapshot, self.acc), retries=1)

        full_transaction(good_function)()

        eq_(self.tm.start_full_transaction.call_count, 1)
        eq_(self.tm.enter_transaction.call_count, 3)
        eq_(self.tm.commit_all_transactions.call_count, 1)

        eq_(self.tm.rollback_all_transactions.call_count, 0)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                TEST_ATTRIBUTE_QUERY,
                TEST_EXTENDED_ATTRIBUTE_QUERY,
                TEST_BINDING_QUERY,
                'COMMIT',
            ],
            db='passportdbshard1',
        )
        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                EavPhoneIdIncrementQuery(False),
                'COMMIT',
            ],
            db='passportdbcentral',
        )

    def test_with_multiple_databases_second_transaction_fails_to_commit_first_cannot_rollback(self):

        self.db.set_side_effect_for_transaction('passportdbshard1', commit=DatabaseError('COMMIT', '', ''))

        def good_function():
            self.acc.uid = 1
            snapshot = self.acc.snapshot()

            self.acc.person.lastname = 'lastname'
            self.acc.phones.create(number='+79991231231', created=unixtime_to_datetime(1234))

            run_eav(snapshot, self.acc, diff(snapshot, self.acc), retries=1)

        with assert_raises(DBError):
            full_transaction(good_function)()

        eq_(self.tm.start_full_transaction.call_count, 1)
        eq_(self.tm.enter_transaction.call_count, 3)
        eq_(self.tm.commit_all_transactions.call_count, 1)
        eq_(self.tm.rollback_all_transactions.call_count, 1)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                EavPhoneIdIncrementQuery(False),
                'COMMIT',
                # Транзакцию уже закоммитили - ничего не поделаешь
            ],
            db='passportdbcentral',
        )
        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                TEST_ATTRIBUTE_QUERY,
                TEST_EXTENDED_ATTRIBUTE_QUERY,
                TEST_BINDING_QUERY,
                'COMMIT',
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )

    def test_with_multiple_databases_serializer_fails_rollback_fails_rollback_fail_postponed(self):

        # По порядку rollback этой базы будет вызван первым. Убедимся что при ошибке rollback будет также вызван
        # rollback второй базы. Кроме того, убедимся что исключение вызвавшее rollback не замаскировано.
        self.db.set_side_effect_for_transaction('passportdbcentral', rollback=DatabaseError('ROLLBACK', '', ''))

        def good_function():
            self.acc.uid = 1
            snapshot = self.acc.snapshot()

            self.acc.person.lastname = 'lastname'
            self.acc.phones.create(number='+79991231231', created=unixtime_to_datetime(1234))

            run_eav(snapshot, self.acc, diff(snapshot, self.acc), retries=1)

            raise SpecialException('Smth went wrong!')

        # исходное исключение не замаскировалось ошибкой rollback-а
        with assert_raises(SpecialException):
            full_transaction(good_function)()

        eq_(self.tm.start_full_transaction.call_count, 1)
        eq_(self.tm.enter_transaction.call_count, 3)
        eq_(self.tm.commit_all_transactions.call_count, 0)
        eq_(self.tm.rollback_all_transactions.call_count, 1)

        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                EavPhoneIdIncrementQuery(False),
                'ROLLBACK',
            ],
            db='passportdbcentral',
        )
        self.db.assert_executed_queries_equal(
            [
                'BEGIN',
                TEST_ATTRIBUTE_QUERY,
                TEST_EXTENDED_ATTRIBUTE_QUERY,
                TEST_BINDING_QUERY,
                'ROLLBACK',
            ],
            db='passportdbshard1',
        )
