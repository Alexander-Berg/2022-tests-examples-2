async def test_dummy(web_app_client):
    response = await web_app_client.get('/example', params={'name': 'John'})
    assert response.status == 200
    content = await response.json()
    assert content == {'name': 'John', 'greetings': 'Hello, John!'}
