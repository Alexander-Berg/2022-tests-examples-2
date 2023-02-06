async def test_ping(taxi_render_template_client):
    response = await taxi_render_template_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
