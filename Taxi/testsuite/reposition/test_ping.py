def test_ping(taxi_reposition):
    response = taxi_reposition.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
