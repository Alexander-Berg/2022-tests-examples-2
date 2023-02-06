METRICS_NAME = 'task-status-metrics'


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(METRICS_NAME, is_distlock=True)


async def test_task_status_metrics(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
):
    @testpoint('eats_nomenclature_collector::task-status-metrics')
    def handle_finished(arg):
        pass

    await taxi_eats_nomenclature_collector.run_distlock_task(
        'task-status-metrics',
    )
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    assert (
        metrics[METRICS_NAME]['tasks_count']['nomenclature_place_tasks']
        == {
            'created': 4,
            'started': 2,
            'finished': 2,
            'failed': 2,
            'creation_failed': 1,
            'processed': 1,
        }
    )
    assert metrics[METRICS_NAME]['tasks_count']['price_tasks'] == {
        'created': 2,
        'started': 1,
        'finished': 0,
        'failed': 2,
        'creation_failed': 0,
        'processed': 0,
    }
    assert metrics[METRICS_NAME]['tasks_count']['stock_tasks'] == {
        'created': 1,
        'started': 1,
        'finished': 2,
        'failed': 1,
        'creation_failed': 1,
        'processed': 0,
    }
    assert metrics[METRICS_NAME]['tasks_count']['availability_tasks'] == {
        'created': 0,
        'started': 2,
        'finished': 1,
        'failed': 0,
        'creation_failed': 1,
        'processed': 0,
    }
    assert (
        metrics[METRICS_NAME]['tasks_count']['nomenclature_brand_tasks']
        == {
            'created': 3,
            'creating': 2,
            'finished': 2,
            'failed': 1,
            'creation_failed': 0,
            'processed': 0,
        }
    )

    assert metrics[METRICS_NAME]['old_tasks_count'][
        'nomenclature_place_tasks'
    ] == {'created': 2, 'started': 2, 'finished': 1}
    assert metrics[METRICS_NAME]['old_tasks_count']['price_tasks'] == {
        'created': 1,
        'started': 1,
        'finished': 0,
    }
    assert metrics[METRICS_NAME]['old_tasks_count']['stock_tasks'] == {
        'created': 1,
        'started': 1,
        'finished': 1,
    }
    assert metrics[METRICS_NAME]['old_tasks_count']['availability_tasks'] == {
        'created': 0,
        'started': 1,
        'finished': 1,
    }
    assert metrics[METRICS_NAME]['old_tasks_count'][
        'nomenclature_brand_tasks'
    ] == {'created': 2, 'creating': 0, 'finished': 0}
