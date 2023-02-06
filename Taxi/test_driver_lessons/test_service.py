async def test_ping(web_app_client):
    response = await web_app_client.get(f'/ping')
    assert response.status == 200
