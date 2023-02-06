# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_rider_metrics_storage import util

CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
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
async def test_v2_unprocessed_and_complete(
        taxi_rider_metrics_storage, pgsql, mocked_time,
):
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
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'events': [
                    {
                        'created': '2019-01-01T00:00:00+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'name': 'user_test',
                        },
                        'event_id': 1,
                        'extra_data': {'extra_field': '0'},
                        'order_id': 'order_id: 0',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:01+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'name': 'user_test',
                        },
                        'event_id': 2,
                        'extra_data': {'extra_field': '1'},
                        'order_id': 'order_id: 1',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:02+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'name': 'user_test',
                        },
                        'event_id': 3,
                        'extra_data': {'extra_field': '2'},
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
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}


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
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_unprocessed_and_complete_big_values(
        taxi_rider_metrics_storage, pgsql, mocked_time,
):
    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))
    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 300000000000,
                        'extra_data': {},
                        'order_id': 'order_id',
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:10:00+00:00',
                        'event_id': 300000000001,
                        'extra_data': {},
                        'tariff_zone': 'spb',
                        'type': 'type-Y',
                    },
                    {
                        'created': '2000-01-01T00:20:00+00:00',
                        'event_id': 300000000002,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': -1,
                'user_id': '100000000000000000000000',
            },
        ],
    }

    for x in range(3):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/complete',
            json={'event_id': x + 300000000000, 'ticket_id': -1},
        )
        assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}


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
async def test_v2_unprocessed_and_complete_check_limit(
        taxi_rider_metrics_storage, pgsql, mocked_time,
):
    for x in range(100):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'user_id': UNIQUE_RIDER_ID0,
                'type': 'type-Z',
                'created': CORRECT_TIMESTAMP,
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

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 10, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert len(response.json()['items'][0]['events']) == 10

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 20, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert len(response.json()['items'][0]['events']) == 20

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 120, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert len(response.json()['items'][0]['events']) == 100


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
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test_consumer.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_unprocessed_and_complete_check_consumer(
        taxi_rider_metrics_storage, pgsql, mocked_time,
):
    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 10, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == 6

    for i in range(6):
        response = await taxi_rider_metrics_storage.post(
            'v2/events/unprocessed/list',
            json={'limit': 10, 'consumer': {'index': i, 'total': 1001}},
        )
        assert response.status_code == 200
        assert len(response.json()['items'][0]['events']) == 1


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
@pytest.mark.pgsql(
    'dbridermetrics', files=['common.sql', 'test_descriptor.sql'],
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v2_unprocessed_descriptor(taxi_rider_metrics_storage, pgsql):
    assert [
        util.select_named('SELECT count(*) FROM events.queue_64', pgsql),
    ] == [[{'count': 8}]]

    response = await taxi_rider_metrics_storage.post(
        'v2/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    expected_events = {
        '100000000000000000000000': [
            {
                'created': '2000-01-01T00:00:00+00:00',
                'event_id': 300000000001,
                'extra_data': {},
                'order_id': 'order_id',
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:10:00+00:00',
                'event_id': 300000000005,
                'extra_data': {},
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
        ],
        '200000000000000000000000': [
            {
                'created': '2000-01-01T00:10:00+00:00',
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'name': 'user_test',
                },
                'event_id': 300000000002,
                'extra_data': {},
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'created': '2000-01-01T00:20:00+00:00',
                'event_id': 300000000006,
                'extra_data': {},
                'type': 'type-X',
            },
        ],
        '300000000000000000000000': [
            {
                'created': '2000-01-01T00:20:00+00:00',
                'event_id': 300000000003,
                'extra_data': {'extra_test': 'extra_test'},
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:40:00+00:00',
                'descriptor': {'name': 'user_test'},
                'event_id': 300000000007,
                'extra_data': {},
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
        ],
        '400000000000000000000000': [
            {
                'created': '2000-01-01T00:40:00+00:00',
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'name': 'user_test',
                },
                'event_id': 300000000004,
                'extra_data': {'extra_test': 'extra_test'},
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'created': '2000-01-01T00:40:00+00:00',
                'event_id': 300000000008,
                'extra_data': {'extra_test': 'extra_test'},
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
        ],
    }
    check = {}
    for item in response.json()['items']:
        check[item['user_id']] = item['events']
    assert expected_events == check
