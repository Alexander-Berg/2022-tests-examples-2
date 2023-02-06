from datetime import datetime
from decimal import Decimal as py_Decimal, ROUND_HALF_EVEN, ROUND_UP
from unittest import TestCase

import pytest
from bson.objectid import ObjectId
from qb2.api.v1 import typing as qb2_tp
from yt.wrapper import YtHttpResponseError

import dmp_suite.yt.operation as op
from dmp_suite.yt import resolve_meta
from dmp_suite.yt.paths import TAXI_DWH_BUFFER_PREFIX, TAXI_DWH_ROTATION_PREFIX
from dmp_suite.yt.table import *
from dmp_suite.yt.table import _YTFieldParameter
from test_dmp_suite.domain.common import test_domain
from test_dmp_suite.yt.utils import random_yt_table


def fake_prefix_manager(service):
    return '//service/'


def test_type_values():
    # |---Simple types---|
    assert Int.data_type == ValueType.INT_64.value
    assert UInt.data_type == ValueType.UINT_64.value
    assert Double.data_type == ValueType.DOUBLE.value
    assert String.data_type == ValueType.STR.value
    assert Any.data_type == ValueType.ANY.value
    assert Any.data_type_v3 == ValueType.YSON.value
    assert Boolean.data_type == ValueType.BOOLEAN.value
    assert Boolean.data_type_v3 == ValueType.BOOL.value
    assert Bool is Boolean
    # Old date types
    assert Date.data_type == ValueType.STR.value
    assert Datetime.data_type == ValueType.STR.value
    assert DatetimeMicroseconds.data_type == ValueType.STR.value
    # Native date types
    assert NativeDate.data_type == ValueType.DATE.value
    assert NativeDatetime.data_type == ValueType.DATETIME.value
    assert NativeTimestamp.data_type == ValueType.TIMESTAMP.value
    assert NativeInterval.data_type == ValueType.INTERVAL.value


@pytest.mark.parametrize(
    'cls,cls_params',
    (
        (Optional, (Int,)),
        (List, (Int,)),
        (Struct, ({'a': Int, 'b': String, 'c': Boolean},)),
        (Tuple, ((Int, Int, UInt),)),
        (Dict, (Int, String)),
        (VariantNamed, ({'a': Int, 'b': Boolean},)),
        (VariantUnnamed, ((Int, Boolean),)),
        (Tagged, ("TAG", Int)),
    )
)
def test_complex_raises(cls, cls_params):
    instance = cls(*cls_params)
    # assert data_type can't be accessed
    with pytest.raises(AttributeError):
        _ = cls.data_type
    with pytest.raises(AttributeError):
        _ = instance.data_type
    # assert required can't be accessed
    with pytest.raises(AttributeError):
        _ = instance.required
    with pytest.raises(AttributeError):
        instance.required = True
    with pytest.raises(AttributeError):
        _ = cls(*cls_params, required=True)
    with pytest.raises(AttributeError):
        _ = cls(*cls_params, required=False)

    # RuntimeError бросается механизмом
    # вызова __set_name__, внутри питона
    with pytest.raises(RuntimeError):
        class _DummyTable(YTTable):
            __dynamic__ = True
            field = instance


class TestTable(TestCase):
    def test_to_string(self):
        class WrongClass(object):
            """ Wrong means that class doesn't override object.__str__ """
            a = 1

        self.assertRaises(TypeError, to_string, WrongClass())
        self.assertIsNone(to_string(None))

        actual = to_string(u'abc')
        expected = b'abc'
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, bytes))

        actual = to_string(1)
        expected = b'1'
        self.assertEqual(expected, actual)

        actual = to_string(1.1)
        expected = b'1.1'
        self.assertEqual(expected, actual)

        # Эта функция обязательно должна возвращать нормальный тип
        # а не future.types.newbytes.newbytes, иначе возможны
        # проблемы типа той что описана в тикете:
        # https://st.yandex-team.ru/TAXIDWH-4819
        actual = to_string(ObjectId('0' * 24))
        expected = b'000000000000000000000000'
        self.assertEqual(expected, actual)
        assert type(actual) is bytes

    def test_to_int(self):
        self.assertRaises(ValueError, to_int, 'asd')
        self.assertIsNone(to_int(None))
        self.assertIsNone(to_int(''))

        actual = to_int('1')
        expected = 1
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, int))

        actual = to_int(10)
        expected = 10
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, int))

        actual = to_int(10.1)
        expected = 10
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, int))

        actual = to_int(10.9)
        expected = 10
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, int))

        actual = to_int(py_Decimal(1010.123123))
        expected = 1010
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, int))

    def test_to_double(self):
        self.assertRaises(ValueError, to_double, 'asd')
        self.assertIsNone(to_double(None))
        self.assertIsNone(to_double(''))

        actual = to_double('1')
        expected = 1.0
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, float))

        actual = to_double('10.1')
        expected = 10.1
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, float))

        actual = to_double(10)
        expected = 10.0
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, float))

        actual = to_double(10.1)
        expected = 10.1
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, float))

        actual = to_double(10.9)
        expected = 10.9
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, float))

        actual = to_double(py_Decimal(1010.123123))
        expected = 1010.123123
        self.assertEqual(expected, actual)
        self.assertTrue(isinstance(actual, float))

    def test_to_boolean(self):
        self.assertTrue(to_boolean(True))
        self.assertTrue(to_boolean(1))
        self.assertTrue(to_boolean('True'))
        self.assertTrue(to_boolean('true'))
        self.assertTrue(to_boolean(b'True'))
        self.assertTrue(to_boolean(b'true'))
        self.assertTrue(to_boolean('1'))
        self.assertTrue(to_boolean('1'))

        self.assertFalse(to_boolean(False))
        self.assertFalse(to_boolean('asdasd'))
        self.assertFalse(to_boolean('0'))
        self.assertFalse(to_boolean(b'0'))
        self.assertFalse(to_boolean(0))

    def test_to_datetime(self):
        datetime_string = '2017-03-03 03:12:15.123123'
        self.assertEqual('2017-03-03 03:12:15', to_datetime(datetime_string))
        self.assertEqual('2017-03-03 03:12:15', to_datetime(datetime(2017, 3, 3, 3, 12, 15, 123123)))
        self.assertEqual(None, to_datetime(None))
        self.assertRaises(ValueError, to_datetime, 'asd')

    def test_to_date(self):
        datetime_string = '2017-03-03 03:12:15.123123'
        self.assertEqual('2017-03-03', to_date(datetime_string))
        self.assertEqual('2017-03-03', to_date(datetime(2017, 3, 3, 3, 12, 15, 123123)))
        self.assertEqual(None, to_date(None))
        self.assertRaises(ValueError, to_date, 'asd')

    def test_to_yson(self):
        self.assertIsNone(to_yson(None))
        value = dict(
            a=1,
            b=[datetime(2017, 1, 1), 2, 3],
            c=dict(
                e=datetime(2017, 1, 1),
                f=py_Decimal(2.0),
                s=['a', 'b'],
                t=('a', 'b')
            ),
            d=[dict(z=1), dict(x=datetime(2017, 1, 1))],
            v=dict(r=[1], t=[datetime(2017, 1, 1), datetime(2017, 2, 2)]),
            s=['a', 'b'],
            t={'a'},
        )
        actual = to_yson(value)
        expected = dict(
            a=1,
            b=['2017-01-01 00:00:00.000000', 2, 3],
            c=dict(
                e='2017-01-01 00:00:00.000000',
                f=2.0,
                s=['a', 'b'],
                t=['a', 'b']
            ),
            d=[dict(z=1), dict(x='2017-01-01 00:00:00.000000')],
            v=dict(r=[1],
                   t=['2017-01-01 00:00:00.000000',
                      '2017-02-02 00:00:00.000000']),
            s=['a', 'b'],
            t=['a']
        )
        self.assertEqual(expected, actual)

    def test_to_json(self):
        self.assertIsNone(to_json(None))

        value = dict(
            a=1,
            b='abc'
        )
        self.assertEqual('{"a": 1, "b": "abc"}', to_json(value))

        value = dict(
            a=1,
            b=datetime(2017, 3, 3)
        )
        self.assertRaises(Exception, to_json, value)

    def test_yt_field_attributes(self):
        field = String(name='abc', sort_key=True)
        self.assertEqual(field.attributes(), dict(
            name='abc',
            type='string',
            sort_order=ASC,
            required=False,
        ))

        field1 = Int(name='field1')
        self.assertIs(field1.qb2_type, qb2_tp.Optional[qb2_tp.Integer])
        self.assertEquals(field1.attributes(), dict(
            name='field1',
            type='int64',
            required=False,
        ))

        field2 = Int(name='field2', required=True)
        self.assertIs(field2.qb2_type, qb2_tp.Integer)
        self.assertEquals(field2.attributes(), dict(
            name='field2',
            type='int64',
            required=True,
        ))

        field3 = Boolean(name='field3')
        self.assertIs(field3.qb2_type, qb2_tp.Optional[qb2_tp.Bool])
        self.assertEquals(field3.attributes(), dict(
            name='field3',
            type='boolean',
            required=False,
        ))

        field4 = Boolean(name='field4', required=True)
        self.assertIs(field4.qb2_type, qb2_tp.Bool)
        self.assertEquals(field4.attributes(), dict(
            name='field4',
            type='boolean',
            required=True,
        ))

    def test_yt_field_invalid_attributes(self):
        self.assertRaises(
            AssertionError,
            lambda: Any(name='abc', required=True)
        )


