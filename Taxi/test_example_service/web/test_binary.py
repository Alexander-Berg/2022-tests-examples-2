async def test_happy_path(web_app_client):
    response = await web_app_client.post(
        '/binary/random',
        data=b'101',
        headers={'Content-Type': 'application/octet-stream'},
    )
    assert response.status == 200
    assert await response.read() == b'abac101'


async def test_referenced_response(web_app_client):
    response = await web_app_client.post(
        '/binary/random/',
        params={'code': '404'},
        data=b'101',
        headers={'Content-Type': 'application/octet-stream'},
    )

    assert response.status == 404
    assert await response.read() == b'xxx'
