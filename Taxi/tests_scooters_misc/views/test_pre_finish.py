import datetime

import pytest
from tests_plugins import utils


NOW = datetime.datetime.now()
URL = '/scooters-misc/v1/pre-finish'
SCOOTER_ID = 'SCOOTER_ID'
POS_INSIDE_PARKING = [30.393905, 59.936387]
POS_OUTSIDE_PARKING = [30.377909, 59.939088]
POS_NEAR_USER = [30.3941607, 59.936187]
POS_FAR_FROM_USER = [30.388395, 59.928780]
AUTH_HEADERS = {'X-Yandex-UID': '4060779350'}


@pytest.mark.parametrize(
    'user_position, scooter_position, allow_finish',
    [
        pytest.param(POS_INSIDE_PARKING, POS_NEAR_USER, True, id='ok'),
        pytest.param(
            POS_OUTSIDE_PARKING,
            POS_OUTSIDE_PARKING,
            False,
            id='user_position_outside_parking_area',
        ),
        pytest.param(
            POS_INSIDE_PARKING,
            POS_FAR_FROM_USER,
            False,
            id='scooter_far_from_user',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_scooters_misc_pre_finish.json')
async def test_base(
        taxi_scooters_misc,
        user_position,
        scooter_position,
        allow_finish,
        mockserver,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def car_telematics_state_mock(_):
        return {
            'sensors': [
                {
                    'id': 102,
                    'name': 'VEGA_LON',
                    'since': int(utils.timestamp(NOW)),
                    'updated': int(utils.timestamp(NOW)),
                    'value': scooter_position[0],
                },
                {
                    'id': 101,
                    'name': 'VEGA_LAT',
                    'since': int(utils.timestamp(NOW)),
                    'updated': int(utils.timestamp(NOW)),
                    'value': scooter_position[1],
                },
            ],
        }

    response = await taxi_scooters_misc.post(
        URL,
        json={'scooter_id': SCOOTER_ID, 'user_position': user_position},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'allow_finish': allow_finish}

    assert car_telematics_state_mock.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_misc_pre_finish.json')
async def test_no_user_position(taxi_scooters_misc):
    response = await taxi_scooters_misc.post(
        URL, json={'scooter_id': SCOOTER_ID}, headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'allow_finish': False}


@pytest.mark.experiments3(filename='exp3_scooters_misc_pre_finish.json')
async def test_sensor_too_old(taxi_scooters_misc, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def car_telematics_state_mock(_):
        return {
            'sensors': [
                {
                    'id': 102,
                    'name': 'VEGA_LON',
                    'since': 10,
                    'updated': 10,
                    'value': POS_FAR_FROM_USER[0],
                },
                {
                    'id': 101,
                    'name': 'VEGA_LAT',
                    'since': 10,
                    'updated': 10,
                    'value': POS_FAR_FROM_USER[1],
                },
            ],
        }

    response = await taxi_scooters_misc.post(
        URL,
        json={'scooter_id': SCOOTER_ID, 'user_position': POS_INSIDE_PARKING},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'allow_finish': True}

    assert car_telematics_state_mock.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_misc_pre_finish.json')
async def test_cache_failure(taxi_scooters_misc, testpoint, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/telematics/state')
    def car_telematics_state_mock(_):
        return {
            'sensors': [
                {
                    'id': 102,
                    'name': 'VEGA_LON',
                    'since': int(utils.timestamp(NOW)),
                    'updated': int(utils.timestamp(NOW)),
                    'value': POS_NEAR_USER[0],
                },
                {
                    'id': 101,
                    'name': 'VEGA_LAT',
                    'since': int(utils.timestamp(NOW)),
                    'updated': int(utils.timestamp(NOW)),
                    'value': POS_NEAR_USER[1],
                },
            ],
        }

    @testpoint('scooters-polygon-cache-injected-error')
    def task_testpoint(_):
        return {'inject_failure': True}

    response = await taxi_scooters_misc.post(
        URL,
        json={'user_position': POS_INSIDE_PARKING, 'scooter_id': SCOOTER_ID},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 500
    assert response.json() == {
        'code': 'polygon_cache_failure',
        'message': 'Failed to get scooters polygon cache',
    }

    assert task_testpoint.times_called == 1
    assert car_telematics_state_mock.times_called == 1
