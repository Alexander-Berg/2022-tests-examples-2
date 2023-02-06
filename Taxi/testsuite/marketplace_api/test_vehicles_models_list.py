def test_vehicles_models_list(taxi_marketplace_api):
    response = taxi_marketplace_api.get(
        '/v1/vehicles/models/list',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['brands']) == 2
