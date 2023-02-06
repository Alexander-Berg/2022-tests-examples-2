def test_integration_ping(taxi_integration):
    response = taxi_integration.get('ping')
    assert response.status_code == 200