def test_native_date_schema():
    assert NativeDate(name='test_name', required=False).attributes() \
           == {'name': 'test_name', 'required': False, 'type': ValueType.DATE.value}
    assert NativeDate(required=False).qb2_type == qb2_tp.Optional[qb2_tp.Integer]
    assert NativeDate(required=True).qb2_type == qb2_tp.Integer


def test_native_datetime__schema():
    assert NativeDatetime(name='test_name', required=False).attributes() \
           == {'name': 'test_name', 'required': False, 'type': ValueType.DATETIME.value}
    assert NativeDatetime(required=False).qb2_type == qb2_tp.Optional[qb2_tp.Integer]
    assert NativeDatetime(required=True).qb2_type == qb2_tp.Integer


def test_native_timestamp_schema():
    assert NativeTimestamp(name='test_name', required=False).attributes() \
           == {'name': 'test_name', 'required': False, 'type': ValueType.TIMESTAMP.value}
    assert NativeTimestamp(required=False).qb2_type == qb2_tp.Optional[qb2_tp.Integer]
    assert NativeTimestamp(required=True).qb2_type == qb2_tp.Integer


def test_native_interval_schema():
    assert NativeInterval(name='test_name', required=False).attributes() \
           == {'name': 'test_name', 'required': False, 'type': ValueType.INTERVAL.value}
    assert NativeInterval(required=False).qb2_type == qb2_tp.Optional[qb2_tp.Integer]
    assert NativeInterval(required=True).qb2_type == qb2_tp.Integer


def _assert_complex_case(
    case_full: YTField,
    case_getitem: _YTFieldParameter,
    expected_schema: dict,
    expected_qb2,
):
    assert isinstance(case_full, YTField)
    assert isinstance(case_getitem, _YTFieldParameter)
    assert case_full.data_type_v3 == expected_schema
    assert case_getitem.data_type_v3 == expected_schema
    assert case_full.qb2_type == expected_qb2
    assert case_getitem.qb2_type == expected_qb2


def _assert_same_argument(cls, args: tuple):
    # проверяем что __getitem__ принимает те же аргументы, что и __call__.
    assert cls(*args).data_type_v3 == cls[args].data_type_v3
    assert cls(*args).qb2_type == cls[args].qb2_type


def test_complex_parameter_raises():
    # проверяем, что бросаются исключения при поле в качестве
    # параметра (при конструировании параметра через __call__)

    with pytest.raises(TypeError):
        Optional(List(Int))

    with pytest.raises(TypeError):
        List(List(Int))

    with pytest.raises(TypeError):
        Dict(String, List(Int))


@pytest.mark.parametrize(
    'args,err_type',
    [
        ((0, 0), ValueError),
        ((36, 0), ValueError),
        ((5, 10), ValueError),
        (('10', 5), TypeError),
    ],
)
def test_decimal_raises(args, err_type):
    with pytest.raises(err_type):
        _ = Decimal(*args)
    with pytest.raises(err_type):
        _ = Decimal.construct_decimal_deserializer(*args)
    with pytest.raises(err_type):
        _ = Decimal.construct_decimal_serializer(*args)


@pytest.mark.parametrize(
    'args,value,err_type',
    [
        # too long (too many bytes) for a specified params
        ((5, 2), "abcde", ValueError),
        # unsupported type
        ((5, 2), ["i am in a list"], TypeError),
        # too short for a specified params
        ((12, 2), "abcd", ValueError),
    ],
)
def test_decimal_deserializer_raises(args, value, err_type):
    with pytest.raises(err_type):
        Decimal.construct_decimal_deserializer(*args)(value)


