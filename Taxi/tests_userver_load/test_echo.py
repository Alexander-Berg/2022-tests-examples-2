async def test_echo(taxi_userver_load):
    json = {'key': 'some key', 'value': 'some value'}
    response = await taxi_userver_load.post('/echo', json=json)
    assert response.status_code == 200
    assert response.json() == json
