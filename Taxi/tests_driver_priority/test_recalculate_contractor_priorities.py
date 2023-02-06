import datetime as dt
from typing import Any
from typing import List
from typing import Optional
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
]


def _check_calculations_record(db, expected: List[Any], condition=''):
    if condition:
        condition = f'WHERE {condition}'
    query = (
        f'SELECT dbid_uuid, tariff_zone, updated_at, last_login_at FROM '
        f'service.last_priority_calculations {condition} ORDER BY dbid_uuid'
    )
    rows = db_tools.select_named(query, db)
    assert len(rows) == len(expected)
    for row, expected_item in zip(rows, expected):
        assert row['dbid_uuid'] == expected_item[0]
        assert row['tariff_zone'] == expected_item[1]
        assert row['updated_at'] == utils.add_local_tz(expected_item[2])
        assert row['last_login_at'] == utils.add_local_tz(expected_item[3])
        # calculation_hash is not checked


@pytest.mark.driver_trackstory(
    positions={
        'dbid_uuid': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
        'position_without-zone': {
            'lon': 1.1,
            'lat': 2.2,
            'timestamp': int(_NOW.timestamp()),
        },
    },
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags_info={'platinum': {'topics': ['priority']}},
)
@pytest.mark.now(_NOW.isoformat())
async def test_empty_stq_worker(stq_runner):
    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': _NOW.isoformat(),
            'profile_event': {
                'dbid': 'dbid',
                'uuid': 'uuid',
                'event_type': 'tags',
            },
        },
        expect_fail=False,
    )
    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': _NOW.isoformat(),
            'unique_driver_event': {
                'unique_driver_id': 'udid',
                'change_type': 'complete_scores',
            },
        },
        expect_fail=False,
    )
    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': _NOW.isoformat(),
            'profile_event': {
                'dbid': 'without',
                'uuid': 'position',
                'event_type': 'login',
            },
        },
        exec_tries=3,
        expect_fail=False,
    )
    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': _NOW.isoformat(),
            'profile_event': {
                'dbid': 'position',
                'uuid': 'without-zone',
                'event_type': 'login',
            },
        },
        exec_tries=3,
        expect_fail=False,
    )


