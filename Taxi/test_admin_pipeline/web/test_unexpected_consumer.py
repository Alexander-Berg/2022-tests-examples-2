async def test_enumerate(web_app_client):
    response = await web_app_client.post(
        '/v2/pipeline/enumerate', params={'consumer': 'invalid'},
    )
    assert response.status == 400
    data = await response.json()

    assert data == {
        'code': 'unexpected_consumer',
        'message': 'Unexpected consumer: invalid',
    }
