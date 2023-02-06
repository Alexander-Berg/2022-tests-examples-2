EXPECTED_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'amenities': ['animals', 'lightbox'],
                'car_id': 'car1',
                'cert_verification': True,
                'lightbox_confirmed': False,
                'number': '0001',
                'park_id': 'park1',
                'registration_cert': '100500',
                'status': 'working',
                'sticker_confirmed': True,
                'vin': 'XW8ED45J7DK123456',
            },
            'park_id_car_id': 'park1_car1',
            'revision': '0_1500000000_1',
        },
        {
            'data': {
                'car_id': 'car2',
                'number': '0002',
                'park_id': 'park1',
                'status': 'working',
            },
            'park_id_car_id': 'park1_car2',
            'revision': '0_1500000000_2',
        },
        {
            'data': {'car_id': 'car_1', 'number': '0001', 'park_id': 'park2'},
            'park_id_car_id': 'park2_car_1',
            'revision': '0_1500000000_3',
        },
    ],
    'cache_lag': 101275005,
    'last_revision': '0_1500000000_3',
    'last_modified': '2017-07-14T02:40:00Z',
}


async def test_vehicles_updates(taxi_fleet_vehicles, sort_amenities):
    response = await taxi_fleet_vehicles.post(
        'v1/vehicles/updates?consumer=test', json={},
    )
    assert response.status_code == 200
    result = response.json()
    sort_amenities(result)

    assert result['vehicles'] == EXPECTED_RESPONSE['vehicles']
    assert result['last_revision'] == EXPECTED_RESPONSE['last_revision']
    assert result['last_modified'] == EXPECTED_RESPONSE['last_modified']