@pytest.mark.driver_trackstory(
    positions={
        'dbid_uuid': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
        'dbid_uuid0': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
        'dbid_uuid2': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
        'dbid_uuid3': {
            'lon': 37.6,
            'lat': 55.75,
            'timestamp': int(_NOW.timestamp()),
        },
        'dbid_uuidpenza': {
            'lon': 41.1,
            'lat': 55.5,
            'timestamp': int(_NOW.timestamp()),
        },
    },
)
@pytest.mark.drivers_car_ids(
    data={'dbid_uuid': 'carid', 'dbid_uuid0': 'carid0'},
)
@pytest.mark.fleet_vehicles(data={'dbid_carid': {'year': 2022}})
@pytest.mark.driver_taximeter(
    profile='dbid_uuid', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid0', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid2', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid3', platform='android', version='10.10', version_type='',
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['moscow', 'tula', 'penza'],
        },
    ],
)
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags_info={'platinum': {'topics': ['priority']}},
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid0',
    tags_info={'platinum': {'topics': ['priority']}},
)
@pytest.mark.config(
    DRIVER_PRIORITY_RECALCULATION_TASK_SETTINGS={
        'enable_client_events_push': True,
        'positions_max_age_seconds': 3600,
    },
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': False},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        db_tools.get_pg_default_data(_NOW)
        + [db_tools.insert_priority_calculations(_DEFAULT_CALCULATIONS)],
    ),
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'dbid, uuid, event_type, event_timestamp, expected_events, '
    'expected_calculations',
    [
        pytest.param(
            'dbid',
            'uuid',
            'login',
            _NOW,
            (True, True, True, True, True, True),
            [('dbid_uuid', 'moscow', _NOW, _NOW)] + _DEFAULT_CALCULATIONS,
            id='insert new record',
        ),
        pytest.param(
            'dbid',
            'uuid0',
            'logout',
            _NOW,
            (False, False, False, False, False, False),
            _DEFAULT_CALCULATIONS[1:],
            id='remove first record',
        ),
        pytest.param(
            'dbid',
            'uuid0',
            'logout',
            _NOW - _HOUR - _MINUTE,
            (False, False, False, False, False, False),
            _DEFAULT_CALCULATIONS,
            id='skip too old logout event, produced before last login',
        ),
        pytest.param(
            'dbid',
            'uuid0',
            'login',
            _NOW,
            (True, True, True, True, True, True),
            [('dbid_uuid0', 'moscow', _NOW, _NOW)] + _DEFAULT_CALCULATIONS[1:],
            id='update first record',
        ),
        pytest.param(
            'dbid',
            'uuid2',
            'login',
            _DAY_AGO + _HOUR,
            (True, True, True, True, True, False),
            _DEFAULT_CALCULATIONS[:-1]
            + [('dbid_uuid2', 'moscow', _NOW, _DAY_AGO + _HOUR)],
            id='update last record with old but actual event time',
        ),
        pytest.param(
            'dbid',
            'uuid2',
            'login',
            _DAY_AGO - _HOUR,
            (False, False, False, False, False, False),
            _DEFAULT_CALCULATIONS,
            id='do not update last record because of too old login event',
        ),
        pytest.param(
            'dbid',
            'uuid0',
            'login',
            _NOW - _HOUR - _MINUTE,
            (False, False, False, False, False, False),
            _DEFAULT_CALCULATIONS,
            id='do not update first record because of too old login event',
        ),
        pytest.param(
            'no',
            'positions',
            'login',
            _NOW,
            (True, False, False, False, False, False),
            _DEFAULT_CALCULATIONS,
            id='driver without position',
        ),
        pytest.param(
            'dbid',
            'uuidpenza',
            'login',
            _NOW,
            (True, False, True, False, False, False),
            _DEFAULT_CALCULATIONS + [('dbid_uuidpenza', 'penza', _NOW, _NOW)],
            id='driver without priorities',
        ),
        pytest.param(
            'dbid',
            'uuid3',
            'login',
            _DAY_AGO + _HOUR,
            (True, True, False, True, True, False),
            _DEFAULT_CALCULATIONS
            + [('dbid_uuid3', 'moscow', _NOW, _DAY_AGO + _HOUR)],
            id='driver does not match config for event push',
        ),
    ],
)
async def test_login_events(
        pgsql,
        stq_runner,
        driver_trackstory_mock,
        driver_tags_mocks,
        driver_profiles_mocks,
        mock_fleet_vehicles,
        mockserver,
        dbid: str,
        uuid: str,
        event_type: str,
        event_timestamp: dt.datetime,
        expected_events: Tuple[bool, bool, bool, bool, bool, bool],
        expected_calculations: List[Any],
):
    (
        expect_trackstory_call,
        expect_tags_call,
        expect_push_call,
        expect_profile_app_call,
        expect_car_ids_call,
        expect_fleet_vehicles_call,
    ) = expected_events

    @mockserver.json_handler('/client-events/push')
    def _client_events_mock(request):
        return mockserver.make_response(json={'version': '1'}, status=200)

    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': event_timestamp.isoformat(),
            'profile_event': {
                'dbid': dbid,
                'uuid': uuid,
                'event_type': event_type,
            },
        },
        expect_fail=False,
    )

    assert driver_trackstory_mock.calls == expect_trackstory_call
    assert driver_tags_mocks.has_calls() == expect_tags_call
    assert _client_events_mock.has_calls == expect_push_call
    assert (
        driver_profiles_mocks.has_calls('profiles/retrieve')
        == expect_profile_app_call
    )
    assert (
        driver_profiles_mocks.has_calls('cars/retrieve_by_driver_id')
        == expect_car_ids_call
    )
    assert mock_fleet_vehicles.has_calls() == expect_fleet_vehicles_call

    db = pgsql['driver_priority']
    _check_calculations_record(db, expected_calculations)


