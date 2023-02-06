import pytest


TASK_NAME = 'periodic-fleet-statistic-collect'


@pytest.fixture(name='run_task')
def run_task_(taxi_fleet_payouts):
    async def run_task():
        await taxi_fleet_payouts.run_task(TASK_NAME)

    return run_task


@pytest.mark.now('2020-06-01T00:00:00+03:00')
async def test_midnight(run_task):
    await run_task()


# TODO(dreame8): add tests
