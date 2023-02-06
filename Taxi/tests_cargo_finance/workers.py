import pytest


@pytest.fixture(name='run_infinite_task')
async def _run_infinite_task(taxi_cargo_finance, testpoint):
    async def _wrapper(task_name):
        @testpoint('%s::result' % task_name)
        def task_progress(data):
            pass

        await taxi_cargo_finance.run_distlock_task(task_name)
        results = await task_progress.wait_call()
        return results['data']

    return _wrapper


@pytest.fixture(name='run_status_monitor_worker')
def _run_status_monitor_worker(run_infinite_task):
    async def _wrapper():
        return await run_infinite_task('cargo-finance-status-monitor')

    return _wrapper