def test_decimal_schema():
    assert Decimal._get_byte_size(1) == 4
    assert Decimal._get_byte_size(9) == 4
    assert Decimal._get_byte_size(10) == 8
    assert Decimal._get_byte_size(18) == 8
    assert Decimal._get_byte_size(19) == 16
    assert Decimal._get_byte_size(35) == 16

    _assert_complex_case(
        Decimal(7, 4),
        Decimal[7, 4],
        {
            'type_name': ValueType.DECIMAL.value,
            'precision': 7,
            'scale': 4,
        },
        qb2_tp.YQLDecimal[7, 4],
    )
    _assert_complex_case(
        Decimal(5, 0),
        Decimal[5, 0],
        {
            'type_name': ValueType.DECIMAL.value,
            'precision': 5,
            'scale': 0,
        },
        qb2_tp.YQLDecimal[5, 0],
    )


def test_optional_schema():
    _assert_complex_case(
        Optional(item=Int),
        Optional[Int],
        {
            'type_name': ValueType.OPTIONAL.value,
            'item': ValueType.INT_64.value,
        },
        qb2_tp.Optional[qb2_tp.Integer],
    )
    _assert_complex_case(
        Optional(item=List[Int]),
        Optional[List[Int]],
        {
            'type_name': ValueType.OPTIONAL.value,
            'item': {
                'type_name': ValueType.LIST.value,
                'item': ValueType.INT_64.value,
            }
        },
        qb2_tp.Optional[qb2_tp.List[qb2_tp.Integer]],
    )
    _assert_complex_case(
        Optional(Optional[UInt]),
        Optional[Optional[UInt]],
        {
            'type_name': ValueType.OPTIONAL.value,
            'item': {
                'type_name': ValueType.OPTIONAL.value,
                'item': ValueType.UINT_64.value,
            }
        },
        qb2_tp.Optional[qb2_tp.Optional[qb2_tp.UnsignedInteger]],
    )


def test_required_behaviour():
    with pytest.raises(AttributeError):
        Optional(Int, required=True)
    with pytest.raises(AttributeError):
        List(Int, required=True)


def test_list_schema():
    _assert_complex_case(
        List(Int),
        List[Int],
        {
            'type_name': ValueType.LIST.value,
            'item': ValueType.INT_64.value,
        },
        qb2_tp.List[qb2_tp.Integer],
    )
    _assert_complex_case(
        List(List[List[Int]]),
        List[List[List[Int]]],
        {
            'type_name': ValueType.LIST.value,
            'item': {
                'type_name': ValueType.LIST.value,
                'item': {
                    'type_name': ValueType.LIST.value,
                    'item': ValueType.INT_64.value
                }
            }
        },
        qb2_tp.List[qb2_tp.List[qb2_tp.List[qb2_tp.Integer]]],
    )


def test_struct_schema():
    _assert_complex_case(
        Struct({'id': Int, 'value': String}),
        Struct['id': Int, 'value': String],
        {
            'type_name': ValueType.STRUCT.value,
            'members': [
                {'name': 'id', 'type': ValueType.INT_64.value},
                {'name': 'value', 'type': ValueType.STR.value}
            ]
        },
        qb2_tp.Struct['id': qb2_tp.Integer, 'value': qb2_tp.String],
    )
    _assert_same_argument(Struct, ({'one': Optional[Int], 'two': String},))


def test_tuple_schema():
    _assert_complex_case(
        Tuple((Int, Double)),
        Tuple[Int, Double],
        {
            'type_name': ValueType.TUPLE.value,
            'elements': [
                {'type': ValueType.INT_64.value},
                {'type': ValueType.DOUBLE.value}
            ]
        },
        qb2_tp.SizedTuple[qb2_tp.Integer, qb2_tp.Float],
    )
    assert Tuple[(Int, Double)].data_type_v3 == Tuple[Int, Double].data_type_v3


def test_dict_schema():
    _assert_complex_case(
        Dict(key=String, value=Any),
        Dict[String, Any],
        {
            'type_name': ValueType.DICT.value,
            'key': ValueType.STR.value,
            'value': ValueType.YSON.value
        },
        qb2_tp.Dict[qb2_tp.String, qb2_tp.Yson],
    )
    _assert_complex_case(
        Dict(key=String, value=Optional[Int]),
        Dict[String, Optional[Int]],
        {
            'type_name': ValueType.DICT.value,
            'key': ValueType.STR.value,
            'value': {
                'type_name': ValueType.OPTIONAL.value,
                'item': ValueType.INT_64.value
            }
        },
        qb2_tp.Dict[qb2_tp.String, qb2_tp.Optional[qb2_tp.Integer]],
    )


def test_variant_unnamed_schema():
    _assert_complex_case(
        VariantUnnamed((Optional[Int], String, Double)),
        VariantUnnamed[Optional[Int], String, Double],
        {
            'type_name': ValueType.VARIANT.value,
            'elements': [
                {
                    'type': {
                        'type_name': ValueType.OPTIONAL.value,
                        'item': ValueType.INT_64.value
                    }
                },
                {
                    'type': ValueType.STR.value
                },
                {
                    'type': ValueType.DOUBLE.value
                },
            ]
        },
        qb2_tp.Union[qb2_tp.SizedTuple[qb2_tp.Integer, qb2_tp.Optional[qb2_tp.Integer]],
                     qb2_tp.SizedTuple[qb2_tp.Integer, qb2_tp.String],
                     qb2_tp.SizedTuple[qb2_tp.Integer, qb2_tp.Float]],
    )
    assert VariantUnnamed[(Int, Double)].data_type_v3 == VariantUnnamed[Int, Double].data_type_v3


def test_variant_named_schema():
    _assert_complex_case(
        VariantNamed({'one': Optional[Int], 'two': String}),
        VariantNamed['one': Optional[Int], 'two': String],
        {
            'type_name': ValueType.VARIANT.value,
            'members': [
                {
                    'name': 'one',
                    'type': {
                        'type_name': ValueType.OPTIONAL.value,
                        'item': ValueType.INT_64.value
                    }
                },
                {
                    'name': 'two',
                    'type': ValueType.STR.value
                },
            ]
        },
        qb2_tp.Union[qb2_tp.SizedTuple[qb2_tp.String, qb2_tp.Optional[qb2_tp.Integer]],
                     qb2_tp.SizedTuple[qb2_tp.String, qb2_tp.String]],
    )
    _assert_same_argument(VariantNamed, ({'one': Optional[Int], 'two': String},))


