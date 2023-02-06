import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_manual_dispatch_cargo_router_plugins import *  # noqa: F403 F401


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_grocery_manual_dispatch_cargo_router, testpoint):
    async def _wrapper(task_name):
        @testpoint('%s::result' % task_name)
        def task_result(result):
            pass

        await taxi_grocery_manual_dispatch_cargo_router.run_task(task_name)
        args = await task_result.wait_call()
        assert not task_result.has_calls

        return args['result']

    return _wrapper
