from datetime import datetime

import pytest

from taxi_driver_metrics.api.v1_service_rules_history_post import (
    CONDITION_FIELDS,
)
from taxi_driver_metrics.api.v1_service_rules_history_post import (
    NESTED_CONDITION_FIELDS,
)
from taxi_driver_metrics.common.storage import clickhouse


def make_date(date_string):
    return datetime.strptime(date_string, clickhouse.TIME_FORMAT_MIN)


PATH = clickhouse.get_env_base_path()

PERIODS = ['1d', '30min', '5min']
TABLES = {
    '/1d': ('2020-02-02', '2020-02-03'),
    '/30min': ('2020-02-03T00:00:00', '2020-02-03T06:00:00'),
    '/stream/5min': ('2020-02-03T06:00:00', '2020-02-03T06:15:00'),
}
SOURCES = [
    f'concatYtTablesRange(\'{PATH}/1d\', \'2020-02-02\', ' '\'2020-02-03\')',
    f'concatYtTablesRange(\'{PATH}/30min\', \'2020-02-03T0'
    '0:00:00\', \'2020-02-03T06:00:00\')',
    f'concatYtTablesRange(\'{PATH}/stream/5min\', \'2020-0'
    '2-03T06:00:00\', \'2020-02-03T06:15:00\')',
]
SOME_DATE = make_date('2020-02-02T00:00:00')


@pytest.mark.parametrize(
    'datetime_from, datetime_to, max_available_table, expected_res_by_period',
    [
        (
            make_date('2020-02-02T00:00:00'),
            make_date('2020-02-10T00:00:01'),
            make_date('2020-02-03T00:00:00'),
            {
                '1d': ('2020-02-02', '2020-02-03'),
                '30min': ('2020-02-02T00:00:00', '2020-02-03T00:00:00'),
                '5min': ('2020-02-02T00:00:00', '2020-02-03T00:00:00'),
            },
        ),
        (
            make_date('2020-02-02T12:31:01'),
            make_date('2020-02-03T12:10:11'),
            make_date('2020-02-04T00:00:00'),
            {
                '1d': ('2020-02-02', '2020-02-03'),
                '30min': ('2020-02-02T12:30:00', '2020-02-03T12:00:00'),
                '5min': ('2020-02-02T12:30:00', '2020-02-03T12:10:00'),
            },
        ),
        (
            make_date('2020-02-02T23:59:00'),
            make_date('2020-02-03T00:30:01'),
            make_date('2020-02-03T00:00:00'),
            {
                '1d': ('2020-02-02', '2020-02-03'),
                '30min': ('2020-02-02T23:30:00', '2020-02-03T00:00:00'),
                '5min': ('2020-02-02T23:55:00', '2020-02-03T00:00:00'),
            },
        ),
        (
            make_date('2020-02-02T15:12:00'),
            make_date('2020-02-02T15:16:00'),
            make_date('2020-02-03T00:00:00'),
            {
                '1d': ('2020-02-02', '2020-02-02'),
                '30min': ('2020-02-02T15:00:00', '2020-02-02T15:00:00'),
                '5min': ('2020-02-02T15:10:00', '2020-02-02T15:15:00'),
            },
        ),
    ],
)
def test_bounds_for_tables(
        datetime_from,
        datetime_to,
        max_available_table,
        expected_res_by_period,
):
    for period in PERIODS:
        res = clickhouse.extract_bounds_for_tables(
            datetime_to=datetime_to,
            datetime_from=datetime_from,
            max_available_table=max_available_table,
            period=period,
        )
        assert res == expected_res_by_period[period]


@pytest.mark.parametrize(
    'data, datetime_to, datetime_from, limit, condition',
    [
        (
            {'rule_name': 'some_name'},
            None,
            None,
            None,
            '1 AND rule_name = \'some_name\'',
        ),
        (
            {'rule_type': 'some_type'},
            None,
            None,
            None,
            '1 AND rule_type = \'some_type\'',
        ),
        (
            {'entity_type': 'driver', 'entity_id': '123'},
            None,
            None,
            None,
            '1 AND entity_type = \'driver\' AND entity_id = \'123\'',
        ),
        (
            {'rule_type': 'some_type'},
            None,
            None,
            5,
            '1 AND rule_type = \'some_type\'',
        ),
        (
            {'rule_type': 'some_type'},
            make_date('2020-02-02T00:00:00'),
            None,
            None,
            f'1 AND rule_type = \'some_type\' '
            f'AND timestamp < {clickhouse.make_timestamp(SOME_DATE)}',
        ),
        (
            {'rule_type': 'some_type'},
            None,
            make_date('2020-02-02T00:00:00'),
            None,
            f'1 AND rule_type = \'some_type\' '
            f'AND timestamp > {clickhouse.make_timestamp(SOME_DATE)}',
        ),
    ],
)
def test_build_query(data, datetime_from, datetime_to, limit, condition):

    query = clickhouse.build_history_query(
        tables=TABLES,
        condition_fields=CONDITION_FIELDS,
        nested_condition_fields=NESTED_CONDITION_FIELDS,
        base_path=PATH,
        data=data,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        limit=limit,
    )
    for source in SOURCES:
        assert source in query

    assert condition in query
    if limit:
        assert f'LIMIT {limit}' in query
    assert 'FORMAT JSON' in query