def test_tagged_schema():
    _assert_complex_case(
        Tagged('RED', Int),
        Tagged['RED', Int],
        {
            'type_name': 'tagged',
            'tag': 'RED',
            'item': ValueType.INT_64.value
        },
        qb2_tp.Integer,
    )


def test_native_date_serializer():
    _serializer = NativeDate.serializer
    assert _serializer(None) is None
    assert _serializer(10) == 10
    assert _serializer('1970-01-01') == 0
    assert _serializer('1970-01-01T13:13:13Z') == 0
    assert _serializer('1970-01-01T13:13:13.123654Z') == 0

    assert _serializer('2105-12-31') == 49673 - 1
    assert _serializer('2105-12-31T23:59:59Z') == 49673 - 1
    assert _serializer('2021-08-26') == 18865
    assert _serializer(b'2021-08-26') == 18865
    assert _serializer('2021-08-27') == 18866
    assert _serializer('2021-08-30') == 18869
    assert _serializer('2021-08-27T10:12:30Z') == 18866
    assert _serializer('2021-08-27T10:12:30.123321Z') == 18866
    assert _serializer(datetime(year=2021, month=8, day=26)) == 18865
    assert _serializer(datetime(
        year=2021, month=8, day=26,
        hour=23, minute=59, second=59
    )) == 18865
    pytest.raises(TypeError, _serializer, [1, 2, 3])
    pytest.raises(TypeError, _serializer, (1, 2, 3))
    pytest.raises(TypeError, _serializer, 123.456)


def test_native_datetime_serializer():
    _serializer = NativeDatetime.serializer
    assert _serializer(None) is None
    assert _serializer(100) == 100
    assert _serializer('1970-01-01') == 0
    assert _serializer('1970-01-01T00:00:00Z') == 0
    assert _serializer('1970-01-01T00:00:00.123654Z') == 0

    assert _serializer('2105-12-31T23:59:59Z') == 49673 * 86400 - 1
    assert _serializer('2021-08-26T23:59:59Z') == 1630022399
    assert _serializer('2021-08-26T23:59:50Z') == 1630022390
    assert _serializer(b'2021-08-26T23:59:59Z') == 1630022399
    assert _serializer(datetime(year=1970, month=1, day=1)) == 0
    assert _serializer(datetime(
        year=1970, month=1, day=1,
        hour=0, minute=0, second=0
    )) == 0
    assert _serializer(datetime(
        year=2021, month=8, day=26,
        hour=23, minute=59, second=59
    )) == 1630022399
    pytest.raises(TypeError, _serializer, [1, 2, 3])
    pytest.raises(TypeError, _serializer, (1, 2, 3))
    pytest.raises(TypeError, _serializer, 123.456)


def test_native_timestamp_serializer():
    _serializer = NativeTimestamp.serializer
    assert _serializer(None) is None
    assert _serializer(1000) == 1000
    assert _serializer('1970-01-01') == 0
    assert _serializer('1970-01-01T00:00:00Z') == 0
    assert _serializer('1970-01-01T00:00:00.000000Z') == 0
    assert _serializer('2105-12-31T23:59:59.999999Z') == 49673 * 86400 * (10 ** 6) - 1

    assert _serializer('2021-08-26T20:50:30.999999Z') == 1630011030999999
    assert _serializer('2021-08-26T20:50:30.000000Z') == 1630011030000000
    assert _serializer('2021-08-26T20:50:30Z') == 1630011030000000
    assert _serializer('2021-08-26T20:50:30.000001Z') == 1630011030000001
    assert _serializer(b'2021-08-26T20:50:30.999999Z') == 1630011030999999
    assert _serializer(datetime(year=1970, month=1, day=1,
                                hour=0, minute=0, second=0,
                                microsecond=0)) == 0
    assert _serializer(datetime(year=2021, month=8, day=26,
                                hour=20, minute=50, second=30,
                                microsecond=999999)) == 1630011030999999
    pytest.raises(TypeError, _serializer, [1, 2, 3])
    pytest.raises(TypeError, _serializer, (1, 2, 3))
    pytest.raises(TypeError, _serializer, 123.456)


def test_native_interval_serializer():
    _serializer = NativeInterval.serializer
    assert _serializer(None) is None
    assert _serializer(-49673 * 86400 * (10 ** 6) + 1) == -49673 * 86400 * (10 ** 6) + 1
    assert _serializer(49673 * 86400 * (10 ** 6) - 1) == 49673 * 86400 * (10 ** 6) - 1

    assert _serializer(10000) == 10000
    assert _serializer(-10000) == -10000
    assert _serializer(timedelta(seconds=10, microseconds=100)) == 10 ** 7 + 100
    pytest.raises(TypeError, _serializer, [1, 2, 3])
    pytest.raises(TypeError, _serializer, (1, 2, 3))
    pytest.raises(ValueError, _serializer, "2012-02-03")


def test_rounder():
    _rounder = get_decimal_rounder(5, 0, ROUND_HALF_EVEN)
    assert _rounder('0.5') == py_Decimal('0')
    assert _rounder('0.55') == py_Decimal('1')
    assert _rounder('1.5') == py_Decimal('2')
    assert _rounder('-1.5') == py_Decimal('-2')
    pytest.raises(ValueError, _rounder, '100000')
    pytest.raises(ValueError, _rounder, '-100000')

    _rounder = get_decimal_rounder(5, 0, ROUND_UP)
    assert _rounder('0.5') == py_Decimal('1')
    assert _rounder('0.55') == py_Decimal('1')
    assert _rounder('1.2') == py_Decimal('2')
    assert _rounder('1.5') == py_Decimal('2')
    assert _rounder('-1.5') == py_Decimal('-2')
    assert _rounder('-1.2') == py_Decimal('-2')
    assert _rounder('2.5') == py_Decimal('3')

    _rounder = get_decimal_rounder(5, 0, ROUND_HALF_EVEN, True)
    assert _rounder('100000') == py_Decimal('inf')
    assert _rounder('-100000') == py_Decimal('-inf')

    _rounder = get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)
    assert _rounder("00.00055") == py_Decimal("0.001")
    assert _rounder("99.9999") == py_Decimal('inf')


