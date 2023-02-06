import copy

import pytest

URL = '/4.0/layers/v1/polygons'

DEFAULT_APPLICATION = (
    'app_name=iphone,app_ver1=3,app_ver2=2,app_ver3=4,app_brand=yataxi'
)

USER_ID = '12345678901234567890123456789012'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-YaTaxi-Bound-Uids': '834149473,834149474',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
}

BASE_REQUEST = {
    'state': {
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'normal',
        'screen': 'multiorder',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
        'known_orders': ['scooters:123'],
    },
}


@pytest.mark.experiments3(filename='experiments3_layers_cache_polygons.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_providers_polygons.json',
)
@pytest.mark.layers_scooters_areas(filename='scooters_areas.json')
@pytest.mark.translations(
    client_messages={'scooters.not_so_fast': {'ru': 'Не гони!'}},
)
@pytest.mark.parametrize('cached', (False, True))
async def test_v1_polygons_simple(taxi_layers, load_json, cached):
    request = copy.deepcopy(BASE_REQUEST)
    expected_response = load_json('response_scooters_areas.json')
    if cached:
        request['known_versions'] = {
            'scooters__polygon__1337': 'poly:123;cfg:1337',
            '1-LOW-wind_city0_map_id': 'poly:;cfg:1337',
            '1-LOW-wind_city1_map_id': 'poly:;cfg:1337',
        }
        expected_response['features'] = []
        expected_response['not_changed_features'] = [
            '1-LOW-wind_city0_map_id',
            '1-LOW-wind_city1_map_id',
            'scooters__polygon__1337',
        ]

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200

    resp_body = response.json()
    if 'not_changed_features' in resp_body:
        resp_body['not_changed_features'] = sorted(
            resp_body['not_changed_features'],
        )

    assert resp_body == expected_response


@pytest.mark.now('2018-05-20T15:00:00+0300')
@pytest.mark.experiments3(
    filename='experiments3_layers_providers_polygons_sdc.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_polygons.json')
@pytest.mark.experiments3(filename='exp3_zones_visibility.json')
@pytest.mark.experiments3(filename='exp3_zones_enable_experiments.json')
async def test_v1_polygons_sdc(taxi_layers, mockserver, load_json):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'sdc'
    request['state']['screen'] = 'main'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200

    expected = load_json('response_sdc_polygon.json')
    resp_data = response.json()
    assert resp_data['features'][0]['properties']['version']
    resp_data['features'][0]['properties'].pop('version')
    assert resp_data == expected
