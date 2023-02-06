from datetime import datetime

import pytest

from .reposition_select import select_named


@pytest.mark.now('2018-05-13T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('mode', ['home', 'poi'])
def test_put(taxi_reposition, load_json, pgsql, mockserver, mode, now):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'new_point',
        'address': {
            'title': 'new_point_address',
            'subtitle': 'new_point_city',
        },
        'point': [3, 4],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=' + mode,
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('test_put_' + mode + '_response.json')
    points = select_named('SELECT * FROM settings.points', pgsql['reposition'])
    saved_points = select_named(
        'SELECT * FROM settings.saved_points', pgsql['reposition'],
    )
    expected_points = [
        {
            'point_id': 2001,
            'mode_id': 1,
            'updated': datetime(2017, 11, 19, 16, 47, 54, 721000),
            'name': 'home_name_1',
            'address': 'home_address_1',
            'city': 'city',
            'location': '(37.41389,55.97194)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 2002,
            'mode_id': 2,
            'updated': datetime(2018, 9, 1, 0, 0),
            'name': 'poi_name_1',
            'address': 'poi_address_1',
            'city': 'city',
            'location': '(3,4)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 2003,
            'mode_id': 2,
            'updated': datetime(2018, 9, 1, 0, 0),
            'name': 'poi_name_2',
            'address': 'poi_address_2',
            'city': 'city',
            'location': '(5,6)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 1,
            'mode_id': 1 if mode == 'home' else 2,
            'updated': datetime(2018, 5, 13, 18, 18, 46),
            'name': 'new_point',
            'address': 'new_point_address',
            'city': 'new_point_city',
            'location': '(3,4)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
    ]
    assert [p for p in expected_points if p not in points] == []
    expected_saved_points = [
        {'saved_point_id': 1, 'point_id': 1, 'deleted': False, 'updated': now},
    ]
    if mode == 'home':
        expected_saved_points.append(
            {
                'saved_point_id': 1001,
                'point_id': 2001,
                'deleted': True,
                'updated': now,
            },
        )
    assert [p for p in expected_saved_points if p not in saved_points] == []


@pytest.mark.now('2018-05-13T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_put_override(taxi_reposition, load_json, pgsql, mockserver):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=poi'
        '&point_id=O3GWpmbkNEazJn4K',
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('test_put_override_response.json')
    points = select_named('SELECT * FROM settings.points', pgsql['reposition'])
    saved_points = select_named(
        'SELECT * FROM settings.saved_points', pgsql['reposition'],
    )
    expected_points = [
        {
            'point_id': 2001,
            'mode_id': 1,
            'updated': datetime(2017, 11, 19, 16, 47, 54, 721000),
            'name': 'home_name_1',
            'address': 'home_address_1',
            'city': 'city',
            'location': '(37.41389,55.97194)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 2002,
            'mode_id': 2,
            'updated': datetime(2018, 9, 1, 0, 0),
            'name': 'poi_name_1',
            'address': 'poi_address_1',
            'city': 'city',
            'location': '(3,4)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 2003,
            'mode_id': 2,
            'updated': datetime(2018, 9, 1, 0, 0),
            'name': 'poi_name_2',
            'address': 'poi_address_2',
            'city': 'city',
            'location': '(5,6)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 1,
            'mode_id': 2,
            'updated': datetime(2018, 5, 13, 18, 18, 46),
            'name': 'upd_point',
            'address': 'upd_point_address',
            'city': 'upd_point_city',
            'location': '(33,44)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
    ]
    assert [p for p in expected_points if p not in points] == []
    expected_saved_points = [
        {
            'saved_point_id': 1002,
            'point_id': 1,
            'deleted': False,
            'updated': datetime(2018, 5, 13, 18, 18, 46),
        },
    ]
    assert [p for p in expected_saved_points if p not in saved_points] == []


@pytest.mark.now('2017-11-20T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_put_too_freq(taxi_reposition, load_json, mockserver):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=home',
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.now('2017-11-20T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_put_no_such_point(taxi_reposition, load_json, mockserver):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [1, 1],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=poi' '&point_id=INVALID',
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {'error': {'text': 'Wrong point id'}}


@pytest.mark.now('2017-11-20T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'home_poi.sql',
        'points_777.sql',
        'forbidden_svo.sql',
    ],
)
def test_put_invalid(taxi_reposition, load_json, mockserver):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [37.399663, 55.972476],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=poi',
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {'error': {'text': 'Invalid point'}}


@pytest.mark.now('2017-11-26T00:00:00+03:00')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('mode', ['home'])
def test_put_timezone_boundary(
        taxi_reposition, load_json, pgsql, mockserver, mode, now,
):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'new_home',
        'address': {'title': 'new_home_address', 'subtitle': 'new_home_city'},
        'point': [3, 4],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=' + mode,
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'test_put_timezone_boundary_response.json',
    )


@pytest.mark.now('2017-11-25T23:59:59+03:00')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('mode', ['home'])
def test_put_timezone_boundary_too_freq(
        taxi_reposition, load_json, pgsql, mockserver, mode, now,
):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'new_home',
        'address': {'title': 'new_home_address', 'subtitle': 'new_home_city'},
        'point': [3, 4],
    }

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=' + mode,
        json=point_data,
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.now('2018-05-13T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_delete(taxi_reposition, load_json, pgsql, mockserver):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}
    response = taxi_reposition.delete(
        '/v2/reposition/locations?park_id=1488&mode=poi'
        '&point_id=O3GWpmbkNEazJn4K',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('test_delete_response.json')
    points = select_named('SELECT * FROM settings.points', pgsql['reposition'])
    saved_points = select_named(
        'SELECT * FROM settings.saved_points', pgsql['reposition'],
    )
    expected_points = [
        {
            'point_id': 2001,
            'mode_id': 1,
            'updated': datetime(2017, 11, 19, 16, 47, 54, 721000),
            'name': 'home_name_1',
            'address': 'home_address_1',
            'city': 'city',
            'location': '(37.41389,55.97194)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 2002,
            'mode_id': 2,
            'updated': datetime(2018, 9, 1, 0, 0),
            'name': 'poi_name_1',
            'address': 'poi_address_1',
            'city': 'city',
            'location': '(3,4)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
        {
            'point_id': 2003,
            'mode_id': 2,
            'updated': datetime(2018, 9, 1, 0, 0),
            'name': 'poi_name_2',
            'address': 'poi_address_2',
            'city': 'city',
            'location': '(5,6)',
            'offer_id': None,
            'driver_id_id': 2,
            'area_radius': None,
        },
    ]
    assert [p for p in expected_points if p not in points] == []
    expected_saved_points = [
        {
            'saved_point_id': 1002,
            'point_id': 2002,
            'deleted': True,
            'updated': datetime(2018, 5, 13, 18, 18, 46),
        },
    ]
    assert [p for p in expected_saved_points if p not in saved_points] == []


@pytest.mark.now('2018-05-13T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_delete_no_such_point(taxi_reposition, load_json, mockserver):
    @mockserver.json_handler(
        ('/driver-authorizer.taxi.yandex.net' '/driver_session'),
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    headers = {'Accept-Language': 'en-EN', 'X-Driver-Session': 'SSsession'}

    # trigger etag data update
    point_data = {
        'name': 'poi_name_1',
        'address': {'title': 'poi_address_1', 'subtitle': 'city'},
        'point': [3, 4],
    }
    response = taxi_reposition.put(
        '/v2/reposition/locations?park_id=1488&mode=poi'
        '&point_id=O3GWpmbkNEazJn4K',
        json=point_data,
        headers=headers,
    )
    assert response.json() == load_json(
        'test_delete_invalid_point_response.json',
    )

    response = taxi_reposition.delete(
        '/v2/reposition/locations?park_id=1488&mode=poi' '&point_id=INVALID',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'test_delete_invalid_point_response.json',
    )


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
    TVM_SERVICE_HANDLER_ACCESS_ENABLED=True,
)
@pytest.mark.parametrize(
    'service_access',
    [
        ({'reposition': {'/v2/reposition/locations': []}}),
        ({'reposition': {'/v2/reposition/locations': ['protocol']}}),
    ],
)
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_check_tvm2_access_deny(
        taxi_reposition, config, service_access, load, mockserver,
):
    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }
    config.set_values(dict(TVM_SERVICE_HANDLER_ACCESS=service_access))
    response = taxi_reposition.put(
        'v2/reposition/locations?park_id=1488&mode=poi',
        headers={
            'Accept-Language': 'en',
            'X-Driver-Session': 'any',
            'X-Ya-Service-Ticket': load('tvm2_ticket_19_18'),
            'X-YaTaxi-Park-Id': '1488',
            'X-YaTaxi-Driver-Profile-Id': 'driverSS',
        },
        json=point_data,
    )
    assert response.status_code == 401
    assert response.json() == {'error': {'text': 'Unauthorized'}}


@pytest.mark.parametrize(
    'tvm_enabled,tvm_header,service_access_enabled,service_access',
    [
        (False, True, None, None),
        (True, True, False, None),
        (True, True, True, {}),
        (True, True, True, {'reposition': {}}),
        (
            True,
            True,
            True,
            {'reposition': {'/v2/reposition/locations': ['driver_protocol']}},
        ),
    ],
)
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.now('2017-10-15T18:18:46')
def test_check_tvm2_access_allow(
        config,
        tvm_enabled,
        tvm_header,
        service_access_enabled,
        service_access,
        taxi_reposition,
        load,
        mockserver,
):
    @mockserver.json_handler(
        '/driver-authorizer.taxi.yandex.net/driver_session',
    )
    def mock_driver_session(request):
        return mockserver.make_response('{"uuid" : "driverSS"}', status=200)

    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }
    config.set_values(
        dict(
            TVM_ENABLED=tvm_enabled,
            TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
            TVM_SERVICE_HANDLER_ACCESS_ENABLED=service_access_enabled,
            TVM_SERVICE_HANDLER_ACCESS=service_access
            if service_access
            else {},
        ),
    )

    response = taxi_reposition.put(
        'v2/reposition/locations?park_id=1488&mode=poi',
        headers={
            'Accept-Language': 'en',
            'X-Driver-Session': 'any',
            'X-Ya-Service-Ticket': load('tvm2_ticket_19_18'),
            'X-YaTaxi-Park-Id': '1488',
            'X-YaTaxi-Driver-Profile-Id': 'driverSS',
        },
        json=point_data,
    )
    assert response.status_code == 200


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'reposition'}],
    TVM_SERVICE_HANDLER_ACCESS_ENABLED=True,
    TVM_SERVICE_HANDLER_ACCESS={
        'reposition': {'/v2/reposition/locations': ['driver_protocol']},
    },
)
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
def test_check_tvm2_no_headers(taxi_reposition, load, mockserver):
    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }
    response = taxi_reposition.put(
        'v2/reposition/locations?park_id=1488&mode=poi',
        headers={
            'Accept-Language': 'en',
            'X-Driver-Session': 'any',
            'X-Ya-Service-Ticket': load('tvm2_ticket_19_18'),
        },
        json=point_data,
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': {
            'text': (
                'Missing park_id and driver_profile_id from driver-authproxy'
            ),
        },
    }
