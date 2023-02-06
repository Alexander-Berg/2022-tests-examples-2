import copy
import hashlib

import pytest

URL = '/4.0/layers/v1/cluster'

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
    'context': {
        'type': 'cluster_complete_request',
        'cluster_id': 1337,
        'provider': 'FILL ME',
    },
    'state': {
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'drive',
        'screen': 'discovery',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}


@pytest.mark.experiments3(filename='experiments3_layers_cluster_card.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.translations(
    client_messages={
        'drive.cluster_car_count': {'ru': 'Вот как много: %(count)s машин'},
        'scooters.cluster_car_count': {
            'ru': 'Вот как много: %(count)s самокатов',
        },
        'scooters.parking_title': {'ru': 'Парковка самокатов'},
    },
)
@pytest.mark.parametrize('provider', ['drive', 'scooters'])
async def test_v1_cluster_simple(taxi_layers, mockserver, load_json, provider):
    request = copy.deepcopy(BASE_REQUEST)
    request['context']['provider'] = provider

    remote_service = (
        'scooter-backend' if provider == 'scooters' else 'yandex-drive'
    )

    @mockserver.json_handler(f'/{remote_service}/car/list')
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
        assert request.args == {'cluster': '1337', 'lang': 'ru'}

        response = load_json('response_yandex_drive_car_list_by_cluster.json')
        if provider == 'scooters':
            for car in response['cars']:
                car['model_id'] = 'ninebot'
        return mockserver.make_response(
            json=response, headers={'X-Req-Id': '123'},
        )

    expected_json = load_json('expected_response_cluster_details.json')

    if provider == 'scooters':
        expected_json['title']['items'][0]['text'] = 'Парковка самокатов'
        # message skipped
        expected_json['subtitle']['items'][0][
            'text'
        ] = 'Вот как много: 3 самокатов'
        for scooter in expected_json['car_details']:
            scooter['onboarding_type'] = 'moscow_scooter_onboarding'

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.experiments3(filename='experiments3_layers_cluster_card.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_no_selected_mode(taxi_layers, mockserver):
    request = copy.deepcopy(BASE_REQUEST)
    request['context']['provider'] = 'scooters'
    request['state']['known_orders'] = ['scooters:x123']

    @mockserver.json_handler('/scooter-backend/car/list')
    def mock(req):
        assert req.query['no_selected'] == '1'

    await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert mock.times_called == 1


@pytest.mark.config(
    LAYERS_WIND_BOARDS_SETTINGS={
        'enabled': True,
        'north_east': [34, 30],
        'south_west': [36, 33],
        'board_count': 100,
    },
)
@pytest.mark.translations(
    client_messages={
        'drive.cluster_car_count': {'ru': 'Вот как много: %(count)s машин'},
        'scooters.cluster_car_count': {
            'ru': 'Вот как много: %(count)s самокатов',
        },
        'scooters.parking_title': {'ru': 'Парковка самокатов'},
    },
)
@pytest.mark.parametrize(
    'cluster_id, expected_status, expected_response_file',
    [
        pytest.param(
            -859138507, 200, 'expected_response_wind_cluster.json', id='ok',
        ),
        pytest.param(
            111,
            404,
            'expected_response_wind_not_found_cluster.json',
            id='not_found',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_layers_cluster_card.json')
async def test_wind_cluster(
        taxi_layers,
        mockserver,
        load_json,
        cluster_id,
        expected_status,
        expected_response_file,
):
    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        response = load_json('response_wind_boards.json')
        for board in response['boards']:
            board['isReadyForRiding'] = 1
        return response

    @mockserver.json_handler(
        'wind/pf/v1/parkingPorts/5dee27cef79257c5c445cada/boards',
    )
    def _mock_parking_ports(request):
        return load_json('response_parking_boards.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['context']['provider'] = 'wind'
    request['context']['cluster_id'] = cluster_id
    request['state']['known_orders'] = ['wind:x123']

    response = await taxi_layers.post(URL, request, headers=AUTHORIZED_HEADERS)
    assert response.status_code == expected_status
    assert response.json() == load_json(expected_response_file)
    assert _mock_wind_boards.times_called == 1
