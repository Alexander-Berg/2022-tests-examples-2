import datetime
from typing import Any
from typing import List

import pytest

from tests_driver_priority import db_tools


NOW = datetime.datetime.now()
MINUTE = datetime.timedelta(minutes=1)
TEN_MINUTES = datetime.timedelta(minutes=10)
DAY = datetime.timedelta(days=1)
WEEK = datetime.timedelta(days=7)
DB_NAME = 'driver_priority'


def _timestamp(timestamp: datetime.datetime) -> str:
    return f'\'{timestamp}\'::timestamp'


def _compare_data(db, query: str, expected_data: List[Any]):
    existing_data = db_tools.select_named(query, db)
    assert existing_data == expected_data


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    DB_NAME,
    queries=[
        f"""INSERT INTO service.request_results VALUES
        ('token1', {_timestamp(NOW + TEN_MINUTES)}, NULL),
        ('token2', {_timestamp(NOW + MINUTE)}, 200),
        ('token3', {_timestamp(NOW)}, 200),
        ('token4', {_timestamp(NOW - db_tools.HOUR)}, 200);
        INSERT INTO service.yql_history_operations VALUES
        ('operation_id_0', 'path_0',{_timestamp(NOW + TEN_MINUTES)}),
        ('operation_id_1', 'path_1',{_timestamp(NOW + MINUTE)}),
        ('operation_id_2', 'path_2', {_timestamp(NOW)}),
        ('operation_id_3', 'path_3',{_timestamp(NOW - db_tools.HOUR)});
        INSERT INTO service.last_priority_calculations VALUES
        ('dbid_uuid0', 'spb', 12345, {_timestamp(NOW)},
        {_timestamp(NOW - WEEK)}),
        ('dbid_uuid1', 'spb', 12345, {_timestamp(NOW - TEN_MINUTES)},
        {_timestamp(NOW - WEEK)}),
        ('dbid_uuid2', 'spb', 12345, {_timestamp(NOW - DAY)},
        {_timestamp(NOW - WEEK)}),
        ('dbid_uuid3', 'spb', 12345, {_timestamp(NOW - WEEK)},
        {_timestamp(NOW - WEEK)})""",
    ],
)
async def test_garbage_collector(taxi_driver_priority, pgsql):
    cron_response = await taxi_driver_priority.post(
        'service/cron', {'task_name': 'garbage-collector'},
    )
    assert cron_response.status_code == 200

    db = pgsql['driver_priority']

    tokens_query = (
        'SELECT confirmation_token FROM service.request_results '
        'ORDER BY confirmation_token;'
    )
    expected_tokens = [
        {'confirmation_token': token} for token in ['token1', 'token2']
    ]
    _compare_data(db, tokens_query, expected_tokens)

    history_operations_query = (
        'SELECT operation_id FROM service.yql_history_operations '
        'ORDER BY operation_id;'
    )
    expected_operations_ids = [
        {'operation_id': token}
        for token in ['operation_id_0', 'operation_id_1']
    ]
    _compare_data(db, history_operations_query, expected_operations_ids)

    calculations_query = (
        'SELECT dbid_uuid FROM service.last_priority_calculations '
        'ORDER BY dbid_uuid;'
    )
    expected_calculations = [
        {'dbid_uuid': 'dbid_uuid0'},
        {'dbid_uuid': 'dbid_uuid1'},
    ]
    _compare_data(db, calculations_query, expected_calculations)
