import copy
import json

import pytest

URL = '/layers/v1/objects'

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
    'X-Remote-IP': '10.10.10.10',
}

BASE_REQUEST = {
    'position': [37.5466, 55.7108],
    'state': {
        'bbox': [30.1, 50.1, 40.1, 60.1],
        'location': [37.51, 55.72],
        'current_mode': 'normal',
        'screen': 'main',
    },
}


@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v1_objects_empty(taxi_layers):
    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = []
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == {
        'type': 'FeatureCollection',
        'features': [],
        'bbox': [30.1, 50.1, 40.1, 60.1],
    }


@pytest.mark.parametrize('mock_code', ['timeout', 200, 400, 500])
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
async def test_v1_objects_stops(taxi_layers, mockserver, load_json, mock_code):
    @mockserver.json_handler('/masstransit/v1/stops')
    def _mock_stops(request):
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        assert json.loads(request.get_data()) == {
            'lang': 'ru',
            'position': [37.5466, 55.7108],
            'types': ['stop', 'exit'],
            'requested_data': ['stops'],
        }
        if mock_code == 'timeout':
            raise mockserver.TimeoutError()
        elif mock_code != 200:
            return mockserver.make_response('{}', status=mock_code)
        return load_json('response_stops.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['stop']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = []
    if mock_code == 200:
        expected_features = load_json('features.json')['stops']

    assert response.status_code == 200
    assert response.json() == {
        'type': 'FeatureCollection',
        'features': expected_features,
        'bbox': [30.1, 50.1, 40.1, 60.1],
    }


@pytest.mark.translations(
    client_messages={'boats_point_title': {'ru': 'Остановка Лодочек'}},
)
@pytest.mark.config(
    MODES=[
        {
            'experiment': 'enable_boats_2',
            'mode': 'boats',
            'zone_activation': {
                'point_image_tag': 'boat_pp_icon',
                'point_title': 'boats_point_title',
                'zone_type': 'boats',
            },
        },
    ],
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_modes.json')
async def test_v1_objects_modes_config_title(
        taxi_layers, mockserver, load_json,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        assert request.headers['X-Request-Language'] == 'ru'
        assert json.loads(request.get_data()) == {
            'type': 'any',
            'geopoint': [37.5466, 55.7108],
            'filter': {'allowed_zone_types': ['boats']},
        }
        return load_json('response_zones_v2_with_boats.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['mode']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = load_json('features.json')['modes_boats']

    assert response.status_code == 200
    assert response.json() == {
        'type': 'FeatureCollection',
        'features': expected_features,
        'bbox': [30.1, 50.1, 40.1, 60.1],
    }


@pytest.mark.translations(
    client_messages={
        'sdc_point_label_key': {'ru': 'Это остановочка самоходочки'},
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_modes.json')
@pytest.mark.parametrize('mock_code', ['timeout', 200, 400, 500])
async def test_v1_objects_modes(taxi_layers, mockserver, load_json, mock_code):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        assert request.headers['X-Request-Language'] == 'ru'
        assert json.loads(request.get_data()) == {
            'type': 'any',
            'geopoint': [37.5466, 55.7108],
            'filter': {'allowed_zone_types': ['sdc', 'boats']},
        }
        if mock_code == 'timeout':
            raise mockserver.TimeoutError()
        elif mock_code != 200:
            return mockserver.make_response('{}', status=mock_code)
        return load_json('response_zones_v2_with_boats.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['mode']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = []
    if mock_code == 200:
        expected_features = load_json('features.json')['modes']

    assert response.status_code == 200
    assert response.json() == {
        'type': 'FeatureCollection',
        'features': expected_features,
        'bbox': [30.1, 50.1, 40.1, 60.1],
    }


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize('mock_code', ['timeout', 200, 400, 500])
async def test_v1_objects_userplaces(
        taxi_layers, mockserver, load_json, mock_code,
):
    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces_list(request):
        assert json.loads(request.get_data()) == {
            'lang': 'ru',
            'app_name': 'iphone',
            'user_identity': {
                'bound_yandex_uids': ['834149473', '834149474'],
                'flags': {'is_phonish': False, 'is_portal': True},
                'phone_id': '123456789012345678901234',
                'user_id': '12345678901234567890123456789012',
                'yandex_uid': '400000000',
            },
        }
        if mock_code == 'timeout':
            raise mockserver.TimeoutError()
        elif mock_code != 200:
            return mockserver.make_response('{}', status=mock_code)
        return load_json('response_userplaces_list.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        request_data = json.loads(request.get_data())
        request_data['excluded_zone_types'].sort()
        assert request_data == {
            'points': [[37.1, 55.1], [37.2, 55.2], [37.56, 55.77]],
            'excluded_zone_types': ['boats', 'falcon', 'sdc', 'skolkovo'],
        }
        return {
            'results': [
                {'in_zone': False},
                {'in_zone': True},
                {'in_zone': False},
            ],
        }

    request = copy.deepcopy(BASE_REQUEST)
    request['types'] = ['userplace']
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    expected_features = []
    if mock_code == 200:
        expected_features = load_json('features.json')['userplaces']

    assert response.status_code == 200
    assert response.json() == {
        'type': 'FeatureCollection',
        'features': expected_features,
        'bbox': [30.1, 50.1, 40.1, 60.1],
    }


@pytest.mark.translations(
    client_messages={
        'sdc_point_label_key': {'ru': 'Это остановочка самоходочки'},
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_stops.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_modes.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize('mock_code', [200, 400, 500])
async def test_v1_objects_all(taxi_layers, mockserver, load_json, mock_code):
    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        results = [{'in_zone': False}, {'in_zone': True}, {'in_zone': False}]
        return {'results': results}

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces_list(request):
        return load_json('response_userplaces_list.json')

    @mockserver.json_handler('/masstransit/v1/stops')
    def _mock_stops(request):
        if mock_code != 200:
            return mockserver.make_response('{}', status=mock_code)
        return load_json('response_stops.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('response_zones_v2_with_boats.json')

    request = copy.deepcopy(BASE_REQUEST)
    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)

    features = load_json('features.json')
    expected = list()
    expected.extend(features['userplaces'])
    expected.extend(features['modes'])
    # check that single provider fail doesn't affect others
    if mock_code == 200:
        expected.extend(features['stops'])
    assert response.status_code == 200
    assert response.json() == {
        'type': 'FeatureCollection',
        'features': expected,
        'bbox': [30.1, 50.1, 40.1, 60.1],
    }
