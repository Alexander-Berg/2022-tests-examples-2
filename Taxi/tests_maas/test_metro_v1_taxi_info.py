import pytest


def _create_deeplink(lon_a, lat_a, lon_b, lat_b):
    return (
        'yandextaxi://maas-ride/?mode=route&vertical_id=maas&'
        f'lon_a={lon_a}&lat_a={lat_a}&lon_b={lon_b}&lat_b={lat_b}'
    )


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_ok(taxi_maas, mockserver, load_json):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        response_file = 'stops_nearby_response.json'
        return mockserver.make_response(json=load_json(response_file))

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/maas/metro/v1/taxi-info',
        json={
            'point_a': {'lon': 38, 'lat': 56},
            'point_b': {'lon': 37.467, 'lat': 55.736},
            'maas_sub_id': 'active_id',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'deeplink': _create_deeplink(38, 56, 37.467, 55.736),
        'eta_seconds': 0,
        'time_on_the_way_seconds': 0,
    }


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'taxi_info_request, expected_status_code, expected_response',
    [
        pytest.param(
            {
                'point_a': {'lon': 38, 'lat': 56},
                'point_b': {'lon': 37.467, 'lat': 55.736},
                'maas_sub_id': 'active_id',
            },
            200,
            {
                'deeplink': _create_deeplink(38, 56, 37.467, 55.736),
                'eta_seconds': 0,
                'time_on_the_way_seconds': 0,
            },
            id='valid_to_metro',
        ),
        pytest.param(
            {
                'point_a': {'lon': 37.50, 'lat': 55.50},
                'maas_sub_id': 'active_id',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 66, path \'\': '
                    'missing required field \'point_b\''
                ),
            },
            id='bad_request',
        ),
        pytest.param(
            {
                'point_a': {'lon': 38, 'lat': 56},
                'point_b': {'lon': 38, 'lat': 56},
                'maas_sub_id': 'active_id',
            },
            406,
            {'code': 'route_points_too_far_from_metro', 'message': ''},
            id='route_points_too_far_from_metro',
        ),
        pytest.param(
            {
                'point_a': {'lon': 38, 'lat': 56},
                'point_b': {'lon': 37.467, 'lat': 55.736},
                'maas_sub_id': 'unknown_id',
            },
            406,
            {'code': 'subscription_unavailable', 'message': ''},
            id='no_subscription',
        ),
        pytest.param(
            {
                'point_a': {'lon': 38, 'lat': 56},
                'point_b': {'lon': 37.467, 'lat': 55.736},
                'maas_sub_id': 'reserved_id',
            },
            406,
            {'code': 'subscription_unavailable', 'message': ''},
            id='inactive_subscription',
        ),
    ],
)
async def test_checks(
        taxi_maas,
        load_json,
        mockserver,
        taxi_info_request,
        expected_status_code,
        expected_response,
):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        response_file = 'stops_nearby_response.json'
        return mockserver.make_response(json=load_json(response_file))

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/maas/metro/v1/taxi-info', json=taxi_info_request,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_response
