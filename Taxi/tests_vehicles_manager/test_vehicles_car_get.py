import pytest

from tests_vehicles_manager import utils


ENDPOINT_URL = '/fleet-api/v1/vehicles/car'


@pytest.mark.parametrize(
    'vehicle_id', ('12345', '123456', '1234567', '12345678'),
)
async def test_get_ok(
        taxi_vehicles_manager, load_json, mock_fleet_vehicles, vehicle_id,
):
    retrieve_response = load_json('vehicles.json')[vehicle_id]
    expected_response = load_json('responses.json')[vehicle_id]
    mock_fleet_vehicles.set_data(retrieve_response, utils.PARK_ID, vehicle_id)

    response = await taxi_vehicles_manager.get(
        ENDPOINT_URL,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params={'vehicle_id': vehicle_id},
    )

    assert mock_fleet_vehicles.has_mock_calls, response.text
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_vehicle_not_found(taxi_vehicles_manager, mock_fleet_vehicles):
    vehicle_id = 'wrong_vehicle_id'

    mock_fleet_vehicles.set_data(
        park_id=utils.PARK_ID, vehicle_id=vehicle_id, vehicle_not_foud=True,
    )

    response = await taxi_vehicles_manager.get(
        ENDPOINT_URL,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params={'vehicle_id': vehicle_id},
    )

    assert mock_fleet_vehicles.has_mock_calls, response.text
    assert response.status_code == 404, response.text
    assert response.json() == {'code': '404', 'message': 'vehicle not found'}
