import datetime

import pytest


JOB_NAME = 'dbdrivers-drivers-updated-ts-monitor'
UPDATED_FIELD = 'modified_date'

TOTAL_DOCUMENTS = 5


@pytest.fixture(name='run_once')
async def _run_once(taxi_api_over_data_metrics, testpoint):
    @testpoint(JOB_NAME + '-finished')
    def finished(data):
        return data

    async def _wrapper():
        await taxi_api_over_data_metrics.run_task(JOB_NAME)
        return (await finished.wait_call())['data']['stats'][
            'full_update_cursor'
        ]

    return _wrapper


def get_config(mode, check_updated=None):
    config = {
        'mode': mode,
        'full-updates-limit-per-iteration': 1,
        'chunk-size': 10,
        'interval-ms': 2000,
        'log-level-updated-too-old': 'error',
        'pg-timeout-ms': 2000,
        'updated-allowed-lag': 1,
        'updated-ts-allowed-lag': 1,
    }
    if check_updated:
        config['check-updated-too-old'] = check_updated
    return config


@pytest.mark.config(
    UPDATED_TS_MONITORING_SETTINGS={
        '__default__': get_config('disabled'),
        'dbdrivers-drivers-updated-ts-monitor': get_config('dryrun'),
    },
)
async def test_worker_dryrun(run_once):
    counter = await run_once()

    x_message = 'in cursor {}'.format('full_update_cursor')
    assert int(counter['processed']) == 5, x_message
    assert int(counter['missing_updated']) == 1, x_message
    assert int(counter['missing_updated_ts']) == 1, x_message
    assert int(counter['too_old_updated']) == 0, x_message
    assert int(counter['too_old_updated_ts']) == 1, x_message


@pytest.mark.config(
    UPDATED_TS_MONITORING_SETTINGS={
        '__default__': get_config('disabled'),
        'dbdrivers-drivers-updated-ts-monitor': get_config(
            'enabled', check_updated='enabled',
        ),
    },
)
async def test_worker_enabled(run_once, mongodb, pgsql):
    await run_once()

    for doc in mongodb.dbdrivers.find():
        updated = doc.get(UPDATED_FIELD)
        updated_ts = doc.get('updated_ts')

        assert updated is not None
        assert updated_ts is not None
        assert (
            abs(
                int(updated.replace(tzinfo=datetime.timezone.utc).timestamp())
                - updated_ts.time,
            )
            <= 1
        )
