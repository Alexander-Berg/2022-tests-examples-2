import json

import pytest

import tests_driver_status.pg_helpers as pg_helpers


async def _post_status(
        taxi_driver_status, park_id, driver_id, status, expected_code=200,
):
    body = {'park_id': park_id, 'driver_id': driver_id, 'status': status}

    response = await taxi_driver_status.post(
        'v2/status/store', data=json.dumps(body),
    )
    assert response.status_code == expected_code


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'status,expected_code',
    [
        pytest.param('online', 200, id='single status insert online'),
        pytest.param('busy', 200, id='single status insert busy'),
        pytest.param('offline', 200, id='single status insert offline'),
        pytest.param('unknown', 400, id='single status insert unknown'),
        pytest.param('free', 400, id='single status insert free'),
    ],
)
async def test_status_insert(
        taxi_driver_status,
        pgsql,
        mocked_time,
        status,
        expected_code,
        taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'

    await _post_status(
        taxi_driver_status,
        park_id,
        driver_id,
        status,
        expected_code=expected_code,
    )

    if expected_code == 200:
        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_statuses_table(
            pgsql, driver_record_id, status, 'service', mocked_time.now(),
        )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_status_insert_multi(
        taxi_driver_status, pgsql, mocked_time, taxi_config,
):
    park_id = 'parkid000'
    driver_id = 'driverid000'
    statuses = ['online', 'busy', 'offline', 'online']

    for status in statuses:
        await _post_status(taxi_driver_status, park_id, driver_id, status)

        driver_record_id = pg_helpers.check_drivers_table(
            pgsql, park_id, driver_id,
        )
        pg_helpers.check_statuses_table(
            pgsql, driver_record_id, status, 'service', mocked_time.now(),
        )
        mocked_time.sleep(0.001)
