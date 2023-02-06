import pytest


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
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_processed_v3_partitioned(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed',
        json={'unique_driver_id': '100000000000000000000000'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '1',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '2',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 111,
            },
            {
                'activity_change': 222,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '3',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
            },
            {
                'activity_change': 444,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '4',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 333,
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '5',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '6',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 666,
            },
            {
                'activity_change': 777,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '7',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
            },
            {
                'activity_change': 999,
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '8',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
                'loyalty_change': 888,
            },
            {
                'event': {
                    'datetime': '2000-01-01T00:00:00+00:00',
                    'event_id': '9',
                    'extra': {},
                    'extra_data': '',
                    'order_alias': 'order_alias',
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-X',
                },
            },
        ],
    }
