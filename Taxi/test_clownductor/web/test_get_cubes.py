async def test_get_cubes(web_app_client):
    response = await web_app_client.get('/task-processor/v1/cubes/')
    assert response.status == 200
    content = await response.json()
    assert len(content['cubes']) > 1
