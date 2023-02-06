import collections

import pytest


JOB_NAME = 'cars-importer-worker'

BEFORE_IMPORTS_CARS_COUNT = 2
AFTER_IMPORTS_CARS_COUNT = 8


def get_cars_importer_work_mode(mode):
    return {
        'mode': mode,
        'chunk-size': 2,
        'full-updates-limit-per-iteration': 2,
        'interval-ms': 1000,
        'lagging-cursor-delay': 1,
        'pg-timeout-ms': 2000,
    }


async def wait_iteration(taxi_fleet_vehicles, job_name, mode, testpoint):
    @testpoint(job_name + '-started')
    def started(data):
        return data

    @testpoint(job_name + '-finished')
    def finished(data):
        return data

    await taxi_fleet_vehicles.enable_testpoints()
    while True:
        start_status = (await started.wait_call())['data']
        if start_status['mode'] == mode:
            break
    while True:
        finish_status = (await finished.wait_call())['data']
        if finish_status['mode'] == mode:
            return finish_status['stats']
    return []


@pytest.mark.config(
    CARS_IMPORTER_WORK_MODE=get_cars_importer_work_mode('enabled'),
)
async def test_worker_enabled(
        taxi_fleet_vehicles, taxi_config, testpoint, mongodb,
):
    await taxi_fleet_vehicles.invalidate_caches()
    for _ in range(3):
        await wait_iteration(
            taxi_fleet_vehicles, JOB_NAME, 'enabled', testpoint,
        )

    assert mongodb.cars.find().count() == AFTER_IMPORTS_CARS_COUNT

    taxi_config.set_values(
        dict(CARS_IMPORTER_WORK_MODE=get_cars_importer_work_mode('disabled')),
    )
    await taxi_fleet_vehicles.invalidate_caches()

    await wait_iteration(taxi_fleet_vehicles, JOB_NAME, 'disabled', testpoint)


@pytest.mark.config(
    CARS_IMPORTER_WORK_MODE=get_cars_importer_work_mode('dryrun'),
)
async def test_worker_dryrun(
        taxi_fleet_vehicles, taxi_config, testpoint, mongodb,
):
    await taxi_fleet_vehicles.invalidate_caches()

    counter = collections.Counter()
    for _ in range(AFTER_IMPORTS_CARS_COUNT):
        stats = await wait_iteration(
            taxi_fleet_vehicles, JOB_NAME, 'dryrun', testpoint,
        )
        counter['full-updates-count'] += stats['full-updates-count']
        counter += collections.Counter(stats['full-update-cursor'])

    assert mongodb.cars.find().count() == BEFORE_IMPORTS_CARS_COUNT
    assert (
        counter['full-updates-count'] > 1
    ), 'expected full_updates_cursor reset'

    taxi_config.set_values(
        dict(CARS_IMPORTER_WORK_MODE=get_cars_importer_work_mode('disabled')),
    )
    await taxi_fleet_vehicles.invalidate_caches()

    await wait_iteration(taxi_fleet_vehicles, JOB_NAME, 'disabled', testpoint)


@pytest.mark.config(
    CARS_IMPORTER_WORK_MODE=get_cars_importer_work_mode('disabled'),
)
async def test_worker_disabled(
        taxi_fleet_vehicles, taxi_config, testpoint, mongodb,
):
    await taxi_fleet_vehicles.invalidate_caches()

    await wait_iteration(taxi_fleet_vehicles, JOB_NAME, 'disabled', testpoint)

    assert mongodb.cars.find().count() == BEFORE_IMPORTS_CARS_COUNT
