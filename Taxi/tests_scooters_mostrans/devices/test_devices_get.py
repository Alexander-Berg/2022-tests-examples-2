import pytest


@pytest.mark.parametrize(
    'car_details_response,expected_response',
    [
        pytest.param(
            'scooter_backend_car_details_response.json',
            'expected_scooter_get_response.json',
            id='scooter_get',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'expected_scooter_get_response_filter.json',
            marks=[
                pytest.mark.now('2021-07-20T01:42:00+0300'),
                pytest.mark.config(
                    SCOOTERS_MOSTRANS_FILTER={
                        'imei_mod_factor': 1,
                        'tag_to_send': 'scooter',
                    },
                ),
            ],
            id='scooter_get_with_filter',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'expected_scooter_get_response_filter_hours.json',
            marks=[
                pytest.mark.now('2021-07-20T01:42:00+0300'),
                pytest.mark.config(
                    SCOOTERS_MOSTRANS_FILTER={
                        'imei_mod_factor': 1,
                        'is_add_current_hour_to_imei_mode_factor_enabled': (
                            True
                        ),
                        'tag_to_send': 'scooter',
                    },
                ),
            ],
            id='scooter_get_with_filter_and_hours',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'expected_scooter_get_response_filter_all.json',
            marks=[
                pytest.mark.now('2021-07-20T04:20:00+0300'),
                pytest.mark.config(
                    SCOOTERS_MOSTRANS_FILTER={
                        'imei_mod_factor': 1,
                        'is_add_current_hour_to_imei_mode_factor_enabled': (
                            True
                        ),
                        'tag_to_send': 'scooter',
                    },
                ),
            ],
            id='scooter_get_with_filter_all',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'expected_scooter_get_response_filter_fuel_level_exists.json',
            marks=[
                pytest.mark.now('2021-07-20T01:42:00+0300'),
                pytest.mark.config(
                    SCOOTERS_MOSTRANS_FILTER={
                        'imei_mod_factor': 0,
                        'telematic_sensors': {
                            'fuel_level_exists': True,
                            'fuel_distance_exists': False,
                        },
                    },
                ),
            ],
            id='scooter_get_with_filter_fuel_level_exists',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'expected_scooter_get_response_filter_fuel_distance_exists.json',
            marks=[
                pytest.mark.now('2021-07-20T01:42:00+0300'),
                pytest.mark.config(
                    SCOOTERS_MOSTRANS_FILTER={
                        'imei_mod_factor': 0,
                        'telematic_sensors': {
                            'fuel_level_exists': False,
                            'fuel_distance_exists': True,
                        },
                    },
                ),
            ],
            id='scooter_get_with_filter_fuel_distance_exists',
        ),
    ],
)
async def test_scooter_get(
        taxi_scooters_mostrans,
        mockserver,
        load_json,
        car_details_response,
        expected_response,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(_):
        return mockserver.make_response(
            status=200, json=load_json(car_details_response),
        )

    response = await taxi_scooters_mostrans.get('/devices')
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
    assert mock_car_details.times_called == 1
