async def test_big_ok(web_app_client):
    body = b'10' * (5 * 1024 ** 2)
    response = await web_app_client.post(
        '/binary/random',
        data=body,
        headers={'Content-Type': 'application/octet-stream'},
    )
    assert response.status == 200
    assert await response.read() == b'abac' + body


async def test_413(web_app_client):
    body = b'10' * (15 * 1024 ** 2)
    response = await web_app_client.post(
        '/binary/random',
        data=body,
        headers={'Content-Type': 'application/octet-stream'},
    )
    assert response.status == 413
    assert (await response.text()).startswith(
        'Maximum request body size 20971520 exceeded',
    )
