import copy
import json

import pytest


BASIC_REQUEST = {
    'id': '1',
    'route': [[37.642563, 55.734760], [37.534248, 55.749920]],
    'selected_class': 'econom',
    'zone_name': 'moscow',
    'surge_value': 1.3,
    'altoffer_types': ['a'],
    'extra': {
        'check_contracts': False,
        'enable_graph': False,
        'limit': 10,
        'max_distance': 10000,
        'requirements': {},
        'price_values': [],
    },
}


@pytest.mark.parametrize(
    'alt_source, altoffer_type, expected_resp_filename',
    [
        pytest.param('source_ml', 'a', 'expected_response_ml_a.json'),
        pytest.param(
            'source_umlaas-geo',
            'a',
            'expected_response.json',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_alt_point_source.json',
                ),
            ],
        ),
        pytest.param(
            'source_umlaas-geo',
            'b',
            'expected_response_altpin_b.json',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_alt_point_source.json',
                ),
            ],
        ),
        pytest.param(
            'source_umlaas-geo',
            'b',
            'expected_response_altpin_b.json',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_alt_point_source_path.json',
                ),
            ],
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_altpin_settings.json')
async def test_simple(
        taxi_alt,
        load_json,
        mockserver,
        alt_source,
        altoffer_type,
        expected_resp_filename,
):

    points = [BASIC_REQUEST['route'][0]]

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/points')
    def _mock_pickup_points_umlaas_geo(request):
        assert alt_source == 'source_umlaas-geo'

        assert request.json == load_json('expected_pp_request.json')
        response = load_json('umlaas-geo_pp_response.json')
        for point in response['pickup_points']:
            points.append(point['address']['position'])
        return response

    @mockserver.json_handler('/ml/2.0/pickup_points')
    def _mock_pickup_points_ml(request):
        assert alt_source == 'source_ml'
        response = load_json('ml_pp_response.json')
        for point in response['pickup_points']:
            points.append(point['geopoint'])
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        expected_eta_request = load_json('eta_request.json')
        eta_request = json.loads(request.get_data())
        assert eta_request['point'] in points
        expected_eta_request['point'] = eta_request['point']
        assert eta_request == expected_eta_request
        return load_json('eta_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['altoffer_types'] = [altoffer_type]
    # preserve all jsons for a-altpins
    if altoffer_type == 'b':
        request['route'] = request['route'][::-1]
    response = await taxi_alt.post('alt/v1/pin', request)
    assert response.status_code == 200
    assert response.json() == load_json(expected_resp_filename)
    assert (
        _mock_pickup_points_umlaas_geo.times_called
        and alt_source == 'source_umlaas-geo'
        or _mock_pickup_points_ml.times_called
        and alt_source == 'source_ml'
    )


@pytest.mark.experiments3(filename='exp3_altpin_settings_with_sort.json')
@pytest.mark.experiments3(filename='exp3_alt_point_source.json')
async def test_sort(taxi_alt, load_json, mockserver):

    points = [BASIC_REQUEST['route'][0]]

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/points')
    def _mock_pickup_points_umlaas_geo(request):
        response = load_json('umlaas-geo_pp_response.json')
        for point in response['pickup_points']:
            points.append(point['address']['position'])
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        return load_json('eta_response.json')

    request = copy.deepcopy(BASIC_REQUEST)
    request['altoffer_types'] = ['b']
    # preserve all jsons for a-altpins
    request['route'] = request['route'][::-1]

    response = await taxi_alt.post('alt/v1/pin', request)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_custom_sort.json')


@pytest.mark.experiments3(filename='exp3_altpin_settings_filter.json')
async def test_simple_settings(taxi_alt, load_json, mockserver):

    points = [BASIC_REQUEST['route'][0]]

    @mockserver.json_handler('/ml/2.0/pickup_points')
    def _mock_pickup_points(request):
        response = load_json('ml_pp_response.json')
        for point in response['pickup_points']:
            points.append(point['geopoint'])
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        expected_eta_request = load_json('eta_request.json')
        eta_request = json.loads(request.get_data())
        assert eta_request['point'] in points
        expected_eta_request['point'] = eta_request['point']
        assert eta_request == expected_eta_request
        return load_json('eta_response.json')

    response = await taxi_alt.post('alt/v1/pin', BASIC_REQUEST)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_filtered.json')


@pytest.mark.experiments3(filename='exp3_altpin_settings.json')
async def test_source_in_zone(taxi_alt, load_json, mockserver):
    @mockserver.json_handler('/ml/2.0/pickup_points')
    def _mock_pickup_points(request):
        return load_json('ml_pp_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        response = load_json('pp_bzf_response.json')
        response['results'][0]['in_zone'] = True
        return response

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        return {'classes': {}}

    response = await taxi_alt.post('alt/v1/pin', BASIC_REQUEST)
    assert response.status_code == 200
    assert not response.json()['points']


@pytest.mark.parametrize(
    'fail_bzf, fail_ml_pp, fail_eta',
    [(True, False, False), (False, True, False), (False, False, True)],
)
@pytest.mark.experiments3(filename='exp3_altpin_settings.json')
async def test_failures(
        taxi_alt, load_json, mockserver, fail_bzf, fail_ml_pp, fail_eta,
):
    @mockserver.json_handler('/ml/2.0/pickup_points')
    def _mock_pickup_points(request):
        if fail_ml_pp:
            return mockserver.make_response('fail', status=500)
        return load_json('ml_pp_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        if fail_bzf:
            return mockserver.make_response('fail', status=500)
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        if fail_eta:
            return mockserver.make_response('fail', status=500)
        return load_json('eta_response.json')

    response = await taxi_alt.post('alt/v1/pin', BASIC_REQUEST)
    assert response.status_code == 200
    assert not response.json()['points']


@pytest.mark.parametrize(
    'fail_bzf, fail_ml_pp, fail_eta',
    [(True, False, False), (False, True, False), (False, False, True)],
)
@pytest.mark.experiments3(filename='exp3_altpin_settings.json')
async def test_timeouts(
        taxi_alt, load_json, mockserver, fail_bzf, fail_ml_pp, fail_eta,
):
    @mockserver.json_handler('/ml/2.0/pickup_points')
    def _mock_pickup_points(request):
        if fail_ml_pp:
            raise mockserver.TimeoutError()
        return load_json('ml_pp_response.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        if fail_bzf:
            raise mockserver.TimeoutError()
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        if fail_eta:
            raise mockserver.TimeoutError()
        return load_json('eta_response.json')

    response = await taxi_alt.post('alt/v1/pin', BASIC_REQUEST)
    assert response.status_code == 200
    assert not response.json()['points']


@pytest.mark.experiments3(filename='exp3_altpin_settings.json')
@pytest.mark.experiments3(filename='exp3_altpin_skip_eta.json')
async def test_skip_eta(taxi_alt, load_json, mockserver):

    points = [BASIC_REQUEST['route'][0]]

    @mockserver.json_handler('/ml/2.0/pickup_points')
    def _mock_pickup_points(request):
        response = load_json('ml_pp_response.json')
        for point in response['pickup_points']:
            points.append(point['geopoint'])
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_bzf(request):
        return load_json('pp_bzf_response.json')

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        assert False

    expected_response = load_json('expected_response.json')
    for point in expected_response['points']:
        del point['eta']
        del point['walk_distance']

    response = await taxi_alt.post('alt/v1/pin', BASIC_REQUEST)
    assert response.status_code == 200
    assert response.json() == expected_response
