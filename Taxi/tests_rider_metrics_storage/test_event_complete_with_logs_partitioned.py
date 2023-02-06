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
async def test_event_complete_logs_partitioned(
        taxi_rider_metrics_storage, pgsql, mocked_time,
):
    for x in range(33):
        util.execute_query(
            (
                'INSERT INTO common.unique_riders  '
                '(unique_rider_id,unique_rider)'
                + 'VALUES'
                + '(%d,\'%s\');' % (x, str(x))
            ),
            pgsql,
        )

    for x in range(33):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/new',
            json={
                'idempotency_token': 'idempotency_token-' + str(x),
                'user_id': str(x),
                'type': 'type-Z',
                'created': CORRECT_TIMESTAMP,
                'extra_data': {'extra_field': str(x)},
                'order_id': 'order_id: ' + str(x),
                'tariff_zone': 'moscow',
            },
        )
        assert [response.status_code, response.json()] == [200, {}]

    mocked_time.set(datetime.datetime(2019, 1, 1, 0, 0, 3))

    for x in range(33):
        response = await taxi_rider_metrics_storage.post(
            'v1/event/complete', json={'event_id': (x + 1), 'ticket_id': -1},
        )
        assert [response.status_code, response.json()] == [200, {}]

        event = util.select_named(
            'select * from events.logs_64_partitioned_'
            + str(x % 30)
            + '_mod_30 '
            + 'where event_id = %d;' % (x + 1),
            pgsql,
        )[0]
        assert event['event_id'] == x + 1 and event['unique_rider_id'] == x

        response = await taxi_rider_metrics_storage.post(
            'v1/events/processed', json={'user_id': str(x)},
        )
        assert response.status_code == 200
        assert response.json() == {
            'events': [
                {
                    'created': CORRECT_TIMESTAMP,
                    'event_id': str(x + 1),
                    'extra_data': '{"extra_field":"' + str(x) + '"}',
                    'descriptor': '',
                    'order_id': 'order_id: ' + str(x),
                    'tariff_zone': 'moscow',
                    'type': 'type-Z',
                },
            ],
        }

        response = await taxi_rider_metrics_storage.post(
            'v1/events/history',
            json={
                'user_id': str(x),
                'created_after': '2000-01-01T00:00:00+00:00',
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            'events': [
                {
                    'event_id': x + 1,
                    'created': CORRECT_TIMESTAMP,
                    'extra_data': '{"extra_field":"' + str(x) + '"}',
                    'order_id': 'order_id: ' + str(x),
                    'tariff_zone': 'moscow',
                    'type': 'type-Z',
                },
            ],
        }
