import copy

import pytest

URL = '/4.0/layers/v1/polylines'

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


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3(filename='exp3_shuttle_enabled_routes.json')
@pytest.mark.experiments3(filename='exp3_layers_providers_polylines.json')
@pytest.mark.experiments3(filename='exp3_shuttle_routes_display_settings.json')
@pytest.mark.experiments3(filename='exp3_layers_cache_polylines.json')
async def test_polylines_simple(taxi_layers, load_json):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'shuttle'
    request['state']['screen'] = 'discovery'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200

    assert response.json() == load_json('polylines_simple_resp.json')
