import datetime

import pytest

from test_pro_profiles_removal import conftest


@pytest.mark.now(conftest.TEST_NOW)
@pytest.mark.config(
    PRO_PROFILES_REMOVAL_CANCELATION_FREEZING_TIME={'freezing_hours': 3},
)
@pytest.mark.parametrize(
    'expected_status, contractor_profile_id, forward_time',
    [
        pytest.param(
            'none',
            'driver_id1',
            datetime.timedelta(hours=0),
            id='status_none',
        ),
        pytest.param(
            'none',
            '150982b584844dfcab07f29adf9661abcanceled',
            datetime.timedelta(hours=0),
            id='canceled_status_none',
        ),
        pytest.param(
            'in_progress',
            conftest.TEST_DRIVER_ID_1,
            datetime.timedelta(hours=4),
            id='status_in_work',
        ),
        pytest.param(
            'freezed',
            conftest.TEST_DRIVER_ID_1,
            datetime.timedelta(hours=2),
            id='status_freezed',
        ),
        pytest.param(
            'freezed_by_cancelation',
            conftest.TEST_DRIVER_ID_4,
            datetime.timedelta(hours=0),
            id='status_freezed_by_cancelation',
        ),
    ],
)
async def test_removal_request_status(
        taxi_pro_profiles_removal_web,
        fleet_parks,
        driver_ui_profile,
        client_experiments3,
        mocked_time,
        load_json,
        expected_status,
        contractor_profile_id,
        forward_time,
):
    client_experiments3.add_record(
        consumer='pro-profiles-removal/removal_request_status',
        config_name='pro-profiles-removal_info_url',
        args=[
            {
                'name': 'park_id',
                'type': 'string',
                'value': conftest.TEST_PARK_ID,
            },
            {
                'name': 'driver_profile_id',
                'type': 'string',
                'value': contractor_profile_id,
            },
            {'name': 'country_id', 'type': 'string', 'value': 'rus'},
            {
                'name': 'display_profile',
                'type': 'string',
                'value': 'display_profile',
            },
        ],
        value={'info_url': 'https://ya.ru'},
    )
    headers = conftest.TEST_HEADERS
    headers.update({'X-YaTaxi-Driver-Profile-Id': contractor_profile_id})
    mocked_time.sleep(forward_time.total_seconds())
    expected_responses = load_json('expected_responses.json')
    response = await taxi_pro_profiles_removal_web.get(
        '/driver/v1/profiles/removal_request_status', headers=headers,
    )

    assert response.status == 200
    body = await response.json()
    assert body == expected_responses[expected_status]
