import datetime
import json
import operator
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import tired_drivers
from tests_driver_weariness import weariness_tools


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql('drivers_status_ranges', files=['pg_working_ranges.sql'])
@pytest.mark.parametrize(
    'udid, status_code, expected_response, config',
    [
        pytest.param(
            'unique1',
            200,
            {
                'unique_driver_id': 'unique1',
                'updated': '2021-02-19T15:53:00+0000',
                'tired_status': 'hours_exceed',
                'remaining_time': 0,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
                'last_online': '1970-01-01T00:00:00+0000',
                'last_status_time': '1970-01-01T00:00:00+0000',
                'block_time': '2021-02-19T16:00:00+0000',
                'block_till': '2021-02-19T16:13:00+0000',
                'is_new_weariness': True,
                'current_rest_minutes': 7,
                'long_rest_minutes': 20,
            },
            weariness_tools.WearinessConfig(20, 19, 12),
        ),
        pytest.param(
            'unique1',
            200,
            {
                'unique_driver_id': 'unique1',
                'updated': '2021-02-19T15:53:00+0000',
                'tired_status': 'no_long_rest',
                'remaining_time': 0,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
                'last_online': '1970-01-01T00:00:00+0000',
                'last_status_time': '1970-01-01T00:00:00+0000',
                'block_time': '2021-02-19T16:00:00+0000',
                'block_till': '2021-02-19T16:13:00+0000',
                'is_new_weariness': True,
                'current_rest_minutes': 7,
                'long_rest_minutes': 20,
            },
            weariness_tools.WearinessConfig(20, 17, 13),
        ),
        pytest.param(
            'unique1',
            200,
            {
                'unique_driver_id': 'unique1',
                'updated': '2021-02-19T15:53:00+0000',
                'tired_status': 'not_tired',
                'remaining_time': 60,
                'working_time': 12 * 60,
                'working_time_no_rest': 18 * 60,
                'last_online': '1970-01-01T00:00:00+0000',
                'last_status_time': '1970-01-01T00:00:00+0000',
                'is_new_weariness': True,
                'current_rest_minutes': 7,
                'long_rest_minutes': 20,
            },
            weariness_tools.WearinessConfig(20, 19, 13),
        ),
        pytest.param(
            'unique1',
            200,
            {
                'unique_driver_id': 'unique1',
                'tired_status': 'not_tired',
                'updated': '2021-02-19T16:00:00+0000',
                'working_time': 0,
                'working_time_no_rest': 0,
                'remaining_time': 13 * 60,
                'last_online': '1970-01-01T00:00:00+0000',
                'last_status_time': '1970-01-01T00:00:00+0000',
                'is_new_weariness': True,
                'current_rest_minutes': 0,
                'long_rest_minutes': 6,
            },
            weariness_tools.WearinessConfig(6, 19, 13),
        ),
        (
            'unique2',
            404,
            {'message': 'no weariness info about driver unique2'},
            None,
        ),
        (
            'UNKNOWN_id',
            404,
            {'message': 'no weariness info about driver UNKNOWN_id'},
            None,
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config_default.json')
async def test_driver_weariness(
        taxi_driver_weariness,
        udid: str,
        status_code: int,
        expected_response: Dict[str, Any],
        config: Optional[weariness_tools.WearinessConfig],
        experiments3,
):
    if config:
        weariness_tools.add_experiment(experiments3, config)
    await taxi_driver_weariness.invalidate_caches(clean_update=False)

    response = await taxi_driver_weariness.post(
        'v1/driver-weariness', data=json.dumps({'unique_driver_id': udid}),
    )

    assert response.status_code == status_code
    assert response.json() == expected_response

    is_tired = (
        status_code == 200 and expected_response['tired_status'] != 'not_tired'
    )
    await tired_drivers.verify_tired_drivers(
        taxi_driver_weariness, udid, is_tired, expected_response,
    )


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql('drivers_status_ranges', files=['pg_working_ranges.sql'])
async def test_driver_weariness_cache_updating(
        taxi_driver_weariness, experiments3, mocked_time, pgsql,
):
    # Driver had been working for 20 minutes in total
    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(20, 25, 19),
    )
    await taxi_driver_weariness.invalidate_caches(clean_update=False)

    udid = 'unique4'
    response = await taxi_driver_weariness.post(
        'v1/driver-weariness', data=json.dumps({'unique_driver_id': udid}),
    )

    expected_response = {
        'unique_driver_id': 'unique4',
        'updated': '2021-02-19T15:53:00+0000',
        'tired_status': 'hours_exceed',
        'remaining_time': 0,
        'working_time': 20 * 60,
        'working_time_no_rest': 23 * 60,
        'last_online': '1970-01-01T00:00:00+0000',
        'last_status_time': '1970-01-01T00:00:00+0000',
        'block_time': '2021-02-19T16:00:00+0000',
        'block_till': '2021-02-19T16:13:00+0000',
        'is_new_weariness': True,
        'current_rest_minutes': 7,
        'long_rest_minutes': 20,
    }
    assert response.status_code == 200
    assert response.json() == expected_response
    await tired_drivers.verify_tired_drivers(
        taxi_driver_weariness, udid, True, expected_response,
    )

    # After 1 minute, we got another one range with 1 work minute. block_until
    # field should move for one minute too, but block_time should be the same
    mocked_time.set(datetime.datetime(2021, 2, 19, 16, 1))

    expected_response['block_till'] = '2021-02-19T16:14:00+0000'
    cursor = pgsql['drivers_status_ranges'].cursor()
    cursor.execute(
        f'INSERT INTO weariness.working_ranges '
        f'(park_driver_profile_id, range_begin, range_end, updated_at) '
        f'VALUES (\'dbid_uuid40\',\'2021-02-19T18:53:00+0300\','
        f'\'2021-02-19T18:54:00+0300\',\'2021-02-19T19:01:00+0300\')',
    )
    await taxi_driver_weariness.invalidate_caches(clean_update=False)

    response = await taxi_driver_weariness.post(
        'v1/driver-weariness', data=json.dumps({'unique_driver_id': udid}),
    )

    assert response.status_code == 200
    await tired_drivers.verify_tired_drivers(
        taxi_driver_weariness, udid, True, expected_response,
    )


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.experiments3(filename='exp3_config_default.json')
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            [
                {
                    'unique_driver_id': 'unique1',
                    'tired_status': 'hours_exceed',
                    'block_time': '2021-02-19T16:00:00+0000',
                    'block_till': '2021-02-19T16:13:00+0000',
                },
                {
                    'unique_driver_id': 'unique4',
                    'tired_status': 'no_long_rest',
                    'block_time': '2021-02-19T16:00:00+0000',
                    'block_till': '2021-02-19T16:13:00+0000',
                },
            ],
            marks=pytest.mark.pgsql(
                'drivers_status_ranges', files=['pg_working_ranges.sql'],
            ),
            id='old cache is used by default',
        ),
        pytest.param(
            [
                {
                    'unique_driver_id': 'unique1',
                    'tired_status': 'no_long_rest',
                    'block_time': '2021-02-19T16:00:00+0000',
                    'block_till': '2021-02-19T16:10:00+0000',
                },
            ],
            marks=pytest.mark.pgsql(
                'drivers_status_ranges', files=['pg_new_working_ranges.sql'],
            ),
            id='new cache is used by default',
        ),
    ],
)
async def test_tired_drivers(
        taxi_driver_weariness,
        experiments3,
        expected_response: List[Dict[str, str]],
):
    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(20, 19, 12),
    )
    await taxi_driver_weariness.invalidate_caches(clean_update=False)

    response = await taxi_driver_weariness.get('v1/tired-drivers')

    assert response.status_code == 200
    response_json_items = response.json()['items']
    response_json_items.sort(key=operator.itemgetter('unique_driver_id'))
    assert response_json_items == expected_response
