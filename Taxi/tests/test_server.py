async def test_server(server_client, mockserver):
    @mockserver.handler('/test')
    def test_handler(request):
        return mockserver.make_response('taxi')

    response = await server_client.get('hello')
    assert response.status == 200
    assert response.text == 'Hello, taxi'

    assert test_handler.times_called
