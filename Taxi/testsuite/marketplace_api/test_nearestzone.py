def test_nearestzone(taxi_marketplace_api):
    response = taxi_marketplace_api.post(
        '/v1/nearestzone',
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-API-Key': 'marketplace_api_key',
        },
        json={'point': [37.1946401739712, 55.478983901730004]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['nearest_zone'] == 'moscow'
