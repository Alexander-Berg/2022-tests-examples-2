# pylint: disable=import-only-modules
from datetime import datetime

import pytest

from .utils import select_named

BACKWARD_COMPATIBLE_URI = '/driver/v1/v2/reposition/locations'
NEW_URI = '/driver/v1/reposition/v2/locations'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': '1488',
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}


@pytest.mark.now('2018-05-13T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('mode', ['home', 'poi'])
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put(
        taxi_reposition_api, load_json, pgsql, mode, now, handler_uri,
):
    point_data = {
        'name': 'new_point',
        'address': {
            'title': 'new_point_address',
            'subtitle': 'new_point_city',
        },
        'point': [3, 4],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?mode={mode}',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
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
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put_override(
        taxi_reposition_api, load_json, pgsql, handler_uri,
):
    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?&mode=poi&point_id=O3GWpmbkNEazJn4K',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
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
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put_too_freq(taxi_reposition_api, load_json, handler_uri):
    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [33, 44],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?&mode=home',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 403


@pytest.mark.now('2017-11-20T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put_no_such_point(taxi_reposition_api, load_json, handler_uri):
    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [1, 1],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?mode=poi&point_id=INVALID',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Wrong point id'}


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
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put_invalid(taxi_reposition_api, load_json, handler_uri):
    point_data = {
        'name': 'upd_point',
        'address': {
            'title': 'upd_point_address',
            'subtitle': 'upd_point_city',
        },
        'point': [37.399663, 55.972476],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?mode=poi', json=point_data, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid point'}


@pytest.mark.now('2018-05-13T18:18:46')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_delete(taxi_reposition_api, load_json, pgsql, handler_uri):
    response = await taxi_reposition_api.delete(
        f'{handler_uri}?mode=poi&point_id=O3GWpmbkNEazJn4K',
        headers=AUTHORIZED_HEADERS,
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
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_delete_no_such_point(
        taxi_reposition_api, load_json, handler_uri,
):
    # trigger etag data update
    point_data = {
        'name': 'poi_name_1',
        'address': {'title': 'poi_address_1', 'subtitle': 'city'},
        'point': [3, 4],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?mode=poi&point_id=O3GWpmbkNEazJn4K',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
    )

    assert response.json() == load_json(
        'test_delete_invalid_point_response.json',
    )

    response = await taxi_reposition_api.delete(
        f'{handler_uri}?mode=poi&point_id=INVALID', headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'test_delete_invalid_point_response.json',
    )


@pytest.mark.now('2017-11-26T00:00:00+03:00')
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'mode_home.sql', 'home_poi.sql', 'points_777.sql'],
)
@pytest.mark.parametrize('mode', ['home'])
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put_timezone_boundary(
        taxi_reposition_api, load_json, pgsql, mode, now, handler_uri,
):
    point_data = {
        'name': 'new_home',
        'address': {'title': 'new_home_address', 'subtitle': 'new_home_city'},
        'point': [3, 4],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?mode={mode}',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
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
@pytest.mark.parametrize('handler_uri', [BACKWARD_COMPATIBLE_URI, NEW_URI])
async def test_put_timezone_boundary_too_freq(
        taxi_reposition_api, load_json, pgsql, mode, now, handler_uri,
):
    point_data = {
        'name': 'new_home',
        'address': {'title': 'new_home_address', 'subtitle': 'new_home_city'},
        'point': [3, 4],
    }

    response = await taxi_reposition_api.put(
        f'{handler_uri}?mode={mode}',
        json=point_data,
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 403
