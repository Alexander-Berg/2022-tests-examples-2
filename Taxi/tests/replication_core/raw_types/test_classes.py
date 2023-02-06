import datetime
import decimal
import uuid

import asyncpg
import bson
import pytest

from replication_core.raw_types import classes
from replication_core.raw_types import common
from replication_core.raw_types import mongo
from replication_core.raw_types import postgres


def bit_string_serializer(value: asyncpg.BitString):
    return value.as_string(), None


def point_serializer(value: asyncpg.Point):
    return list(value), None


def polygon_serializer(value: asyncpg.Polygon):
    return list(list(point) for point in value.points), None


def range_serializer(value: asyncpg.Range):
    return {
        'lower': value.lower,
        'lower_inc': value.lower_inc,
        'upper': value.upper,
        'upper_inc': value.upper_inc,
    }, None


def bit_string_deserializer(value, attrs):
    return asyncpg.BitString(value)


def point_deserializer(value, attrs):
    return asyncpg.Point(*value)


def polygon_deserializer(value, attrs):
    return asyncpg.Polygon(*value)


def range_deserializer(value, attrs):
    return asyncpg.Range(**value)


# TODO: make separate minimal test for hook (de)serializers
@pytest.mark.parametrize(
    'serializing_hooks, deserializing_hooks, document, expected_json',
    [
        ((), (), {}, '{}'),
        (common.HOOKS, common.HOOKS, {}, '{}'),
        (
            common.HOOKS,
            common.HOOKS,
            {'datetime': datetime.datetime(2020, 5, 20, 10, 0)},
            '{"datetime": {"$a": {"raw_type": "datetime"}, '
            '"$v": "2020-05-20T10:00:00"}}',
        ),
        (
            common.HOOKS,
            common.HOOKS,
            {'foo': 'value', 'bar': 123},
            '{"bar": 123, "foo": "value"}',
        ),
        (
            common.HOOKS,
            common.HOOKS,
            {'bar': 123, 'foo': 'value'},
            '{"bar": 123, "foo": "value"}',
        ),
        (
            [
                *common.HOOKS,
                postgres.PgPointHook().with_serializer(
                    point_serializer,
                    lambda value: isinstance(value, asyncpg.Point),
                ),
                postgres.PgPolygonHook().with_serializer(
                    polygon_serializer,
                    lambda value: isinstance(value, asyncpg.Polygon),
                ),
                postgres.PgBitStringHook().with_serializer(
                    bit_string_serializer,
                    lambda value: isinstance(value, asyncpg.BitString),
                ),
                postgres.PgRangeHook().with_serializer(
                    range_serializer,
                    lambda value: isinstance(value, asyncpg.Range),
                ),
            ],
            [
                *common.HOOKS,
                postgres.PgPointHook().with_deserializer(point_deserializer),
                postgres.PgPolygonHook().with_deserializer(
                    polygon_deserializer,
                ),
                postgres.PgBitStringHook().with_deserializer(
                    bit_string_deserializer,
                ),
                postgres.PgRangeHook().with_deserializer(
                    range_deserializer,
                ),
            ],
            {
                'pg': {
                    'bit': asyncpg.BitString('0101'),
                    'polygon': asyncpg.Polygon(
                        asyncpg.Point(0, 1),
                        asyncpg.Point(1, 1),
                        asyncpg.Point(1, 0),
                        asyncpg.Point(0, 1),
                    ),
                    'range': asyncpg.Range(0, 1),
                    'range_dttm': asyncpg.Range(
                        datetime.datetime(2020, 5, 20, 10, 0),
                        None,
                        lower_inc=False,
                    ),
                },
                'datetime': datetime.datetime(2020, 5, 20, 10, 0),
                'date': datetime.date(2020, 5, 20),
                'time': datetime.time(22, 15),
                'decimal': decimal.Decimal('123.555'),
                'binary': b'test',
            },
            '{"binary": {"$a": {"raw_type": "bytes"}, "$v": "dGVzdA=="}, '
            '"date": {"$a": {"raw_type": "date"}, "$v": "2020-05-20"}, '
            '"datetime": {"$a": {"raw_type": "datetime"}, '
            '"$v": "2020-05-20T10:00:00"}, "decimal": {"$a": {"raw_type": '
            '"decimal"}, "$v": "123.555"}, "pg": {"bit": {"$a": {"raw_type": '
            '"pg_bit"}, "$v": "0101"}, "polygon": {"$a": {"raw_type": '
            '"pg_polygon"}, "$v": [[0.0, 1.0], [1.0, 1.0], [1.0, 0.0], '
            '[0.0, 1.0]]}, "range": {"$a": {"raw_type": "pg_range"}, '
            '"$v": {"lower": 0, "lower_inc": true, "upper": 1, '
            '"upper_inc": false}}, "range_dttm": {"$a": {"raw_type": '
            '"pg_range"}, "$v": {"lower": {"$a": {"raw_type": "datetime"}, '
            '"$v": "2020-05-20T10:00:00"}, "lower_inc": false, "upper": null, '
            '"upper_inc": false}}}, "time": {"$a": {"raw_type": "time"}, '
            '"$v": "22:15:00"}}',
        ),
        (
            common.HOOKS + mongo.HOOKS,
            common.HOOKS + mongo.HOOKS,
            {
                'datetime': datetime.datetime(2020, 5, 20, 10, 0),
                'obj_id': bson.ObjectId('5b2cae5cb2682a976914c2a5'),
                'ts': bson.timestamp.Timestamp(123, 10),
                'binary': b'test',
                'decimal128': bson.Decimal128('0.123456'),
                'uuid': uuid.UUID('146e6b76-0069-4db1-9e87-0babb5e9bc00'),
            },
            '{'
            '"binary": {'
            '"$a": {"raw_type": "bytes"}, '
            '"$v": "dGVzdA=="'
            '}, '
            '"datetime": {'
            '"$a": {"raw_type": "datetime"}, '
            '"$v": "2020-05-20T10:00:00"'
            '}, '
            '"decimal128": {'
            '"$a": {"raw_type": "bson_decimal128"}, '
            '"$v": "0.123456"'
            '}, '
            '"obj_id": {'
            '"$a": {"raw_type": "bson_object_id"}, '
            '"$v": "5b2cae5cb2682a976914c2a5"'
            '}, '
            '"ts": {'
            '"$a": {"raw_attrs": {"inc": 10}, "raw_type": "bson_ts"}, '
            '"$v": 123'
            '}, '
            '"uuid": {"$a": {"raw_type": "uuid"}, '
            '"$v": "146e6b76-0069-4db1-9e87-0babb5e9bc00"'
            '}'
            '}',
        ),
    ],
)
def test_raw_types_json(
        serializing_hooks, deserializing_hooks, document, expected_json,
):
    serializer = classes.JsonSerializer(hooks=serializing_hooks)
    serialized = serializer.serialize(document)
    assert serialized == expected_json

    deserializer = classes.JsonDeserializer(hooks=deserializing_hooks)
    deserialized = deserializer.deserialize(serialized)
    assert deserialized == document
