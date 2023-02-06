import copy

import pytest

from . import utils

URL = '/4.0/layers/v2/objects'

DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)

USER_ID = '12345678901234567890123456789012'

NOT_AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
    'X-Request-Id': 'request1',
}

AUTHORIZED_HEADERS = {
    **NOT_AUTHORIZED_HEADERS,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
}

BASE_REQUEST = {
    'state': {
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'restaurants',
        'screen': 'discovery',
        'pin': [37.5466, 55.7108],
        'zoom': 13.5,
    },
}

BASE_RESPONSE = {
    'clean_sec': 120,
    'features': [],
    'throttle_ms': 100,
    'type': 'FeatureCollection',
    'validity_sec': 60,
}


@pytest.mark.experiments3(
    filename='experiments3_display_settings_restaurants.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='eats_asset_to_image_tag.json')
async def test_v2_objects_restaurants_discovery(
        taxi_layers, mockserver, load_json,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'restaurants'
    request['state']['screen'] = 'discovery'
    request['state']['restaurants'] = {'image_size_hint': 240}

    @mockserver.json_handler(
        '/eats-catalog-map/internal/v1/catalog-for-superapp-map',
    )
    def mock_eats_catalog(catalog_request):
        assert catalog_request.json == {
            'bounding_box': request['state']['bbox'],
            'location': {
                'latitude': request['state']['location'][1],
                'longitude': request['state']['location'][0],
            },
            'zoom': request['state']['zoom'],
            'image_size_hint': request['state']['restaurants'][
                'image_size_hint'
            ],
        }
        return mockserver.make_response(
            json=load_json('catalog_for_map_response.json'), status=200,
        )

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert utils.sort_features(response.json()) == utils.sort_features(
        load_json('layers_restaurants_discovery_response.json'),
    )
    assert mock_eats_catalog.times_called == 1


@pytest.mark.experiments3(
    filename='experiments3_display_settings_restaurants.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='eats_asset_to_image_tag.json')
async def test_v2_objects_restaurants_out_of_zoom_range(
        taxi_layers, mockserver, load_json, experiments3,
):
    zoom_min = 12.0
    config = load_json('layers_providers_restaurants.json')
    config['configs'][0]['clauses'][0]['value']['restaurants'][
        'zoom_min'
    ] = zoom_min
    experiments3.add_experiments_json(config)

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['zoom'] = zoom_min - 1

    @mockserver.json_handler(
        '/eats-catalog-map/internal/v1/catalog-for-superapp-map',
    )
    def mock_eats_catalog(catalog_request):
        return mockserver.make_response(status=200)

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    assert response.status_code == 200
    assert response.json() == {
        **BASE_RESPONSE,
        'bbox': [-180.0, -90.0, 180.0, 90.0],
        'optimal_view': {'no_objects_message': 'Приблизьте карту'},
        'zooms': [0.0, zoom_min],
    }
    assert mock_eats_catalog.times_called == 0


@pytest.mark.experiments3(
    filename='experiments3_display_settings_restaurants.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='eats_asset_to_image_tag.json')
async def test_v2_objects_restaurants_empty_features(
        taxi_layers, mockserver, load_json,
):
    catalog_resp = load_json('catalog_for_map_response.json')
    catalog_resp['single_places'].clear()
    catalog_resp['clusters'].clear()

    @mockserver.json_handler(
        '/eats-catalog-map/internal/v1/catalog-for-superapp-map',
    )
    def mock_eats_catalog(_):
        return mockserver.make_response(json=catalog_resp, status=200)

    response = await taxi_layers.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {
        **BASE_RESPONSE,
        'bbox': catalog_resp['bounding_box'],
        'zooms': [
            catalog_resp['zoom_range']['min'],
            catalog_resp['zoom_range']['max'],
        ],
        'optimal_view': {'no_objects_message': 'Нет ресторанов поблизости'},
    }
    assert mock_eats_catalog.times_called == 1


@pytest.mark.experiments3(
    filename='experiments3_display_settings_restaurants.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='eats_asset_to_image_tag.json')
async def test_v2_objects_restaurants_provider_error(
        taxi_layers, mockserver, load_json,
):
    @mockserver.json_handler(
        '/eats-catalog-map/internal/v1/catalog-for-superapp-map',
    )
    def mock_eats_catalog(_):
        return mockserver.make_response(
            json={'message': '', 'code': '500'}, status=500,
        )

    response = await taxi_layers.post(
        URL, BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': 'provider_request_failed',
        'message': 'Provider restaurants features request failed',
    }
    assert mock_eats_catalog.times_called == 1
