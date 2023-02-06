async def test_ping(hiring_forms_mockserver, web_app_client, wait_until_ready):
    await wait_until_ready()
    response = await web_app_client.get('/ping')
    assert response.status == 200
    await response.json()
