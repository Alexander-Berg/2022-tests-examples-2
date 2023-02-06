# -*- coding: utf-8 -*-

import datetime

import pytest

from testsuite.utils import ordered_object

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
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test_data_logs.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v3_unprocessed_and_complete(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))
    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'limit': 100, 'consumer': {'index': 0, 'total': 1}},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        {
            'items': [
                {
                    'current_activity': 12,
                    'events': [
                        {
                            'created': '2000-01-01T00:10:00+00:00',
                            'descriptor': {
                                'tags': ['yam-yam', 'tas_teful'],
                                'type': 'user_test',
                            },
                            'event_id': 300000000002,
                            'extra_data': {},
                            'tariff_zone': 'spb',
                            'type': 'type-Y',
                        },
                    ],
                    'ticket_id': -1,
                    'unique_driver_id': '200000000000000000000000',
                },
                {
                    'current_activity': 11,
                    'current_complete_score': {
                        'last_updated_at': '2000-01-01T00:00:00+00:00',
                        'value': 1,
                    },
                    'events': [
                        {
                            'created': '2000-01-01T00:00:00+00:00',
                            'event_id': 300000000001,
                            'extra_data': {},
                            'order_id': 'order_id',
                            'tariff_zone': 'moscow',
                            'type': 'type-X',
                        },
                    ],
                    'ticket_id': -1,
                    'unique_driver_id': '100000000000000000000000',
                },
                {
                    'current_activity': 13,
                    'events': [
                        {
                            'created': '2000-01-01T00:20:00+00:00',
                            'event_id': 300000000003,
                            'extra_data': {'extra_test': 'extra_test'},
                            'type': 'type-X',
                        },
                    ],
                    'ticket_id': -1,
                    'unique_driver_id': '300000000000000000000000',
                },
                {
                    'events': [
                        {
                            'created': '2000-01-01T00:50:00+00:00',
                            'descriptor': {
                                'tags': ['yam-yam', 'tas_teful'],
                                'type': 'user_test',
                            },
                            'event_id': 300000000006,
                            'extra_data': {'extra_test': 'extra_test'},
                            'type': 'type-X',
                        },
                    ],
                    'ticket_id': -1,
                    'unique_driver_id': '600000000000000000000000',
                },
                {
                    'current_activity': 15,
                    'current_complete_score': {
                        'last_updated_at': '2000-01-01T00:00:00+00:00',
                        'value': 5,
                    },
                    'events': [
                        {
                            'created': '2000-01-01T00:40:00+00:00',
                            'descriptor': {
                                'tags': ['yam-yam', 'tas_teful'],
                                'type': 'user_test',
                            },
                            'event_id': 300000000005,
                            'extra_data': {'extra_test': 'extra_test'},
                            'tariff_zone': 'spb',
                            'type': 'type-Y',
                        },
                    ],
                    'ticket_id': -1,
                    'unique_driver_id': '500000000000000000000000',
                },
            ],
        },
        ['items'],
    )
