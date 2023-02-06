def test_ping_handles(taxi_geofence_handles):
    response = taxi_geofence_handles.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
