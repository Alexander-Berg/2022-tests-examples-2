import datetime

import psycopg2
import pytest

from tests_contractor_events_producer import db_tools
from tests_contractor_events_producer import geo_hierarchies
from tests_contractor_events_producer import online_events


_NOW = datetime.datetime(2021, 12, 8, 9, 20, 21)
_HOUR = datetime.timedelta(hours=1)
_DAY = datetime.timedelta(days=1)

_NOW_TZ = (_NOW + datetime.timedelta(hours=3)).replace(
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
)

_CONTRACTOR_EVENTS = [
    online_events.OnlineDbEvent(
        f'dbid{index}', f'uuid{index}', status, _NOW_TZ - duration,
    )
    for index, status, duration in [
        (1, online_events.OFFLINE_STATUS, _DAY),
        (2, online_events.OFFLINE_STATUS, _DAY + _HOUR),
        (4, online_events.OFFLINE_STATUS, _HOUR),
        (6, online_events.ONLINE_STATUS, _DAY + 2 * _HOUR),
        (7, online_events.OFFLINE_STATUS, 2 * _DAY),
    ]
]

_CONTRACTOR_GEO_HIERARCHIES = [
    geo_hierarchies.GeoHierarchyDb(
        f'dbid{index}', f'uuid{index}', index, _NOW_TZ - duration,
    )
    for index, duration in [
        (1, _DAY),
        (3, _DAY + _HOUR),
        (4, _HOUR),
        (5, _DAY - _HOUR),
        (6, _DAY + 2 * _HOUR),
        (7, 2 * _DAY + _HOUR),
    ]
]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'contractor_events_producer',
    queries=[
        db_tools.insert_online_events(_CONTRACTOR_EVENTS),
        db_tools.insert_geo_hierarchies(_CONTRACTOR_GEO_HIERARCHIES),
    ],
)
@pytest.mark.parametrize(
    'online_status_limit, geo_hierarchy_limit, expired_duration_d, '
    'expected_counts, left_online_events, left_geo_hierarchies',
    (
        pytest.param(
            1,
            1,
            1,
            [(4, 5), (3, 4), (2, 3), (2, 2), (2, 2)],
            _CONTRACTOR_EVENTS[2:4],
            _CONTRACTOR_GEO_HIERARCHIES[2:4],
            id='partly clean',
        ),
        pytest.param(
            0,
            0,
            1,
            [(5, 6)],
            _CONTRACTOR_EVENTS,
            _CONTRACTOR_GEO_HIERARCHIES,
            id='turn off',
        ),
        pytest.param(
            1,
            0,
            1,
            [(4, 6), (3, 6), (2, 6), (2, 6)],
            _CONTRACTOR_EVENTS[2:4],
            _CONTRACTOR_GEO_HIERARCHIES,
            id='online events only',
        ),
        pytest.param(
            0,
            2,
            1,
            [(5, 4), (5, 2), (5, 2)],
            _CONTRACTOR_EVENTS,
            _CONTRACTOR_GEO_HIERARCHIES[2:4],
            id='geo hierarchy only',
        ),
        pytest.param(
            3,
            3,
            1,
            [(2, 3), (2, 2), (2, 2)],
            _CONTRACTOR_EVENTS[2:4],
            _CONTRACTOR_GEO_HIERARCHIES[2:4],
            id='bulk clean',
        ),
        pytest.param(
            3,
            3,
            2,
            [(4, 5), (4, 5)],
            _CONTRACTOR_EVENTS[:4],
            _CONTRACTOR_GEO_HIERARCHIES[:5],
            id='2 days expired duration',
        ),
    ),
)
async def test_garbage_collector(
        pgsql,
        testpoint,
        taxi_config,
        taxi_contractor_events_producer,
        online_status_limit,
        geo_hierarchy_limit,
        expired_duration_d,
        expected_counts,
        left_online_events,
        left_geo_hierarchies,
):
    @testpoint('garbage-collector-testpoint')
    def garbage_collector_testpoint(arg):
        pass

    taxi_config.set(
        CONTRACTOR_EVENTS_PRODUCER_GARBAGE_COLLECTOR={
            'polling_delay_ms': 60000,
            'online_status_limit': online_status_limit,
            'geo_hierarchy_limit': geo_hierarchy_limit,
            'expired_duration_d': expired_duration_d,
        },
    )

    for expected_online_events, expected_geo_hierarchies in expected_counts:
        async with taxi_contractor_events_producer.spawn_task(
                'workers/garbage-collector',
        ):
            await garbage_collector_testpoint.wait_call()

        actual_online_events = len(db_tools.get_online_events(pgsql))
        assert actual_online_events == expected_online_events

        actual_geo_hierarchies = len(db_tools.get_geo_hierarchies(pgsql))
        assert actual_geo_hierarchies == expected_geo_hierarchies

    assert db_tools.get_online_events(pgsql) == left_online_events
    assert db_tools.get_geo_hierarchies(pgsql) == left_geo_hierarchies
