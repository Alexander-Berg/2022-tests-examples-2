# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_driver_metrics_storage import util

CORRECT_TIMESTAMP = '2019-01-01T00:00:00+00:00'
UDID_ID0 = '0123456789AB0123456789AB'


def get_udid(num):
    num_str = str(num)
    return '0' * (24 - len(num_str)) + num_str


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
async def test_event_complete_logs_partitioned(
        taxi_driver_metrics_storage, pgsql, mocked_time,
):
    for x in range(35):
        util.execute_query(
            (
                'INSERT INTO common.udids  '
                '(udid_id,udid)' + 'VALUES' + '(%d,\'%s\');' % (x, get_udid(x))
            ),
            pgsql,
        )

    for x in range(33):
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'unique_driver_id': get_udid(x),
                'type': 'type-Z',
                'created': CORRECT_TIMESTAMP,
                'extra_data': {'extra_field': str(x)},
                'descriptor': {
                    'tags': ['yam-yam', 'tas_teful'],
                    'type': 'user_test',
                },
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))

    for x in range(33):
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete',
            json={
                'event_id': (x + 1),
                'ticket_id': -1,
                'wallet_increment': 1,
                'activity': {'increment': 5, 'value_to_set': 10},
                'loyalty_increment': 1,
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

        event = util.select_named(
            'select * from events.logs_64_partitioned_'
            + str(x % 30)
            + '_mod_30 '
            + 'where event_id = %d;' % (x + 1),
            pgsql,
        )[0]
        assert event['event_id'] == x + 1 and event['udid_id'] == x

        response = await taxi_driver_metrics_storage.post(
            'v3/events/processed', json={'unique_driver_id': get_udid(x)},
        )
        assert response.status_code == 200
        assert response.json() == {
            'events': [
                {
                    'loyalty_change': 1,
                    'activity_change': 5,
                    'event': {
                        'datetime': '2019-01-01T00:00:00+00:00',
                        'descriptor': {
                            'tags': ['yam-yam', 'tas_teful'],
                            'type': 'user_test',
                        },
                        'event_id': str(x + 1),
                        'extra': {'extra_field': str(x)},
                        'extra_data': '',
                        'order_alias': '',
                        'order_id': 'order_id: ' + str(x),
                        'park_driver_profile_id': '',
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                },
            ],
        }

        response = await taxi_driver_metrics_storage.post(
            'v2/events/history',
            json={
                'unique_driver_id': get_udid(x),
                'created_after': '2000-01-01T00:00:00+00:00',
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            'events': [
                {
                    'event_id': x + 1,
                    'created': '2019-01-01T00:00:00+00:00',
                    'extra_data': (
                        '{"extra_field":"'
                        + str(x)
                        + '","descriptor":{"type":"user_test",'
                        '"tags":["yam-yam","tas_teful"]}}'
                    ),
                    'extra': {'extra_field': str(x)},
                    'descriptor': {
                        'type': 'user_test',
                        'tags': ['yam-yam', 'tas_teful'],
                    },
                    'order_id': 'order_id: ' + str(x),
                    'tariff_zone': 'moscow',
                    'type': 'type-Z',
                },
            ],
        }

        response = await taxi_driver_metrics_storage.post(
            'v1/wallet/history',
            json={
                'ts_from': '2000-01-01T00:00:00+0000',
                'ts_to': '2100-01-01T00:00:00+0000',
                'udid': get_udid(x),
            },
        )
        assert response.status_code == 200
        assert response.json() == [
            {
                'amount': 1,
                'reason': '',
                'tariff_zone': 'moscow',
                'timestamp': '2019-01-01T00:00:03+00:00',
                'transaction_id': 'ev-' + str(x + 1),
                'value': 1,
            },
        ]

    # add event with empty extra_data
    for x in range(33, 35):
        event_data = {
            'idempotency_token': 'idempotency_token-' + str(x),
            'unique_driver_id': get_udid(x),
            'type': 'type-Z',
            'created': CORRECT_TIMESTAMP,
            'order_id': 'order_id: ' + str(x),
            'tariff_zone': 'moscow',
        }
        if x == 33:
            event_data['descriptor'] = {
                'tags': ['yam-yam', 'tas_teful'],
                'type': 'user_test',
            }
        response = await taxi_driver_metrics_storage.post(
            'v2/event/new', json=event_data,
        )
        assert [response.status_code, response.json()] == [200, {}]

        # process
        response = await taxi_driver_metrics_storage.post(
            'v3/event/complete',
            json={
                'event_id': (x + 1),
                'ticket_id': -1,
                'wallet_increment': 1,
                'activity': {'increment': 5, 'value_to_set': 10},
                'loyalty_increment': 1,
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

        event = util.select_named(
            'select * from events.logs_64_partitioned_'
            + str(x % 30)
            + '_mod_30 '
            + 'where event_id = %d;' % (x + 1),
            pgsql,
        )[0]
        assert event['event_id'] == x + 1 and event['udid_id'] == x

        response = await taxi_driver_metrics_storage.post(
            'v3/events/processed', json={'unique_driver_id': get_udid(x)},
        )
        assert response.status_code == 200
        expected_extra_data = '{}'
        expected_event = {
            'datetime': '2019-01-01T00:00:00+00:00',
            'event_id': str(x + 1),
            'extra': {},
            'extra_data': '',
            'order_alias': '',
            'order_id': 'order_id: ' + str(x),
            'park_driver_profile_id': '',
            'tariff_zone': 'moscow',
            'type': 'type-Z',
        }

        if x == 33:
            expected_event['descriptor'] = {
                'tags': ['yam-yam', 'tas_teful'],
                'type': 'user_test',
            }
            expected_extra_data = (
                '{"descriptor":{"type":"user_test",'
                '"tags":["yam-yam","tas_teful"]}}'
            )
        assert response.json() == {
            'events': [
                {
                    'loyalty_change': 1,
                    'activity_change': 5,
                    'event': expected_event,
                },
            ],
        }

        response = await taxi_driver_metrics_storage.post(
            'v2/events/history',
            json={
                'unique_driver_id': get_udid(x),
                'created_after': '2000-01-01T00:00:00+00:00',
            },
        )

        assert response.status_code == 200

        def patch_with_descriptor(event, descriptor):
            if descriptor:
                event['descriptor'] = descriptor
            return event

        assert response.json() == {
            'events': [
                patch_with_descriptor(
                    {
                        'event_id': x + 1,
                        'created': '2019-01-01T00:00:00+00:00',
                        'extra_data': expected_extra_data,
                        'extra': {},
                        'order_id': 'order_id: ' + str(x),
                        'tariff_zone': 'moscow',
                        'type': 'type-Z',
                    },
                    expected_event.get('descriptor'),
                ),
            ],
        }

        response = await taxi_driver_metrics_storage.post(
            'v1/wallet/history',
            json={
                'ts_from': '2000-01-01T00:00:00+0000',
                'ts_to': '2100-01-01T00:00:00+0000',
                'udid': get_udid(x),
            },
        )
        assert response.status_code == 200
        assert response.json() == [
            {
                'amount': 1,
                'reason': '',
                'tariff_zone': 'moscow',
                'timestamp': '2019-01-01T00:00:03+00:00',
                'transaction_id': 'ev-' + str(x + 1),
                'value': 1,
            },
        ]
