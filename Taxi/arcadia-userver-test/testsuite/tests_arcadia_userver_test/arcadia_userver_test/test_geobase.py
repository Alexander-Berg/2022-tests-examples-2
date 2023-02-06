async def test_geobase_cityid_by_position(taxi_arcadia_userver_test):
    response = await taxi_arcadia_userver_test.get(
        '/geobase/position/cityid',
        params={'lon': 37.588144, 'lat': 55.733842},
    )

    assert response.status_code == 200
    assert response.json()['city_id'] == 213
