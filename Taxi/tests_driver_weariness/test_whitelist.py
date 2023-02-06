# flake8: noqa IS001, I101
import datetime
import json
from typing import Dict, Any

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import tired_drivers
from tests_driver_weariness import weariness_tools


@pytest.mark.now('2021-02-19T15:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.parametrize(
    'first_ttl, second_ttl, status_code',
    [
        ('2021-02-19T16:00:00+0000', '2021-02-19T16:00:00+0000', 200),
        ('2021-02-19T16:00:00+0000', '2022-02-19T16:00:00+0000', 409),
    ],
)
async def test_whitelist_add_same(
        taxi_driver_weariness,
        first_ttl: str,
        second_ttl: str,
        status_code: int,
        pgsql,
):
    response = await taxi_driver_weariness.post(
        'v1/whitelist/add',
        data=json.dumps({'unique_driver_id': 'unique1', 'ttl': first_ttl}),
        headers={'X-Yandex-Login': 'ivanov'},
    )
    assert response.status_code == 200
    whitelist = weariness_tools.select_whitelist(
        pgsql['drivers_status_ranges'],
    )
    assert whitelist == [
        {'unique_driver_id': 'unique1', 'author': 'ivanov', 'ttl': first_ttl},
    ]

    response = await taxi_driver_weariness.post(
        'v1/whitelist/add',
        data=json.dumps({'unique_driver_id': 'unique1', 'ttl': second_ttl}),
        headers={'X-Yandex-Login': 'sidorov'},
    )
    assert response.status_code == 200
    whitelist = weariness_tools.select_whitelist(
        pgsql['drivers_status_ranges'],
    )
    assert whitelist == [
        {
            'unique_driver_id': 'unique1',
            'author': 'sidorov',
            'ttl': second_ttl,
        },
    ]


_NOW = datetime.datetime(2021, 2, 19, 16)


@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql('drivers_status_ranges', files=['pg_working_ranges.sql'])
@pytest.mark.parametrize(
    'whitelist_ttl, expected_fields, config',
    [
        pytest.param(
            datetime.datetime(2021, 2, 19, 16, 15),
            {
                'tired_status': 'not_tired',
                'remaining_time': 15 * 60,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
            },
            weariness_tools.WearinessConfig(100, 15, 10),
            id='all checks are failing, but there is whitelist ttl',
        ),
        pytest.param(
            datetime.datetime(2021, 2, 19, 16, 15),
            {
                'tired_status': 'not_tired',
                'remaining_time': 15 * 60,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
            },
            weariness_tools.WearinessConfig(100, 25, 20),
            id='ttl in whitelist is further in time, than any other locks',
        ),
        pytest.param(
            datetime.datetime(2021, 2, 19, 16, 15),
            {
                'tired_status': 'not_tired',
                'remaining_time': 188 * 60,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
            },
            weariness_tools.WearinessConfig(100, 250, 200),
            id='ttl in whitelist is not further in time, than any other locks',
        ),
        pytest.param(
            datetime.datetime(2021, 2, 19, 15, 15),
            {
                'tired_status': 'hours_exceed',
                'remaining_time': 0,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
                'block_time': '2021-02-19T16:00:00+0000',
                'block_till': '2021-02-19T17:33:00+0000',
            },
            weariness_tools.WearinessConfig(100, 20, 10),
            id='whitelist entry is too old',
        ),
    ],
)
async def test_whitelist_add(
        taxi_driver_weariness,
        whitelist_ttl: datetime.datetime,
        expected_fields: Dict[str, Any],
        config: weariness_tools.WearinessConfig,
        mocked_time,
        experiments3,
):
    weariness_tools.add_experiment(experiments3, config)
    await taxi_driver_weariness.invalidate_caches()

    udid = 'unique1'

    # time is updated to be able to set ttl in the past
    mocked_time.set(whitelist_ttl)

    response = await taxi_driver_weariness.post(
        'v1/whitelist/add',
        data=json.dumps(
            {
                'unique_driver_id': udid,
                'ttl': whitelist_ttl.isoformat() + '+0000',
            },
        ),
        headers={'X-Yandex-Login': 'abacaba'},
    )

    mocked_time.set(_NOW)

    assert response.status_code == 200
    await taxi_driver_weariness.invalidate_caches()

    response = await taxi_driver_weariness.post(
        'v1/driver-weariness', data=json.dumps({'unique_driver_id': udid}),
    )

    assert response.status_code == 200
    result = response.json()
    for key, val in expected_fields.items():
        assert result[key] == val

    is_tired = expected_fields['tired_status'] != 'not_tired'
    await tired_drivers.verify_tired_drivers(
        taxi_driver_weariness, udid, is_tired, expected_fields,
    )


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
async def test_wrong_ttl(taxi_driver_weariness):
    response = await taxi_driver_weariness.post(
        'v1/whitelist/add',
        data=json.dumps(
            {'unique_driver_id': 'unique1', 'ttl': '2021-02-19T18:00:00+0300'},
        ),
        headers={'X-Yandex-Login': 'abacaba'},
    )

    assert response.status_code == 400
