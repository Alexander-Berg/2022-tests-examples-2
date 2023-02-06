import datetime as dt
import decimal

import bson
import pytest

from replication_suite import common_plugins


@pytest.mark.dontfreeze
@pytest.mark.parametrize(
    'input_value, expected_value',
    (
        (
            dt.datetime(2020, 1, 1, 12, 32, 22, 111111),
            '2020-01-01 12:32:22.111111',
        ),
        (dt.date(2020, 5, 5), '2020-05-05'),
        (decimal.Decimal('12.35'), '12.35'),
        (
            bson.ObjectId('235f78ae535b184e245f78c2'),
            '235f78ae535b184e245f78c2',
        ),
        (bson.Timestamp(0, 0), 0),
        (
            {
                1: {
                    '2': [
                        dt.datetime(2020, 1, 1, 12, 32, 22, 111111),
                        dt.date(2020, 5, 7),
                        decimal.Decimal('12.35'),
                        bson.ObjectId('235f78ae535b184e245f78c2'),
                        bson.Timestamp(0, 0),
                    ],
                },
            },
            {
                1: {
                    '2': [
                        '2020-01-01 12:32:22.111111',
                        '2020-05-07',
                        '12.35',
                        '235f78ae535b184e245f78c2',
                        0,
                    ],
                },
            },
        ),
    ),
)
def test_to_yson_with_casters(input_value, expected_value):
    assert common_plugins.to_yson(input_value) == expected_value
