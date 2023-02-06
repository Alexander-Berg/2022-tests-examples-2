def test_ping(taxi_ml):
    response = taxi_ml.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