def test_decimal_serializer():

    # Trivial tests with scale=0
    _field = Decimal(precision=9, scale=0)
    _serializer = _field.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x00\x01'
    assert _serializer(-1) == b'\x7f\xff\xff\xff'
    assert _serializer(2) == b'\x80\x00\x00\x02'
    assert _serializer(-2) == b'\x7f\xff\xff\xfe'
    assert _serializer(15) == b'\x80\x00\x00\x0f'
    assert _serializer(16 * 16) == b'\x80\x00\x01\x00'
    assert _serializer(16 ** 3 + 16 ** 2 + 16) == b'\x80\x00\x11\x10'
    assert _serializer("999999999") == b'\xbb\x9a\xc9\xff'
    assert _serializer("-999999999") == b'\x44\x65\x36\x01'
    assert _serializer('inf') == Decimal._plus_inf[4]
    assert _serializer('inf') == _serializer('+inf')
    assert _serializer('-inf') == Decimal._minus_inf[4]
    assert _serializer('nan') == Decimal._nan[4]
    pytest.raises(ValueError, _serializer, 1000000000)
    pytest.raises(ValueError, _serializer, -1000000000)
    pytest.raises(ValueError, _serializer, "0.1")
    pytest.raises(ValueError, _serializer, "-0.1")

    _field = Decimal(precision=18, scale=0)
    _serializer = _field.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00\x00\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x00\x00\x00\x00\x00\x01'
    assert _serializer(-1) == b'\x7f\xff\xff\xff\xff\xff\xff\xff'
    assert _serializer(2) == b'\x80\x00\x00\x00\x00\x00\x00\x02'
    assert _serializer(-2) == b'\x7f\xff\xff\xff\xff\xff\xff\xfe'
    assert _serializer(15) == b'\x80\x00\x00\x00\x00\x00\x00\x0f'
    assert _serializer(16 * 16) == b'\x80\x00\x00\x00\x00\x00\x01\x00'
    assert _serializer(16 ** 3 + 16 ** 2 + 16) == b'\x80\x00\x00\x00\x00\x00\x11\x10'
    assert _serializer("999999999999999999") == b'\x8d\xe0\xb6\xb3\xa7\x63\xff\xff'
    assert _serializer("-999999999999999999") == b'\x72\x1f\x49\x4c\x58\x9c\x00\x01'
    assert _serializer('inf') == Decimal._plus_inf[8]
    assert _serializer('inf') == _serializer('+inf')
    assert _serializer('-inf') == Decimal._minus_inf[8]
    assert _serializer('nan') == Decimal._nan[8]
    pytest.raises(ValueError, _serializer, 1000000000000000000)
    pytest.raises(ValueError, _serializer, -1000000000000000000)
    pytest.raises(ValueError, _serializer, "0.1")
    pytest.raises(ValueError, _serializer, "-0.1")

    _field = Decimal(precision=35, scale=0)
    _serializer = _field.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
    assert _serializer(-1) == b'\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    assert _serializer(2) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02'
    assert _serializer(-2) == b'\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe'
    assert _serializer(15) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f'
    assert _serializer(16 * 16) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00'
    assert _serializer(16 ** 3 + 16 ** 2 + 16) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\x10'
    assert _serializer("99999999999999999999999999999999999") ==\
           b"\x80\x13\x42\x61\x72\xc7\x4d\x82\x2b\x87\x8f\xe7\xff\xff\xff\xff"
    assert _serializer("-99999999999999999999999999999999999") ==\
           b"\x7f\xec\xbd\x9e\x8d\x38\xb2\x7d\xd4\x78\x70\x18\x00\x00\x00\x01"
    assert _serializer('inf') == Decimal._plus_inf[16]
    assert _serializer('inf') == _serializer('+inf')
    assert _serializer('-inf') == Decimal._minus_inf[16]
    assert _serializer('nan') == Decimal._nan[16]
    pytest.raises(ValueError, _serializer, 100000000000000000000000000000000000)
    pytest.raises(ValueError, _serializer, -100000000000000000000000000000000000)
    pytest.raises(ValueError, _serializer, "0.1")
    pytest.raises(ValueError, _serializer, "-0.1")

    # Some tests with scale
    _field = Decimal(precision=5, scale=3)
    _serializer = _field.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x03\xe8'
    assert _serializer(-1) == b'\x7f\xff\xfc\x18'
    assert _serializer("10.200") == b'\x80\x00\x27\xd8'

    _field = Decimal(precision=5, scale=4)
    _serializer = _field.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x27\x10'
    assert _serializer("0.0001") == b'\x80\x00\x00\x01'
    assert _serializer("3.1415") == b'\x80\x00\x7A\xB7'
    assert _serializer("-2.7182") == b'\x7F\xFF\x95\xD2'

    _field = Decimal(precision=12, scale=6)
    _serializer = _field.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00\x00\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x00\x00\x00\x0F\x42\x40'
    assert _serializer("000000.000001") == b'\x80\x00\x00\x00\x00\x00\x00\x01'

    # Parameter's serializer is same
    _parameter = Decimal[20, 6]
    _serializer = _parameter.serializer
    assert _serializer(0) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    assert _serializer(1) == b'\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x42\x40'

    # Tests with Rounding
    _parameter = Decimal[5, 0]
    _rounder = get_decimal_rounder(5, 0, ROUND_HALF_EVEN, False)
    _serializer = _parameter.serializer
    _combo = lambda v: _serializer(_rounder(v))
    assert _combo("-1.5") == _serializer(-2)
    assert _combo("-1.5") == b'\x7F\xFF\xFF\xFE'
    assert _combo('1.5') == _serializer(2)

    _field = Decimal(precision=5, scale=3)
    _rounder = get_decimal_rounder(5, 3, ROUND_HALF_EVEN, False)
    _serializer = _field.serializer
    _combo = lambda v: _serializer(_rounder(v))
    assert _combo("00.0005") == b'\x80\x00\x00\x00'
    assert _combo("00.0005") == _serializer(0)
    assert _combo("00.00055") == b'\x80\x00\x00\x01'
    assert _combo("00.00055") == _serializer("00.001")
    assert _combo("00.00055555") == b'\x80\x00\x00\x01'
    assert _combo("00.00055555") == _serializer("00.001")
    assert _combo("00.00049") == b'\x80\x00\x00\x00'
    assert _combo("00.00049") == _serializer(0)
    assert _combo("00.00149") == b'\x80\x00\x00\x01'
    assert _combo("00.00149") == _serializer("00.001")
    assert _combo("00.00059") == b'\x80\x00\x00\x01'
    assert _combo("00.00059") == _serializer("00.001")
    assert _combo("00.00159") == b'\x80\x00\x00\x02'
    assert _combo("00.00159") == _serializer("00.002")
    assert _combo("00.0009") == b'\x80\x00\x00\x01'
    assert _combo("00.0009") == _serializer("00.001")
    assert _combo("00.0015") == b'\x80\x00\x00\x02'
    assert _combo("00.0015") == _serializer("00.002")
    assert _combo("00.0019") == b'\x80\x00\x00\x02'
    assert _combo("00.0019") == _serializer("00.002")
    assert _combo("99.8999") == b'\x80\x01\x86\x3c'
    assert _combo("99.8999") == _serializer("99.900")
    assert _combo("00.00000001") == b'\x80\x00\x00\x00'
    assert _combo("00.00000001") == _serializer("00.000")
    pytest.raises(ValueError, _combo, "99.9999")

    _field = Decimal(5, 3)
    _rounder = get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)
    _serializer = _field.serializer
    _combo = lambda v: _serializer(_rounder(v))
    assert _combo("99.9999") == Decimal._plus_inf[4]
    assert _combo("123456") == Decimal._plus_inf[4]
    assert _combo("10.200567") == _serializer("10.201")


