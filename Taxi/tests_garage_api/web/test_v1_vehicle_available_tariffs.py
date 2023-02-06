URL = '/v1/vehicle/available-tariffs'


async def test_v1_vehicle_available_tariffs_200(
        load_json, taxi_garage_api, cars_catalog_mock_200, classifier_mock_200,
):
    test_io = load_json('test_v1_vehicle_available_tariffs.json')
    test_io = filter(lambda x: x['code'] in [200], test_io)
    for test_case in test_io:
        request = test_case['request']
        expected_response = test_case['response']
        response = await taxi_garage_api.post(URL, json=request)
        assert response.status == 200
        assert response.json() == expected_response


async def test_v1_vehicle_available_tariffs_400(
        load_json, taxi_garage_api, cars_catalog_mock_200, classifier_mock_404,
):
    test_io = load_json('test_v1_vehicle_available_tariffs.json')
    test_io = filter(lambda x: x['code'] in [400], test_io)

    for test_case in test_io:
        request = test_case['request']
        response = await taxi_garage_api.post(URL, json=request)
        assert response.status == 400
