# -*- coding: utf-8 -*-

import datetime

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
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_400(suffix, tvm, code, taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v2/events/history' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code if code == 401 else 200


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['events_processed_and_history.sql'])
async def test_v2_events_history(taxi_driver_metrics_storage, pgsql):
    descriptor_expected = {'type': 'type', 'tags': ['tag1', 'tag2']}
    extra_expected = {
        'activity_value': 75,
        'activity_change': 0,
        'driver_id': '400000000000_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'time_to_a': 26,
        'distance_to_a': 52,
        'tariff_class': 'econom',
        'dtags': [],
    }
    extra_data_expected = (
        '{"activity_value":75,"activity_change":0,'
        + '"driver_id":"400000000000_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
        + '"time_to_a":26,"distance_to_a":52,"tariff_class":"econom",'
        + '"dtags":[],"descriptor":{"type":"type","tags":["tag1","tag2"]}}'
    )

    await taxi_driver_metrics_storage.invalidate_caches()

    response = await taxi_driver_metrics_storage.post(
        'v2/events/history',
        json={
            'unique_driver_id': '100000000000000000000000',
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event_id': 1,
                'created': '2000-01-01T00:00:00+00:00',
                'extra_data': extra_data_expected,
                'extra': extra_expected,
                'descriptor': descriptor_expected,
                'order_alias': 'order_alias',
                'order_id': 'order_id',
                'park_driver_profile_id': 'dbid_uuid1',
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
            {
                'event_id': 2,
                'created': '2000-01-01T00:10:00+00:00',
                'extra_data': extra_data_expected,
                'extra': extra_expected,
                'descriptor': descriptor_expected,
                'order_alias': 'order_alias',
                'park_driver_profile_id': 'dbid_uuid2',
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'event_id': 3,
                'created': '2000-01-01T00:20:00+00:00',
                'extra_data': extra_data_expected,
                'extra': extra_expected,
                'descriptor': descriptor_expected,
                'park_driver_profile_id': 'dbid_uuid1',
                'type': 'type-X',
            },
            {
                'event_id': 4,
                'created': '2000-01-01T00:30:00+00:00',
                'extra_data': extra_data_expected,
                'extra': extra_expected,
                'descriptor': descriptor_expected,
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v2/events/history',
        json={
            'unique_driver_id': '100000000000000000000000',
            'created_after': '2000-01-01T00:20:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event_id': 3,
                'created': '2000-01-01T00:20:00+00:00',
                'extra_data': extra_data_expected,
                'extra': extra_expected,
                'descriptor': descriptor_expected,
                'park_driver_profile_id': 'dbid_uuid1',
                'type': 'type-X',
            },
            {
                'event_id': 4,
                'created': '2000-01-01T00:30:00+00:00',
                'extra_data': extra_data_expected,
                'extra': extra_expected,
                'descriptor': descriptor_expected,
                'type': 'type-X',
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v2/events/history',
        json={
            'unique_driver_id': 'X00000000000000000000000',
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'events': []}


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_REQUEST_LIMITS={
        '__default__': 1000,
        'events/history': 10,
    },
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 123},
        'type-Z': {'__default__': 7 * 24 * 60},
    },
    DRIVER_METRICS_STORAGE_EVENTS_SPLITTING=2,
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.pgsql('drivermetrics', files=['common.sql'])
async def test_v2_events_history_limit(
        taxi_driver_metrics_storage, mocked_time, pgsql,
):
    await taxi_driver_metrics_storage.invalidate_caches()

    date = datetime.datetime(2018, 12, 31, 23, 0, 0)
    delta = datetime.timedelta(minutes=1)

    for x in range(33):
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'unique_driver_id': '100000000000000000000000',
                'type': 'type-Z',
                'created': (date + delta * x).strftime(
                    '%Y-%m-%dT%H:%M:%S+00:00',
                ),
                'extra_data': {'extra_field': str(x)},
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 5))

    for x in range(33):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete', json={'event_id': x + 1, 'ticket_id': -1},
        )
        assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v2/events/history',
        json={
            'unique_driver_id': '100000000000000000000000',
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 10
    assert list(map(lambda e: e['event_id'], response.json()['events'])) == [
        x for x in range(1, 11)
    ]

    response = await taxi_driver_metrics_storage.post(
        'v2/events/history',
        json={
            'unique_driver_id': '100000000000000000000000',
            'created_after': '2000-01-01T00:00:00+00:00',
            'limit': 5,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['events']) == 5
    assert list(map(lambda e: e['event_id'], response.json()['events'])) == [
        x for x in range(1, 6)
    ]
