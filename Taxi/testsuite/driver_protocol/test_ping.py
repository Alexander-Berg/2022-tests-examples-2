def test_ping(taxi_driver_protocol):
    response = taxi_driver_protocol.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
