import pytest

import dmp_suite.yt.table as yt
from dmp_suite.yql.types import YQLType, YTtoYQL
from dmp_suite.yt.type_parser import Blank


def test_converter_not_initializable():
    with pytest.raises(TypeError):
        _ = YTtoYQL()


@pytest.mark.parametrize(
    'data',
    [
        {
            'type_name': 'list',
            'item': 'notexist'
        },
        {
            'type_name': 'what',
            'item': 'int64'
        },
        {
            'type_name': 'tuple',
            'elements': [
                {
                    'type': 'nowyouhearme'
                },
            ]
        },
        {
            'type_name': 'tuple',
            'nowyoudont': [
                {
                    'type': 'int64'
                },
            ]
        },
        {
            'type_name': 'tuple',
            'members': [
                {
                    'type': 'int64'
                },
            ]
        },
        {
            'type_name': 'struct',
            'hoho': [
                {
                    'name': 'some_name',
                    'type': 'int64',
                },
            ]
        },
        {
            'type_name': 'struct',
            'members': [
                {
                    'name': 'some_name',
                    'type': 'lame',
                },
            ]
        },
    ]
)
def test_converter_throws_on_some_wrong_data(data):
    with pytest.raises(ValueError):
        _ = YTtoYQL.convert(data)


@pytest.mark.parametrize(
    'yt_cls,expected',
    [
        (yt.Int, YQLType.INT_64.value),
        (yt.UInt, YQLType.UINT_64.value),
        (yt.Boolean, YQLType.BOOL.value),
        (yt.Bool, YQLType.BOOL.value),
        (yt.String, YQLType.STRING.value),
        (yt.Date, YQLType.STRING.value),
        (yt.Datetime, YQLType.STRING.value),
        (yt.DatetimeMicroseconds, YQLType.STRING.value),
        (yt.NativeDate, YQLType.DATE.value),
        (yt.NativeDatetime, YQLType.DATETIME.value),
        (yt.NativeTimestamp, YQLType.TIMESTAMP.value),
        (yt.NativeInterval, YQLType.INTERVAL.value),
    ]
)
def test_simple_type_conversion(yt_cls, expected):
    assert YTtoYQL.convert(yt_cls(required=True)) == expected
    assert YTtoYQL.convert(yt_cls(required=False)) == f"{expected}?"


def test_simple_type_conversion_any():
    assert YTtoYQL.convert(yt.Any()) == f"{YQLType.YSON.value}?"


@pytest.mark.parametrize(
    'yt_field,expected',
    [
        (yt.List(yt.Int), "List<Int64>"),
        (yt.Decimal(7, 4), 'Decimal(7, 4)'),
        (yt.Decimal(5, 2), 'Decimal(5, 2)'),
        (yt.Optional(yt.Int), 'Optional<Int64>'),
        (yt.Optional(yt.List[yt.Int]), 'Optional<List<Int64>>'),
        (yt.Optional(yt.Optional[yt.UInt]), 'Optional<Optional<Uint64>>'),
        (yt.List(yt.Int), 'List<Int64>'),
        (yt.List(yt.List[yt.List[yt.Int]]), 'List<List<List<Int64>>>'),
        (yt.Struct({'id': yt.Int, 'value': yt.String}), 'Struct<id:Int64, value:String>'),
        (yt.Tuple((yt.Int, yt.Double)), 'Tuple<Int64, Double>'),
        (yt.Dict(key=yt.String, value=yt.Optional[yt.Int]), 'Dict<String, Optional<Int64>>'),
        (yt.VariantUnnamed((yt.Optional[yt.Int], yt.String, yt.Double)), 'Variant<Optional<Int64>, String, Double>'),
        (yt.VariantNamed({'one': yt.Optional[yt.Int], 'two': yt.String}), 'Variant<one:Optional<Int64>, two:String>'),
        (yt.Tagged('RED', yt.Int), 'Int64'),
        (yt.List[yt.Int], 'List<Int64>'),
    ]
)
def test_complex_type_conversion(yt_field, expected):
    assert YTtoYQL.convert(yt_field) == expected


@pytest.mark.parametrize(
    'yt_field',
    [
        yt.List[Blank],
        yt.Decimal[5, Blank],
        yt.Decimal[Blank, 3],
        yt.Decimal[Blank, Blank],
    ]
)
def test_raises_on_incomplete(yt_field):
    with pytest.raises(TypeError):
        YTtoYQL.convert(yt_field)
