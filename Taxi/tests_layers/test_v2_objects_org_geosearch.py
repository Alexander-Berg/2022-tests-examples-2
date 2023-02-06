import copy

import pytest

from . import utils

URL = '/4.0/layers/v2/objects'

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

NOT_AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': '',
    'X-Request-Application': DEFAULT_APPLICATION,
    'X-Request-Language': 'ru',
    'X-AppMetrica-DeviceId': 'DeviceId',
    'X-AppMetrica-UUID': 'UUID',
}

BASE_REQUEST = {
    'state': {
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'geosearch',
        'screen': 'discovery',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}

SEARCH_QUERY = '{"some": "yamaps query"}'


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
async def test_v2_objects_org_geosearch_simple(
        taxi_layers, mockserver, load_json, yamaps,
):
    yamaps.set_fmt_response(load_json('yamaps_response.json'))
    yamaps.set_checks(
        {
            'type': 'biz',
            'text': SEARCH_QUERY,
            'ull': '37.510000,55.720000',
            'bbox': '37.450000,55.600000~37.700000,55.900000',
            'results': '7',
        },
    )

    request = copy.deepcopy(BASE_REQUEST)
    request['context'] = {
        'type': 'org_geosearch',
        'search_query': SEARCH_QUERY,
    }

    response = await taxi_layers.post(
        URL, request, headers=NOT_AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert utils.sort_features(response.json()) == utils.sort_features(
        load_json('expected_response_ikea.json'),
    )
