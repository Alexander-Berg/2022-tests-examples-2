def test_launch_simple(taxi_integration):
    response = taxi_integration.post('3.0/launch', {})
    assert response.status_code == 200
    data = response.json()
    assert not data['authorized']
    user_id = data['id']

    response = taxi_integration.post('3.0/launch', {'id': user_id})
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == user_id
    assert not data['authorized']
