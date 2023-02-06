import pytest


@pytest.mark.now('2021-07-13T00:00:00+0000')
async def test_moderation_stats(
        taxi_eats_moderation, taxi_eats_moderation_monitor,
):
    await taxi_eats_moderation.run_periodic_task('moderation-stats-periodic')

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
