# -*- coding: utf-8 -*-

import pytest


# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76'
    'Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXDiiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848P'
    'W-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkH'
    'R3s'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'rider-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_400(suffix, tvm, code, taxi_rider_metrics_storage):
    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code if code == 401 else 200


@pytest.mark.config(RIDER_METRICS_STORAGE_REQUEST_LIMITS={'__default__': 1})
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql(
    'dbridermetrics',
    files=['common.sql', 'v1_events_history_or_processed.sql'],
)
async def test_v1_events_processed_limit_above_max(taxi_rider_metrics_storage):
    # XXX: it is also checks no exception thrown on request with limit gt max
    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={'user_id': '100000000000000000000000', 'limit': 10},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
        ],
    }


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql(
    'dbridermetrics',
    files=['common.sql', 'v1_events_history_or_processed.sql'],
)
@pytest.mark.parametrize('from_replica', (True, False))
async def test_v1_events_processed(
        taxi_rider_metrics_storage, taxi_config, from_replica,
):
    taxi_config.set_values(
        {'RIDER_METRICS_STORAGE_EVENTS_PROCESSED_FROM_REPLICA': from_replica},
    )
    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed', json={},
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed', json={'user_id': 'bad udid'},
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed', json={'user_id': '100000000000000000000000'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:20:00+00:00',
                'event_id': '3',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:10:00+00:00',
                'event_id': '2',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'created': '2000-01-01T00:00:00+00:00',
                'event_id': '1',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': 'order_id',
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={'user_id': '100000000000000000000000', 'limit': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:20:00+00:00',
                'event_id': '3',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={'user_id': 'Q', 'datetime_from': '2000-01-01T00:05:00+0000'},
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={
            'user_id': '100000000000000000000000',
            'datetime_from': '2000-01-01T00:25:00+0000',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={
            'user_id': '100000000000000000000000',
            'datetime_from': '2000-01-01T00:25:00+0000',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={
            'user_id': '100000000000000000000000',
            'datetime_from': '2000-01-01T00:25:00+0000',
            'event_types': [],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={
            'user_id': '100000000000000000000000',
            'event_types': ['type-X'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:20:00+00:00',
                'event_id': '3',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:00:00+00:00',
                'event_id': '1',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': 'order_id',
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={
            'user_id': '100000000000000000000000',
            'event_types': ['type-Y'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:10:00+00:00',
                'event_id': '2',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
        ],
    }

    response = await taxi_rider_metrics_storage.post(
        'v1/events/processed',
        json={
            'user_id': '100000000000000000000000',
            'event_types': ['type-X', 'type-Y'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'created': '2000-01-01T00:30:00+00:00',
                'event_id': '4',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:20:00+00:00',
                'event_id': '3',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': '',
                'type': 'type-X',
            },
            {
                'created': '2000-01-01T00:10:00+00:00',
                'event_id': '2',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': '',
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'created': '2000-01-01T00:00:00+00:00',
                'event_id': '1',
                'extra_data': '{}',
                'descriptor': '',
                'order_id': 'order_id',
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
        ],
    }
