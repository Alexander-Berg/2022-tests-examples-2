def test_ping_reader(taxi_geofence):
    response = taxi_geofence.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
