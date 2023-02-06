import copy
import hashlib

import pytest

URL = '/4.0/layers/v1/drive-filters'

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
        'mode': 'drive',
        'screen': 'discovery',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v1_drive_filters_empty(taxi_layers, mockserver, load_json):
    request = copy.deepcopy(BASE_REQUEST)

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        return mockserver.make_response(
            json=load_json('drive_response_no_filters.json'),
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 500


@pytest.mark.parametrize(
    'mode, screen',
    [
        pytest.param('scooters', 'discovery', id='wrong_mode'),
        pytest.param('drive', 'totw', id='wrong_screen'),
    ],
)
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v1_drive_filters_not_drive_discovery(
        taxi_layers, mockserver, load_json, mode, screen,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = mode
    request['state']['screen'] = screen

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        return mockserver.make_response(
            json=load_json('drive_response_no_filters.json'),
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 400


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v1_drive_filters(taxi_layers, mockserver, load_json):
    request = copy.deepcopy(BASE_REQUEST)

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['UUID'] == 'UUID'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert request.headers['X-YaTaxi-UserId'] == USER_ID
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'400000000').hexdigest()
        )
        assert request.args == {
            'bbox': '37.45 55.6 37.7 55.9',
            'limit': '1000',
            'lang': 'ru',
        }
        return mockserver.make_response(
            json=load_json('drive_response_filters.json'),
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('base_filters_response.json')


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v1_drive_filters_with_empty_fields(
        taxi_layers, mockserver, load_json,
):
    request = copy.deepcopy(BASE_REQUEST)

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        return mockserver.make_response(
            json=load_json('drive_response_filters_empty_fields.json'),
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('filters_response_empty_fields.json')
