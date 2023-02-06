def test_ping(taxi_user_tracker):
    response = taxi_user_tracker.get('ping')
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}
