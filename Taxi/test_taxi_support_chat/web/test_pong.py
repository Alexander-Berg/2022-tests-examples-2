async def test_pong(web_app_client):
    response = await web_app_client.get('/pong')
    assert response.status == 200
    content = await response.text()
    assert content == ''
