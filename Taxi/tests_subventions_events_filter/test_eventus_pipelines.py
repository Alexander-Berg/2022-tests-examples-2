import datetime
import json

import pytest

from tests_subventions_events_filter import eventus_tools
from . import test_common


def _get_events_from_pg(pgsql):
    cursor = pgsql['subventions-events-filter'].cursor()
    cursor.execute(
        """SELECT dbid_uuid, event_time, updated_at, event_type_bits
         FROM subventions_events_filter.events
         ORDER BY id;""",
    )
    return [
        {
            'dbid_uuid': row[0],
            'event_time': row[1],
            'updated_at': row[2],
            'event_type_bits': row[3],
        }
        for row in cursor
    ]


def _put_events_to_pg(pgsql, events):
    cursor = pgsql['subventions-events-filter'].cursor()
    rows = [
        (
            e['dbid_uuid'],
            e['event_time'],
            e['updated_at'],
            e['event_type_bits'],
        )
        for e in events
    ]
    cursor.executemany(
        """INSERT INTO subventions_events_filter.events (
            dbid_uuid, event_time, updated_at, event_type_bits
        )
         VALUES (
            %s, %s, %s, %s
        );""",
        rows,
    )


@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_EVENTS_PROCESSING={
        'enable_storing_to_db': True,
        'events_processor': {
            'enabled': False,
            'timeout_ms': 100,
            'batch_size': 100,
        },
    },
)
async def test_receive_subventions_tags_updates(
        taxi_subventions_events_filter,
        testpoint,
        taxi_eventus_orchestrator_mock,
        mockserver,
        pgsql,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_subventions_events_filter,
        eventus_tools.create_pipelines(bulk_size_threshold=1),
    )

    events = [
        json.dumps(
            {
                'topic': 'subventions',
                'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                'profile_id': 'f8d769f7fe66414b891a1c87aa346119',
                'car_id': '6cc729e3caee4959a77490c5772a23c7',
                'unique_driver_id': '5b05621ee6c22ea265484a41',
                'old_tags': ['2orders'],
                'new_tags': ['2orders', 'moscow_tag'],
                'source_timestamp': 1652340800559,
            },
        ),
    ]

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    response = await taxi_subventions_events_filter.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'tags-events-subventions',
                'data': '\n'.join(events),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()

    assert _get_events_from_pg(pgsql) == [
        {
            'dbid_uuid': (
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                'f8d769f7fe66414b891a1c87aa346119'
            ),
            'event_time': datetime.datetime.fromisoformat(
                '2022-05-12T10:33:20.559000+03:00',
            ),
            'updated_at': test_common.DOESNT_MATTER,
            'event_type_bits': 0x0001,
        },
    ]


@pytest.mark.servicetest
@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_EVENTS_PROCESSING={
        'enable_storing_to_db': True,
        'events_processor': {
            'enabled': False,
            'timeout_ms': 100,
            'batch_size': 100,
        },
    },
)
async def test_receive_geohierarchy_updates(
        taxi_subventions_events_filter,
        testpoint,
        taxi_eventus_orchestrator_mock,
        mockserver,
        pgsql,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_subventions_events_filter,
        eventus_tools.create_pipelines(bulk_size_threshold=1),
    )

    events = [
        json.dumps(
            {
                'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                'driver_id': 'f8d769f7fe66414b891a1c87aa346119',
                'geo_hierarchy': [
                    'br_root',
                    'br_russia',
                    'br_tsentralniy_region',
                    'br_moscow',
                ],
                'updated_at': '2022-05-25T12:35:56.595+03:00',
            },
        ),
    ]

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    response = await taxi_subventions_events_filter.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'contractor-geo-hierarchies',
                'data': '\n'.join(events),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()

    assert _get_events_from_pg(pgsql) == [
        {
            'event_time': datetime.datetime.fromisoformat(
                '2022-05-25T12:35:56.595+03:00',
            ),
            'updated_at': test_common.DOESNT_MATTER,
            'event_type_bits': 0x0002,
            'dbid_uuid': (
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                'f8d769f7fe66414b891a1c87aa346119'
            ),
        },
    ]


