async def test_expected_destinations(taxi_umlaas_geo_ext, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo_ext.post(
        '/expected_destinations', json=request,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response.json')
