async def test_categories_availability_to_parks(taxi_driver_categories_api):
    response = await taxi_driver_categories_api.get(
        'v1/categories/availability/to-parks',
        params={'park_id': 'ppp', 'car_id': 'ccc', 'driver_id': 'ddd'},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'This handler is not implemented yet',
    }
