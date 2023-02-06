import datetime
from typing import List

import pytest

from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)


_POLYLINE = maps_utils.POLYLINE


def _get_middle_point(x: List[float], y: List[float]) -> List[float]:
    return [round((x[0] + y[0]) / 2, 5), round((x[1] + y[1]) / 2, 5)]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(RIDA_ROUTE_IMAGE_URL_SOURCE='gmaps')
@pytest.mark.parametrize(
    'return_code, status, corrupt_response, expected_return_code',
    [
        pytest.param(200, 'OK', False, 200, id='ok path'),
        pytest.param(200, 'NOT_FOUND', False, 404, id='place not found'),
        pytest.param(
            400,
            'INVALID_REQUEST',
            False,
            500,
            id='some parameters were not passed',
        ),
        pytest.param(200, 'ZERO_RESULTS', False, 404, id='route not found'),
        pytest.param(
            200, 'NE_HVATAET_DENEG_NA_KARTE', False, 500, id='strange status',
        ),
        pytest.param(200, 'OK', True, 500, id='no routes'),
    ],
)
async def test_two_points_gmaps(
        taxi_rida_web,
        mockserver,
        return_code,
        status,
        corrupt_response,
        expected_return_code,
):
    source_lat, source_lon = _POLYLINE[0][1], _POLYLINE[0][0]
    destination_lat, destination_lon = _POLYLINE[-1][1], _POLYLINE[-1][0]
    expected_distance, duration, duration_in_traffic = 228, 359, 322

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/directions/json',
    )
    def _mock_google_maps(request):
        return maps_utils.make_gmaps_directions_response(
            _POLYLINE,
            duration,
            expected_distance,
            duration_in_traffic,
            return_code,
            status,
            corrupt_response,
            mockserver,
        )

    request_body = {
        'coordinates': [_POLYLINE[0], _POLYLINE[-1]],
        'country_code': 'ng',
    }
    response = await taxi_rida_web.post(
        '/v1/route/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json=request_body,
    )

    assert response.status == expected_return_code
    if expected_return_code == 200:
        response_json = await response.json()
        expected_response = {
            'steps': [
                {'polyline': [x[0], _get_middle_point(x[0], x[1]), x[1]]}
                for x in zip(_POLYLINE, _POLYLINE[1:])
            ],
            'duration_s': duration_in_traffic,
            'distance_m': expected_distance,
        }
        assert response_json == expected_response

    assert _mock_google_maps.times_called >= 1
    google_maps_request = _mock_google_maps.next_call()['request']
    expected_request = {
        'origin': f'{source_lat},{source_lon}',
        'destination': f'{destination_lat},{destination_lon}',
        'traffic_model': 'best_guess',
        'language': 'en',
        'departure_time': str(int(_NOW.timestamp())),
        'google_api_key': 'rida',
    }
    assert dict(google_maps_request.query) == expected_request


