import http


async def test_ping(api_app_client):
    response = await api_app_client.get('/ping')
    assert response.status == http.HTTPStatus.OK
    content = await response.text()
    assert content == ''