_common_decimal_data = [
    0, 1, -1, 2, -2, 15, 16 * 16,
    16 ** 3 + 16 ** 2 + 16,
]


@pytest.mark.parametrize(
    'precision,scale,data,is_optional',
    [
        (9, 0, _common_decimal_data + ["999999999", "-999999999"], False),
        (9, 3, _common_decimal_data, False),
        (9, 5, _common_decimal_data, False),
        (9, 5, _common_decimal_data + [None], True),
        (10, 3, _common_decimal_data, False),
        (15, 10, _common_decimal_data, False),
        (18, 10, _common_decimal_data, False),
        (18, 10, _common_decimal_data + [None], True),
        (18, 18, ["0.123", "0.1", "0.5678943210"], False),
        (19, 0, _common_decimal_data, False),
        (25, 10, _common_decimal_data, False),
        (25, 10, _common_decimal_data + [None], True),
        (35, 0, _common_decimal_data, False),
    ]
)
def test_decimal_deserializer(precision, scale, data, is_optional):

    if is_optional:
        _field = Optional(Decimal[precision, scale])
    else:
        _field = Decimal(precision=precision, scale=scale)

    _serializer = _field.serializer
    _deserializer = _field.deserializer

    for x in data:
        if x is None:
            assert _deserializer(_serializer(x)) is None
        else:
            assert _deserializer(_serializer(x)) == py_Decimal(x)

    _special_values = ['inf', '+inf', '-inf']

    for s in _special_values:
        assert _deserializer(_serializer(s)) == py_Decimal(s)

    assert _deserializer(_serializer('nan')).is_nan()


def test_optional_serializer():
    _field = Optional(Bool)
    _serializer = _field.serializer

    assert _serializer('1') is True
    assert _serializer('0') is False
    assert _serializer(None) is None


def test_list_serializer():
    _field = List(Optional[Int])
    _serializer = _field.serializer

    test_list_1 = [None, 10, '123', True, 200]
    test_list_2 = [None, 10, '123', True, 'euler']
    test_list_3 = [None, 10, {1, 2, 3}, True, 200]
    test_list_4 = [['a', 'b'], [], ['c'], ['d', 'e', 'f']]
    test_list_4_b = [[b'a', b'b'], [], [b'c'], [b'd', b'e', b'f']]

    assert _serializer(test_list_1) == [None, 10, 123, 1, 200]
    pytest.raises(ValueError, _serializer, test_list_2)
    pytest.raises(TypeError, _serializer, test_list_3)
    pytest.raises(TypeError, _serializer, test_list_4)

    _field = List(List[String])
    _serializer = _field.serializer
    pytest.raises(TypeError, _serializer, test_list_1)
    pytest.raises(TypeError, _serializer, test_list_2)
    pytest.raises(TypeError, _serializer, test_list_3)
    assert _serializer(test_list_4) == test_list_4_b

    _field = Optional(List[Int])
    _serializer = _field.serializer
    assert _serializer(['1', 12, b'123']) == [1, 12, 123]
    assert _serializer(None) is None
    # pytest.raises(TypeError, _serializer, [10, 100, None])


def test_struct_serializer():
    _field = Struct({'id': Optional[Int], 'value': String})
    _serializer = _field.serializer
    test_1 = {'id': 100, 'value': b'Alonsi'}
    test_2 = [('id', None), ('value', b'Alonso')]
    test_3 = {'id': ['fail'], 'value': 'type'}
    test_4 = {'id': [b'a', b'b', b'c'], 'value': 23.19}
    assert _serializer(test_1) == test_1
    assert _serializer(test_2) == dict(test_2)
    pytest.raises(TypeError, _serializer, test_3)
    pytest.raises(TypeError, _serializer, test_4)

    _field = Struct({'id': List[String], 'value': Double})
    _serializer = _field.serializer
    pytest.raises(TypeError, _serializer, test_1)
    pytest.raises(TypeError, _serializer, test_2)
    pytest.raises(ValueError, _serializer, test_3)
    assert _serializer(test_4) == test_4


def test_tuple_serializer():
    _field = Tuple((Int, String), sort_key=True)
    _serializer = _field.serializer
    test_1 = [1, 'abc']
    test_2 = (2, b'def')
    test_3 = (['fail'], 'type')
    test_4 = ([2020], (b'Jeronimo', 3.14))
    assert _serializer(test_1) == (1, b'abc')
    assert _serializer(test_2) == test_2
    pytest.raises(TypeError, _serializer, test_3)
    pytest.raises(TypeError, _serializer, test_4)

    _field = Tuple(
        (
            List[Int],
            Tuple[
                (String, Double)
            ]
        )
    )
    _serializer = _field.serializer
    pytest.raises(TypeError, _serializer, test_1)
    pytest.raises(TypeError, _serializer, test_2)
    pytest.raises(ValueError, _serializer, test_3)
    assert _serializer(test_4) == test_4


def test_dict_serializer():
    _field = Dict(key=String, value=Int)
    _serializer = _field.serializer
    true_case =[(b'a', 100), (b'b', 200)]
    assert _serializer([('a', 100), ('b', 200)]) == true_case
    assert _serializer((('a', 100), ('b', 200))) == true_case
    assert _serializer(true_case) == true_case
    pytest.raises(TypeError, _serializer, 115)

    _field = Dict(key=Int, value=Tuple[(Int, Bool)])
    _serializer = _field.serializer
    true_case = [(0, (20, False)), (1, (10, True))]
    assert _serializer({0: ('20', 0), 1: (10, True)}) == true_case
    assert _serializer(true_case) == true_case
    pytest.raises(TypeError, _serializer, None)


