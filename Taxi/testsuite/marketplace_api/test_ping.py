def test_ping(taxi_marketplace_api):
    response = taxi_marketplace_api.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
