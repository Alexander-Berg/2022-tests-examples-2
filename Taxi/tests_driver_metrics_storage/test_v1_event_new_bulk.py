# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_driver_metrics_storage import util

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76'
    'Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXDiiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848P'
    'W-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkH'
    'R3s'
)

WRONG_TIMESTAMP = '2019-01-01T00:00:00+0000'
CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UNIQUE_DRIVER_ID0 = '0123456789AB0123456789AB'
UNIQUE_DRIVER_ID1 = '02468AbCdEfF02468AbCdEfF'
UNIQUE_DRIVER_WRONG = ''


def sort_item_events(item):
    item['events'].sort(key=lambda event: event['event_id'])
    return item


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_v1_event_new_bulk_400(
        suffix, tvm, code, taxi_driver_metrics_storage,
):
    response = await taxi_driver_metrics_storage.post(
        'v1/event/new/bulk' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_bulk_missed_parameter(taxi_driver_metrics_storage):
    for field in ['idempotency_token', 'unique_driver_id', 'type', 'created']:
        json_object = {
            'idempotency_token': 'idempotency_token-' + field,
            'unique_driver_id': UNIQUE_DRIVER_ID0,
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
        }
        del json_object[field]
        response = await taxi_driver_metrics_storage.post(
            'v1/event/new/bulk', json={'events': [json_object]},
        )
        assert response.status_code == 400
        assert response.json()['code'] == '400'


@pytest.mark.config(DRIVER_METRICS_STORAGE_EVENT_NEW_BULK_LIMIT=2)
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_bulk_exceed_limit(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v1/event/new/bulk',
        json={
            'events': [
                {
                    'idempotency_token': 'idempotency_token-0',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-1',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '1'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 1',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-2',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '2'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 2',
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )
    assert [response.status_code, response.json()] == [
        400,
        {'code': '400', 'message': 'events number 3 exceeds the limit 2'},
    ]


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
    DRIVER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS={
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
    DRIVER_METRICS_STORAGE_EVENTS_SPLITTING=2,
)
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_event_new_bulk_complete(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    response = await taxi_driver_metrics_storage.post(
        'v1/event/new/bulk',
        json={
            'events': [
                {
                    'idempotency_token': 'idempotency_token-0',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-1',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '1'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 1',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-2',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '2'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 2',
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )
    assert [response.status_code, response.json()] == [
        200,
        {
            'events': [
                {'idempotency_token': 'idempotency_token-0'},
                {'idempotency_token': 'idempotency_token-1'},
                {'idempotency_token': 'idempotency_token-2'},
            ],
        },
    ]

    response = await taxi_driver_metrics_storage.post(
        'v1/event/new/bulk',
        json={
            'events': [
                {
                    'idempotency_token': 'idempotency_token-0',
                    'unique_driver_id': UNIQUE_DRIVER_ID1,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-1',
                    'unique_driver_id': UNIQUE_DRIVER_ID1,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '1'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 1',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-2',
                    'unique_driver_id': UNIQUE_DRIVER_ID1,
                    'type': 'type-Z',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '2'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 2',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-3',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-wrong',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
                {
                    'idempotency_token': 'idempotency_token-4',
                    'unique_driver_id': UNIQUE_DRIVER_ID0,
                    'type': 'type-wrong-2',
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': {'extra_field': '0'},
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'order_id': 'order_id: 0',
                    'tariff_zone': 'moscow',
                },
            ],
        },
    )

    assert [response.status_code, response.json()] == [
        200,
        {
            'events': [
                {'idempotency_token': 'idempotency_token-0'},
                {'idempotency_token': 'idempotency_token-1'},
                {'idempotency_token': 'idempotency_token-2'},
                {
                    'idempotency_token': 'idempotency_token-3',
                    'error': {
                        'code': '403',
                        'message': 'invalid event type type-wrong',
                    },
                },
                {
                    'idempotency_token': 'idempotency_token-4',
                    'error': {
                        'code': '403',
                        'message': 'invalid event type type-wrong-2',
                    },
                },
            ],
        },
    ]

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert (
        util.to_map(
            response.json()['items'], 'unique_driver_id', sort_item_events,
        )
        == {
            '0123456789AB0123456789AB': {
                'events': [
                    {
                        'created': '2019-01-01T00:00:00+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'type': 'user_test',
                        },
                        'event_id': 10,
                        'extra_data': {'extra_field': '0'},
                        'order_id': 'order_id: 0',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:00+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'type': 'user_test',
                        },
                        'event_id': 11,
                        'extra_data': {'extra_field': '1'},
                        'order_id': 'order_id: 1',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:00+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'type': 'user_test',
                        },
                        'event_id': 12,
                        'extra_data': {'extra_field': '2'},
                        'order_id': 'order_id: 2',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '0123456789AB0123456789AB',
            },
            '100000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'order_id': 'order_id',
                        'tariff_zone': 'moscow',
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:10:00+00:00',
                        'event_id': 2,
                        'extra_data': {},
                        'tariff_zone': 'spb',
                        'type': 'type-Y',
                    },
                    {
                        'created': '2000-01-01T00:20:00+00:00',
                        'event_id': 3,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:30:00+00:00',
                        'event_id': 4,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '100000000000000000000000',
            },
            '200000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:10:00+00:00',
                        'event_id': 9,
                        'extra_data': {},
                        'order_id': 'order_id2',
                        'tariff_zone': 'spb',
                        'type': 'type-Y',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '200000000000000000000000',
            },
            '300000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:40:00+00:00',
                        'event_id': 5,
                        'extra_data': {},
                        'type': 'type-Z',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '300000000000000000000000',
            },
            '400000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:50+00:00',
                        'event_id': 6,
                        'extra_data': {},
                        'tariff_zone': 'moscow',
                        'type': 'type-Y',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '400000000000000000000000',
            },
            '500000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:01:00+00:00',
                        'event_id': 7,
                        'extra_data': {},
                        'tariff_zone': 'spb',
                        'type': 'type-X',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '500000000000000000000000',
            },
            '600000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:01:10+00:00',
                        'event_id': 8,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '600000000000000000000000',
            },
        }
    )

    for item in response.json()['items']:
        for event in item['events']:
            response = await taxi_driver_metrics_storage.post(
                'v3/event/complete',
                json={
                    'event_id': event['event_id'],
                    'ticket_id': item['ticket_id'],
                },
            )
            assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert [response.status_code, response.json()] == [200, {'items': []}]
