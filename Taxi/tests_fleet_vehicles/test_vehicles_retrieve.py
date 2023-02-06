import pytest

EXPECTED_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'car_id': 'car1',
                'amenities': ['animals', 'lightbox'],
                'lightbox_confirmed': False,
                'sticker_confirmed': True,
                'cert_verification': True,
                'number': '0001',
                'number_normalized': '0001',
                'park_id': 'park1',
                'rental': True,
                'status': 'working',
                'vin': 'XW8ED45J7DK123456',
                'registration_cert': '100500',
            },
            'park_id_car_id': 'park1_car1',
            'revision': '0_1500000000_1',
        },
        {
            'data': {
                'car_id': 'car2',
                'number': 'ТТ003777',
                'number_normalized': 'TT003777',
                'park_id': 'park1',
                'status': 'working',
                'boosters': 0,
                'confirmed_boosters': 0,
                'chairs': [
                    {
                        'brand': 'Other',
                        'isofix': False,
                        'categories': [1, 2, 3],
                    },
                ],
                'confirmed_chairs': [{'is_enabled': True}],
                'driver_boosters': [{'driver_profile_id': 'uuid1', 'data': 1}],
                'driver_confirmed_boosters': [
                    {'driver_profile_id': 'uuid1', 'data': 0},
                ],
                'driver_chairs': [
                    {
                        'driver_profile_id': 'uuid1',
                        'data': [{'brand': 'Other', 'isofix': False}],
                    },
                ],
                'driver_confirmed_chairs': [
                    {
                        'driver_profile_id': 'uuid1',
                        'data': [{'is_enabled': False}],
                    },
                ],
                'rental': False,
            },
            'park_id_car_id': 'park1_car2',
            'revision': '0_1500000000_2',
        },
    ],
}


async def test_vehicles_retrieve(taxi_fleet_vehicles, sort_amenities):

    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/retrieve',
        params={'consumer': 'test'},
        json={'id_in_set': ['park1_car1', 'park1_car2']},
    )
    assert response.status_code == 200

    response_json = response.json()
    sort_amenities(response_json)
    assert response_json == EXPECTED_RESPONSE


@pytest.mark.parametrize(
    'uri', ['v1/vehicles/retrieve', 'v1/vehicles/cache-retrieve'],
)
async def test_two_underscores(taxi_fleet_vehicles, uri):

    response = await taxi_fleet_vehicles.post(
        uri, params={'consumer': 'test'}, json={'id_in_set': ['park4_car_1']},
    )
    assert response.status_code == 200
    assert response.json() == {
        'vehicles': [
            {
                'data': {
                    'car_id': 'car_1',
                    'number': '0001',
                    'park_id': 'park4',
                    'status': 'working',
                },
                'park_id_car_id': 'park4_car_1',
                'revision': '0_1500000001_4',
            },
        ],
    }


@pytest.mark.parametrize('car_id', ['_', '__', 'asd_', '', 'qwe'])
async def test_invalid_id(taxi_fleet_vehicles, car_id):

    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/retrieve',
        params={'consumer': 'test'},
        json={'id_in_set': [car_id]},
    )
    assert response.status_code == 400
    assert response.text == 'invalid id'


async def test_vehicles_retrieve_by_park(taxi_fleet_vehicles, sort_amenities):

    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/retrieve_by_park',
        params={'consumer': 'test'},
        json={'park_id': 'park1'},
    )
    assert response.status_code == 200
    response_json = response.json()
    sort_amenities(response_json)
    assert response_json == EXPECTED_RESPONSE


async def test_vehicles_retrieve_by_number(
        taxi_fleet_vehicles, sort_amenities,
):

    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/retrieve_by_number_with_normalization',
        params={'consumer': 'test'},
        json={'numbers_in_set': ['   0001']},
    )
    assert response.status_code == 200
    response_json = response.json()
    sort_amenities(response_json)

    assert response_json == {
        'vehicles': [
            {
                'data': {
                    'amenities': ['animals', 'lightbox'],
                    'car_id': 'car1',
                    'cert_verification': True,
                    'lightbox_confirmed': False,
                    'number': '0001',
                    'number_normalized': '0001',
                    'park_id': 'park1',
                    'registration_cert': '100500',
                    'rental': True,
                    'status': 'working',
                    'sticker_confirmed': True,
                    'vin': 'XW8ED45J7DK123456',
                },
                'park_id_car_id': 'park1_car1',
                'revision': '0_1500000000_1',
            },
        ],
    }

    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/retrieve_by_number_with_normalization',
        params={'consumer': 'test'},
        json={'numbers_in_set': ['ТТ003777', '0001   ']},
    )
    assert response.status_code == 200

    response_json = response.json()
    sort_amenities(response_json)
    assert response_json == {
        'vehicles': [
            {
                'data': {
                    'car_id': 'car3',
                    'number': 'ТТ003777',
                    'number_normalized': 'TT003777',
                    'park_id': 'park3',
                    'status': 'working',
                },
                'park_id_car_id': 'park3_car3',
                'revision': '0_1500000001_3',
            },
            {
                'data': {
                    'car_id': 'car2',
                    'number': 'ТТ003777',
                    'number_normalized': 'TT003777',
                    'park_id': 'park1',
                    'rental': False,
                    'status': 'working',
                },
                'park_id_car_id': 'park1_car2',
                'revision': '0_1500000000_2',
            },
            {
                'data': {
                    'amenities': ['animals', 'lightbox'],
                    'car_id': 'car1',
                    'cert_verification': True,
                    'lightbox_confirmed': False,
                    'number': '0001',
                    'number_normalized': '0001',
                    'park_id': 'park1',
                    'registration_cert': '100500',
                    'rental': True,
                    'status': 'working',
                    'sticker_confirmed': True,
                    'vin': 'XW8ED45J7DK123456',
                },
                'park_id_car_id': 'park1_car1',
                'revision': '0_1500000000_1',
            },
        ],
    }
