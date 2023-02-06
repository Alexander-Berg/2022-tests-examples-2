async def test_get_cubes(taxi_clowny_roles_web):
    response = await taxi_clowny_roles_web.get('/task-processor/v1/cubes/')
    assert response.status == 200, await response.text()
    result = await response.json()
    assert len(result['cubes']) == 3
