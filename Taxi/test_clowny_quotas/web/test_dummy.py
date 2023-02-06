async def test_empty_handle(web_app_client):
    response = await web_app_client.get(
        '/quotas', params={'resource_provider': 'yp_quotas'},
    )
    assert response.status == 200
    content = await response.json()
    print(content)
    assert content == {}
