import datetime

import pytest

from tests_unique_drivers import utils

IMPORTS_JOB_NAME = 'unique-drivers-importer-worker'
EVENTS_JOB_NAME = 'unique-drivers-events-worker'


def get_work_mode(mode, limit_per_iteration=2):
    return {
        'mode': mode,
        'chunk-size': 10,
        'interval-ms': 1000,
        'lagging-cursor-delay': 1,
        'full-updates-limit-per-iteration': limit_per_iteration,
        'pg-timeout-ms': 2000,
    }


async def wait_imports_iteration(
        taxi_unique_drivers, job_name, mode, testpoint,
):
    @testpoint(job_name + '-started')
    def started(data):
        return data

    @testpoint(job_name + '-finished')
    def finished(data):
        return data

    await taxi_unique_drivers.enable_testpoints()
    while True:
        start_status = (await started.wait_call())['data']
        if start_status['mode'] == mode:
            break
    while True:
        finish_status = (await finished.wait_call())['data']
        if finish_status['mode'] == mode:
            return finish_status['stats']
    return []


async def wait_events_iteration(taxi_unique_drivers, testpoint):
    @testpoint(EVENTS_JOB_NAME + '-finished')
    def finished(data):
        return data

    await taxi_unique_drivers.run_task(EVENTS_JOB_NAME)

    return (await finished.wait_call())['data']['stats']


@pytest.mark.config(
    UNIQUE_DRIVERS_IMPORTER_WORK_MODE=get_work_mode('disabled'),
)
async def test_worker_disabled(
        taxi_unique_drivers, testpoint, mongodb, taxi_config,
):
    await taxi_unique_drivers.invalidate_caches()
    await wait_imports_iteration(
        taxi_unique_drivers, IMPORTS_JOB_NAME, 'disabled', testpoint,
    )

    assert mongodb.unique_drivers.find().count() == 5


@pytest.mark.config(
    UNIQUE_DRIVERS_IMPORTER_WORK_MODE=get_work_mode('enabled', 0),
    UNIQUE_DRIVERS_EVENTS_WORKER_SETTINGS={
        'mode': 'enabled',
        'work-interval-ms': 5000,
        'chunk-size': 100,
        'log-skipped': False,
        'events': {'merge': False, 'divide': False, 'new': True},
        'lb-events': {'merge': False, 'divide': False, 'new': True},
    },
)
@pytest.mark.now('2021-03-01T00:00:00')
async def test_worker_with_events(
        taxi_unique_drivers, testpoint, mongodb, taxi_config,
):
    await taxi_unique_drivers.invalidate_caches()
    await wait_imports_iteration(
        taxi_unique_drivers, IMPORTS_JOB_NAME, 'enabled', testpoint,
    )

    payloads = []
    for event in mongodb.unique_drivers_events.find():
        assert event['source'] == 'importer-worker'
        assert event['login'] == '[none]'
        payload = event['payload']
        payload['unique_driver'].pop('id')
        payloads.append(payload)

    assert utils.ordered(payloads) == utils.ordered(
        [
            {
                'process_license_pd_ids': [
                    {'id': 'personal_LICENSE_NO_UNIQUE_003'},
                ],
                'unique_driver': {
                    'licenses': [{'license': 'LICENSE_NO_UNIQUE_003'}],
                    'license_pd_ids': [
                        {'id': 'personal_LICENSE_NO_UNIQUE_003'},
                    ],
                    'park_driver_profile_ids': [{'id': 'park2_driver3'}],
                    'clid_driver_profile_ids': [{'id': '002_driver3'}],
                },
                'unique_data': {
                    'city': 'city2',
                    'uber_driver_id': 'uber_driver3',
                },
            },
        ],
    )

    stats = await wait_events_iteration(taxi_unique_drivers, testpoint)
    assert stats['new'] == 1
    assert stats['failed'] == 0

    unique_driver = utils.get_unique_driver(
        'LICENSE_NO_UNIQUE_003', 'licenses.license', mongodb, fields=None,
    )
    unique_driver.pop('_id')
    unique_driver.pop('created_ts')
    unique_driver.pop('updated_ts')
    assert utils.ordered(unique_driver) == utils.ordered(
        {
            'license_ids': [{'id': 'personal_LICENSE_NO_UNIQUE_003'}],
            'licenses': [{'license': 'LICENSE_NO_UNIQUE_003'}],
            'profiles': [{'driver_id': '002_driver3'}],
            'city': 'city2',
            'uber_driver_id': 'uber_driver3',
            'score': {
                'base_total': 0.5773503,
                'total': 0.5773503,
                'complete_daily': [],
                'complete_today': 0,
            },
            'created': datetime.datetime(2021, 3, 1, 0, 0),
            'updated': datetime.datetime(2021, 3, 1, 0, 0),
        },
    )


@pytest.mark.config(UNIQUE_DRIVERS_IMPORTER_WORK_MODE=get_work_mode('enabled'))
async def test_worker_pd_phone(
        taxi_unique_drivers, testpoint, mongodb, taxi_config,
):
    await taxi_unique_drivers.invalidate_caches()
    await wait_imports_iteration(
        taxi_unique_drivers, IMPORTS_JOB_NAME, 'enabled', testpoint,
    )

    assert (
        mongodb.unique_drivers.find_one(
            {'licenses.license': 'LICENSE_NO_UNIQUE_005'},
        )
        is None
    )
    assert mongodb.unique_drivers.find().count() == 6

    taxi_config.set_values(
        dict(UNIQUE_DRIVERS_IMPORTER_WORK_MODE=get_work_mode('disabled')),
    )
    await taxi_unique_drivers.invalidate_caches()

    await wait_imports_iteration(
        taxi_unique_drivers, IMPORTS_JOB_NAME, 'disabled', testpoint,
    )
