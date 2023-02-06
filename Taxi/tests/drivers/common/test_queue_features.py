import pandas as pd
import six

from projects.drivers.common.extractors import QueueFeatures

from taxi_pyml.common.time_utils import SECONDS_IN_DAY


source_a = pd.DataFrame(
    [
        {b'log_source': b'a', b'timestamp': -i * SECONDS_IN_DAY, b'value': i}
        for i in range(10)
    ],
)

source_b = pd.DataFrame(
    [
        {
            b'log_source': b'b',
            b'timestamp': -i * SECONDS_IN_DAY,
            b'cat_value': six.ensure_binary(str(i % 2)),
            b'value': i if i % 2 == 0 else None,
        }
        for i in range(10)
    ],
)

source_dfs = {b'a': source_a, b'b': source_b}

queue_1 = QueueFeatures(source_dfs, 1, 0)
queue_5 = QueueFeatures(source_dfs, 5, 0)
queue_10 = QueueFeatures(source_dfs, 10, 0)


def test_get_sub_queue_from_source():
    assert len(queue_10._get_sub_queue_from_source('b')) == 10
    assert len(queue_10._get_sub_queue_from_source('a')) == 10


def test_get_many_fields():
    # none_2_num = True
    fields = queue_10._get_many_fields(
        b'b', [b'cat_value', b'value'], none_2_num=True,
    )
    assert type(fields) is pd.DataFrame
    assert len(fields) == 10
    assert len(fields.columns) == 2
    assert b'cat_value' in fields
    assert b'value' in fields

    # none_2_num = False
    fields = queue_10._get_many_fields(
        b'b', [b'cat_value', b'value'], none_2_num=False,
    )
    assert type(fields) is pd.DataFrame
    assert len(fields) == 5
    assert len(fields.columns) == 2
    assert b'cat_value' in fields
    assert b'value' in fields


def test_get_field():
    field = queue_10._get_field('b', b'value', none_2_num=True)
    assert type(field) is pd.Series
    assert len(field) == 10

    # none_2_num = False
    field = queue_10._get_field('b', b'value', none_2_num=False)
    assert type(field) is pd.Series
    assert len(field) == 5
