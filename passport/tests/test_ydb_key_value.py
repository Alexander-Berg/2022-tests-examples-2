# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.exceptions import (
    YdbGenericError,
    YdbInvalidResponseError,
    YdbMissingKeyColumnsError,
    YdbTemporaryError,
    YdbUnknownKeyColumnsError,
)
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.ydb import YdbKeyValue
import passport.backend.core.ydb_client as ydb


TEST_YDB_ENDPOINT1 = 'ydb-magic.yandex.net:2135'
TEST_YDB_DATABASE1 = '/ru-prestable/passport-data/prestable/passport-users'


@with_settings_hosts(
    YDB_ENDPOINT=TEST_YDB_ENDPOINT1,
    YDB_DATABASE=TEST_YDB_DATABASE1,
    YDB_RETRIES=5,
)
class TestYdbKeyValue(PassportTestCase):
    def setUp(self):
        self.fake_ydb = FakeYdb()
        self.fake_ydb.start()
        self.ydb_client = YdbKeyValue(
            endpoint=settings.YDB_ENDPOINT,
            database=settings.YDB_DATABASE,
            enabled=True,
            table_name='test_table',
            key_columns={'key1': 'String', 'key2': 'Uint64'},
            value_column='value',
            retries=settings.YDB_RETRIES,
        )

    def tearDown(self):
        self.fake_ydb.stop()
        del self.fake_ydb

    def test_ok(self):
        self.ydb_client.set({'key1': 'ololo', 'key2': 1}, '{"k": "v"}')
        eq_(
            {
                'query': (
                    'declare $key1 as String;\n'
                    'declare $key2 as Uint64;\n'
                    'declare $value as Json;\n'
                    'upsert into [test_table] (key1, key2, value)\n'
                    'values ($key1, $key2, $value);\n'
                ),
                'parameters': {
                    '$key1': 'ololo',
                    '$key2': 1,
                    '$value': '{"k": "v"}',
                },
                'commit_tx': True,
            },
            self.fake_ydb.executed_queries()[-1],
        )

    def test_get_string(self):
        ydb_client = YdbKeyValue(
            endpoint=TEST_YDB_ENDPOINT1,
            database='',
            enabled=True,
            table_name='test_table',
            key_columns={'key1': 'String', 'key2': 'Uint64'},
            value_column='value',
            value_type='String',
        )
        self.fake_ydb.set_execute_return_value([FakeResultSet([{'value': 'kek'}])])
        eq_(
            ydb_client.first({'key1': 'ololo'}),
            'kek',
        )

    def test_get_int(self):
        ydb_client = YdbKeyValue(
            endpoint=TEST_YDB_ENDPOINT1,
            database='',
            enabled=True,
            table_name='test_table',
            key_columns={'key1': 'String', 'key2': 'Uint64'},
            value_column='value',
            value_type='Uint32',
        )
        self.fake_ydb.set_execute_return_value([FakeResultSet([{'value': '1'}])])
        eq_(
            ydb_client.first({'key1': 'ololo'}),
            1,
        )

    def test_get_float(self):
        ydb_client = YdbKeyValue(
            endpoint=TEST_YDB_ENDPOINT1,
            database='',
            enabled=True,
            table_name='test_table',
            key_columns={'key1': 'String', 'key2': 'Uint64'},
            value_column='value',
            value_type='Float',
        )
        self.fake_ydb.set_execute_return_value([FakeResultSet([{'value': 1.0}])])
        eq_(
            ydb_client.first({'key1': 'ololo'}),
            1.0,
        )

    def test_get_ok(self):
        self.fake_ydb.set_execute_return_value([FakeResultSet([{'value': '{"k": "v"}'}])])
        r = self.ydb_client.get({'key1': 'ololo', 'key2': 1})
        eq_(
            {
                'query': (
                    'declare $key1 as String;\n'
                    'declare $key2 as Uint64;\n'
                    'select value from [test_table] where key1 = $key1 and key2 = $key2;\n'
                ),
                'parameters': {
                    '$key1': 'ololo',
                    '$key2': 1,
                },
                'commit_tx': True,
            },
            self.fake_ydb.executed_queries()[-1],
        )
        eq_(list(r), [{"k": "v"}])
        r = self.ydb_client.first({'key1': 'ololo', 'key2': 1})
        eq_(r, {"k": "v"})

    def test_first_with_default(self):
        self.fake_ydb.set_execute_return_value([])
        r = self.ydb_client.first({'key1': '0', 'key2': 0}, {})
        eq_(r, {})

    @raises(YdbTemporaryError)
    def test_connection_error(self):
        self.fake_ydb.set_execute_side_effect(ydb.ConnectionError('ConnectionError'))
        self.ydb_client.get({'key1': 'ololo', 'key2': 1})

    @raises(YdbTemporaryError)
    def test_deadline_exceed(self):
        self.fake_ydb.set_execute_side_effect(ydb.DeadlineExceed('DeadlineExceed'))
        self.ydb_client.get({'key1': 'ololo', 'key2': 1})

    @raises(YdbGenericError)
    def test_generic_error(self):
        self.fake_ydb.set_execute_side_effect(ydb.Error('Error'))
        self.ydb_client.get({'key1': 'ololo', 'key2': 1})

    @raises(YdbMissingKeyColumnsError)
    def test_missing_columns_error(self):
        self.ydb_client.set({'key1': 'ololo'}, '{}')

    @raises(YdbUnknownKeyColumnsError)
    def test_unknown_columns_error(self):
        self.ydb_client.get({'unknown': 'ololo'})

    @raises(YdbInvalidResponseError)
    def test_invalid_response_error(self):
        self.fake_ydb.set_execute_return_value([FakeResultSet([{'value': 'aasdad'}])])
        self.ydb_client.first({'key1': 'ololo', 'key2': 1})

    def test_delete(self):
        self.ydb_client.delete({'key1': 'ololo', 'key2': 1})
        eq_(
            {
                'query': (
                    'declare $key1 as String;\n'
                    'declare $key2 as Uint64;\n'
                    'delete from [test_table] where key1 = $key1 and key2 = $key2;\n'
                ),
                'parameters': {
                    '$key1': 'ololo',
                    '$key2': 1,
                },
                'commit_tx': True,
            },
            self.fake_ydb.executed_queries()[-1],
        )
