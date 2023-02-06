import inspect

import bson
import datetime
import pytest

from taxi.internal.yt_import import cast


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    (
        '0123456789ab0123456789ab',
        bson.ObjectId('0123456789ab0123456789ab'),
    ),
    ('foo', cast.CastError),
    (1, cast.CastError),
])
def test_to_obj_id(value, expected):
    _test_cast_func(cast._to_obj_id, value, expected)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    (
        '2018-08-22 18:00:00',
        datetime.datetime(2018, 8, 22, 18, 0, 0),
    ),
    ('foo', cast.CastError),
    (None, cast.CastError),
])
def test_parse_timestring(value, expected):
    _test_cast_func(cast._parse_timestring, value, expected)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    (
        '2018-08-22T18:30:0.12Z',
        datetime.datetime(2018, 8, 22, 18, 30),
    ),
    ('foo', cast.CastError),
    (None, cast.CastError),
])
def test_parse_yt_datetime(value, expected):
    _test_cast_func(cast._parse_yt_datetime, value, expected)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    (
        '2018-08-22',
        datetime.datetime(2018, 8, 22),
    ),
    (
        '2018-08-22T00:00:00.0Z',
        cast.CastError,
    ),
    ('foo', cast.CastError),
    (None, cast.CastError),
])
def test_parse_yt(value, expected):
    _test_cast_func(cast._parse_yt_date, value, expected)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    ([1], [1]),
    ([1, 1], [1]),
    (['a', 'b', 'a', 'b', 'c'], ['a', 'b', 'c']),
    ([], []),
    (None, None),
    (1, cast.CastError),
])
def test_to_unique_list(value, expected):
    cast_func = cast._to_unique_list
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            cast_func(value)
    else:
        casted_value = cast_func(value)
        if casted_value:
            casted_value = sorted(casted_value)
        assert casted_value == expected


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    (
        {
            '15': {'a': 1},
            30: {'b': 2},
            '3.14': {'c': 3},
            0.01: {'d': 4},
            'key': {'e': 5},
        },
        {
            'num15': {'a': 1},
            'num30': {'b': 2},
            '3.14': {'c': 3},
            0.01: {'d': 4},
            'key': {'e': 5},
        },
    ),
    ({}, {}),
    ('{}', cast.CastError),
    (None, cast.CastError),
])
def test_convert_digit_only_keys(value, expected):
    _test_cast_func(cast._convert_digit_only_keys, value, expected)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('value,expected', [
    ('english', u'english'),
    ('\xd0\x9c\xd0\xbe\xd1\x81\xd0\xba\xd0\xb2\xd0\xb0', u'\u041c\u043e\u0441\u043a\u0432\u0430'),
    (u'\u041c\u043e\u0441\u043a\u0432\u0430', u'\u041c\u043e\u0441\u043a\u0432\u0430'),
    ('english'.encode('utf-32'), cast.CastError),
    (None, cast.CastError),
])
def test_to_unicode(value, expected):
    _test_cast_func(cast._to_unicode, value, expected)


def _test_cast_func(cast_func, value, expected):
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            cast_func(value)
    else:
        casted_value = cast_func(value)
        assert casted_value == expected
