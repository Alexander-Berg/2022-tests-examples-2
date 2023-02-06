def test_ping(taxi_communications):
    response = taxi_communications.get('ping')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
