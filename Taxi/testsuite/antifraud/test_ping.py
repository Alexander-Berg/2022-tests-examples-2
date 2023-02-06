def test_ping(taxi_antifraud):
    response = taxi_antifraud.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
