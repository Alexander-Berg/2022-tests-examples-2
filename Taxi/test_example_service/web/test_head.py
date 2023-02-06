async def test_head(web_app_client):
    response = await web_app_client.head('/ping')
    content = await response.text()
    assert response.status == 200
    assert content == ''
