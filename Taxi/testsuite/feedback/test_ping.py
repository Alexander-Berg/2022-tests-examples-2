def test_ping(taxi_feedback):
    response = taxi_feedback.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
