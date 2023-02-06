async def test_multiunit(taxi_arcadia_userver_test, common_fixture):
    response = await taxi_arcadia_userver_test.get('/ping')
    assert response.status == 200
    assert common_fixture == 'foo'
