import pytest


@pytest.mark.config(
    HEATMAP_SAMPLE_STORAGE_ENABLED_JOBS={'calc-surge-cells-scheduler': True},
    CALC_SURGE_CELLS_FULL_MAP_LAYERS=['default', 'alternative'],
)
@pytest.mark.suspend_periodic_tasks('calc-surge-cells-scheduler-periodic')
async def test_calc_surge_cells_scheduler(
        taxi_heatmap_sample_storage, mockserver, testpoint, redis_store,
):
    @testpoint('calc-surge-cells-scheduler-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-surge-cells-scheduler-finish')
    def handle_calc_job_finish(arg):
        pass

    redis_store.delete('calc-surge-cells-tasks')
    await taxi_heatmap_sample_storage.enable_testpoints()
    await taxi_heatmap_sample_storage.run_periodic_task(
        'calc-surge-cells-scheduler-periodic',
    )
    await handle_calc_job_start.wait_call()
    cells_calc_stats = await handle_calc_job_finish.wait_call()

    assert cells_calc_stats == {
        'arg': {
            'queue_size': 0,
            'tasks_created': 2,
            'skip_scheduling': 0,
            'schedule_error': 0,
        },
    }
    scheduled_tasks = redis_store.lrange('calc-surge-cells-tasks', 0, -1)

    assert sorted(scheduled_tasks) == [
        b'__default__/alternative',
        b'__default__/default',
    ]
