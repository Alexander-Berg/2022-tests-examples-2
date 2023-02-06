# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_rider_metrics_storage import util

UNIQUE_RIDER_ID0 = '0123456789AB0123456789AB'


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
    RIDER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS={
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
    RIDER_METRICS_STORAGE_EVENTS_SPLITTING=2,
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_pipeline(taxi_rider_metrics_storage, pgsql, mocked_time):
    for x in range(3):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'user_id': UNIQUE_RIDER_ID0,
                'type': 'type-Z',
                'created': '2019-01-01T00:00:0%s+00:00' % str(x),
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'name': 'user_test',
                },
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 5))
    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'events': [
                    {
                        'created': '2019-01-01T00:00:00+00:00',
                        'descriptor': {
                            'name': 'user_test',
                            'tags': ['yam-yam', 'tas_teful'],
                        },
                        'extra_data': {'extra_field': '0'},
                        'event_id': 1,
                        'order_id': 'order_id: 0',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:01+00:00',
                        'event_id': 2,
                        'descriptor': {
                            'name': 'user_test',
                            'tags': ['yam-yam', 'tas_teful'],
                        },
                        'extra_data': {'extra_field': '1'},
                        'order_id': 'order_id: 1',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:02+00:00',
                        'descriptor': {
                            'name': 'user_test',
                            'tags': ['yam-yam', 'tas_teful'],
                        },
                        'extra_data': {'extra_field': '2'},
                        'event_id': 3,
                        'order_id': 'order_id: 2',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                ],
                'ticket_id': -1,
                'user_id': '0123456789AB0123456789AB',
            },
        ],
    }

    for x in range(1, 4):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/complete', json={'event_id': x, 'ticket_id': -1},
        )
        assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}

    assert (
        util.to_map(
            util.select_named(
                'select * from events.logs_64_partitioned', pgsql,
            ),
            'event_id',
        )
        == {
            1: {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': 1,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"0"}',
                'order_id': 'order_id: 0',
                'processed': datetime.datetime(2019, 1, 1, 0, 0, 5),
                'tariff_zone_id': 1,
                'unique_rider_id': 1,
            },
            2: {
                'created': datetime.datetime(2019, 1, 1, 0, 0, 1),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': 2,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"1"}',
                'order_id': 'order_id: 1',
                'processed': datetime.datetime(2019, 1, 1, 0, 0, 5),
                'tariff_zone_id': 1,
                'unique_rider_id': 1,
            },
            3: {
                'created': datetime.datetime(2019, 1, 1, 0, 0, 2),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': 3,
                'event_type_id': 3,
                'extra_data': '{"extra_field":"2"}',
                'order_id': 'order_id: 2',
                'processed': datetime.datetime(2019, 1, 1, 0, 0, 5),
                'tariff_zone_id': 1,
                'unique_rider_id': 1,
            },
        }
    )

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed', json={'user_id': UNIQUE_RIDER_ID0},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2019-01-01T00:00:02+00:00',
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': '3',
                'extra_data': '{"extra_field":"2"}',
                'order_id': 'order_id: 2',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
            {
                'created': '2019-01-01T00:00:01+00:00',
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': '2',
                'extra_data': '{"extra_field":"1"}',
                'order_id': 'order_id: 1',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
            {
                'created': '2019-01-01T00:00:00+00:00',
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'event_id': '1',
                'extra_data': '{"extra_field":"0"}',
                'order_id': 'order_id: 0',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/history',
        json={
            'user_id': UNIQUE_RIDER_ID0,
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event_id': 1,
                'created': '2019-01-01T00:00:00+00:00',
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'extra_data': '{"extra_field":"0"}',
                'order_id': 'order_id: 0',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
            {
                'event_id': 2,
                'created': '2019-01-01T00:00:01+00:00',
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'extra_data': '{"extra_field":"1"}',
                'order_id': 'order_id: 1',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
            {
                'event_id': 3,
                'created': '2019-01-01T00:00:02+00:00',
                'descriptor': (
                    '{"name":"user_test","tags":["yam-yam","tas_teful"]}'
                ),
                'extra_data': '{"extra_field":"2"}',
                'order_id': 'order_id: 2',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
        ],
    }
