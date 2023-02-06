# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_driver_metrics_storage import util

CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UDID_ID0 = '0123456789AB0123456789AB'


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
@pytest.mark.pgsql('drivermetrics', files=['common.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_pipeline(taxi_driver_metrics_storage, pgsql, mocked_time):
    await taxi_driver_metrics_storage.invalidate_caches()
    for x in range(3):
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'unique_driver_id': UDID_ID0,
                'type': 'type-Z',
                'created': '2019-01-01T00:00:%02d+00:00' % x,
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'type': 'user_test',
                },
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
                'order_alias': 'order-alias-' + str(x),
                'park_driver_profile_id': 'dbid_uuid1',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'events': [
                    {
                        'created': '2019-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {'extra_field': '0'},
                        'descriptor': {
                            'type': 'user_test',
                            'tags': ['yam-yam', 'tas_teful'],
                        },
                        'order_alias': 'order-alias-0',
                        'order_id': 'order_id: 0',
                        'park_driver_profile_id': 'dbid_uuid1',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:01+00:00',
                        'event_id': 2,
                        'extra_data': {'extra_field': '1'},
                        'descriptor': {
                            'type': 'user_test',
                            'tags': ['yam-yam', 'tas_teful'],
                        },
                        'order_alias': 'order-alias-1',
                        'order_id': 'order_id: 1',
                        'park_driver_profile_id': 'dbid_uuid1',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    {
                        'created': '2019-01-01T00:00:02+00:00',
                        'event_id': 3,
                        'extra_data': {'extra_field': '2'},
                        'descriptor': {
                            'type': 'user_test',
                            'tags': ['yam-yam', 'tas_teful'],
                        },
                        'order_alias': 'order-alias-2',
                        'order_id': 'order_id: 2',
                        'park_driver_profile_id': 'dbid_uuid1',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '0123456789AB0123456789AB',
            },
        ],
    }

    for x in range(1, 4):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete',
            json={
                'event_id': x,
                'ticket_id': -1,
                'loyalty_increment': x,
                'activity': {'value_to_set': x, 'increment': x},
                'complete_score': {'increment': 1 + x, 'value_to_set': 10 + x},
                'priority': {'increment': 1 + x, 'absolute_value': 20 + x},
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        params={},
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 100},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}

    assert (
        util.to_map(
            util.select_named(
                'select * from data.logs_64_partitioned '
                'order by event_id asc',
                pgsql,
            ),
            'event_id',
        )
        == {
            1: {
                'event_id': 1,
                'udid_id': 1,
                'created': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'activity_increment': 1,
                'loyalty_increment': 1,
                'complete_score_increment': 2,
                'priority_increment': 2,
                'priority_absolute': 21,
            },
            2: {
                'udid_id': 1,
                'event_id': 2,
                'created': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'activity_increment': 2,
                'loyalty_increment': 2,
                'complete_score_increment': 3,
                'priority_increment': 3,
                'priority_absolute': 22,
            },
            3: {
                'udid_id': 1,
                'event_id': 3,
                'created': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'activity_increment': 3,
                'loyalty_increment': 3,
                'complete_score_increment': 4,
                'priority_increment': 4,
                'priority_absolute': 23,
            },
        }
    )

    assert (
        util.to_map(
            util.select_named(
                'select * from events.logs_64_partitioned '
                'order by event_id asc',
                pgsql,
            ),
            'event_id',
        )
        == {
            1: {
                'created': datetime.datetime(2019, 1, 1, 0, 0),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'descriptor': (
                    '{"type":"user_test",' '"tags":["yam-yam","tas_teful"]}'
                ),
                'extra_data': '{"extra_field":"0"}',
                'event_id': 1,
                'event_type_id': 3,
                'order_id': 'order_id: 0',
                'order_alias': 'order-alias-0',
                'processed': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'tariff_zone_id': 1,
                'udid_id': 1,
                'dbid_uuid_id': 1,
            },
            2: {
                'created': datetime.datetime(2019, 1, 1, 0, 0, 1),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'event_id': 2,
                'event_type_id': 3,
                'descriptor': (
                    '{"type":"user_test",' '"tags":["yam-yam","tas_teful"]}'
                ),
                'extra_data': '{"extra_field":"1"}',
                'order_id': 'order_id: 1',
                'order_alias': 'order-alias-1',
                'processed': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'tariff_zone_id': 1,
                'udid_id': 1,
                'dbid_uuid_id': 1,
            },
            3: {
                'created': datetime.datetime(2019, 1, 1, 0, 0, 2),
                'deadline': datetime.datetime(2019, 1, 8, 0, 0),
                'event_id': 3,
                'event_type_id': 3,
                'descriptor': (
                    '{"type":"user_test",' '"tags":["yam-yam","tas_teful"]}'
                ),
                'extra_data': '{"extra_field":"2"}',
                'order_id': 'order_id: 2',
                'order_alias': 'order-alias-2',
                'processed': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'tariff_zone_id': 1,
                'udid_id': 1,
                'dbid_uuid_id': 1,
            },
        }
    )
    assert (
        util.to_map(
            util.select_named(
                'select * from data.logs_64_partitioned '
                'order by event_id asc',
                pgsql,
            ),
            'event_id',
        )
        == {
            1: {
                'activity_increment': 1,
                'complete_score_increment': 2,
                'created': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'event_id': 1,
                'loyalty_increment': 1,
                'priority_absolute': 21,
                'priority_increment': 2,
                'udid_id': 1,
            },
            2: {
                'activity_increment': 2,
                'complete_score_increment': 3,
                'created': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'event_id': 2,
                'loyalty_increment': 2,
                'priority_absolute': 22,
                'priority_increment': 3,
                'udid_id': 1,
            },
            3: {
                'activity_increment': 3,
                'complete_score_increment': 4,
                'created': datetime.datetime(2019, 1, 1, 0, 0, 3),
                'event_id': 3,
                'loyalty_increment': 3,
                'priority_absolute': 23,
                'priority_increment': 4,
                'udid_id': 1,
            },
        }
    )

    response = await taxi_driver_metrics_storage.post(
        'v3/events/processed', json={'unique_driver_id': UDID_ID0},
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event': {
                    'datetime': '2019-01-01T00:00:02+00:00',
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'event_id': '3',
                    'extra': {'extra_field': '2'},
                    'extra_data': '',
                    'order_alias': 'order-alias-2',
                    'order_id': 'order_id: 2',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-Z',
                },
                'activity_change': 3,
                'loyalty_change': 3,
                'priority_change': 4,
                'priority_absolute': 23,
                'complete_score_change': 4,
            },
            {
                'event': {
                    'datetime': '2019-01-01T00:00:01+00:00',
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'event_id': '2',
                    'extra': {'extra_field': '1'},
                    'extra_data': '',
                    'order_alias': 'order-alias-1',
                    'order_id': 'order_id: 1',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-Z',
                },
                'activity_change': 2,
                'loyalty_change': 2,
                'priority_change': 3,
                'priority_absolute': 22,
                'complete_score_change': 3,
            },
            {
                'event': {
                    'datetime': '2019-01-01T00:00:00+00:00',
                    'descriptor': {
                        'tags': ['yam-yam', 'tas_teful'],
                        'type': 'user_test',
                    },
                    'event_id': '1',
                    'extra': {'extra_field': '0'},
                    'extra_data': '',
                    'order_alias': 'order-alias-0',
                    'order_id': 'order_id: 0',
                    'park_driver_profile_id': 'dbid_uuid1',
                    'tariff_zone': 'moscow',
                    'type': 'type-Z',
                },
                'activity_change': 1,
                'loyalty_change': 1,
                'priority_change': 2,
                'priority_absolute': 21,
                'complete_score_change': 2,
            },
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v2/events/history',
        json={
            'unique_driver_id': UDID_ID0,
            'created_after': '2000-01-01T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'events': [
            {
                'event_id': 1,
                'created': '2019-01-01T00:00:00+00:00',
                'extra_data': (
                    '{"extra_field":"0","descriptor":'
                    '{"type":"user_test",'
                    '"tags":["yam-yam","tas_teful"]}}'
                ),
                'extra': {'extra_field': '0'},
                'descriptor': {
                    'type': 'user_test',
                    'tags': ['yam-yam', 'tas_teful'],
                },
                'order_alias': 'order-alias-0',
                'order_id': 'order_id: 0',
                'park_driver_profile_id': 'dbid_uuid1',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
            {
                'event_id': 2,
                'created': '2019-01-01T00:00:01+00:00',
                'extra_data': (
                    '{"extra_field":"1","descriptor":'
                    '{"type":"user_test",'
                    '"tags":["yam-yam","tas_teful"]}}'
                ),
                'extra': {'extra_field': '1'},
                'descriptor': {
                    'type': 'user_test',
                    'tags': ['yam-yam', 'tas_teful'],
                },
                'order_alias': 'order-alias-1',
                'order_id': 'order_id: 1',
                'park_driver_profile_id': 'dbid_uuid1',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
            {
                'event_id': 3,
                'created': '2019-01-01T00:00:02+00:00',
                'extra_data': (
                    '{"extra_field":"2","descriptor":'
                    '{"type":"user_test",'
                    '"tags":["yam-yam","tas_teful"]}}'
                ),
                'extra': {'extra_field': '2'},
                'descriptor': {
                    'type': 'user_test',
                    'tags': ['yam-yam', 'tas_teful'],
                },
                'order_alias': 'order-alias-2',
                'order_id': 'order_id: 2',
                'park_driver_profile_id': 'dbid_uuid1',
                'tariff_zone': 'moscow',
                'type': 'type-Z',
            },
        ],
    }
