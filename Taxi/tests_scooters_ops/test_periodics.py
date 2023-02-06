import pytest

from tests_scooters_ops import utils


DISTLOCK_NAME = 'scooters-ops-periodic'


@pytest.mark.config(SCOOTERS_OPS_PERIODICS={'sleep_time_ms': 200})
async def test_empty_worker(taxi_scooters_ops, pgsql):
    await taxi_scooters_ops.run_distlock_task(DISTLOCK_NAME)

    cursor = pgsql['scooters_ops'].cursor()
    cursor.execute('SELECT * FROM scooters_ops.periodics')
    assert cursor.fetchall() == []


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 200,
        'scooters_fetch': {'enabled': True, 'sleep_time_ms': 200},
    },
)
async def test_worker(taxi_scooters_ops, pgsql, stq):
    await taxi_scooters_ops.run_distlock_task(DISTLOCK_NAME)

    cursor = pgsql['scooters_ops'].cursor()
    cursor.execute('SELECT * FROM scooters_ops.periodics')
    assert cursor.fetchall() == [('scooters_fetch', utils.AnyValue())]
    assert stq.scooters_fetch.times_called == 1
