import copy
import operator

import pytest

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
        'mode': 'normal',
        'screen': 'main',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}


@pytest.mark.uservice_oneshot
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.layers_qr_objects(data={})  # invalid response
async def test_v2_objects_qr_cache(
        taxi_layers, mockserver, load_json, qr_objects_mock,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'qr'
    request['state']['screen'] = 'discovery'

    # fails when cache is not updated since start
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 500
    assert response.json() == {
        'code': 'provider_request_failed',
        'message': 'Provider qr features request failed',
    }

    # succeeds after successfull update
    qr_objects_mock.update(
        load_json('iiko_integration_qr_objects_response.json'),
    )
    await taxi_layers.invalidate_caches(
        clean_update=True, cache_names=['qr-objects-cache'],
    )
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    response_json = response.json()

    # retains cache contents after subsequent fails
    qr_objects_mock.update({})
    await taxi_layers.invalidate_caches(
        clean_update=True, cache_names=['qr-objects-cache'],
    )
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == response_json


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
@pytest.mark.translations(
    qr_payment={'restaurants.khleb.title': {'ru': 'Хлеб Насущный'}},
)
@pytest.mark.parametrize(
    ['bbox', 'expected_features_idxes'],
    [
        ([37, 55, 38, 56], [0, 1, 2, 3, 4]),
        ([37.620, 55.772, 37.621, 55.773], [0]),
    ],
)
async def test_v2_objects_qr_normal(
        taxi_layers, mockserver, load_json, bbox, expected_features_idxes,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['bbox'] = bbox
    request['state']['mode'] = 'qr'
    request['state']['screen'] = 'discovery'

    expected = load_json('qr_discovery_expected_response_basic.json')
    assert expected['features'] == []
    for i, feature in enumerate(
            load_json('qr_discovery_expected_features.json'),
    ):
        if i in expected_features_idxes:
            expected['features'].append(feature)
    expected['features'].sort(key=operator.itemgetter('id'))
    expected['bbox'] = 'whatever'
    expected['optimal_view'] = 'whatever or nothing'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    response_json = response.json()
    response_json['features'].sort(key=operator.itemgetter('id'))
    response_json['bbox'] = 'whatever'
    response_json['optimal_view'] = 'whatever or nothing'
    assert response_json == expected


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
@pytest.mark.translations(
    client_messages={
        'layers.qr.no_features_title': {'ru': 'Нет объектов'},
        'layers.qr.no_features_subtitle': {'ru': 'Попробуйте подвигать карту'},
    },
)
async def test_v2_objects_qr_no_objects(taxi_layers, mockserver, load_json):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['bbox'] = [1, 2, 3, 4]
    request['state']['mode'] = 'qr'
    request['state']['screen'] = 'discovery'

    expected = load_json('qr_discovery_expected_response_no_objects.json')
    expected['bbox'] = 'whatever'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    response_json = response.json()
    response_json['bbox'] = 'whatever'
    assert response_json == expected


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.translations(
    client_messages={
        'layers.qr.unavailable_title': {'ru': 'QR недоступен'},
        'layers.qr.unavailable_subtitle': {'ru': 'Такие дела'},
    },
)
async def test_v2_objects_qr_unavailable(taxi_layers, mockserver, load_json):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'qr'
    request['state']['screen'] = 'discovery'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'qr_discovery_expected_response_unavailable.json',
    )


@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_providers_qr_from_geosearch.json',
)
@pytest.mark.config(MAPS_QR_PAYMENT_FILTER='provider:that_qr_thing')
@pytest.mark.layers_qr_objects(
    filename='iiko_integration_qr_objects_response.json',
)
async def test_v2_objects_qr_from_geosearch(taxi_layers, yamaps, load_json):
    yamaps.set_fmt_response(load_json('yamaps_response_qr_filter.json'))
    yamaps.set_checks(
        {
            'type': 'biz',
            'text': 'provider:that_qr_thing',
            'ull': '37.510000,55.720000',
            'bbox': '37.450000,55.600000~37.700000,55.900000',
            'results': '6',
        },
    )

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'qr'
    request['state']['screen'] = 'discovery'

    expected = load_json('qr_discovery_expected_response_basic.json')
    expected['bbox'] = pytest.approx([30.505, 59.8889, 30.6241, 59.907])
    expected['optimal_view'] = {'optimal_bbox': expected['bbox']}
    expected['features'] = load_json(
        'qr_discovery_expected_features_from_geosearch.json',
    )
    expected['features'].sort(key=operator.itemgetter('id'))

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    response_json = response.json()
    response_json['features'].sort(key=operator.itemgetter('id'))
    assert response_json == expected