@pytest.mark.driver_taximeter(
    profile='dbid_uuid0', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid1', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid2', platform='android', version='10.10', version_type='',
)
@pytest.mark.driver_taximeter(
    profile='dbid_uuid3', platform='android', version='10.10', version_type='',
)
@pytest.mark.drivers_car_ids(
    data={f'dbid_uuid{i}': f'carid{i}' for i in range(4)},
)
@pytest.mark.fleet_vehicles(
    data={f'dbid_carid{i}': {'year': 2022} for i in range(4)},
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['moscow', 'tula', 'penza'],
        },
    ],
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid0',
    tags_info={'platinum': {'topics': ['priority']}},
)
@pytest.mark.driver_tags_match(
    dbid='dbid',
    uuid='uuid1',
    tags_info={'platinum': {'topics': ['priority']}},
)
@pytest.mark.unique_drivers(
    data={
        'good_udid': [('dbid', 'uuid0')],
        'multiple_udid': [
            ('dbid', 'uuid1'),
            ('dbid', 'uuid2'),
            ('no', 'calculation'),
        ],
    },
)
@pytest.mark.config(
    DRIVER_PRIORITY_RECALCULATION_TASK_SETTINGS={
        'enable_client_events_push': True,
        'positions_max_age_seconds': 3600,
    },
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': False},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=db_tools.join_queries(
        db_tools.get_pg_default_data(_NOW)
        + [db_tools.insert_priority_calculations(_DEFAULT_CALCULATIONS)],
    ),
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'udid, new_calculations',
    [
        pytest.param('unknown', [], id='no changes for unknown udid'),
        pytest.param(
            'good_udid',
            [['dbid_uuid0', 'moscow', _NOW, _NOW - _HOUR]],
            id='update single profile',
        ),
        pytest.param(
            'multiple_udid',
            [
                ['dbid_uuid1', 'spb', _NOW, _DAY_AGO - _MINUTE],
                ['dbid_uuid2', 'moscow', _NOW, _DAY_AGO - _MINUTE],
            ],
            id='update single profile',
        ),
    ],
)
async def test_udid_events(
        pgsql,
        stq_runner,
        mockserver,
        mock_fleet_vehicles,
        udid: str,
        new_calculations: List[Any],
):
    @mockserver.json_handler('/client-events/push')
    def _client_events_mock(request):
        return mockserver.make_response(json={'version': '1'}, status=200)

    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': _NOW.isoformat(),
            'unique_driver_event': {
                'unique_driver_id': udid,
                'change_type': 'rating',
            },
        },
        expect_fail=False,
    )
    has_new_calculations = len(new_calculations) > 0
    assert _client_events_mock.has_calls == has_new_calculations
    assert mock_fleet_vehicles.has_calls() == has_new_calculations

    db = pgsql['driver_priority']
    condition = f'updated_at >= \'{utils.add_local_tz(_NOW)}\'::timestamptz'
    _check_calculations_record(db, new_calculations, condition=condition)


@pytest.mark.config(
    DRIVER_PRIORITY_RECALCULATION_TASK_SETTINGS={
        'enable_client_events_push': True,
        'positions_max_age_seconds': 3600,
    },
    ENABLE_PRIORITY_BY_EXPERIMENTS={'__default__': False},
    PRIORITY_ZONES_WHITELIST=constants.DEFAULT_ZONES_WHITELIST,
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'reschedule_counter, eta_seconds',
    [(0, 10), (1, 30), (2, 60), (3, 180), (4, None)],
)
async def test_reschedule_on_position_errors(
        stq,
        stq_runner,
        driver_trackstory_mock,
        reschedule_counter: int,
        eta_seconds: Optional[int],
):
    await stq_runner.recalculate_contractor_priorities.call(
        task_id='some_id',
        kwargs={
            'created_at': (_NOW - _MINUTE).isoformat(),
            'profile_event': {
                'dbid': 'dbid',
                'uuid': 'uuid',
                'event_type': 'login',
            },
        },
        reschedule_counter=reschedule_counter,
    )

    assert driver_trackstory_mock.calls

    if eta_seconds is None:
        assert not stq.recalculate_contractor_priorities.has_calls
        return

    eta = _NOW + dt.timedelta(seconds=eta_seconds)
    stq_call = stq.recalculate_contractor_priorities.next_call()
    assert stq_call['queue'] == 'recalculate_contractor_priorities'
    assert stq_call['eta'] == eta.replace(tzinfo=None)
    assert stq_call['id'] == 'some_id'
