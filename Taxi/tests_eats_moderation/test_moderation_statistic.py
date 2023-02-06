import pytest


@pytest.mark.now('2021-07-13T00:00:00+0000')
async def test_moderation_statistic(
        taxi_eats_moderation, taxi_eats_moderation_monitor,
):
    await taxi_eats_moderation.run_periodic_task('moderation-stats-periodic')
    await taxi_eats_moderation.run_periodic_task(
        'task-executing-time-count-periodic',
    )

    metrics = await taxi_eats_moderation_monitor.get_metrics()
    assert metrics['task-executing-time-count'][
        'task_executing_time_by_day'
    ] == {'avg': 60000000000, 'max': 60000000000, 'min': 60000000000}
    assert metrics['task-executing-time-count'][
        'task_executing_time_by_week'
    ] == {'avg': 120000000000, 'max': 180000000000, 'min': 60000000000}

    metrics = await taxi_eats_moderation_monitor.get_metrics()
    assert metrics['moderation-stats']['undistributed_tasks_count'] == 1
    assert metrics['moderation-stats']['total_count_by_scope_eda'] == 5
    assert (
        metrics['moderation-stats'][
            'total_count_by_scope_eda_and_queue_restapp_moderation_category'
        ]
        == 2
    )
    assert metrics['moderation-stats']['day_count_by_scope_eda'] == 1
    assert (
        metrics['moderation-stats'][
            'day_count_by_scope_eda_and_queue_restapp_moderation_menu'
        ]
        == 0
    )

    response = await taxi_eats_moderation.get('/moderation/v1/statistic')

    assert response.status_code == 200
    assert response.json() == {
        'count_old_open_task': {'one': 1, 'three': 1, 'seven': 1},
        'count_old_open_task_group_by_tag': {'one': 1, 'three': 1, 'seven': 1},
        'count_tasks': [{'count': 5, 'count_group_by_tag': 2, 'scope': 'eda'}],
        'queues_and_statuses': [
            {
                'queue': 'restapp_moderation_category',
                'statuses': [
                    {'count': 1, 'count_by_tag': 1, 'status': 'approved'},
                    {'count': 1, 'count_by_tag': 1, 'status': 'new'},
                ],
            },
            {
                'queue': 'restapp_moderation_hero',
                'statuses': [
                    {'count': 1, 'count_by_tag': 1, 'status': 'approved'},
                ],
            },
            {
                'queue': 'restapp_moderation_menu',
                'statuses': [
                    {'count': 1, 'count_by_tag': 1, 'status': 'deleted'},
                    {'count': 1, 'count_by_tag': 1, 'status': 'rejected'},
                ],
            },
        ],
        'min_max_avg_old_open_tasks': {
            'avg': 120000000000,
            'max': 180000000000,
            'min': 60000000000,
        },
    }