def test_variant_unnamed_serializer():
    _field = VariantUnnamed((Optional[Int], String, Double))
    _serializer = _field.serializer
    assert _serializer((0, 123)) == (0, 123)
    assert _serializer((1, 'abc')) == (1, b'abc')
    assert _serializer((2, 12.34)) == (2, 12.34)
    assert _serializer((2, None)) == (2, None)
    pytest.raises(ValueError, _serializer, [1, 2, 3])
    pytest.raises(TypeError, _serializer, (1, [1, 2, 3]))


def test_variant_named_serializer():
    _field = VariantNamed({'one': Optional[Int], 'two': String})
    _serializer = _field.serializer
    assert _serializer(('one', '100')) == ('one', 100)
    assert _serializer(('two', 'fer')) == ('two', b'fer')


def test_tagged_serializer():
    _field = Tagged('RED', Int)
    _serializer = _field.serializer
    assert _serializer(42) == 42
    pytest.raises(ValueError, _serializer, 'abc')


def make_table_cls(entity_name, location=DeprecatedYTLocation, partition_scale=None):
    class Tab(YTTable):
        __layout__ = entity_name
        __location_cls__ = location
        __partition_scale__ = partition_scale

        field = Datetime()
    return Tab


def test_yt_location():
    cls = make_table_cls(LayeredLayout('layer', 'name', 'groups'))
    location = cls.__location_cls__(cls, fake_prefix_manager)
    assert location.rel_folder() == 'layer/groups'
    assert location.folder() == '//service/layer/groups'
    assert location.rel() == 'layer/groups/name'
    with pytest.raises(DWHError):
        location.rel('2019-01-01')
    assert location.full() == '//service/layer/groups/name'
    assert location.rel_wo_partition() == 'layer/groups/name'
    assert location.wo_partition() == '//service/layer/groups/name'
    assert location.buffer() == join_path_parts('//service', TAXI_DWH_BUFFER_PREFIX, 'layer/groups/name')
    assert location.rotation() == join_path_parts('//service', TAXI_DWH_ROTATION_PREFIX, 'layer/groups/name')


def test_yt_location_with_domain():
    cls = make_table_cls(LayeredLayout('layer', 'name', domain=test_domain))
    location = cls.__location_cls__(cls, fake_prefix_manager)
    assert location.rel_folder() == 'layer/test_domain_code'
    assert location.full() == '//service/layer/test_domain_code/name'


def test_yt_location_with_scale():
    cls = make_table_cls(LayeredLayout('layer', 'name', 'groups'), partition_scale=MonthPartitionScale('field'))
    location = cls.__location_cls__(cls, fake_prefix_manager)
    assert location.rel_folder() == 'layer/groups/name'
    assert location.rel_wo_partition() == 'layer/groups/name'
    assert location.wo_partition() == '//service/layer/groups/name'
    with pytest.raises(DWHError):
        location.rel()
    with pytest.raises(DWHError):
        location.rel('')
    assert location.rel('2019-10-01') == 'layer/groups/name/2019-10-01'
    assert location.buffer('2019-10-01') == join_path_parts('//service', TAXI_DWH_BUFFER_PREFIX, 'layer/groups/name/2019-10-01')
    assert location.buffer() == join_path_parts('//service', TAXI_DWH_BUFFER_PREFIX, 'layer/groups/name/name')
    assert location.rotation('2019-10-01') == join_path_parts('//service', TAXI_DWH_ROTATION_PREFIX, 'layer/groups/name/2019-10-01')
    assert location.rotation() == join_path_parts('//service', TAXI_DWH_ROTATION_PREFIX, 'layer/groups/name/name')


def test_yt_location_with_multi_groups_and_service():
    cls = make_table_cls(DeprecatedLayeredYtLayout('layer', 'name', 'lvl1/lvl2/lvl3', prefix_key='custom'))
    location = cls.__location_cls__(cls)
    assert location.rel() == 'layer/lvl1/lvl2/lvl3/name'


def test_not_layered_yt_location_with_service_success():
    class ExtTable(NotLayeredYtTable):
        __layout__ = NotLayeredYtLayout('folder', 'table', prefix_key='test')

    assert NotLayeredYtLocation(ExtTable).full() == '//dummy/folder/table'
    assert NotLayeredYtLocation(ExtTable).prefix == '//dummy'
    assert NotLayeredYtLocation(ExtTable).folder() == '//dummy/folder'
    assert NotLayeredYtLocation(ExtTable).rel_folder() == 'folder'
    assert NotLayeredYtLocation(ExtTable).rel() == 'folder/table'


def test_not_layered_yt_location_without_service_success():
    class ExtTable(NotLayeredYtTable):
        __layout__ = NotLayeredYtLayout('//service/folder', 'table')

    assert NotLayeredYtLocation(ExtTable).prefix == '//service/folder'
    assert NotLayeredYtLocation(ExtTable).full() == '//service/folder/table'
    assert NotLayeredYtLocation(ExtTable).folder() == '//service/folder'
    assert NotLayeredYtLocation(ExtTable).rel_folder() == ''
    assert NotLayeredYtLocation(ExtTable).rel() == 'table'


def test_not_layered_yt_location_with_period():
    class ExtTable(NotLayeredYtTable):
        __layout__ = NotLayeredYtLayout('folder', 'name')
        __partition_scale__ = DayPartitionScale('d')

    assert NotLayeredYtLocation(ExtTable).full('2019-01-01') == '//dummy/folder/name/2019-01-01'
    assert NotLayeredYtLocation(ExtTable).folder() == '//dummy/folder/name'
    assert NotLayeredYtLocation(ExtTable).rel_folder() == 'folder/name'
    assert NotLayeredYtLocation(ExtTable).rel('2019-01-01') == 'folder/name/2019-01-01'


@pytest.mark.parametrize('layout, partition', (
        (NotLayeredYtLayout(folder='//folder/table', name='table', prefix_key='service'), None),
))
def test_not_layered_yt_location(layout, partition):
    class ExtTable(NotLayeredYtTable):
        __layout__ = layout

    with pytest.raises(DWHError):
        NotLayeredYtLocation(ExtTable).full(partition)


