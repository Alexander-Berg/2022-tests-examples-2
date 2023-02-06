async def test_happy_path(web_app_client):
    response = await web_app_client.get(
        '/raise_error_response', params={'name': 'Arthas'},
    )
    assert response.status == 404
    assert await response.json() == {'name': 'Arthas'}
