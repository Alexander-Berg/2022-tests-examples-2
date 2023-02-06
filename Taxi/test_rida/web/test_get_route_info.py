import datetime

import pytest

from test_rida import helpers
from test_rida import maps_utils


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize('request_body_as_query', [True, False])
@pytest.mark.parametrize(
    ['google_status_code', 'expected_response'],
    [
        (
            200,
            {
                'status': 'OK',
                'data': {
                    'distance': 232,
                    'duration': 200,
                    'polyline': maps_utils.generate_encoded_polyline(
                        maps_utils.POLYLINE, False,
                    ),
                    'static_map_url': '',
                },
            },
        ),
        (
            500,
            {
                'status': 'INVALID_DATA',
                'errors': {'message': 'Can not get route info !'},
            },
        ),
    ],
)
async def test_get_route_info(
        taxi_rida_web,
        mockserver,
        request_body_as_query,
        google_status_code,
        expected_response,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/directions/json',
    )
    def _mock_google_maps(request):
        assert request.query == {
            'origin': '40.2104518,50.2104518',
            'destination': '44.5288846,54.5288846',
            'language': 'en',
            'traffic_model': 'best_guess',
            'departure_time': '1609459200',
            'google_api_key': 'rida',
        }
        return maps_utils.make_gmaps_directions_response(
            maps_utils.POLYLINE,
            100,
            232,
            200,
            google_status_code,
            'OK',
            False,
            mockserver,
        )

    request_params = {'headers': helpers.get_auth_headers(user_id=1234)}
    request_body = {
        'lat1': '40.2104518',
        'lat2': '44.5288846',
        'lng1': '50.2104518',
        'lng2': '54.5288846',
        'country_code': 'ng',
    }

    if request_body_as_query:
        request_params['data'] = request_body
    else:
        request_params['json'] = request_body

    response = await taxi_rida_web.post(
        '/v1/maps/getRouteInfo', **request_params,
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
