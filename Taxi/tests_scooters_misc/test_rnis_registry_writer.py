import pytest

DISTLOCK_NAME = 'scooters-misc-rnis-registry-writer'


@pytest.mark.config(
    SCOOTERS_MISC_RNIS_REGISTRY_WRITER_SETTINGS={
        'sleep_time_ms': 100,
        'enabled': True,
        'timeout_between_requests_ms': 1,
    },
)
@pytest.mark.now('2021-06-23T12:00:00+0000')
@pytest.mark.parametrize(
    'car_details_response,rnis_response,expected_create_update_count,'
    'expected_delete_count,expected_deleted_vehicle',
    [
        pytest.param(
            'scooter_backend_car_details_response.json',
            'rnis_registry_v1_vehicle_response_empty.json',
            2,
            0,
            None,
            id='create_all',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'rnis_registry_v1_vehicle_response_need_update.json',
            1,
            1,
            '102',
            id='update_delete',
        ),
        pytest.param(
            'scooter_backend_car_details_response.json',
            'rnis_registry_v1_vehicle_response_all_created.json',
            0,
            0,
            None,
            id='no_update_create_delete',
        ),
    ],
)
async def test_rnis_registry_writer(
        taxi_scooters_misc,
        mockserver,
        load_json,
        car_details_response,
        rnis_response,
        expected_create_update_count,
        expected_delete_count,
        expected_deleted_vehicle,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(_):
        return mockserver.make_response(
            status=200, json=load_json(car_details_response),
        )

    @mockserver.json_handler('/rnis/api/v1/vehicle')
    def mock_rnis_vehicle(request):
        if request.method == 'GET':
            return mockserver.make_response(
                status=200, json=load_json(rnis_response),
            )
        if request.method == 'POST' and expected_create_update_count > 0:
            return mockserver.make_response(
                status=200,
                json=load_json('rnis_registry_v1_vehicle_POST_response.json'),
            )
        return mockserver.make_response(status=500, json={})

    @mockserver.json_handler(
        f'/rnis/api/v1/vehicle/{expected_deleted_vehicle}',
    )
    def mock_rnis_vehicle_delete(request):
        if (
                request.method == 'DELETE'
                and expected_deleted_vehicle
                and expected_delete_count > 0
        ):
            return mockserver.make_response(status=200, json={})
        return mockserver.make_response(status=500, json={})

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert mock_car_details.times_called == 2
    assert mock_rnis_vehicle.times_called == 1 + expected_create_update_count
    assert mock_rnis_vehicle_delete.times_called == expected_delete_count
