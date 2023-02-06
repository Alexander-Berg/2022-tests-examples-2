BASE_CUBE_CLASS = 'DashboardsCube'


async def test_get_all_cubes(web_app_client):
    response = await web_app_client.get('/task-processor/v1/cubes/')
    assert response.status == 200
    content = await response.json()
    assert content['cubes']
