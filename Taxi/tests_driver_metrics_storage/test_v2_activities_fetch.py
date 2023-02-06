# -*- coding: utf-8 -*-

import pytest

from tests_driver_metrics_storage import util


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_EVENTS_PROCESSING_SETTINGS={
        'new_event_age_limit_mins': 720,
        'idempotency_token_ttl_mins': 1440,
        'default_event_ttl_hours': 168,
        'processing_ticket_ttl_secs': 60,
        'processing_lag_msecs': 200,
        'default_unprocessed_list_limit': 100,
        'round_robin_process': False,
        'non_transactional_polling': True,
        'polling_max_passes': 1,
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.parametrize('strict', [False, True])
async def test_fetch(taxi_driver_metrics_storage, pgsql, strict):
    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    assert (
        util.select_named(
            'select udid_id,value,complete_score_value '
            'from data.activity_values order by udid_id',
            pgsql,
        )
        == [
            {'udid_id': 1002, 'value': 222, 'complete_score_value': None},
            {'udid_id': 1004, 'value': 444, 'complete_score_value': None},
        ]
    )

    assert (
        util.select_named(
            'select *'
            + ' from data.activity_values_generations order by udid_id',
            pgsql,
        )
        == [
            {'generation': 1, 'udid_id': 1002},
            {'generation': 2, 'udid_id': 1004},
        ]
    )

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/fetch', json={'limit': 100},
    )
    assert response.status_code == 200
    last_generation = response.json()['last_generation']
    res = response.json()
    res['last_generation'] = '*'
    res['items'] = util.to_map(res['items'], 'unique_driver_id')
    assert res == {
        'items': {
            'W00000000000000000000000': {
                'activity': 222,
                'unique_driver_id': 'W00000000000000000000000',
            },
            'R00000000000000000000000': {
                'activity': 444,
                'unique_driver_id': 'R00000000000000000000000',
            },
        },
        'last_generation': '*',
        'more_updates': False,
    }

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/list',
        json={
            'unique_driver_ids': [
                'Q00000000000000000000000',
                'W00000000000000000000000',
                'E00000000000000000000000',
                'R00000000000000000000000',
                'T00000000000000000000000',
                'Y00000000000000000000000',
                'ЙЦУКЕН000000000000000000',
            ],
            'strict': strict,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'unique_driver_id': 'Q00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'W00000000000000000000000', 'value': 222},
            {'unique_driver_id': 'E00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'R00000000000000000000000', 'value': 444},
            {'unique_driver_id': 'T00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'Y00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'ЙЦУКЕН000000000000000000', 'value': 100},
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 4},
    )
    assert response.status_code == 200
    assert (
        util.to_map(
            response.json()['items'], 'unique_driver_id', util.hide_ticket,
        )
        == {
            'E00000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-03T00:00:00+00:00',
                        'event_id': 3,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': 'E00000000000000000000000',
            },
            'Q00000000000000000000000': {
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 1,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                    {
                        'created': '2000-01-04T00:00:00+00:00',
                        'event_id': 4,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': 'Q00000000000000000000000',
            },
            'W00000000000000000000000': {
                'current_activity': 222,
                'events': [
                    {
                        'created': '2000-01-02T00:00:00+00:00',
                        'event_id': 2,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': '*',
                'unique_driver_id': 'W00000000000000000000000',
            },
        }
    )

    items = response.json()['items']
    for item in items:
        for i in range(len(item['events'])):
            event = item['events'][i]
            desired_activity = 10000 * event['event_id']
            for _ in range(2):
                response = await taxi_driver_metrics_storage.post(
                    'v3/event/complete',
                    json={
                        'ticket_id': item['ticket_id'],
                        'event_id': event['event_id'],
                        'activity': {
                            'increment': 9999,
                            'value_to_set': desired_activity,
                        },
                    },
                )
                if response.status_code != 409:
                    break
            assert [response.status_code, response.json()] == [200, {}]

    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    assert (
        util.select_named(
            'select udid_id,value,complete_score_value '
            'from data.activity_values order by udid_id',
            pgsql,
        )
        == [
            {'udid_id': 1001, 'value': 40000, 'complete_score_value': None},
            {'udid_id': 1002, 'value': 20000, 'complete_score_value': None},
            {'udid_id': 1003, 'value': 30000, 'complete_score_value': None},
            {'udid_id': 1004, 'value': 444, 'complete_score_value': None},
        ]
    )

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/fetch',
        json={'last_generation': last_generation, 'limit': 100},
    )
    assert response.status_code == 200
    last_generation = response.json()['last_generation']
    res = response.json()
    res['last_generation'] = '*'
    res['items'] = util.to_map(res['items'], 'unique_driver_id')
    assert res == {
        'items': {
            'E00000000000000000000000': {
                'activity': 30000,
                'unique_driver_id': 'E00000000000000000000000',
            },
            'Q00000000000000000000000': {
                'activity': 40000,
                'unique_driver_id': 'Q00000000000000000000000',
            },
            'W00000000000000000000000': {
                'activity': 20000,
                'unique_driver_id': 'W00000000000000000000000',
            },
        },
        'last_generation': '*',
        'more_updates': False,
    }

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/list',
        json={
            'unique_driver_ids': [
                'Q00000000000000000000000',
                'W00000000000000000000000',
                'E00000000000000000000000',
                'R00000000000000000000000',
                'T00000000000000000000000',
                'Y00000000000000000000000',
                'ЙЦУКЕН000000000000000000',
            ],
            'strict': strict,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'unique_driver_id': 'Q00000000000000000000000', 'value': 40000},
            {'unique_driver_id': 'W00000000000000000000000', 'value': 20000},
            {'unique_driver_id': 'E00000000000000000000000', 'value': 30000},
            {'unique_driver_id': 'R00000000000000000000000', 'value': 444},
            {'unique_driver_id': 'T00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'Y00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'ЙЦУКЕН000000000000000000', 'value': 100},
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        'v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 1000},
    )
    assert response.status_code == 200

    items = response.json()['items']
    for item in items:
        for i in range(len(item['events'])):
            event = item['events'][i]
            desired_activity = 10000 + event['event_id']
            for _ in range(2):
                response = await taxi_driver_metrics_storage.post(
                    'v3/event/complete',
                    json={
                        'ticket_id': item['ticket_id'],
                        'event_id': event['event_id'],
                        'activity': {
                            'increment': 9999,
                            'value_to_set': desired_activity,
                        },
                    },
                )
                if response.status_code != 409:
                    break
            assert [response.status_code, response.json()] == [200, {}]

    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    assert (
        util.select_named(
            'select udid_id,value from data.activity_values order by udid_id',
            pgsql,
        )
        == [
            {'udid_id': 1001, 'value': 10010},
            {'udid_id': 1002, 'value': 10008},
            {'udid_id': 1003, 'value': 10009},
            {'udid_id': 1004, 'value': 444},
        ]
    )

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/fetch',
        json={'last_generation': last_generation, 'limit': 100},
    )
    assert response.status_code == 200
    last_generation = response.json()['last_generation']
    res = response.json()
    res['last_generation'] = '*'
    res['items'] = util.to_map(res['items'], 'unique_driver_id')
    assert res == {
        'items': {
            'E00000000000000000000000': {
                'activity': 10009,
                'unique_driver_id': 'E00000000000000000000000',
            },
            'Q00000000000000000000000': {
                'activity': 10010,
                'unique_driver_id': 'Q00000000000000000000000',
            },
            'W00000000000000000000000': {
                'activity': 10008,
                'unique_driver_id': 'W00000000000000000000000',
            },
        },
        'last_generation': '*',
        'more_updates': False,
    }

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/fetch', json={'limit': 100},
    )
    assert response.status_code == 200
    last_generation = response.json()['last_generation']
    res = response.json()
    res['last_generation'] = '*'
    res['items'] = util.to_map(res['items'], 'unique_driver_id')
    assert res == {
        'items': {
            'E00000000000000000000000': {
                'activity': 10009,
                'unique_driver_id': 'E00000000000000000000000',
            },
            'Q00000000000000000000000': {
                'activity': 10010,
                'unique_driver_id': 'Q00000000000000000000000',
            },
            'W00000000000000000000000': {
                'activity': 10008,
                'unique_driver_id': 'W00000000000000000000000',
            },
            'R00000000000000000000000': {
                'activity': 444,
                'unique_driver_id': 'R00000000000000000000000',
            },
        },
        'last_generation': '*',
        'more_updates': False,
    }

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/fetch',
        json={'last_generation': last_generation, 'limit': 100},
    )
    assert response.status_code == 200
    res = response.json()
    res['last_generation'] = '*'
    res['items'] = util.to_map(res['items'], 'unique_driver_id')
    assert res == {'items': {}, 'last_generation': '*', 'more_updates': False}

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/fetch', json={'limit': 2},
    )
    assert response.status_code == 200
    assert len(response.json()['items']) == 2
    assert response.json()['more_updates'] is True

    response = await taxi_driver_metrics_storage.post(
        '/v2/activity_values/list',
        json={
            'unique_driver_ids': [
                'Q00000000000000000000000',
                'W00000000000000000000000',
                'E00000000000000000000000',
                'R00000000000000000000000',
                'T00000000000000000000000',
                'Y00000000000000000000000',
                'ЙЦУКЕН000000000000000000',
            ],
            'strict': strict,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'unique_driver_id': 'Q00000000000000000000000', 'value': 10010},
            {'unique_driver_id': 'W00000000000000000000000', 'value': 10008},
            {'unique_driver_id': 'E00000000000000000000000', 'value': 10009},
            {'unique_driver_id': 'R00000000000000000000000', 'value': 444},
            {'unique_driver_id': 'T00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'Y00000000000000000000000', 'value': 100},
            {'unique_driver_id': 'ЙЦУКЕН000000000000000000', 'value': 100},
        ],
    }
