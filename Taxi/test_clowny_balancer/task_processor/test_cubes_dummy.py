async def test_cube_dummy(call_cube):
    response = await call_cube('Dummy', {'name': 'd1mbas'})
    assert response['payload'] == {'message': 'Hello d1mbas'}
