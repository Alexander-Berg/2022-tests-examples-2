import pytest


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_c2c, run_cargo_distlock_worker):
    async def _wrapper(task_name):
        return await run_cargo_distlock_worker(taxi_cargo_c2c, task_name)

    return _wrapper


@pytest.fixture(name='run_flush_postcards')
def _run_flush_postcards(run_task_once):
    async def _wrapper():
        return await run_task_once('flush-postcards')

    return _wrapper


@pytest.fixture(name='run_update_delivery_resolution')
def _run_update_delivery_resolution(run_task_once):
    async def _wrapper():
        return await run_task_once('update-delivery-resolution')

    return _wrapper
