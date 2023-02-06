import json

import pytest


TICKET = 'ticket'
TVM_TICKETS = {
    '21': {'ticket': TICKET},
    '36': {'ticket': TICKET},
    '45': {'ticket': TICKET},
}


def mock_bigb(mockserver, return_value=None, status_code=200):
    @mockserver.json_handler('/bigb')
    def route_bigb(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == TICKET
        if status_code == 200:
            return return_value
        else:
            return mockserver.make_response(status=status_code)

    return route_bigb


def mock_pickup_points_manager(mockserver, return_value=None, status_code=200):
    @mockserver.json_handler('/pickup-points-manager/v1/points')
    def route_pickup_points_manager(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == TICKET
        if status_code == 200:
            return return_value
        else:
            return mockserver.make_response(status=status_code)

    return route_pickup_points_manager


def get_configs(
        enable_ml=False,
        enable_manual=False,
        enable_history=False,
        intersection_distance=40,
        search_radius=200,
        stick_radius=10,
        use_pickup_points_manager=False,
):
    return {
        'PICKUP_POINTS_ML_PREPARATION_CONFIG': {
            '__default__': {
                'enabled': enable_ml,
                'search_radius': search_radius,
            },
        },
        'PICKUP_POINTS_ML_MANUAL_CONFIG': {
            '__default__': {
                'enabled': enable_manual,
                'search_radius': search_radius,
                'use_pickup_points_manager': use_pickup_points_manager,
            },
        },
        'PICKUP_POINTS_ML_PERSONAL_CONFIG': {
            '__default__': {
                'enabled': enable_history,
                'max_pin_distance': search_radius,
            },
        },
        'PICKUP_POINTS_ML_POSTPROCESSING_CONFIG': {
            '__default__': {
                'max_earth_distance': search_radius,
                'intersection_distance': intersection_distance,
                'stick_radius': stick_radius,
                'manual_stick_radius': stick_radius,
            },
        },
    }


def get_smart_pp_config(use_manual_points=True):
    return {
        'PICKUP_POINTS_ML_ALTPINS_CONFIG': {
            '__default__': {
                'max_candidates_count': 100,
                'max_pickup_points_count': 100,
                'max_earth_distance': 1000,
                'max_route_time': 1000,
                'min_score': 0,
                'sort_asc_by_earth_dist': True,
                'sort_asc_by_walk_time': True,
                'use_manual_points': use_manual_points,
            },
        },
    }


def test_bad_request(tvm2_client, taxi_ml, load_json, mockserver):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    response = taxi_ml.post('2.0/pickup_points', json={})
    assert response.status_code == 400


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(**get_configs(enable_ml=True))
def test_router_fallback(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)

    request = load_json(request_file)
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200

    request['smart_pp_candidate'] = True
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(**get_configs(enable_history=True))
def test_personal_point(
        tvm2_client,
        taxi_ml,
        load_json,
        mockserver,
        request_file,
        routehistory,
):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    request = load_json(request_file)

    routehistory.expect_request(False)
    routehistory.set_response(None)
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert routehistory.called is False
    assert response.status_code == 200
    assert response.json()['pickup_points'] == []

    rh_request = load_json('routehistory_request.json')
    rh_headers = {'X-YaTaxi-PhoneId': '5bbb5faf15870bd76635d5e2'}
    if 'user_id' in request['user_identity']:
        rh_headers['X-YaTaxi-UserId'] = request['user_identity']['user_id']
    routehistory.expect_request(rh_request, rh_headers)
    request['user_identity']['phone_id'] = '5bbb5faf15870bd76635d5e2'
    routehistory.set_response('routehistory_response.json')
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert len(response.json()['pickup_points']) == 1
    assert response.json()['pickup_points'][0]['id'] == 'history_id_1'
    assert response.json()['sticky_pickup_point_id'] == 'history_id_1'


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(
    **get_configs(
        enable_ml=True,
        enable_manual=True,
        intersection_distance=1,
        stick_radius=1,
    ),
)
def test_manual_and_ml(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    request = load_json(request_file)
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert len(response.json()['pickup_points']) == 2
    assert response.json()['pickup_points'][0]['id'] == 'manual_id'
    assert response.json()['pickup_points'][1]['id'] == 'ml_id'
    assert response.json()['pickup_points'][1]['organization_id'] == 'oid'
    assert 'sticky_pickup_point_id' not in response.json()


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(
    **get_configs(
        enable_ml=True,
        enable_manual=True,
        intersection_distance=100,
        stick_radius=50,
    ),
)
def test_only_manual(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    request = load_json(request_file)
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert len(response.json()['pickup_points']) == 1
    assert response.json()['pickup_points'][0]['id'] == 'manual_id'
    assert response.json()['sticky_pickup_point_id'] == 'manual_id'


@pytest.mark.config(
    **get_configs(enable_manual=True, use_pickup_points_manager=True),
)
def test_manual_from_manager(tvm2_client, taxi_ml, load_json, mockserver):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    manager_response = load_json('pickup_points_manager_response.json')
    mock_pickup_points_manager(mockserver, manager_response)
    request = load_json('request.json')
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert len(response.json()['pickup_points']) == 2
    assert response.json()['pickup_points'][0]['id'] == '1'
    assert response.json()['pickup_points'][1]['id'] == '2'
    assert response.json()['sticky_pickup_point_id'] == '1'


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(
    **get_configs(
        enable_ml=True,
        enable_manual=True,
        enable_history=True,
        search_radius=1,
    ),
)
def test_no_points(tvm2_client, taxi_ml, load_json, mockserver, request_file):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    request = load_json(request_file)
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert response.json()['pickup_points'] == []


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(**get_smart_pp_config(use_manual_points=True))
def test_smart_pp(tvm2_client, taxi_ml, load_json, mockserver, request_file):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    request = load_json(request_file)
    request['smart_pp_candidate'] = True
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert len(response.json()['pickup_points']) == 2


@pytest.mark.parametrize('request_file', ['request.json', 'request_noid.json'])
@pytest.mark.config(**get_smart_pp_config(use_manual_points=False))
def test_smart_pp_without_manual(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps(TVM_TICKETS))
    mock_bigb(mockserver)
    request = load_json(request_file)
    request['smart_pp_candidate'] = True
    response = taxi_ml.post('2.0/pickup_points', json=request)
    assert response.status_code == 200
    assert len(response.json()['pickup_points']) == 1
