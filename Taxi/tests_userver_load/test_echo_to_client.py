async def test_echo_to_client(taxi_userver_load):
    json = {'key': 'some echo key', 'value': 'some echo value'}
    response = await taxi_userver_load.post('/echo-to-client', json=json)
    assert response.status_code == 200
    assert response.json() == json
