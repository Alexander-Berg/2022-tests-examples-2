# -*- coding: utf-8 -*-

from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.exceptions import (
    YdbMultipleResultFound,
    YdbNoResultFound,
)
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.ydb import (
    Ydb,
    YdbQuery,
    YdbQueryExecutor,
)
import passport.backend.core.ydb_client as ydb


TEST_YDB_ENDPOINT1 = 'ydb-magic.yandex.net:2135'
TEST_YDB_DATABASE1 = '/ru-prestable/passport-data/prestable/passport-users'


@with_settings_hosts()
class TestYdbQueryExecutor(PassportTestCase):
    def setUp(self):
        super(TestYdbQueryExecutor, self).setUp()
        self.fake_ydb = FakeYdb()
        self.fake_ydb.start()

        self.query_executor = self.build_ydb_query_executor()

    def tearDown(self):
        del self.query_executor
        self.fake_ydb.stop()
        del self.fake_ydb
        super(TestYdbQueryExecutor, self).tearDown()

    def build_ydb_query_executor(self, retries=None):
        ydb = Ydb(
            endpoint=TEST_YDB_ENDPOINT1,
            database=TEST_YDB_DATABASE1,
            enabled=True,
        )
        kwargs = dict(
            ydb=ydb,
        )
        return YdbQueryExecutor(**kwargs)

    def build_ydb_query(self):
        return YdbQuery('hello', dict(foo='bar'))

    def assert_result_set_equals(self, actual, expected):
        actual = [a._asdict() for a in actual]
        self.assertEqual(actual, expected)

    def test_execute_queries_ok(self):
        self.fake_ydb.set_execute_return_value([])
        self.query_executor.execute_queries([YdbQuery('spam')])
        self.query_executor.execute_queries([YdbQuery('hello', {'foo': 'bar'})])

        self.assertEqual(
            self.fake_ydb.executed_queries(),
            [
                dict(query='spam', parameters=None, commit_tx=True),
                dict(query='hello', parameters={'foo': 'bar'}, commit_tx=True),
            ],
        )

    def test_execute_queries_no_result_sets(self):
        self.fake_ydb.set_execute_side_effect([[]])
        ydb_query = self.build_ydb_query()
        result_sets = self.query_executor.execute_queries([ydb_query])
        self.assertEqual(result_sets, list())

    def test_execute_queries_single_empty_result_set(self):
        self.fake_ydb.set_execute_side_effect([[FakeResultSet([])]])
        ydb_query = self.build_ydb_query()
        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(len(result_sets), 1)
        self.assert_result_set_equals(result_sets[0], list())

    def test_execute_queries_single_result_set(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    [
                        dict(foo='bar', bar='foo'),
                        dict(foo='foo', bar='bar'),
                    ],
                )],
            ],
        )
        ydb_query = self.build_ydb_query()
        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(len(result_sets), 1)
        self.assert_result_set_equals(
            result_sets[0],
            [
                dict(foo='bar', bar='foo'),
                dict(foo='foo', bar='bar'),
            ],
        )

    def test_execute_queries_many_result_sets(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [
                    FakeResultSet([dict(foo='bar', bar='foo')]),
                    FakeResultSet([dict(foo='foo', bar='bar')]),
                ],
            ],
        )
        ydb_query = self.build_ydb_query()

        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(len(result_sets), 2)
        self.assert_result_set_equals(result_sets[0], [dict(foo='bar', bar='foo')])
        self.assert_result_set_equals(result_sets[1], [dict(foo='foo', bar='bar')])

    def test_execute_queries_parses_result_sets(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet([dict(foo='bar', bar='foo')])],
            ],
        )

        class ParsingYdbQuery(YdbQuery):
            def parse_query_result(self, result):
                return result.foo + result.bar

        ydb_query = ParsingYdbQuery('hello')

        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(list(result_sets[0]), ['barfoo'])

    def test_default_transaction_mode(self):
        self.fake_ydb.set_execute_return_value([])
        ydb_query = self.build_ydb_query()
        self.query_executor.execute_queries([ydb_query])

        self.fake_ydb._transaction.assert_called()
        call_args = self.fake_ydb._transaction.call_args_list[0]
        assert 'tx_mode' in call_args.kwargs
        self.assertIs(call_args.kwargs['tx_mode'], None)

    def test_uses_transaction_mode(self):
        self.fake_ydb.set_execute_return_value([])
        ydb_query = self.build_ydb_query()
        self.query_executor.execute_queries([ydb_query], tx_mode=ydb.StaleReadOnly())

        self.fake_ydb._transaction.assert_called()
        call_args = self.fake_ydb._transaction.call_args_list[0]
        assert 'tx_mode' in call_args.kwargs
        self.assertIs(type(call_args.kwargs['tx_mode']), ydb.StaleReadOnly)

    def test_get_one(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    [
                        dict(foo='bar', bar='foo'),
                    ],
                )],
            ],
        )

        ydb_query = self.build_ydb_query()

        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(len(result_sets), 1)
        self.assertEqual(
            result_sets[0].one()._asdict(),
            dict(foo='bar', bar='foo'),
        )

    def test_get_one_not_found(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet([])],
            ],
        )

        ydb_query = self.build_ydb_query()

        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(len(result_sets), 1)
        with self.assertRaises(YdbNoResultFound):
            result_sets[0].one()

    def test_get_one_multiple(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [
                    FakeResultSet(
                        [
                            dict(foo='bar', bar='foo'),
                            dict(foo='bar', bar='foo'),
                        ],
                    ),
                ],
            ],
        )

        ydb_query = self.build_ydb_query()

        result_sets = self.query_executor.execute_queries([ydb_query])

        self.assertEqual(len(result_sets), 1)
        with self.assertRaises(YdbMultipleResultFound):
            result_sets[0].one()
