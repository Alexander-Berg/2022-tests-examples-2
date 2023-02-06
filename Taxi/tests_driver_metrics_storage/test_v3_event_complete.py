# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_driver_metrics_storage import util

CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UDID_ID0 = '0123456789AB0123456789AB'

CONFIG_VALUES = {
    'DRIVER_METRICS_STORAGE_EVENTS_TTL': {
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
    'DRIVER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS': {
        'new_event_age_limit_mins': 720,
        'idempotency_token_ttl_mins': 1440,
        'default_event_ttl_hours': 168,
        'processing_ticket_ttl_secs': 60,
        'processing_lag_msecs': 200,
        'default_unprocessed_list_limit': 100,
        'round_robin_process': False,
        'non_transactional_polling': True,
        'polling_max_passes': 3,
    },
    'DRIVER_METRICS_STORAGE_EVENTS_SPLITTING': 2,
    'DRIVER_POINTS_FIRST_VALUE': {'__default__': 99},
}


@pytest.mark.config(**CONFIG_VALUES)
@pytest.mark.pgsql(
    'drivermetrics', files=['common.sql', 'unprocessed_events.sql'],
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v3_event_complete_basic(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    for x in range(1, 5):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete', json={'event_id': x, 'ticket_id': -1},
        )
        assert [response.status_code, response.json()] == [200, {}]

    await taxi_driver_metrics_storage.invalidate_caches()

    assert [
        util.select_named('SELECT count(*) FROM events.queue_64', pgsql),
    ] == [[{'count': 0}]]
    assert [
        util.select_named(
            'SELECT count(*) FROM data.logs_64_partitioned', pgsql,
        ),
    ] == [[{'count': 0}]]
    assert [
        util.select_named('SELECT count(*) FROM data.activity_values', pgsql),
    ] == [[{'count': 0}]]


@pytest.mark.config(**CONFIG_VALUES)
@pytest.mark.pgsql(
    'drivermetrics', files=['common.sql', 'unprocessed_events.sql'],
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v3_event_complete_with_activity(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    for x in range(1, 5):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete',
            json={
                'event_id': x,
                'ticket_id': -1,
                'activity': {'increment': x, 'value_to_set': 80 + x},
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    await taxi_driver_metrics_storage.invalidate_caches()

    assert util.select_named(
        'SELECT count(*) FROM events.queue_64', pgsql,
    ) == [{'count': 0}]

    assert (
        util.to_map(
            util.select_named('SELECT * FROM data.logs_64_partitioned', pgsql),
            'event_id',
        )
        == {
            1: {
                'activity_increment': 1,
                'complete_score_increment': None,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 1,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1001,
            },
            2: {
                'activity_increment': 2,
                'complete_score_increment': None,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 2,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1002,
            },
            3: {
                'activity_increment': 3,
                'complete_score_increment': None,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 3,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1003,
            },
            4: {
                'activity_increment': 4,
                'complete_score_increment': None,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 4,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1004,
            },
        }
    )

    assert (
        util.to_map(
            util.select_named('SELECT * FROM data.activity_values', pgsql),
            'udid_id',
        )
        == {
            1001: {
                'complete_score_value': None,
                'udid_id': 1001,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 81,
            },
            1002: {
                'complete_score_value': None,
                'udid_id': 1002,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 82,
            },
            1003: {
                'complete_score_value': None,
                'udid_id': 1003,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 83,
            },
            1004: {
                'complete_score_value': None,
                'udid_id': 1004,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 84,
            },
        }
    )


@pytest.mark.config(**CONFIG_VALUES)
@pytest.mark.pgsql(
    'drivermetrics', files=['common.sql', 'unprocessed_events.sql'],
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v3_event_complete_with_complete_score(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    for x in range(1, 5):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete',
            json={
                'event_id': x,
                'ticket_id': -1,
                'complete_score': {'value_to_set': 80 + x, 'increment': x},
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    await taxi_driver_metrics_storage.invalidate_caches()

    assert util.select_named(
        'SELECT count(*) FROM events.queue_64', pgsql,
    ) == [{'count': 0}]

    assert (
        util.to_map(
            util.select_named('SELECT * FROM data.logs_64_partitioned', pgsql),
            'event_id',
        )
        == {
            1: {
                'activity_increment': None,
                'complete_score_increment': 1,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 1,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1001,
            },
            2: {
                'activity_increment': None,
                'complete_score_increment': 2,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 2,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1002,
            },
            3: {
                'activity_increment': None,
                'complete_score_increment': 3,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 3,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1003,
            },
            4: {
                'activity_increment': None,
                'complete_score_increment': 4,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 4,
                'loyalty_increment': None,
                'priority_absolute': None,
                'priority_increment': None,
                'udid_id': 1004,
            },
        }
    )

    assert (
        util.to_map(
            util.select_named('SELECT * FROM data.activity_values', pgsql),
            'udid_id',
        )
        == {
            1001: {
                'complete_score_value': 81,
                'udid_id': 1001,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 99,
            },
            1002: {
                'complete_score_value': 82,
                'udid_id': 1002,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 99,
            },
            1003: {
                'complete_score_value': 83,
                'udid_id': 1003,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 99,
            },
            1004: {
                'complete_score_value': 84,
                'udid_id': 1004,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 99,
            },
        }
    )


@pytest.mark.config(**CONFIG_VALUES)
@pytest.mark.pgsql(
    'drivermetrics', files=['common.sql', 'unprocessed_events.sql'],
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v3_event_complete_full_stack(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    for x in range(1, 5):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete',
            json={
                'event_id': x,
                'ticket_id': -1,
                'activity': {'value_to_set': 80 + x, 'increment': x},
                'complete_score': {'value_to_set': 70 + x, 'increment': x},
                'priority': {'absolute_value': 10 + x, 'increment': x},
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    await taxi_driver_metrics_storage.invalidate_caches()

    assert util.select_named(
        'SELECT count(*) FROM events.queue_64', pgsql,
    ) == [{'count': 0}]

    assert (
        util.to_map(
            util.select_named('SELECT * FROM data.logs_64_partitioned', pgsql),
            'event_id',
        )
        == {
            1: {
                'activity_increment': 1,
                'complete_score_increment': 1,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 1,
                'loyalty_increment': None,
                'priority_absolute': 11,
                'priority_increment': 1,
                'udid_id': 1001,
            },
            2: {
                'activity_increment': 2,
                'complete_score_increment': 2,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 2,
                'loyalty_increment': None,
                'priority_absolute': 12,
                'priority_increment': 2,
                'udid_id': 1002,
            },
            3: {
                'activity_increment': 3,
                'complete_score_increment': 3,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 3,
                'loyalty_increment': None,
                'priority_absolute': 13,
                'priority_increment': 3,
                'udid_id': 1003,
            },
            4: {
                'activity_increment': 4,
                'complete_score_increment': 4,
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'event_id': 4,
                'loyalty_increment': None,
                'priority_absolute': 14,
                'priority_increment': 4,
                'udid_id': 1004,
            },
        }
    )

    assert (
        util.to_map(
            util.select_named('SELECT * FROM data.activity_values', pgsql),
            'udid_id',
        )
        == {
            1001: {
                'complete_score_value': 71,
                'udid_id': 1001,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 81,
            },
            1002: {
                'complete_score_value': 72,
                'udid_id': 1002,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 82,
            },
            1003: {
                'complete_score_value': 73,
                'udid_id': 1003,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 83,
            },
            1004: {
                'complete_score_value': 74,
                'udid_id': 1004,
                'updated': datetime.datetime(2019, 1, 1, 0, 0),
                'value': 84,
            },
        }
    )
