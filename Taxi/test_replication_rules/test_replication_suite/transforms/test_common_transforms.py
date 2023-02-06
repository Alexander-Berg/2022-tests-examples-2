import datetime as dt
import decimal
import functools

import pytest

from replication_suite.transforms import general_transforms
from replication_suite.casts import dates_casts


@pytest.mark.now('2019-09-18T03:00:00+0000')
def test_upload_time():
    assert general_transforms.upload_time({}) == '2019-09-18 03:00:00'


@pytest.mark.parametrize(
    'input_value, expected_value',
    (
        (None, None),
        (123, 123),
        (22.12, 22.12),
        (True, True),
        ('abc', 'abc'),
        ([123, '123'], [123, '123']),
        ([123, '123', [55, False]], [123, '123', [55, False]]),
        (
            {1: 2, '3': '4', '5': [{6: [7, 8, True]}]},
            {1: 2, '3': '4', '5': [{6: [7, 8, True]}]},
        ),
    ),
)
def test_to_yson(input_value, expected_value):
    assert general_transforms.to_yson(input_value) == expected_value
