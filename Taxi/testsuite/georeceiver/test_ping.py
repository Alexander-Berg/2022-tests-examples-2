def test_ping(taxi_georeceiver):
    response = taxi_georeceiver.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
