import json


BASIC_REQUEST = {
    'id': '1',
    'route': [[37.642563, 55.734760], [37.534248, 55.749920]],
    'selected_class': 'econom',
    'zone_name': 'moscow',
    'surge_value': 1.3,
    'extra': {
        'check_contracts': False,
        'enable_graph': False,
        'limit': 10,
        'max_distance': 10000,
        'requirements': {},
        'price_values': [],
    },
}


async def test_simple_v1(taxi_alt, load_json, mockserver):

    points = [BASIC_REQUEST['route'][0]]

    @mockserver.json_handler('/masstransit/masstransit/v1/routepoints')
    def _mock_pickup_points(request):
        data = json.loads(request.get_data())
        assert data.get('metro_first', None)
        response = load_json('masstransit_routepoints.json')
        for point in response['options']:
            points.append(point['last_position'])
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        request_data = json.loads(request.get_data())
        assert request_data == load_json('filter_points_request.json')
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        expected_eta_request = load_json('eta_request.json')
        eta_request = json.loads(request.get_data())
        assert eta_request['point'] in points
        expected_eta_request['point'] = eta_request['point']
        assert eta_request == expected_eta_request
        if eta_request['point'] == [37.972872436, 55.73530476]:
            return load_json('eta_response_not_found.json')
        return load_json('eta_response.json')

    response = await taxi_alt.post('alt/v1/mtpin', BASIC_REQUEST)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
