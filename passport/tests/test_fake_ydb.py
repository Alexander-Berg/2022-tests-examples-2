# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.exceptions import YdbGenericError
from passport.backend.core.ydb.faker.stubs import (
    FakeResultSet,
    FakeYdbCommit,
)
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.ydb import (
    Ydb,
    YdbQuery,
)


TEST_AUTH_TOKEN1 = 'token1'
TEST_DATABASE1 = '/ru/passport-data/prod/passport'
TEST_ENDPOINT1 = 'ydb-ru.yandex.net:2135'


@with_settings_hosts()
class TestFakeYdb(PassportTestCase):
    def setUp(self):
        super(TestFakeYdb, self).setUp()
        self.fake_ydb = FakeYdb()
        self.fake_ydb.start()

        self.ydb = Ydb(
            endpoint=TEST_ENDPOINT1,
            database=TEST_DATABASE1,
            enabled=True,
            auth_token=TEST_AUTH_TOKEN1,
        )

    def tearDown(self):
        del self.ydb
        self.fake_ydb.stop()
        del self.fake_ydb
        super(TestFakeYdb, self).tearDown()

    def test_ydb_kikimr_is_fake(self):
        self.assertIs(self.ydb.driver, self.fake_ydb.driver)

    def test_executed_queries(self):
        def exec_tx_1(session):
            tx = session.transaction()
            tx.execute('foo')
            tx.execute('bar', dict(foo='bar'))

        def exec_tx_2(session):
            tx = session.transaction()
            tx.execute('foo', commit_tx=True)
            tx.execute('bar', dict(), False)

        self.ydb.session_call(exec_tx_1)
        self.ydb.session_call(exec_tx_2)

        self.assertEqual(
            self.fake_ydb.executed_queries(),
            [
                dict(query='foo', parameters=None, commit_tx=False),
                dict(query='bar', parameters=dict(foo='bar'), commit_tx=False),
                dict(query='foo', parameters=None, commit_tx=True),
                dict(query='bar', parameters=dict(), commit_tx=False),
            ],
        )

    def test_assert_queries_executed(self):
        query1 = YdbQuery('foo', dict(bar='foo'))
        self.ydb.session_call(lambda session: session.transaction().execute(
            query1.get_raw_statement(),
            query1.get_parameters(),
            commit_tx=True,
        ))

        self.fake_ydb.assert_queries_executed(
            [
                YdbQuery('foo', dict(bar='foo')),
                FakeYdbCommit,
            ],
        )

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_queries_executed(
                [
                    YdbQuery('foo', dict(bar='hello')),
                    FakeYdbCommit,
                ],
            )

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_queries_executed(
                [
                    YdbQuery('bar', dict(bar='foo')),
                    FakeYdbCommit,
                ],
            )

        query2 = YdbQuery('bar', dict(bar='hello', spam='yello'))
        self.ydb.session_call(lambda session: session.transaction().execute(
            query1.get_raw_statement(),
            query1.get_parameters(),
        ))
        self.ydb.session_call(lambda session: session.transaction().execute(
            query2.get_raw_statement(),
            query2.get_parameters(),
            True,
        ))

        self.fake_ydb.assert_queries_executed(
            [
                query1,
                FakeYdbCommit,
                query1,
                query2,
                FakeYdbCommit,
            ],
        )

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_queries_executed([])

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_queries_executed(
                [
                    query1,
                    FakeYdbCommit,
                ],
            )

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_queries_executed(
                [
                    query2,
                    FakeYdbCommit,
                ],
            )

    def test_assert_fake_query_equals(self):
        query = YdbQuery('foo', dict(bar='foo'))
        self.ydb.session_call(lambda session: session.transaction().execute(
            query.get_raw_statement(),
            query.get_parameters(),
        ))
        fake_query = self.fake_ydb.executed_queries()[0]

        self.fake_ydb.assert_fake_query_equals(fake_query, query)

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_fake_query_equals(fake_query, query, True)

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_fake_query_equals(
                fake_query,
                query,
                YdbQuery('bar', dict(bar='foo')),
            )

        with self.assertRaises(AssertionError):
            self.fake_ydb.assert_fake_query_equals(
                fake_query,
                YdbQuery('foo', dict(bar='bar')),
            )

    def test_set_response_side_effect(self):
        response = []
        self.fake_ydb.set_execute_side_effect([
            response,
            Exception('side effect!'),
        ])

        self.ydb.session_call(lambda session: self.assertIs(
            session.transaction().execute('foo'),
            response,
        ))

        with self.assertRaises(YdbGenericError) as assertion:
            self.ydb.session_call(lambda session: session.transaction().execute('foo'))

        self.assertEqual(str(assertion.exception), str(YdbGenericError('side effect!', Exception('side effect!'))))

    def test_set_response_value(self):
        def asserts(session):
            tx = session.transaction()
            self.assertIs(tx.execute('foo'), response)
            self.assertIs(tx.execute('foo'), response)

        response = []
        self.fake_ydb.set_execute_return_value(response)

        self.ydb.session_call(asserts)

    def test_no_results_response(self):
        response = []
        self.fake_ydb.set_execute_side_effect([response])

        self.ydb.session_call(lambda session: self.assertEqual(
            len(session.transaction().execute('foo')),
            0,
        ))

    def test_single_empty_result_response(self):
        actual_response = [FakeResultSet([])]
        self.fake_ydb.set_execute_side_effect([actual_response])
        response = self.ydb.session_call(lambda s: s.transaction().execute('foo'))

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0].rows, list())

    def test_single_not_empty_result_response(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [
                    FakeResultSet(
                        [
                            {'x': 1},
                            {'x': 2},
                        ],
                    ),
                ],
            ],
        )

        response = self.ydb.session_call(lambda s: s.transaction().execute('foo'))
        self.assertEqual(len(response), 1)
        self.assertEqual(len(response[0].rows), 2)
        self.assertEqual(response[0].rows[0].x, 1)
        self.assertEqual(response[0].rows[1].x, 2)

    def test_many_results_response(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [
                    FakeResultSet(
                        [
                            {'x': 1},
                            {'x': 2},
                        ],
                    ),
                    FakeResultSet(
                        [
                            {'y': 3},
                        ],
                    ),
                ],
            ],
        )

        response = self.ydb.session_call(lambda s: s.transaction().execute('foo'))

        self.assertEqual(len(response), 2)
        rows = response[0].rows
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].x, 1)
        self.assertEqual(rows[1].x, 2)
        rows = response[1].rows
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].y, 3)
