async def test_handler(web_app_client):
    response = await web_app_client.get('/v1/audit/config/')
    assert response.status == 200
    assert (await response.json()) == {}
