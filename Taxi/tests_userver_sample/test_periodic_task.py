import asyncio

import pytest

PERIODIC_TASK_PERIOD = 0.2


async def test_periodic_task_runs_periodically(taxi_userver_sample, testpoint):
    @testpoint('task::periodic-task-sample')
    def task_testpoint(data):
        pass

    await taxi_userver_sample.enable_testpoints()
    await asyncio.sleep(3 * PERIODIC_TASK_PERIOD)
    assert task_testpoint.times_called > 1


@pytest.mark.suspend_periodic_tasks('periodic-task-sample')
async def test_suspended_periodic_task_is_not_executed(
        taxi_userver_sample, testpoint,
):
    @testpoint('task::periodic-task-sample')
    def task_testpoint(data):
        pass

    await taxi_userver_sample.enable_testpoints()
    # ensure suspend_periodic_tasks stopped periodic task execution
    await asyncio.sleep(2 * PERIODIC_TASK_PERIOD)
    assert task_testpoint.times_called == 0


async def test_manually_suspended_periodic_task_is_not_executed(
        taxi_userver_sample, testpoint,
):
    await taxi_userver_sample.suspend_periodic_tasks(['periodic-task-sample'])

    @testpoint('task::periodic-task-sample')
    def task_testpoint(data):
        pass

    await taxi_userver_sample.enable_testpoints()
    # ensure suspend_periodic_tasks stopped periodic task execution
    await asyncio.sleep(2 * PERIODIC_TASK_PERIOD)
    assert task_testpoint.times_called == 0


@pytest.mark.suspend_periodic_tasks('periodic-task-sample')
async def test_resumed_periodic_task_runs_periodically(
        taxi_userver_sample, testpoint,
):
    @testpoint('task::periodic-task-sample')
    def task_testpoint(data):
        pass

    await taxi_userver_sample.enable_testpoints()
    await taxi_userver_sample.resume_periodic_tasks(['periodic-task-sample'])

    await asyncio.sleep(3 * PERIODIC_TASK_PERIOD)
    assert task_testpoint.times_called > 1


@pytest.mark.suspend_periodic_tasks('periodic-task-sample')
async def test_resume_all_resumes_periodic_task(
        taxi_userver_sample, testpoint,
):
    await taxi_userver_sample.resume_all_periodic_tasks()

    @testpoint('task::periodic-task-sample')
    def task_testpoint(data):
        pass

    await taxi_userver_sample.enable_testpoints()

    # ensure suspend_periodic_tasks stopped periodic task execution
    await asyncio.sleep(3 * PERIODIC_TASK_PERIOD)
    assert task_testpoint.times_called > 1
