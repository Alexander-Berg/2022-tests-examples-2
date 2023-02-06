async def test_maps_expected_destinations_v1(taxi_umlaas_geo_ext, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo_ext.post(
        '/maps/expected_destinations/v1', json=request,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response.json')
