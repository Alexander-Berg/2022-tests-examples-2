import pytest


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
async def test_descriptor_and_extra_data(taxi_driver_metrics_storage, pgsql):
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
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
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'type': 'user_test',
                        },
                        'event_id': 2,
                        'extra_data': {},
                        'tariff_zone': 'spb',
                        'type': 'type-Y',
                    },
                    {
                        'created': '2000-01-01T00:20:00+00:00',
                        'event_id': 3,
                        'extra_data': {'extra_test': 'extra_test'},
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-01T00:40:00+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'type': 'user_test',
                        },
                        'event_id': 4,
                        'extra_data': {'extra_test': 'extra_test'},
                        'tariff_zone': 'spb',
                        'type': 'type-Y',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '100000000000000000000000',
            },
        ],
    }

    for x in range(1, 5):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete', json={'event_id': x, 'ticket_id': -1},
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
    assert response.json() == {
        'events': [
            {
                'event_id': 1,
                'created': '2000-01-01T00:00:00+00:00',
                'order_id': 'order_id',
                'extra_data': '{}',
                'extra': {},
                'tariff_zone': 'moscow',
                'type': 'type-X',
            },
            {
                'event_id': 2,
                'created': '2000-01-01T00:10:00+00:00',
                'extra_data': (
                    '{"descriptor":{"tags":'
                    '["yam-yam","tas_teful"],"type":"user_test"}}'
                ),
                'extra': {},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'type': 'user_test',
                },
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
            {
                'event_id': 3,
                'created': '2000-01-01T00:20:00+00:00',
                'extra_data': '{"extra_test":"extra_test"}',
                'extra': {'extra_test': 'extra_test'},
                'type': 'type-X',
            },
            {
                'event_id': 4,
                'created': '2000-01-01T00:40:00+00:00',
                'extra_data': (
                    '{"extra_test":"extra_test","descriptor":{"tags":'
                    '["yam-yam","tas_teful"],"type":"user_test"}}'
                ),
                'extra': {'extra_test': 'extra_test'},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'type': 'user_test',
                },
                'tariff_zone': 'spb',
                'type': 'type-Y',
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={'unique_driver_id': '100000000000000000000000'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:40:00+00:00',
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'event_id': '4',
                    'extra': {'extra_test': 'extra_test'},
                    'extra_data': '',
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': 'spb',
                    'type': 'type-Y',
                },
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:20:00+00:00',
                    'event_id': '3',
                    'extra': {'extra_test': 'extra_test'},
                    'extra_data': '',
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': '',
                    'type': 'type-X',
                },
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:10:00+00:00',
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'event_id': '2',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': '',
                    'order_id': '',
                    'park_driver_profile_id': '',
                    'tariff_zone': 'spb',
                    'type': 'type-Y',
                },
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '1',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': '',
                    'order_id': 'order_id',
                    'park_driver_profile_id': '',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
            },
        ],
    }
