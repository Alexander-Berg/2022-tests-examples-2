import datetime
import datetime as dt
from typing import List
from typing import Tuple

import pytest

from tests_driver_priority import constants
from tests_driver_priority import db_tools
from tests_driver_priority import utils

_MINUTE = dt.timedelta(minutes=1)
_HOUR = dt.timedelta(hours=1)
_DAY = dt.timedelta(days=1)

_NOW = dt.datetime.now(dt.timezone.utc)
_DAY_AGO = _NOW - _DAY

_DEFAULT_CALCULATIONS: List[Tuple[str, str, dt.datetime, dt.datetime]] = [
    ('dbid_uuid0', 'moscow', _NOW - _HOUR, _NOW - _HOUR),
    ('dbid_uuid1', 'spb', _DAY_AGO, _DAY_AGO - _MINUTE),
    ('dbid_uuid2', 'moscow', _DAY_AGO, _DAY_AGO - _MINUTE),
    ('dbid_uuid3', 'tula', _NOW - _MINUTE, _NOW - _HOUR),
    ('dbid_uuid4', 'spb', _NOW - _MINUTE, _NOW - _HOUR),
]


def _insert_recalculation_task(
        db, execution_time: dt.datetime, agglomerations: List[str],
):
    joined_agglomerations = '\'{' + ','.join(agglomerations) + '}\''
    query = (
        f'INSERT INTO service.recalculation_tasks (created_at, agglomerations,'
        f'execution_time, last_processed_timestamp) VALUES (\'{_DAY_AGO}\'::'
        f'timestamptz, {joined_agglomerations}, \'{execution_time}\''
        f'::timestamptz, NULL);'
    )
    with db.conn.cursor() as cursor:
        cursor.execute(query)


def _check_updated_calculations(
        db, expected_ids: List[str], now: datetime.datetime,
):
    query = (
        f'SELECT dbid_uuid FROM service.last_priority_calculations WHERE '
        f'updated_at >= \'{utils.add_local_tz(now)}\'::timestamptz ORDER BY '
        f'dbid_uuid;'
    )

    with db.conn.cursor() as cursor:
        cursor.execute(query)
        ids = [x[0] for x in cursor.fetchall()]
        assert ids == expected_ids


@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.get_pg_default_data(_NOW)
    + [db_tools.insert_priority_calculations(_DEFAULT_CALCULATIONS)],
)
@pytest.mark.config(
    DRIVER_PRIORITY_RECALCULATION_WORKER_SETTINGS={
        'is_enabled': True,
        'chunk_limit': 3,
        'enable_client_events_push': True,
        'max_parallel_events_push': 24,
        'iterations_count': 8,
    },
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': False},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid0', tags_info={}, udid='udid0',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid1', tags_info={}, udid='udid0',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid2', tags_info={}, udid='udid1',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid3', tags_info={}, udid='udid1',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid4', tags_info={}, udid='udid2',
)
@pytest.mark.drivers_car_ids(
    data={f'dbid_uuid{i}': f'carid{i}' for i in range(5)},
)
@pytest.mark.fleet_vehicles(
    data={f'dbid_carid{i}': {'year': 2022} for i in range(5)},
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'node',
            'parent_name': 'br_root',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_spb',
            'name_en': 'SPb',
            'name_ru': 'СПб',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tariff_zones': ['spb'],
        },
        {
            'name': 'br_tula',
            'name_en': 'Tula',
            'name_ru': 'Тула',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'tariff_zones': ['tula'],
        },
    ],
)
@pytest.mark.experiments3(filename='send_client_events_push_config.json')
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'task_execution_time, updated_ids, task_agglomerations',
    [
        (_NOW, [f'dbid_uuid{i}' for i in range(5)], []),
        (_NOW, [f'dbid_uuid{i}' for i in range(5)], ['br_root']),
        (_NOW, [f'dbid_uuid{i}' for i in range(5)], ['br_russia']),
        (_NOW, ['dbid_uuid0', 'dbid_uuid2'], ['br_moscow']),
        (_NOW, ['dbid_uuid0', 'dbid_uuid2'], ['moscow']),
        (_NOW, ['dbid_uuid1', 'dbid_uuid4'], ['spb']),
        (_NOW, ['dbid_uuid3'], ['tula']),
        (_NOW - _MINUTE, [f'dbid_uuid{i}' for i in range(3)], []),
        (_NOW - _HOUR + _MINUTE, [f'dbid_uuid{i}' for i in range(3)], []),
        (_NOW - _HOUR, ['dbid_uuid1', 'dbid_uuid2'], []),
        (_NOW - _HOUR, [], ['tula']),
        (_NOW - _HOUR, ['dbid_uuid2'], ['moscow']),
        (_DAY_AGO + _MINUTE, ['dbid_uuid1', 'dbid_uuid2'], []),
        (_DAY_AGO, [], []),
    ],
)
async def test_worker(
        taxi_driver_priority,
        pgsql,
        mockserver,
        driver_profiles_mocks,
        mock_fleet_vehicles,
        task_execution_time: dt.datetime,
        updated_ids: List[str],
        task_agglomerations: List[str],
):
    pushed_ids = []

    @mockserver.json_handler('/client-events/push')
    def _client_events_mock(request):
        nonlocal pushed_ids

        body = request.json
        parts = body['channel'].split(':')
        assert body['event'] == 'priority-update'
        assert body['service'] == 'yandex.pro'
        assert body['send_notification']
        assert len(parts) == 2
        assert parts[0] == 'contractor'

        pushed_ids.append(parts[1])
        return mockserver.make_response(json={'version': '1'}, status=200)

    db = pgsql['driver_priority']
    _insert_recalculation_task(db, task_execution_time, task_agglomerations)

    cron_response = await taxi_driver_priority.post(
        'service/cron', {'task_name': 'priority-recalculation'},
    )
    assert cron_response.status_code == 200

    db_tools.check_recalculation_task(db, None)
    _check_updated_calculations(db, updated_ids, _NOW)
    has_calls = bool(updated_ids)
    assert (
        driver_profiles_mocks.has_calls('cars/retrieve_by_driver_id')
        == has_calls
    )
    assert mock_fleet_vehicles.has_calls() == has_calls

    pushed_ids.sort()
    assert pushed_ids == updated_ids