def test_layout_check_table():
    class LTable(YTTable):
        __layout__ = LayeredLayout('raw', 'name')

    class NLTable(YTTable):
        __layout__ = NotLayeredYtLayout('folder', 'name')

    class DTable(YTTable):
        __layout__ = DeprecatedLayeredYtLayout('raw', 'name')

    assert DeprecatedYTLocation(LTable)
    assert DeprecatedYTLocation(DTable)
    assert NotLayeredYtLocation(NLTable)

    with pytest.raises(DWHError):
        DeprecatedYTLocation(NLTable)

    with pytest.raises(DWHError):
        NotLayeredYtLocation(LTable)


def test_deprecated_layered_layout_entity_name_validator_ok():
    DeprecatedLayeredYtLayout('layer', 'name_1', group='lvl1/lvl2')


@pytest.mark.slow
def test_native_dttm_write_read():

    @random_yt_table
    class _TestTable(YTTable):
        date = NativeDate(sort_key=True, sort_position=0)
        datetime = NativeDatetime(sort_key=True, sort_position=1)
        timestamp = NativeTimestamp(sort_key=True, sort_position=2)

    meta = resolve_meta(_TestTable)

    op.init_yt_table(meta.target_path(), meta.attributes(), replace=True)

    def _write_dates_to_target(dates_list):
        _data = [
            {
                'date': NativeDate.serializer(d),
                'datetime': NativeDatetime.serializer(d),
                'timestamp': NativeTimestamp.serializer(d),
            }
            for d in dates_list
        ]
        op.write_yt_table(meta.target_path(), _data)

    # порядок данных соответствует порядку сортировки,
    # поэтому они записываются на YT без проблем
    dates = [
        "1970-01-01T00:00:00.000000Z",
        "1970-01-01T00:00:00.123654Z",
    ]
    _write_dates_to_target(dates)

    expected = [
        {
            'date': 0,
            'datetime': 0,
            'timestamp': 0,
        },
        {
            'date': 0,
            'datetime': 0,
            'timestamp': 123654,
        },
    ]
    assert expected == list(op.read_yt_table(meta.target_path()))

    # порядок данных НЕ соответствует порядку сортировки,
    # поэтому запрос на запись завершается с ошибкой.
    dates = [
        "1970-01-01T00:00:00.123654Z",
        "1970-01-01T00:00:00.000000Z",
    ]
    with pytest.raises(YtHttpResponseError):
        _write_dates_to_target(dates)


_write_read_data = [
    (
        Decimal(5, 3),
        (
            '00.000',
            '10.202',
            '-1',
            '-99.900',
            'nan'
        ),
        (
            b'\x80\x00\x00\x00',
            b'\x80\x00\x27\xda',
            b'\x7f\xff\xfc\x18',
            b'\x7f\xfe\x79\xc4',
            Decimal._nan[4],
        ),
    ),
    (
        Decimal(5, 3),
        (
            get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)('00.000'),
            get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)('00.0015'),
            get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)('10.2015'),
            get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)('-1'),
            get_decimal_rounder(5, 3, ROUND_HALF_EVEN, True)('123456'),
        ),
        (
            b'\x80\x00\x00\x00',
            b'\x80\x00\x00\x02',
            b'\x80\x00\x27\xda',
            b'\x7f\xff\xfc\x18',
            Decimal._plus_inf[4],
        ),
    ),
    (
        Optional(Int),
        (
            42,
            None,
            128,
        ),
        (
            42,
            None,
            128,
        ),
    ),
    (
        List(String),
        (
            ['Alone'],
            ['Emperor', 'Zurg'],
            [],
        ),
        (
            ['Alone'],
            ['Emperor', 'Zurg'],
            [],
        ),
    ),
    (
        Struct({'id': Int, 'name': String, 'other': Optional[Int]}),
        (
            {'id': 0, 'name': 'Gendalf', 'other': None},
            {'id': 1, 'name': 'Sauron', },
            {'id': 2, 'name': 'Juliet', 'other': 128},
        ),
        (
            {'id': 0, 'name': 'Gendalf', 'other': None},
            {'id': 1, 'name': 'Sauron', 'other': None},
            {'id': 2, 'name': 'Juliet', 'other': 128},
        ),
    ),
    (
        Tuple((Bool, Bool, Int)),
        (
            (True, True, 100),
            (True, False, 0),
            (1, 1, True),
        ),
        (
            [True, True, 100],
            [True, False, 0],
            [1, 1, True],
        ),
    ),
    (
        VariantNamed({'id': Int, 'name': String}),
        (
            ('id', 0),
            ('name', 'Kate'),
            ('id', 17),
        ),
        (
            ['id', 0],
            ['name', 'Kate'],
            ['id', 17],
        ),
    ),
    (
        VariantUnnamed((String, Int, List[Int])),
        (
            (0, 'FirstVariant'),
            (1, 2),
            (2, [1, 2, 3]),
        ),
        (
            [0, 'FirstVariant'],
            [1, 2],
            [2, [1, 2, 3]],
        ),
    ),
    (
        Dict(Int, Bool),
        (
            {1: True},
            {100: False},
            {},
        ),
        (
            [[1, True]],
            [[100, False]],
            [],
        ),
    ),
    (
        Tagged('RedFlag', Bool),
        (
            True,
            False,
            True,
        ),
        (
            True,
            False,
            True,
        ),
    ),
    (
        List(List[Optional[Bool]]),
        (
            [[]],
            [[True, False]],
            [[None, False], [None, None, None]],
        ),
        (
            [[]],
            [[True, False]],
            [[None, False], [None, None, None]],
        ),
    ),
    (
        Tuple((String, Optional[List[Bool]])),
        (
            ('ASD', [True, False, True]),
            ('BSD', []),
            ('BFG', None),
        ),
        (
            ['ASD', [True, False, True]],
            ['BSD', []],
            ['BFG', None],
        ),
    ),
]


@pytest.mark.parametrize(
    'field,data,expected',
    _write_read_data,
)
@pytest.mark.slow
def test_write_read_ytc(field, data, expected):

    @random_yt_table
    class _TestTable(YTTable):
        test_field = field

    meta = resolve_meta(_TestTable)

    op.init_yt_table(meta.target_path(), meta.attributes(), replace=True)

    _serializer = field.serializer
    _data = [{'test_field': _serializer(x)} for x in data]
    op.write_yt_table(meta.target_path(), _data)

    expected = [{'test_field': x} for x in expected]
    assert expected == list(op.read_yt_table(meta.target_path()))
