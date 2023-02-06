import pytest


@pytest.mark.now('2021-07-13T00:00:00+0000')
async def test_task_executing_time_count(
        taxi_eats_moderation, taxi_eats_moderation_monitor,
):
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
