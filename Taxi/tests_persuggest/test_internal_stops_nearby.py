import copy

import pytest

URL = 'internal/persuggest/v1/stops_nearby'

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}

BASIC_REQUEST = {
    'position': [37.53, 55.74],
    'distance_meters': 5000,
    'point_type': 'b',
    'pickup_points_type': 'finalized',
    'route_method': 'by_car',
    'transport_types': ['metro'],
}


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_basic(taxi_persuggest, mockserver, load_json, yamaps):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        request_position = request.json['position']
        pickup_points = load_json('uml_finalsuggest_points.json')
        for idx, point in enumerate(pickup_points['points']):
            pp_position = point['address']['position']
            pp_position[0] = request_position[0] + 0.0001 * idx
            pp_position[1] = request_position[1] + 0.0001 * idx
            point[
                'id'
            ] = f'{point["id"]}__{str(request_position[0])[-2:]}__p_{idx}'
        return pickup_points

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response_none.json')

    @mockserver.json_handler(
        '/masstransit/4.0/masstransit/v1/stops_with_lines',
    )
    def _mock_mt_stops_with_lines(request):
        return load_json('mt_stops_with_lines.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'business_oid' in request.args:
            return [load_json('geosearch_org.json')]
        return [load_json('yamaps_simple_geo_object.json')]

    response = await taxi_persuggest.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    assert response.json() == load_json('expected_response_basic.json')


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(
    ROUTE_RETRIES=1,
    ROUTER_SELECT=[{'routers': ['yamaps-matrix']}],
    ROUTER_MAPS_ENABLED=True,
    ROUTER_MATRIX_MAPS_ENABLED=True,
)
async def test_router_fallback(taxi_persuggest, mockserver, load_json, yamaps):
    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def _mock_router(request):
        return mockserver.make_response('internal error', status=500)

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        request_position = request.json['position']
        pickup_points = load_json('uml_finalsuggest_points.json')
        for idx, point in enumerate(pickup_points['points']):
            pp_position = point['address']['position']
            pp_position[0] = request_position[0] + 0.0001 * idx
            pp_position[1] = request_position[1] + 0.0001 * idx
            point[
                'id'
            ] = f'{point["id"]}__{str(request_position[0])[-2:]}__p_{idx}'
        return pickup_points

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response_none.json')

    @mockserver.json_handler(
        '/masstransit/4.0/masstransit/v1/stops_with_lines',
    )
    def _mock_mt_stops_with_lines(request):
        return load_json('mt_stops_with_lines.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'business_oid' in request.args:
            return [load_json('geosearch_org.json')]
        return [load_json('yamaps_simple_geo_object.json')]

    request = copy.deepcopy(BASIC_REQUEST)
    request['route_method'] = 'by_car'

    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200

    expected_response = load_json('expected_response_basic.json')
    for pickup_point in expected_response['pickup_points']:
        pickup_point['route_method'] = 'fallback'

    assert response.json() == expected_response


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_identical_pps(taxi_persuggest, mockserver, load_json, yamaps):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response_none.json')

    @mockserver.json_handler(
        '/masstransit/4.0/masstransit/v1/stops_with_lines',
    )
    def _mock_mt_stops_with_lines(request):
        return load_json('mt_stops_with_lines.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'business_oid' in request.args:
            return [load_json('geosearch_org.json')]
        return [load_json('yamaps_simple_geo_object.json')]

    request = copy.deepcopy(BASIC_REQUEST)
    request['pickup_points_type'] = 'identical'

    response = await taxi_persuggest.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200

    assert response.json() == load_json('expected_response_identical.json')
