import pytest

import common

MAAS_NEAREST_METRO_SETTINGS = {
    'fallback_line': {
        'id': 'fallback_line',
        'name': 'fallback_line',
        'color': 'FA11BA',
    },
}

CLIENT_MESSAGES = {
    'maas.nearest_metro.station_screen.title': {'en': 'station screen title'},
    'maas.nearest_metro.station_screen.button_text': {
        'en': 'station screen button',
    },
    'maas.nearest_metro.dropoff_screen.title': {'en': 'dropoff screen title'},
    'maas.nearest_metro.dropoff_screen.button_text': {
        'en': 'dropoff screen button',
    },
    'maas.nearest_metro.exit_name': {'en': 'exit %(name)s'},
    'maas.nearest_metro.estimated_time': {'en': '~ %(min)s min'},
}


def sort_stops_nearby_response(response):
    response['dropoff_points'].sort(key=lambda o: o['id'])
    response['lines'].sort(key=lambda o: o['id'])
    return response


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(
    MAAS_NEAREST_METRO_SETTINGS={
        'line_numbers_fallback_settings': {
            'enabled': True,
            'delimiter': ' · ',
        },
    },
)
async def test_main(taxi_maas, taxi_config, load_json, mockserver):
    await taxi_maas.invalidate_caches()

    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        assert request.json == common.create_stops_nearby_request(
            position=[37.62, 55.75],
            distance_meters=30000.0,
            pickup_points_type='identical',
            transfer_type='from_mt',
            routers={'bee': {'type': 'bee_line'}},
            transport_types=['underground'],
            fetch_lines=False,
        )
        assert request.headers['X-Request-Language'] == 'en'
        response = load_json('stops_nearby_response.json')
        return mockserver.make_response(json=response)

    headers = {'X-Request-Language': 'en'}
    params = {'lat': 55.5, 'lon': 37.5}
    response = await taxi_maas.get(
        '/4.0/maas/v1/nearest-metro', headers=headers, params=params,
    )
    assert response.status_code == 200
    expected_response = load_json('nearest_metro_response.json')
    assert sort_stops_nearby_response(
        response.json(),
    ) == sort_stops_nearby_response(expected_response)


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.config(MAAS_NEAREST_METRO_SETTINGS=MAAS_NEAREST_METRO_SETTINGS)
async def test_fallback_line(taxi_maas, load_json, mockserver):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        response = load_json('stops_nearby_response.json')
        del response['lines']
        for stop in response['stops']:
            del stop['line_ids']
        return mockserver.make_response(json=response)

    headers = {'X-Request-Language': 'en'}
    params = {'lat': 55.5, 'lon': 37.5}
    response = await taxi_maas.get(
        '/4.0/maas/v1/nearest-metro', headers=headers, params=params,
    )
    assert response.status_code == 200
    expected_response = load_json('nearest_metro_fallback_line_response.json')
    assert sort_stops_nearby_response(
        response.json(),
    ) == sort_stops_nearby_response(expected_response)


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
async def test_geo_client_qos(taxi_maas, mockserver, taxi_config, load_json):
    taxi_config.set(
        MAAS_GEO_HELPER_SETTINGS={
            'geo_client_qos': {
                'get_all_available_metro': {'timeout-ms': 50, 'attempts': 5},
            },
            'route_validation_settings': {
                'enable_geo_checks': True,
                'ignore_geo_errors': False,
            },
            'geo_settings': load_json('geo_settings.json'),
        },
    )

    await taxi_maas.invalidate_caches()

    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        assert request.json == common.create_stops_nearby_request(
            position=[37.62, 55.75],
            distance_meters=30000.0,
            pickup_points_type='identical',
            transfer_type='from_mt',
            routers={'bee': {'type': 'bee_line'}},
            transport_types=['underground'],
            fetch_lines=False,
        )
        assert request.headers['X-Request-Language'] == 'en'

        return mockserver.make_response(json={}, status=500)

    headers = {'X-Request-Language': 'en'}
    params = {'lat': 55.5, 'lon': 37.5}
    response = await taxi_maas.get(
        '/4.0/maas/v1/nearest-metro', headers=headers, params=params,
    )
    assert response.status_code == 500
    assert _stops_nearby.times_called == 5


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
async def test_response_with_railway(
        taxi_maas, load_json, mockserver, taxi_config,
):
    taxi_config.set(
        MAAS_GEO_HELPER_SETTINGS={
            'geo_client_qos': {},
            'route_validation_settings': {
                'enable_geo_checks': True,
                'ignore_geo_errors': False,
            },
            'geo_settings': load_json('geo_settings_with_railway.json'),
        },
    )

    await taxi_maas.invalidate_caches()

    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        request_json = request.json
        assert len(request_json['transport_types']) == 1
        assert request_json['transport_types'][0] in {'underground', 'railway'}
        assert request_json == common.create_stops_nearby_request(
            position=[37.5, 55.5],
            distance_meters=5000.0,
            pickup_points_type='identical',
            transfer_type='from_mt',
            routers={'default': {'type': 'by_car'}},
            transport_types=request_json['transport_types'],
            fetch_lines=True,
        )
        assert request.headers['X-Request-Language'] == 'en'

        response_file = (
            'stops_nearby_response.json'
            if request_json['transport_types'] == ['underground']
            else 'stops_nearby_railway_response.json'
        )

        return mockserver.make_response(json=load_json(response_file))

    headers = {'X-Request-Language': 'en'}
    params = {'lat': 55.5, 'lon': 37.5}
    response = await taxi_maas.get(
        '/4.0/maas/v1/nearest-metro', headers=headers, params=params,
    )

    assert _stops_nearby.times_called == 2

    assert response.status_code == 200
    expected_response = load_json('nearest_metro_with_railway_response.json')
    assert sort_stops_nearby_response(response.json()) == expected_response
