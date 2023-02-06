def test_ping(taxi_fleet_management_api):
    response = taxi_fleet_management_api.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
