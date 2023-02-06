import datetime
from typing import Union

import pytest

from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
_POLYLINE = maps_utils.POLYLINE


DISABLED_CONFIG_MARKS = [
    pytest.mark.config(
        RIDA_GEO_CACHE_SETTINGS=dict(is_enabled=False, ttl=300),
    ),
]
ENABLED_CONFIG_MARKS = [
    pytest.mark.config(RIDA_GEO_CACHE_SETTINGS=dict(is_enabled=True, ttl=300)),
]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    [
        'source_lat',
        'source_lon',
        'destination_lat',
        'destination_lon',
        'is_expected_in_cache',
        'expected_distance',
        'expected_duration',
    ],
    [
        pytest.param(
            '1',
            '2',
            '3',
            '4',
            False,
            1234,
            123,
            marks=DISABLED_CONFIG_MARKS,
            id='cache_disabled',
        ),
        pytest.param(
            '1',
            '2',
            '3',
            '4',
            False,
            1234,
            123,
            marks=ENABLED_CONFIG_MARKS,
            id='cache_enabled_but_missed',
        ),
        pytest.param(
            '40.2104517',
            '44.5288845',
            '50.2104517',
            '54.5288845',
            True,
            1337,
            1418,
            marks=ENABLED_CONFIG_MARKS,
            id='cache_exact_match',
        ),
        pytest.param(
            '40.2104518',
            '44.5288846',
            '50.2104518',
            '54.5288846',
            True,
            1337,
            1418,
            marks=ENABLED_CONFIG_MARKS,
            id='cache_close_match',
        ),
        pytest.param(
            40.2104518,
            44.5288846,
            50.2104518,
            54.5288846,
            True,
            1337,
            1418,
            marks=ENABLED_CONFIG_MARKS,
            id='cache_close_match_iphone_params',
        ),
    ],
)
@pytest.mark.parametrize('request_body_as_query', [True, False])
async def test_get_distance_info(
        web_app,
        web_app_client,
        mockserver,
        get_stats_by_label_values,
        source_lat: Union[int, str],
        source_lon: Union[int, str],
        destination_lat: Union[int, str],
        destination_lon: Union[int, str],
        is_expected_in_cache: bool,
        expected_distance: int,
        expected_duration: int,
        request_body_as_query: bool,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                expected_distance, expected_duration,
            ),
        )

    request_params = {'headers': helpers.get_auth_headers(user_id=1234)}
    request_body = {
        'lat1': source_lat,
        'lat2': destination_lat,
        'lng1': source_lon,
        'lng2': destination_lon,
    }
    if request_body_as_query:
        request_params['data'] = request_body
    else:
        request_params['json'] = request_body
    response = await web_app_client.post(
        '/v1/maps/getDistanceInfo', **request_params,
    )
    if is_expected_in_cache:
        assert _mock_google_maps.times_called == 0
    else:
        maps_utils.validate_gmaps_request(
            _mock_google_maps,
            False,
            [source_lon, source_lat],
            [destination_lon, destination_lat],
            _NOW,
        )

    assert response.status == 200
    response_json = await response.json()
    expected_response = {
        'status': 'OK',
        'data': {'distance': expected_distance, 'duration': expected_duration},
    }
    assert response_json == expected_response

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'geo.get_distance_info'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'geo.get_distance_info',
                'data_provider': (
                    'cache' if is_expected_in_cache else 'google_maps'
                ),
            },
            'value': 1,
            'timestamp': None,
        },
    ]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_GEO_TRAFFIC_MODEL_SETTINGS={
        'traffic_model': 'best_guess',
        'use_duration_in_traffic': True,
        'log_response': True,
    },
)
@pytest.mark.parametrize(
    'routing_source',
    [
        pytest.param(
            'gmaps_with_traffic',
            marks=[
                experiments_utils.get_distance_info_config(
                    'gmaps_with_traffic', 'v1/maps/getDistanceInfo',
                ),
            ],
        ),
        pytest.param(
            'mapbox',
            marks=[
                experiments_utils.get_distance_info_config(
                    'mapbox', 'v1/maps/getDistanceInfo',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'maps_response, corrupt_response',
    [(200, False), (200, True), (400, False), (500, False)],
)
async def test_google_maps_different_responses(
        taxi_rida_web,
        taxi_config,
        routing_source: str,
        maps_response: int,
        corrupt_response: bool,
        mockserver,
):
    source_lat, source_lon = 123, 456
    destination_lat, destination_lon = 789, 12
    expected_distance, duration, traffic_duration = 228, 359, 322

    if routing_source == 'gmaps_with_traffic':

        @mockserver.json_handler(
            '/api-proxy-external-geo/google/maps/api/distancematrix/json',
        )
        def _mock_maps(request):
            response = maps_utils.make_gmaps_distance_response(
                expected_distance, duration, traffic_duration,
            )
            if corrupt_response:
                response['rows'] = []
            return mockserver.make_response(
                status=maps_response, json=response,
            )

    else:

        @mockserver.json_handler(
            '/api-proxy-external-geo/directions/v5/mapbox',
        )
        def _mock_maps(request):
            return maps_utils.make_mapbox_directions_response(
                [],
                traffic_duration,
                expected_distance,
                maps_response,
                'Ok',
                corrupt_response,
                mockserver,
            )

    request_body = {
        'lat1': source_lat,
        'lat2': destination_lat,
        'lng1': source_lon,
        'lng2': destination_lon,
    }
    response = await taxi_rida_web.post(
        '/v1/maps/getDistanceInfo',
        headers=helpers.get_auth_headers(user_id=1234),
        json=request_body,
    )

    assert response.status == 200
    response_json = await response.json()
    if maps_response == 200 and not corrupt_response:
        expected_response = {
            'status': 'OK',
            'data': {
                'distance': expected_distance,
                'duration': traffic_duration,
            },
        }
    else:
        expected_response = {
            'status': 'INVALID_DATA',
            'errors': {'message': 'Can not get distance info !'},
        }
    assert response_json == expected_response

    if routing_source == 'gmaps_with_traffic':
        maps_utils.validate_gmaps_request(
            _mock_maps,
            maps_response == 500,
            [source_lon, source_lat],
            [destination_lon, destination_lat],
            _NOW,
        )
    else:
        maps_utils.validate_mapbox_request(
            _mock_maps,
            maps_response == 500,
            [source_lon, source_lat],
            [destination_lon, destination_lat],
        )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['traffic_model', 'use_duration_in_traffic', 'expected_duration'],
    [
        pytest.param('best_guess', False, 10, id='best_guess'),
        pytest.param('pessimistic', False, 10, id='pessimistic'),
        pytest.param('optimistic', False, 10, id='pessimistic'),
        pytest.param('best_guess', True, 20, id='use_duration_in_traffic'),
    ],
)
async def test_distancematrix_with_traffic(
        web_app,
        web_app_client,
        taxi_rida_web,
        mockserver,
        taxi_config,
        traffic_model,
        use_duration_in_traffic,
        expected_duration,
):
    taxi_config.set_values(
        {
            'RIDA_GEO_TRAFFIC_MODEL_SETTINGS': {
                'traffic_model': traffic_model,
                'use_duration_in_traffic': use_duration_in_traffic,
                'log_response': True,
            },
        },
    )

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(10, 10, 20),
        )

    response = await taxi_rida_web.post(
        '/v1/maps/getDistanceInfo',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'lat1': 1, 'lat2': 2, 'lng1': 3, 'lng2': 4},
    )
    response_json = await response.json()
    assert response_json == {
        'data': {'distance': 10, 'duration': expected_duration},
        'status': 'OK',
    }

    maps_utils.validate_gmaps_request(
        _mock_google_maps, False, [3, 1], [4, 2], _NOW, traffic_model,
    )


async def _dummy_query_to_gmaps(taxi_rida_web, user_id=1234):
    response = await taxi_rida_web.post(
        '/v1/maps/getDistanceInfo',
        headers=helpers.get_auth_headers(user_id),
        json={'lat1': 1, 'lat2': 2, 'lng1': 3, 'lng2': 4},
    )
    response_json = await response.json()
    assert response_json['status'] == 'OK'


@experiments_utils.get_distance_info_config(
    'ruler', 'v1/maps/getDistanceInfo_fallback',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_RATE_LIMITER_SETTINGS={
        'v1/maps/getDistanceInfo': {
            'rules': [{'max_number_of_requests': 1, 'period_s': 1}],
        },
    },
    RIDA_GEO_STRAIGHT_LINE_FALLBACK={
        'speed': 60,
        'const_offset': 100,
        'distance_coefficient': 2,
    },
)
async def test_distancematrix_limited_response(
        taxi_rida_web, mockserver, mocked_time,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(10, 10, 20),
        )

    await _dummy_query_to_gmaps(taxi_rida_web)

    response = await taxi_rida_web.post(
        '/v1/maps/getDistanceInfo',
        headers=helpers.get_auth_headers(1234),
        json={
            'lat1': 59.958611,
            'lng1': 30.405313,
            'lat2': 59.953858,
            'lng2': 30.356573,
        },
    )
    response_json = await response.json()
    assert response_json['status'] == 'OK'
    data = response_json['data']
    assert data['distance'] == 6484
    assert data['duration'] == 395


@experiments_utils.get_distance_info_config(
    'ruler', 'v1/maps/getDistanceInfo_fallback',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_RATE_LIMITER_SETTINGS={
        'v1/maps/getDistanceInfo': {
            'rules': [{'max_number_of_requests': 3, 'period_s': 2}],
        },
    },
)
async def test_distancematrix_rate_limiter_refilling(
        taxi_rida_web, mockserver, mocked_time,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(10, 10, 20),
        )

    for _ in range(3):
        await _dummy_query_to_gmaps(taxi_rida_web)

    assert _mock_google_maps.times_called == 3

    mocked_time.sleep(1)
    await taxi_rida_web.invalidate_caches()

    for _ in range(2):
        await _dummy_query_to_gmaps(taxi_rida_web)

    assert _mock_google_maps.times_called == 4


@experiments_utils.get_distance_info_config(
    'ruler', 'v1/maps/getDistanceInfo_fallback',
)
@experiments_utils.get_distance_info_config(
    'ruler',
    'v1/maps/getDistanceInfo_fallback',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    RIDA_RATE_LIMITER_SETTINGS={
        'v1/maps/getDistanceInfo': {
            'rules': [{'max_number_of_requests': 2, 'period_s': 1}],
        },
    },
)
async def test_distancematrix_rate_limiter_two_users(
        taxi_rida_web, mockserver,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(10, 10, 20),
        )

    for i in range(8):
        user_id = 1234 if i % 2 == 0 else 5678
        await _dummy_query_to_gmaps(taxi_rida_web, user_id)

    # each user called gmaps twice
    assert _mock_google_maps.times_called == 4


@pytest.mark.parametrize('empty_response', [False, True])
@experiments_utils.get_distance_info_config(
    'yamaps_over_osm',
    'v1/maps/getDistanceInfo',
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)
async def test_yamaps_distance_info(
        taxi_rida_web, mockserver, empty_response: bool,
):
    src_lat, src_lon, dst_lat, dst_lon = (
        _POLYLINE[0][1],
        _POLYLINE[0][0],
        _POLYLINE[-1][1],
        _POLYLINE[-1][0],
    )

    @mockserver.json_handler('/yamaps-over-osm-router/v2/route')
    def _mock_yamaps(request):
        return maps_utils.mock_yamaps(request, empty_response, mockserver)

    response = await taxi_rida_web.post(
        '/v1/maps/getDistanceInfo',
        headers=helpers.get_auth_headers(user_id=1234),
        json={
            'lat1': src_lat,
            'lat2': dst_lat,
            'lng1': src_lon,
            'lng2': dst_lon,
        },
    )

    assert response.status == 200
    response_json = await response.json()
    if empty_response:
        assert response_json == {
            'status': 'INVALID_DATA',
            'errors': {'message': 'Can not get distance info !'},
        }
    else:
        assert response_json == {
            'status': 'OK',
            'data': {'distance': 10, 'duration': 7},
        }
