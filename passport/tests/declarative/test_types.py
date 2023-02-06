# -*- coding: utf-8 -*-

from functools import partial

from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.ydb.declarative.types import (
    Bool,
    Date,
    DateTime,
    Float,
    init_type,
    Int8,
    Int16,
    Int32,
    Int64,
    Integer,
    Json,
    pytype_to_data_type,
    String,
    Timestamp,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    Utf8,
)
from passport.backend.utils.time import unixtime_to_datetime
import six


TEST_BINARY = 'some_STRING12345'.encode('utf8')
TEST_BOOL = True
TEST_DATE = unixtime_to_datetime(1234567890).date()
TEST_DATETIME = unixtime_to_datetime(1234567890)
TEST_DAYS = (TEST_DATE - unixtime_to_datetime(0).date()).days
TEST_DICT = {'a': 1, 'b': 2}
TEST_DICT_STR = '{"a": 1, "b": 2}'
TEST_FLOAT = 1.1234
TEST_FLOAT_TIMESTAMP = 1234567890.123456
TEST_INT = 1
TEST_LIST = [1, 2, 3]
TEST_LIST_STR = '[1, 2, 3]'
TEST_TIMESTAMP = 1234567890
TEST_UNICODE = u'некая_СТРОКА12345'


class TestTypes(PassportTestCase):

    def test_bool(self):
        data_type = Bool()

        self.assertEqual(data_type.get_type_annotation(), 'Bool')
        self.assertEqual(data_type.to_pyval(TEST_INT), TEST_BOOL)
        self.assertEqual(data_type.from_pyval(TEST_INT), TEST_BOOL)

    def test_int(self):
        data_type = Integer(64, False)

        self.assertEqual(data_type.get_type_annotation(), 'Uint64')
        self.assertEqual(data_type.size, 64)
        self.assertEqual(data_type.signed, False)
        self.assertEqual(data_type.to_pyval(TEST_INT), TEST_INT)
        self.assertEqual(data_type.from_pyval(TEST_INT), TEST_INT)
        if six.PY2:
            t_long = six.integer_types[0]
            self.assertEqual(data_type.from_pyval(t_long(TEST_INT)), t_long(TEST_INT))
        self.assertEqual(data_type.from_pyval(TEST_FLOAT), TEST_INT)

        with self.assertRaises(ValueError):
            data_type.from_pyval('aa')

    def test_int_aliases(self):
        def assert_int(data_type, size, signed):
            self.assertEqual(data_type.size, size)
            self.assertEqual(data_type.signed, signed)

        assert_int(Int8(), 8, True)
        assert_int(Int16(), 16, True)
        assert_int(Int32(), 32, True)
        assert_int(Int64(), 64, True)
        assert_int(Uint8(), 8, False)
        assert_int(Uint16(), 16, False)
        assert_int(Uint32(), 32, False)
        assert_int(Uint64(), 64, False)

    def test_datetime(self):
        data_type = DateTime()

        self.assertEqual(data_type.get_type_annotation(), 'Datetime')
        self.assertEqual(data_type.to_pyval(TEST_TIMESTAMP), TEST_DATETIME)
        self.assertEqual(data_type.from_pyval(1), 1)
        self.assertEqual(data_type.from_pyval(TEST_DATETIME), TEST_TIMESTAMP)
        self.assertEqual(data_type.from_pyval(TEST_TIMESTAMP), TEST_TIMESTAMP)
        self.assertEqual(data_type.from_pyval(TEST_FLOAT_TIMESTAMP), TEST_TIMESTAMP)

        with self.assertRaises(TypeError):
            data_type.from_pyval('aa')

    def test_float(self):
        data_type = Float()

        self.assertEqual(data_type.get_type_annotation(), 'Float')
        self.assertEqual(data_type.to_pyval(TEST_FLOAT), TEST_FLOAT)
        self.assertEqual(data_type.from_pyval(TEST_FLOAT), TEST_FLOAT)
        self.assertEqual(data_type.from_pyval(TEST_INT), 1.0)

        with self.assertRaises(ValueError):
            data_type.from_pyval('aa')

    def test_string(self):
        data_type = String()

        self.assertEqual(data_type.get_type_annotation(), 'String')
        self.assertTrue(data_type.to_pyval(TEST_BINARY) == TEST_BINARY)
        self.assertTrue(data_type.from_pyval(TEST_BINARY) == TEST_BINARY)
        self.assertTrue(data_type.from_pyval(TEST_UNICODE) == TEST_UNICODE.encode('utf8'))
        self.assertTrue(data_type.from_pyval(TEST_INT) == '1'.encode())

    def test_utf8(self):
        data_type = Utf8()

        self.assertEqual(data_type.get_type_annotation(), 'Utf8')
        self.assertTrue(data_type.to_pyval(TEST_UNICODE) == TEST_UNICODE)
        self.assertTrue(data_type.from_pyval(TEST_BINARY) == TEST_BINARY.decode('utf8'))
        self.assertTrue(data_type.from_pyval(TEST_UNICODE) == TEST_UNICODE)
        self.assertTrue(data_type.from_pyval(TEST_INT) == u'1')

    def test_date(self):
        data_type = Date()

        self.assertEqual(data_type.get_type_annotation(), 'Date')
        self.assertEqual(data_type.to_pyval(TEST_DAYS), TEST_DATE)
        self.assertEqual(data_type.from_pyval(TEST_DAYS), TEST_DAYS)
        self.assertEqual(data_type.from_pyval(TEST_DATE), TEST_DAYS)
        self.assertEqual(data_type.from_pyval(TEST_DATETIME), TEST_DAYS)

        with self.assertRaises(TypeError):
            data_type.from_pyval(1.0)

    def test_timestamp(self):
        data_type = Timestamp()

        self.assertEqual(data_type.get_type_annotation(), 'Timestamp')
        self.assertEqual(data_type.to_pyval(TEST_TIMESTAMP*1000000), TEST_TIMESTAMP)
        self.assertEqual(data_type.from_pyval(TEST_TIMESTAMP), TEST_TIMESTAMP*1000000)
        self.assertEqual(data_type.from_pyval(TEST_FLOAT_TIMESTAMP), int(TEST_FLOAT_TIMESTAMP*1000000))
        self.assertEqual(data_type.from_pyval(TEST_DATETIME), TEST_TIMESTAMP*1000000)

        with self.assertRaises(TypeError):
            data_type.from_pyval('aa')

    def test_timestamp_as_datetime(self):
        data_type = Timestamp(as_float=False)

        self.assertEqual(data_type.to_pyval(TEST_TIMESTAMP*1000000), TEST_DATETIME)

    def test_json(self):
        data_type = Json()

        self.assertEqual(data_type.get_type_annotation(), 'Json')
        self.assertEqual(data_type.to_pyval(TEST_DICT_STR), TEST_DICT)
        self.assertEqual(data_type.to_pyval(TEST_LIST_STR), TEST_LIST)
        self.assertEqual(data_type.from_pyval(TEST_DICT_STR), TEST_DICT_STR)
        self.assertEqual(data_type.from_pyval(TEST_DICT), TEST_DICT_STR)
        self.assertEqual(data_type.from_pyval(TEST_LIST), TEST_LIST_STR)

        with self.assertRaises(TypeError):
            data_type.from_pyval(TEST_DATETIME)

    def test_pytype_to_data_type(self):
        self.assertIsInstance(pytype_to_data_type(type(TEST_BOOL)), Bool)
        self.assertIsInstance(pytype_to_data_type(type(TEST_BINARY)), String)
        self.assertIsInstance(pytype_to_data_type(type(TEST_UNICODE)), Utf8)
        self.assertIsInstance(pytype_to_data_type(type(TEST_INT)), Integer)
        if six.PY2:
            t_long = six.integer_types[0]
            self.assertIsInstance(pytype_to_data_type(type(t_long(TEST_INT))), Integer)
        self.assertIsInstance(pytype_to_data_type(type(TEST_FLOAT)), Float)
        self.assertIsInstance(pytype_to_data_type(type(TEST_DATETIME)), DateTime)
        self.assertIsInstance(pytype_to_data_type(type(TEST_DATE)), Date)
        self.assertIsInstance(pytype_to_data_type(type(TEST_DICT)), Json)
        self.assertIsInstance(pytype_to_data_type(type(TEST_LIST)), Json)

        self.assertIsInstance(pytype_to_data_type(type(object())), Utf8)

    def test_init_type(self):
        self.assertIsInstance(init_type(String), String)
        self.assertIsInstance(init_type(partial(String)), String)
        data_type = String()
        self.assertIs(init_type(data_type), data_type)
        with self.assertRaises(TypeError):
            init_type('aa')
