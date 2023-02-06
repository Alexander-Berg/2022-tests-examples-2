def test_ping(taxi_experiments3_proxy):
    response = taxi_experiments3_proxy.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
