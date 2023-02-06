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

EXTRA_DATA_EXPECTED = ''  # deprecated field

EXTRA_EXPECTED = {
    'activity_value': 75,
    'activity_change': 0,
    'driver_id': '400000000000_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    'time_to_a': 26,
    'distance_to_a': 52,
    'tariff_class': 'econom',
    'dtags': [],
}

DESCRIPTOR_EXPECTED = {'type': 'type', 'tags': ['tag1', 'tag2']}


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_400(suffix, tvm, code, taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.config(DRIVER_METRICS_STORAGE_REQUEST_LIMITS={'__default__': 1})
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['events_processed_and_history.sql'])
async def test_v1_events_processed_limit_above_max(
        taxi_driver_metrics_storage,
):
    # XXX: it is also checks no exception thrown on request with limit gt max
    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={'unique_driver_id': '100000000000000000000000', 'limit': 10},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:30:00+00:00',
                    'event_id': '4',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 40,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_CLEANER_SETTINGS={
        'wallet_logs_expire_days': 20000,
        'wallet_logs_clean_limit': 300,
        'wallet_logs_clean_repeat': 1,
        'events_expire_days': 20000,
        'events_clean_limit': 300,
        'events_clean_repeat': 1,
        'events_logs_partitioned_clean_limit': 300,
    },
)
@pytest.mark.pgsql('drivermetrics', files=['events_processed_and_history.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.parametrize('from_replica', (True, False))
async def test_processed_v3(
        taxi_driver_metrics_storage, taxi_config, from_replica,
):

    taxi_config.set_values(
        {'DRIVER_METRICS_STORAGE_EVENTS_PROCESSED_FROM_REPLICA': from_replica},
    )
    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed', json={},
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed', json={'unique_driver_id': 'bad udid'},
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={'unique_driver_id': '100000000000000000000000'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:30:00+00:00',
                    'event_id': '4',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 40,
            },
            {
                'activity_change': 300,
                'event': {
                    'datetime': '2000-01-01T00:20:00+00:00',
                    'event_id': '3',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 30,
            },
            {
                'activity_change': 200,
                'event': {
                    'datetime': '2000-01-01T00:10:00+00:00',
                    'event_id': '2',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': 'order_alias',
                    'order_id': '',
                    'park_driver_profile_id': 'dbid_uuid2',
                    'tariff_zone': 'spb',
                    'type': 'type-Y',
                },
                'loyalty_change': 20,
            },
            {
                'activity_change': 100,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '1',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 10,
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={'unique_driver_id': '100000000000000000000000', 'limit': 2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:30:00+00:00',
                    'event_id': '4',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 40,
            },
            {
                'activity_change': 300,
                'event': {
                    'datetime': '2000-01-01T00:20:00+00:00',
                    'event_id': '3',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 30,
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={
            'unique_driver_id': '100000000000000000000000',
            'park_driver_profile_id': 'dbid_uuid1',
            'alias_ids': ['order_alias'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'activity_change': 100,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '1',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 10,
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={
            'unique_driver_id': 'Q',
            'datetime_from': '2000-01-01T00:05:00+0000',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={
            'unique_driver_id': '100000000000000000000000',
            'datetime_from': '2000-01-01T00:25:00+0000',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:30:00+00:00',
                    'event_id': '4',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 40,
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={
            'unique_driver_id': '100000000000000000000000',
            'datetime_from': '2000-01-01T00:25:00+0000',
            'with_additional_info': False,
            'event_types': [],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:30:00+00:00',
                    'event_id': '4',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                # loyalty_change should be unset
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={
            'unique_driver_id': '100000000000000000000000',
            'event_types': ['type-X'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:30:00+00:00',
                    'event_id': '4',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 40,
            },
            {
                'activity_change': 300,
                'event': {
                    'datetime': '2000-01-01T00:20:00+00:00',
                    'event_id': '3',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
                'loyalty_change': 30,
            },
            {
                'activity_change': 100,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '1',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 10,
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={
            'unique_driver_id': '100000000000000000000000',
            'event_types': ['type-Y'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'activity_change': 200,
                'event': {
                    'datetime': '2000-01-01T00:10:00+00:00',
                    'event_id': '2',
                    'extra_data': EXTRA_DATA_EXPECTED,
                    'extra': EXTRA_EXPECTED,
                    'descriptor': DESCRIPTOR_EXPECTED,
                    'order_alias': 'order_alias',
                    'order_id': '',
                    'park_driver_profile_id': 'dbid_uuid2',
                    'tariff_zone': 'spb',
                    'type': 'type-Y',
                },
                'loyalty_change': 20,
            },
        ],
    }
