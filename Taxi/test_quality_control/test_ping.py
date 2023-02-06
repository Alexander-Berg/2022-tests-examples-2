import http


async def test_ping(qc_client):
    response = await qc_client.get('/ping')
    assert response.status == http.HTTPStatus.OK
    content = await response.text()
    assert content == ''
