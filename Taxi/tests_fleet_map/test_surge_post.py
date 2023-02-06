ENDPOINT = '/fleet/map/v1/surge'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park1',
}

ENUMERATE_MAP_RESPONSE = {
    'content_keys': {
        'taxi_surge/__default__/default': {'description': 'Driver'},
        'taxi_surge_lightweight/__default__/default': {'description': 'Rider'},
    },
    'default_key': 'taxi_surge/__default__/default',
}

HEATMAP_RESPONSE = {
    'features': [
        {
            'geometry': {'coordinates': [37.685, 55.727], 'type': 'Point'},
            'properties': {'surge': 5.0},
            'type': 'Feature',
        },
        {
            'geometry': {'coordinates': [37.682, 55.726], 'type': 'Point'},
            'properties': {'surge': 3.0},
            'type': 'Feature',
        },
        {
            'geometry': {'coordinates': [37.679, 55.727], 'type': 'Point'},
            'properties': {'surge': 2.0},
            'type': 'Feature',
        },
        {
            'geometry': {'coordinates': [37.673, 55.727], 'type': 'Point'},
            'properties': {'surge': 0.0},
            'type': 'Feature',
        },
        {
            'geometry': {'coordinates': [37.676, 55.726], 'type': 'Point'},
            'properties': {'surge': 1.0},
            'type': 'Feature',
        },
    ],
    'type': 'FeatureCollection',
}

V2_META_RESPONSE = {
    'legend': '1.1 - 1.4',
    'legend_max': 1.4,
    'legend_min': 1.1,
    'legend_precision': 2,
    'legend_measurement_units': 'RUB',
    'updated_epoch': 1546398000,
    'version_id': '5',
}

RESPONSE_HEADERS = {'Access-Control-Allow-Origin': '*'}

SERVICE_REQUEST = {'lon': 55.290000, 'lat': 127.300000}

SERVICE_RESPONSE = {
    'legend': '1.1 - 1.4',
    'legend_measurement_units': 'RUB',
    'legend_max': 1.4,
    'legend_min': 1.1,
    'surge_features': [
        {'coordinates': [37.685, 55.727], 'surge': 5.0},
        {'coordinates': [37.682, 55.726], 'surge': 3.0},
        {'coordinates': [37.679, 55.727], 'surge': 2.0},
        {'coordinates': [37.673, 55.727], 'surge': 0.0},
        {'coordinates': [37.676, 55.726], 'surge': 1.0},
    ],
}


async def test_default(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/heatmap-renderer/v2/meta')
    def _meta_get(request):
        assert request.query == {
            'lon': '55.290000',
            'lat': '127.300000',
            'content': 'taxi_surge/__default__/default',
        }
        return mockserver.make_response(
            json=V2_META_RESPONSE, headers=RESPONSE_HEADERS, status=200,
        )

    @mockserver.json_handler('/heatmap-renderer/heatmap')
    def _profiles_retrieve(request):
        assert request.query == {
            'lon': '55.290000',
            'lat': '127.300000',
            'v': '5',
        }
        return mockserver.make_response(
            json=HEATMAP_RESPONSE, headers=RESPONSE_HEADERS, status=200,
        )

    @mockserver.json_handler('/heatmap-surge-api/enumerate_maps')
    def _phones_bulk_retrieve(request):
        assert request.query == {}
        return mockserver.make_response(
            json=ENUMERATE_MAP_RESPONSE, headers=RESPONSE_HEADERS, status=200,
        )

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == SERVICE_RESPONSE


async def test_no_map(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/heatmap-renderer/v2/meta')
    def _meta_get(request):
        assert request.query == {
            'lon': '55.290000',
            'lat': '127.300000',
            'content': 'taxi_surge/__default__/default',
        }
        return mockserver.make_response(
            json='', headers=RESPONSE_HEADERS, status=204,
        )

    @mockserver.json_handler('/heatmap-surge-api/enumerate_maps')
    def _phones_bulk_retrieve(request):
        assert request.query == {}
        return mockserver.make_response(
            json=ENUMERATE_MAP_RESPONSE, headers=RESPONSE_HEADERS, status=200,
        )

    response = await taxi_fleet_map.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status_code == 204
