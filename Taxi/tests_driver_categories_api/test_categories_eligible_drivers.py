async def test_categories_eligible_drivers(taxi_driver_categories_api):
    response = await taxi_driver_categories_api.post(
        'v1/categories/eligible-drivers',
        params={'park_id': 'ppp'},
        json={'categories': ['c1', 'c2', 'c3']},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'This handler is not implemented yet',
    }
