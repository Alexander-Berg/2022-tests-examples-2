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
    DRIVER_METRICS_STORAGE_EVENTS_SPLITTING=2,
)
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_v1_complete_scores_list(taxi_driver_metrics_storage, pgsql):
    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    assert (
        util.select_named(
            'select udid_id,complete_score_value '
            'from data.activity_values order by udid_id',
            pgsql,
        )
        == [
            {'udid_id': 1002, 'complete_score_value': 201},
            {'udid_id': 1004, 'complete_score_value': 401},
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
        '/v1/completion_scores/list',
        json={
            'unique_driver_ids': [
                '200000000000000000000000',
                '400000000000000000000000',
                '300000000000000000000000',
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'contractor_scores': [
            {
                'last_updated_at': '2000-01-01T00:00:00+00:00',
                'unique_driver_id': '200000000000000000000000',
                'value': 201,
            },
            {
                'last_updated_at': '2000-01-01T00:00:00+00:00',
                'unique_driver_id': '400000000000000000000000',
                'value': 401,
            },
            {'unique_driver_id': '300000000000000000000000'},
        ],
    }

    response = await taxi_driver_metrics_storage.post(
        '/v3/events/unprocessed/list',
        json={'consumer': {'index': 0, 'total': 1}, 'limit': 10},
    )
    assert response.status_code == 200
    uncompleted_items = response.json()
    assert uncompleted_items == {
        'items': [
            {
                'current_activity': 222,
                'current_complete_score': {
                    'last_updated_at': '2000-01-01T00:00:00+00:00',
                    'value': 201,
                },
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 3,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '200000000000000000000000',
            },
            {
                'current_activity': 444,
                'current_complete_score': {
                    'last_updated_at': '2000-01-01T00:00:00+00:00',
                    'value': 401,
                },
                'events': [
                    {
                        'created': '2000-01-01T00:00:00+00:00',
                        'event_id': 4,
                        'extra_data': {},
                        'type': 'type-X',
                    },
                ],
                'ticket_id': -1,
                'unique_driver_id': '400000000000000000000000',
            },
        ],
    }

    for item in uncompleted_items['items']:
        for event in item['events']:
            response = await taxi_driver_metrics_storage.post(
                '/v3/event/complete',
                json={
                    'event_id': event['event_id'],
                    'ticket_id': -1,
                    'unique_driver_id': item['unique_driver_id'],
                    'complete_score': {
                        'increment': 2,
                        'value_to_set': (
                            item['current_complete_score']['value'] + 2
                        ),
                    },
                },
            )
            assert response.status_code == 200

    assert (
        util.select_named(
            'select * from events.queue_64 order by udid_id', pgsql,
        )
        == []
    )

    await taxi_driver_metrics_storage.invalidate_caches()
    await taxi_driver_metrics_storage.run_task('dist-version-refresher')

    assert (
        util.select_named(
            'select udid_id,complete_score_value '
            'from data.activity_values order by udid_id',
            pgsql,
        )
        == [
            {'udid_id': 1002, 'complete_score_value': 203},
            {'udid_id': 1004, 'complete_score_value': 403},
        ]
    )

    assert (
        util.select_named(
            'select *'
            + ' from data.activity_values_generations order by udid_id',
            pgsql,
        )
        == [
            {'generation': 5, 'udid_id': 1002},
            {'generation': 4, 'udid_id': 1004},
        ]
    )

    response = await taxi_driver_metrics_storage.post(
        '/v1/completion_scores/list',
        json={
            'unique_driver_ids': [
                '200000000000000000000000',
                '400000000000000000000000',
                'random0udid0wo0compscore',
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'contractor_scores': [
            {
                'last_updated_at': '2019-01-01T00:00:00+00:00',
                'unique_driver_id': '200000000000000000000000',
                'value': 203,
            },
            {
                'last_updated_at': '2019-01-01T00:00:00+00:00',
                'unique_driver_id': '400000000000000000000000',
                'value': 403,
            },
            {'unique_driver_id': 'random0udid0wo0compscore'},
        ],
    }
