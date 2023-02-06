# -*- coding: utf-8 -*-
import json

from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.exceptions import (
    YdbGenericError,
    YdbUnknownKeyColumnsError,
)
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.faker.ydb_keyvalue import FakeYdbKeyValue
from passport.backend.core.ydb.ydb import (
    YdbKeyValue,
    YdbProfile,
)


TEST_AUTH_TOKEN1 = 'token1'
TEST_DATABASE1 = '/ru/passport-data/prod/passport'
TEST_ENDPOINT1 = 'ydb-ru.yandex.net:2135'


@with_settings_hosts()
class TestFakeYdbKeyValue(PassportTestCase):
    def setUp(self):
        super(TestFakeYdbKeyValue, self).setUp()
        self.fake_ydb_key_value = FakeYdbKeyValue()
        self.__patches = [
            FakeYdb(),
            self.fake_ydb_key_value,
        ]
        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.fake_ydb_key_value
        super(TestFakeYdbKeyValue, self).tearDown()

    def build_ydb_client(self, table_name='table', key_columns=None, value_type='String'):
        if key_columns is None:
            key_columns = {'key1': 'String'}
        return YdbKeyValue(
            endpoint='endpoint',
            database='database',
            enabled=True,
            table_name=table_name,
            key_columns=key_columns,
            value_column='value',
            value_type=value_type,
        )

    def test_set_get_delete(self):
        ydb_client = self.build_ydb_client()
        ydb_client.set({'key1': 'foo'}, 'bar')
        result = ydb_client.get({'key1': 'foo'})
        self.assertEqual(list(result), ['bar'])
        ydb_client.delete({'key1': 'foo'})
        result = ydb_client.get({'key1': 'foo'})
        self.assertEqual(list(result), [])

    def test_different_tables(self):
        ydb_client1 = self.build_ydb_client(table_name='table1')
        ydb_client2 = self.build_ydb_client(table_name='table2')
        ydb_client1.set({'key1': 'foo'}, 'bar')
        result = ydb_client2.get({'key1': 'foo'})
        self.assertEqual(list(result), [])
        ydb_client2.delete({'key1': 'foo'})
        result = ydb_client1.get({'key1': 'foo'})
        self.assertEqual(list(result), ['bar'])

    def test_get_subkey(self):
        ydb_client = self.build_ydb_client(
            key_columns={
                'key1': 'String',
                'key2': 'String',
            },
        )
        ydb_client.set({'key1': 'foo', 'key2': 'bar'}, 'red')
        ydb_client.set({'key1': 'bar', 'key2': 'foo'}, 'green')
        ydb_client.set({'key1': 'foo', 'key2': 'spam'}, 'yellow')
        result = ydb_client.get({'key1': 'foo'})
        self.assertEqual(sorted(result), ['red', 'yellow'])

    def test_delete_subkey(self):
        ydb_client = self.build_ydb_client(
            key_columns={
                'key1': 'String',
                'key2': 'String',
            },
        )
        ydb_client.set({'key1': 'foo', 'key2': 'bar'}, 'red')
        ydb_client.set({'key1': 'bar', 'key2': 'foo'}, 'green')
        ydb_client.set({'key1': 'foo', 'key2': 'spam'}, 'yellow')
        ydb_client.delete({'key1': 'foo'})
        result = ydb_client.get({'key1': 'foo'})
        self.assertEqual(list(result), [])
        result = ydb_client.get({'key1': 'bar'})
        self.assertEqual(sorted(result), ['green'])

    def test_works_for_subclasses(self):
        ydb_client = YdbProfile()
        ydb_client.set(
            {
                'uid': 1,
                'inverted_event_timestamp': 2,
                'unique_id': 3,
                'updated_at': 4,
            },
            '"hello"',
        )
        result = ydb_client.get({'uid': 1})
        self.assertEqual(list(result), ['hello'])

    def test_side_effect(self):
        e = Exception('side_effect')
        self.fake_ydb_key_value.set_response_side_effect(e)
        ydb_client = self.build_ydb_client()

        with self.assertRaises(YdbGenericError) as assertion:
            ydb_client.set({'key1': 'foo'}, 'bar')
        self.assertIs(assertion.exception.args[1], e)

        with self.assertRaises(YdbGenericError) as assertion:
            ydb_client.get({'key1': 'foo'})
        self.assertIs(assertion.exception.args[1], e)

        with self.assertRaises(YdbGenericError) as assertion:
            ydb_client.delete({'key1': 'foo'})
        self.assertIs(assertion.exception.args[1], e)

    def test_get_raises_unknown_column(self):
        ydb_client = self.build_ydb_client()
        with self.assertRaises(YdbUnknownKeyColumnsError):
            ydb_client.get({'unknown_key': 'foo'})

    def test_delete_raises_unknown_column(self):
        ydb_client = self.build_ydb_client()
        with self.assertRaises(YdbUnknownKeyColumnsError):
            ydb_client.delete({'unknown_key': 'foo'})

    def test_type_postprocessing_works(self):
        ydb_client = self.build_ydb_client(value_type='Json')
        value = {'red': 'sad'}
        ydb_client.set({'key1': 'foo'}, json.dumps(value))
        result = ydb_client.get({'key1': 'foo'})
        self.assertEqual(list(result), [value])
