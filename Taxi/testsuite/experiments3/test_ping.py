def test_ping(taxi_experiments3):
    response = taxi_experiments3.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
