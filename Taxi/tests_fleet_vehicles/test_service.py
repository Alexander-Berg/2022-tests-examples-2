# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from fleet_vehicles_plugins.generated_tests import *  # noqa

EXPECTED_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'car_id': 'car1-1',
                'cert_verification': True,
                'number': '0001',
                'park_id': 'park1',
                'status': 'working',
                'vin': 'XW8ED45J7DK123456',
            },
            'park_id_car_id': 'park1_car1-1',
            'revision': '0_1500000000_1',
        },
        {
            'data': {
                'car_id': 'car2',
                'number': '0003',
                'park_id': 'park2',
                'status': 'working',
            },
            'park_id_car_id': 'park2_car2',
            'revision': '0_1500000000_3',
        },
        {'park_id_car_id': 'park1_carUnknown'},
        {'park_id_car_id': 'parkUnknown_car2'},
        {'park_id_car_id': 'parkUnknown_carUnknown'},
    ],
}


async def test_retrieve(taxi_fleet_vehicles):
    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/retrieve',
        params={'consumer': 'test'},
        json={
            'id_in_set': [
                'park1_car1-1',
                'park2_car2',
                'park1_carUnknown',
                'parkUnknown_car2',
                'parkUnknown_carUnknown',
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE
