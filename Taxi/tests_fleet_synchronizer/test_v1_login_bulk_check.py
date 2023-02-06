ENDPOINT_URL = '/fleet-synchronizer/v1/parks/login-bulk-check'


async def test_login_bulk_check(taxi_fleet_synchronizer):

    response = await taxi_fleet_synchronizer.post(
        ENDPOINT_URL,
        json={
            'app_family': 'uberdriver',
            'park_ids': [
                'ParkOne',  # mapped not found
                'ParkTwo',  # mapped inactive
                'ParkThree',  # mapped ok
                'ParkFour',  # unexistent park
            ],
        },
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [{'park_id': 'ParkThree', 'mapped_park_id': 'ParkThreeUber'}],
    }
