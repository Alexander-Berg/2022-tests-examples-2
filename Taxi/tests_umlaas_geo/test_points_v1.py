URL = 'umlaas-geo/v1/points'


async def test_ok(taxi_umlaas_geo, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
