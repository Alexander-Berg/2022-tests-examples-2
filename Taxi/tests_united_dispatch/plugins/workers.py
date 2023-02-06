import pytest


@pytest.fixture(name='run_task_once')
def _run_task_once(united_dispatch_unit, run_cargo_distlock_worker):
    async def _wrapper(task_name):
        return await run_cargo_distlock_worker(united_dispatch_unit, task_name)

    return _wrapper


@pytest.fixture(name='run_logistic_dispatcher_metrics_checker')
def _run_logistic_dispatcher_metrics_checker(run_task_once):
    async def _wrapper():
        return await run_task_once('logistic-dispatcher-metrics-checker')

    return _wrapper


@pytest.fixture(name='run_ld_segments_journal_reader')
def _run_ld_segments_journal_reader(run_task_once):
    async def _wrapper():
        return await run_task_once('ld-segments-journal-reader')

    return _wrapper


@pytest.fixture(name='run_segments_reader')
def _run_segments_reader(
        run_task_once,
        mock_segment_dispatch_journal,
        mock_dispatch_segment_info,
):
    async def _wrapper():
        return await run_task_once('segments-reader')

    return _wrapper


@pytest.fixture(name='run_executor_watchdog')
def _run_executor_watchdog(run_task_once):
    async def _wrapper():
        return await run_task_once('segments-watchdog')

    return _wrapper


@pytest.fixture(name='run_waybill_reader')
def _run_waybill_reader(
        run_task_once,
        autorun_stq,
        mock_waybill_dispatch_journal,
        mock_dispatch_waybill_info,
):
    async def _wrapper(only_journal=False):
        stats = await run_task_once('waybill-reader')

        if not only_journal:
            await autorun_stq('united_dispatch_waybill_reader')

        return stats

    return _wrapper


@pytest.fixture(name='run_single_planner')
def _run_single_planner(cargo_dispatch, run_planner):
    async def _wrapper(**kwargs):
        planners = set(
            s.planner for s in cargo_dispatch.segments.segments.values()
        )

        # only single planner allowed for this fixture, use specific
        # fixture if you want to run multiple planners
        assert len(planners) == 1

        planner_type = list(planners)[0]
        assert planner_type in {
            'delivery',
            'eats',
            'grocery',
            'crutches',
            'testsuite-candidates',
        }

        component_name = f'{planner_type}-planner'
        return await run_planner(component_name=component_name, **kwargs)

    return _wrapper


@pytest.fixture(name='run_planner')
def _run_planner(
        sharded_distlock_task,
        united_dispatch_unit,
        mock_waybill_propose,
        mock_update_proposition,
        get_metric_labels,
):
    async def _wrapper(
            component_name, *, shard='default', invalidate_caches=True,
    ):
        if invalidate_caches:
            await united_dispatch_unit.invalidate_caches(
                clean_update=False, cache_names=['active-waybills-cache'],
            )

        planner_task = sharded_distlock_task(
            united_dispatch_unit, component_name,
        )

        if not planner_task.get_shards():
            await planner_task.add_shards({shard})

        stats = await planner_task.run_shard(shard)

        return get_metric_labels(stats)

    return _wrapper
