# pylint: disable=protected-access

import datetime

import pytest

from taxi_driver_metrics.common.models.sql_query.exception import (
    InvalidContextValueError,
)
from taxi_driver_metrics.common.models.sql_query.execute import (
    insert_context_values,
)

TIMESTAMP = datetime.datetime(2020, 2, 12)


@pytest.mark.parametrize(
    'query, context, expected',
    (
        (
            'SELECT countIf(event_name == \'complete\') as complete'
            ' FROM db.OrderEvents'
            ' WHERE TRUE'
            ' AND event_timestamp > $event_timestamp - 7*24*3600'
            ' AND $unique_driver_id == driver_id',
            {'unique_driver_id': '123', 'event_timestamp': 1000},
            'SELECT countIf(event_name == \'complete\') as complete'
            ' FROM db.OrderEvents'
            ' WHERE TRUE AND event_timestamp > 1000 - 7*24*3600 '
            'AND \'123\' == driver_id',
        ),
        (
            'SELECT countIf(event_name == \'complete\') as complete'
            ' FROM db.OrderEvents'
            ' WHERE TRUE'
            ' AND event_timestamp > $event_timestamp - 7*24*3600 --last week'
            ' AND $unique_driver_id == driver_id --this driver',
            {'unique_driver_id': 'test_id', 'event_timestamp': None},
            InvalidContextValueError,
        ),
        (
            'SELECT COUNT_IF(event_name == \'complete\') as complete'
            ' FROM db.OrderEvents'
            ' WHERE TRUE'
            ' AND event_timestamp > $event_timestamp - 7*24*3600 --last week'
            ' AND $unique_driver_id == driver_id --this driver',
            {'unique_driver_id': 'test_id'},
            InvalidContextValueError,
        ),
        (
            'SELECT COUNT_IF(event_name == \'complete\') as complete'
            ' FROM db.OrderEvents'
            ' WHERE TRUE'
            ' AND event_timestamp > $event_timestamp - 7*24*3600 --last week'
            ' AND $unique_driver_id == driver_id --this driver',
            {
                'unique_driver_id': 'this is hack *** ()()',
                'event_timestamp': 1000,
            },
            InvalidContextValueError,
        ),
    ),
)
def test_insert_query_values(query, context, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            insert_context_values(query=query, context=context)
    else:
        assert expected == insert_context_values(query=query, context=context)
