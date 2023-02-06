async def test_hello(taxi_userver_load):
    response = await taxi_userver_load.get('/hello')
    assert response.status_code == 200
    assert response.text == 'Hello world!\n'
