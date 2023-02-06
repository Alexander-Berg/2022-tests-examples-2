def test_ping(taxi_parks):
    response = taxi_parks.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