@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_EVENTS_PROCESSING={
        'enable_storing_to_db': True,
        'events_processor': {
            'enabled': True,
            'timeout_ms': 100,
            'batch_size': 100,
        },
    },
)
@pytest.mark.now('2022-01-01T12:02:00+03:00')
@pytest.mark.parametrize(
    'handlers, expected_payload',
    [
        (None, {'event_id': test_common.DOESNT_MATTER}),
        (
            ['schedule', 'summary'],
            {
                'event_id': test_common.DOESNT_MATTER,
                'updated': ['schedule', 'summary'],
            },
        ),
    ],
)
async def test_process_events(
        taxi_subventions_events_filter,
        taxi_config,
        pgsql,
        mockserver,
        handlers,
        expected_payload,
):
    db_events = [
        {
            'dbid_uuid': (
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                'f8d769f7fe66414b891a1c87aa346119'
            ),
            'event_time': datetime.datetime.fromisoformat(
                '2022-01-01T12:00:00+03:00',
            ),
            'updated_at': datetime.datetime.fromisoformat(
                '2022-01-01T12:01:00+03:00',
            ),
            'event_type_bits': 0x0001,
        },
    ]

    if handlers:
        taxi_config.set_values(
            {
                'SUBVENTIONS_EVENTS_FILTER_EVENTS_ENABLED_HANDLERS': {
                    'handlers': handlers,
                },
            },
        )

    _put_events_to_pg(pgsql, db_events)

    @mockserver.json_handler('/client-events/push')
    def _client_events_push(request):
        assert request.json == {
            'service': 'yandex.pro',
            'channel': (
                'contractor:7f74df331eb04ad78bc2ff25ff88a8f2_'
                'f8d769f7fe66414b891a1c87aa346119'
            ),
            'event': 'subventions_updated',
            'payload': expected_payload,
        }
        return {'version': '1'}

    await taxi_subventions_events_filter.run_task('events-processor')
    assert _client_events_push.times_called == 1

    assert _get_events_from_pg(pgsql) == []


@pytest.mark.parametrize(
    'mock_now, event_updated_at, update_lag_ms, expect_sent',
    [
        (
            # mock_now
            '2022-01-01T12:01:00+03:00',
            # event_updated_at
            '2022-01-01T12:00:59+03:00',
            # update_lag_ms
            500,
            # expect_sent
            True,
        ),
        (
            # mock_now
            '2022-01-01T12:01:00+03:00',
            # event_updated_at
            '2022-01-01T12:00:59+03:00',
            # update_lag_ms
            5000,
            # expect_sent
            False,
        ),
    ],
)
async def test_process_events_update_lag(
        taxi_subventions_events_filter,
        taxi_config,
        mocked_time,
        pgsql,
        mockserver,
        mock_now,
        event_updated_at,
        update_lag_ms,
        expect_sent,
):
    taxi_config.set_values(
        {
            'SUBVENTIONS_EVENTS_FILTER_EVENTS_PROCESSING': {
                'enable_storing_to_db': True,
                'events_processor': {
                    'enabled': True,
                    'timeout_ms': 100,
                    'batch_size': 100,
                    'update_lag_ms': update_lag_ms,
                },
            },
        },
    )
    mocked_time.set(datetime.datetime.fromisoformat(mock_now))

    db_events = [
        {
            'dbid_uuid': (
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                'f8d769f7fe66414b891a1c87aa346119'
            ),
            'event_time': datetime.datetime.fromisoformat(
                '2022-01-01T12:00:00+03:00',
            ),
            'updated_at': datetime.datetime.fromisoformat(event_updated_at),
            'event_type_bits': 0x0001,
        },
    ]

    _put_events_to_pg(pgsql, db_events)

    @mockserver.json_handler('/client-events/push')
    def _client_events_push(request):
        return {'version': '1'}

    await taxi_subventions_events_filter.run_task('events-processor')
    assert _client_events_push.times_called == (1 if expect_sent else 0)
    assert len(_get_events_from_pg(pgsql)) == (0 if expect_sent else 1)


@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_EVENTS_PROCESSING={
        'enable_storing_to_db': True,
        'events_processor': {
            'enabled': True,
            'timeout_ms': 100,
            'batch_size': 100,
            'dry_mode': True,
        },
    },
)
@pytest.mark.now('2022-01-01T12:02:00+03:00')
async def test_process_events_dry_mode(
        taxi_subventions_events_filter, pgsql, mockserver,
):
    db_events = [
        {
            'dbid_uuid': (
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                'f8d769f7fe66414b891a1c87aa346119'
            ),
            'event_time': datetime.datetime.fromisoformat(
                '2022-01-01T12:00:00+03:00',
            ),
            'updated_at': datetime.datetime.fromisoformat(
                '2022-01-01T12:01:00+03:00',
            ),
            'event_type_bits': 0x0001,
        },
    ]

    _put_events_to_pg(pgsql, db_events)

    @mockserver.json_handler('/client-events/push')
    def _client_events_push(request):
        return {'version': '1'}

    await taxi_subventions_events_filter.run_task('events-processor')
    assert _client_events_push.times_called == 0
    assert _get_events_from_pg(pgsql) == []