@experiments_utils.get_route_info_config(
    'mapbox', 'summary', user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(RIDA_ROUTE_IMAGE_URL_SOURCE='gmaps')
@pytest.mark.parametrize(
    'return_code, status, corrupt_response, expected_return_code',
    [
        pytest.param(200, 'Ok', False, 200, id='ok path'),
        pytest.param(200, 'NoRoute', False, 404, id='route not found'),
        pytest.param(200, 'OK', True, 500, id='no routes'),
    ],
)
async def test_two_points_mapbox(
        taxi_rida_web,
        mockserver,
        return_code,
        status,
        corrupt_response,
        expected_return_code,
):
    source_lat, source_lon = _POLYLINE[0][1], _POLYLINE[0][0]
    destination_lat, destination_lon = _POLYLINE[-1][1], _POLYLINE[-1][0]
    expected_distance, duration = 228.5, 359.8

    @mockserver.json_handler('/api-proxy-external-geo/directions/v5/mapbox')
    def _mock_mapbox(request):
        return maps_utils.make_mapbox_directions_response(
            _POLYLINE,
            duration,
            expected_distance,
            return_code,
            status,
            corrupt_response,
            mockserver,
        )

    request_body = {
        'coordinates': [_POLYLINE[0], _POLYLINE[-1]],
        'country_code': 'ng',
    }
    response = await taxi_rida_web.post(
        '/v1/route/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json=request_body,
    )

    assert response.status == expected_return_code
    if expected_return_code == 200:
        response_json = await response.json()
        expected_response = {
            'steps': [
                {'polyline': [x[0], _get_middle_point(x[0], x[1]), x[1]]}
                for x in zip(_POLYLINE, _POLYLINE[1:])
            ],
            'duration_s': int(duration),
            'distance_m': int(expected_distance),
        }
        assert response_json == expected_response

    assert _mock_mapbox.times_called >= 1
    maps_request = _mock_mapbox.next_call()['request']
    expected_request = {
        'path': (
            f'{source_lon},{source_lat};{destination_lon},{destination_lat}'
        ),
        'alternatives': 'false',
        'mode': 'driving',
        'geometries': 'polyline',
        'steps': 'true',
        'mapbox_api_key': 'rida',
    }
    assert dict(maps_request.query) == expected_request


@pytest.mark.config(RIDA_ROUTE_IMAGE_URL_SOURCE='gmaps')
@pytest.mark.now(_NOW.isoformat())
async def test_one_point(taxi_rida_web, mockserver):
    request_body = {'coordinates': [_POLYLINE[0]], 'country_code': 'ng'}
    response = await taxi_rida_web.post(
        '/v1/route/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json=request_body,
    )

    assert response.status == 200
    response_json = await response.json()
    expected_response = {'steps': []}
    assert response_json == expected_response


async def _perform_old_and_new_requests(
        taxi_rida_web, user_id: int, expected_response: int,
):
    request_body = {
        'coordinates': [_POLYLINE[0], _POLYLINE[-1]],
        'country_code': 'ng',
    }
    response = await taxi_rida_web.post(
        '/v1/route/info',
        headers=helpers.get_auth_headers(user_id),
        json=request_body,
    )

    assert response.status == expected_response

    request_body = {
        'lat1': '40.2104518',
        'lat2': '44.5288846',
        'lng1': '50.2104518',
        'lng2': '54.5288846',
        'country_code': 'ng',
    }
    response = await taxi_rida_web.post(
        '/v1/maps/getRouteInfo',
        json=request_body,
        headers=helpers.get_auth_headers(user_id),
    )

    assert response.status == expected_response


@pytest.mark.mongodb_collections('rida_offers', 'rida_drivers')
@pytest.mark.filldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(RIDA_ROUTE_IMAGE_URL_SOURCE='gmaps')
@pytest.mark.parametrize(
    'user_id, should_use_traffic',
    [
        pytest.param(
            1234,
            True,
            id='user with complete order',
            marks=[
                experiments_utils.get_route_info_config(
                    'gmaps_with_traffic',
                    'summary',
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                ),
            ],
        ),
        pytest.param(
            1451,
            False,
            id='user with active order and without driver account',
            marks=[
                experiments_utils.get_route_info_config(
                    'gmaps',
                    'passenger_ride',
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD4Z',
                ),
            ],
        ),
        pytest.param(
            5678,
            False,
            id='user with active order',
            marks=[
                experiments_utils.get_route_info_config(
                    'gmaps',
                    'passenger_ride',
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
                ),
            ],
        ),
        pytest.param(
            3456,
            True,
            id='user without orders',
            marks=[
                experiments_utils.get_route_info_config(
                    'gmaps_with_traffic',
                    'summary',
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5J',
                ),
            ],
        ),
        pytest.param(
            3457,
            True,
            id='driver with complete order',
            marks=[
                experiments_utils.get_route_info_config(
                    'gmaps_with_traffic',
                    'summary',
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q',
                ),
            ],
        ),
        pytest.param(
            1449,
            False,
            id='driver with active order',
            marks=[
                experiments_utils.get_route_info_config(
                    'gmaps',
                    'driver_ride',
                    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
                ),
            ],
        ),
    ],
)
async def test_traffic_depending_on_user(
        taxi_rida_web, mockserver, user_id: int, should_use_traffic: bool,
):
    expected_distance, duration, duration_in_traffic = 228, 359, 322

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/directions/json',
    )
    def _mock_google_maps(request):
        return maps_utils.make_gmaps_directions_response(
            _POLYLINE,
            duration,
            expected_distance,
            duration_in_traffic,
            200,
            'OK',
            False,
            mockserver,
        )

    await _perform_old_and_new_requests(
        taxi_rida_web, expected_response=200, user_id=user_id,
    )

    assert _mock_google_maps.times_called == 2
    for _ in range(2):
        google_maps_request = _mock_google_maps.next_call()['request']
        query = google_maps_request.query
        assert ('departure_time' in query) == should_use_traffic
        assert ('traffic_model' in query) == should_use_traffic


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_RATE_LIMITER_SETTINGS={
        'v1/maps/getRouteInfo': {
            'rules': [{'max_number_of_requests': 1, 'period_s': 1}],
        },
        'v1/route/info': {
            'rules': [{'max_number_of_requests': 1, 'period_s': 1}],
        },
    },
)
async def test_distancematrix_limited_response(
        taxi_rida_web, mockserver, mocked_time,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/directions/json',
    )
    def _mock_google_maps(request):
        return maps_utils.make_gmaps_directions_response(
            _POLYLINE, 1, 1, 1, 200, 'OK', False, mockserver,
        )

    await _perform_old_and_new_requests(
        taxi_rida_web, expected_response=200, user_id=1234,
    )

    await _perform_old_and_new_requests(
        taxi_rida_web, expected_response=429, user_id=1234,
    )


@pytest.mark.parametrize('empty_response', [False, True])
@experiments_utils.get_route_info_config(
    'yamaps_over_osm',
    'summary',
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)
async def test_route_info_from_yamaps(
        taxi_rida_web, mockserver, empty_response: bool,
):
    @mockserver.json_handler('/yamaps-over-osm-router/v2/route')
    def _mock_yamaps(request):
        return maps_utils.mock_yamaps(request, empty_response, mockserver)

    response = await taxi_rida_web.post(
        '/v1/route/info',
        json={
            'coordinates': [_POLYLINE[0], _POLYLINE[-1]],
            'country_code': 'ng',
        },
        headers=helpers.get_auth_headers(user_id=1234),
    )
    if empty_response:
        assert response.status == 404
    else:
        assert response.status == 200
        expected_response = {
            'steps': [
                {'polyline': [x[0], _get_middle_point(x[0], x[1]), x[1]]}
                for x in zip(
                    maps_utils.round_all(_POLYLINE, digits=5),
                    maps_utils.round_all(_POLYLINE[1:], digits=5),
                )
            ],
            'duration_s': 7,
            'distance_m': 10,
        }
        response_json = await response.json()
        response_json['steps'] = [
            {'polyline': maps_utils.round_all(step['polyline'], digits=5)}
            for step in response_json['steps']
        ]
        assert response_json == expected_response
