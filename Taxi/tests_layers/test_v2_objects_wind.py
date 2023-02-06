import copy
import typing

import pytest

from . import consts

URL = '/4.0/layers/v2/objects'

BASE_REQUEST = {
    'state': {
        # after normalization these coordinates gonna become:
        # [37.45, 55.60000000000001, 37.7, 55.89999999999999]
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'scooters',
        'screen': 'discovery',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}


class MyTestCase(typing.NamedTuple):
    wind_response_file: str = 'response_wind_boards.json'
    expected_response_file: str = 'response_v2_objects.json'
    has_selected_scooter_number: bool = False
    is_selected_scooter_ready_for_riding: bool = True


@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_wind_max_board_count.json',
)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                wind_response_file='response_wind_empty.json',
                expected_response_file='response_v2_objects_only_area_centroids.json',  # noqa: E501
            ),
            id='empty_wind_response',
        ),
        pytest.param(
            MyTestCase(has_selected_scooter_number=True),
            id='boards_wind_response_with_selected_object_id',
        ),
        pytest.param(
            MyTestCase(
                has_selected_scooter_number=True,
                is_selected_scooter_ready_for_riding=False,
            ),
            id='boards_wind_response_without_selected_object_id',
        ),
        pytest.param(MyTestCase(), id='boards_wind_response'),
    ],
)
async def test_wind_success(taxi_layers, mockserver, load_json, case):
    selected_scooter_number = 'A0000998'

    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        assert request.headers['x-api-key'] == 'windapikey'

        south_west = request.json['bbox']['southWest']
        assert south_west['longitude'] == 37.45
        assert south_west['latitude'] == 55.60000000000001

        north_east = request.json['bbox']['northEast']
        assert north_east['longitude'] == 37.7
        assert north_east['latitude'] == 55.89999999999999

        assert request.json['maxBoardCount'] == 100
        return load_json(case.wind_response_file)

    @mockserver.json_handler(f'/wind/pf/v1/boards/{selected_scooter_number}')
    def _mock_wind_board(request):
        assert request.headers['x-api-key'] == 'windapikey'
        resp = load_json('response_wind_board.json')
        if not case.is_selected_scooter_ready_for_riding:
            resp['board']['isReadyForRiding'] = 0
        return resp

    request = copy.deepcopy(BASE_REQUEST)
    if case.has_selected_scooter_number:
        request['state']['scooters'] = {
            'selected_scooter_number': selected_scooter_number,
        }

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200

    expected_response = load_json(case.expected_response_file)
    if (
            case.has_selected_scooter_number
            and case.is_selected_scooter_ready_for_riding
    ):
        expected_response[
            'selected_object_id'
        ] = f'wind__{selected_scooter_number}'

    assert response.json() == expected_response


@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.parametrize('wind_response', ('timeout', 500, 400, 401))
async def test_wind_error(taxi_layers, mockserver, load_json, wind_response):
    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        if wind_response == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=wind_response)

    request = copy.deepcopy(BASE_REQUEST)
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_v2_objects_empty.json')


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                expected_response_file='response_v2_objects_cache_selected.json',
                has_selected_scooter_number=True,
            ),
            id='selected_scooters',
        ),
        pytest.param(
            MyTestCase(
                expected_response_file='response_v2_objects_cache.json',
            ),
            id='bbox_scooters',
        ),
    ],
)
@pytest.mark.config(
    LAYERS_WIND_BOARDS_SETTINGS={
        'enabled': True,
        'north_east': [34, 30],
        'south_west': [36, 33],
        'board_count': 100,
    },
)
@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings_cache.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
async def test_wind_cache(taxi_layers, mockserver, load_json, case):
    selected_scooter_number = 'A0000998'

    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        assert request.headers['x-api-key'] == 'windapikey'

        south_west = request.json['bbox']['southWest']
        assert south_west['longitude'] == 36
        assert south_west['latitude'] == 33

        north_east = request.json['bbox']['northEast']
        assert north_east['longitude'] == 34
        assert north_east['latitude'] == 30

        assert request.json['maxBoardCount'] == 100
        response = load_json(case.wind_response_file)
        for board in response['boards']:
            board['isReadyForRiding'] = 1
        return response

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['bbox'] = [34.74, 32.03, 34.78, 32.06]
    if case.has_selected_scooter_number:
        request['state']['bbox'] = [37.5, 55.7, 37.6, 55.8]
        request['state']['scooters'] = {
            'selected_scooter_number': selected_scooter_number,
        }

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200

    expected_response = load_json(case.expected_response_file)
    if case.has_selected_scooter_number:
        expected_response[
            'selected_object_id'
        ] = f'wind__{selected_scooter_number}'

    assert response.json() == expected_response
    assert _mock_wind_boards.times_called == 1


@pytest.mark.parametrize(
    'session_current_response',
    [
        pytest.param('200', id='ok'),
        pytest.param('400', id='bad_request'),
        pytest.param('401', id='unauth'),
        pytest.param('404', id='not_found'),
        pytest.param('timeout_error', id='timeout'),
        pytest.param('network_error', id='network'),
    ],
)
@pytest.mark.config(
    LAYERS_WIND_BOARDS_SETTINGS={
        'enabled': True,
        'north_east': [34, 30],
        'south_west': [36, 33],
        'board_count': 100,
    },
)
@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings_cache.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
async def test_active_order(
        taxi_layers, mockserver, load_json, session_current_response,
):
    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        response = load_json('response_wind_boards.json')
        for board in response['boards']:
            board['isReadyForRiding'] = 1
        return response

    @mockserver.json_handler(
        '/talaria-misc/4.0/scooters/external/sessions/current',
    )
    def _mock_talara_misc_sessions_current(request):
        assert request.headers['x-yataxi-scooters-tag'] == 'wind'
        assert request.headers['x-long'] == '37.510000'
        assert request.headers['x-lat'] == '55.720000'
        assert request.headers['X-YaTaxi-Bound-Uids'] == '834149473,834149474'
        assert (
            request.headers['X-YaTaxi-PhoneId'] == '123456789012345678901234'
        )
        assert request.headers['X-Yandex-UID'] == '400000000'
        assert (
            request.headers['X-YaTaxi-UserId']
            == '12345678901234567890123456789012'
        )
        if session_current_response == 'timeout_error':
            raise mockserver.TimeoutError()
        elif session_current_response == 'network_error':
            raise mockserver.NetworkError()

        status_code = int(session_current_response)
        if status_code != 200:
            return mockserver.make_response(status=status_code, json={})
        return load_json('response_sessions_current.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['known_orders_info'] = [
        {'api_tag': 'wind', 'orderid': 'orderid', 'service': 'scooters'},
    ]
    request['state']['known_orders'] = ['scooters:orderid']
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    if session_current_response == '200':
        assert response.json() == load_json(
            'response_v2_object_active_order.json',
        )
        assert _mock_talara_misc_sessions_current.times_called == 1
    else:
        assert response.json() == load_json(
            'response_v2_objects_only_area_centroids.json',
        )
        assert _mock_talara_misc_sessions_current.times_called >= 1
    assert _mock_wind_boards.times_called == 1


@pytest.mark.parametrize('screen', ['multiorder', 'totw'])
@pytest.mark.config(
    LAYERS_WIND_BOARDS_SETTINGS={
        'enabled': True,
        'north_east': [34, 30],
        'south_west': [36, 33],
        'board_count': 100,
    },
)
@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings_cache.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
async def test_active_order_on_screens(
        taxi_layers, mockserver, load_json, screen,
):
    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        response = load_json('response_wind_boards.json')
        for board in response['boards']:
            board['isReadyForRiding'] = 1
        return response

    @mockserver.json_handler(
        '/talaria-misc/4.0/scooters/external/sessions/current',
    )
    def _mock_talara_misc_sessions_current(request):
        return load_json('response_sessions_current.json')

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['known_orders_info'] = [
        {'api_tag': 'wind', 'orderid': 'orderid', 'service': 'scooters'},
    ]
    request['state']['bbox'] = [34.74, 32.03, 34.78, 32.06]
    request['state']['known_orders'] = ['scooters:orderid']
    request['state']['screen'] = screen
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    expected_response = load_json('response_v2_object_active_on_order.json')
    if screen == 'multiorder':
        expected_response['multiorder_extra'] = {
            'focus_features_ids': ['wind__S0035404'],
        }
    assert response.status_code == 200
    assert response.json() == expected_response
    assert _mock_talara_misc_sessions_current.times_called == 1
    assert _mock_wind_boards.times_called == 1


@pytest.mark.config(
    LAYERS_WIND_BOARDS_SETTINGS={
        'enabled': True,
        'north_east': [34, 30],
        'south_west': [36, 33],
        'board_count': 100,
    },
)
@pytest.mark.experiments3(filename='experiments3_scooters_enabled.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings_cache.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
async def test_active_order_on_main(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        response = load_json('response_wind_boards.json')
        for board in response['boards']:
            board['isReadyForRiding'] = 1
        return response

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['bbox'] = [34.74, 32.03, 34.78, 32.06]
    request['state']['pin'] = [34.76, 32.042]
    request['state']['mode'] = 'normal'
    request['state']['screen'] = 'main'
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    expected_response = load_json('response_v2_object_on_main.json')
    assert response.status_code == 200
    assert response.json() == expected_response
    assert _mock_wind_boards.times_called == 1


@pytest.mark.config(
    LAYERS_WIND_BOARDS_SETTINGS={
        'enabled': True,
        'north_east': [34, 30],
        'south_west': [36, 33],
        'board_count': 100,
    },
)
@pytest.mark.experiments3(filename='experiments3_scooters_enabled.json')
@pytest.mark.experiments3(
    filename='experiments3_layers_wind_display_settings_group.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
async def test_parking_group(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/wind/pf/v2/boards')
    def _mock_wind_boards(request):
        response = load_json('response_wind_boards.json')
        for board in response['boards']:
            board['isReadyForRiding'] = 1
        return response

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['bbox'] = [34.74, 32.03, 34.78, 32.06]
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    expected_response = load_json('response_v2_object_group.json')
    assert response.status_code == 200
    assert response.json() == expected_response
    assert _mock_wind_boards.times_called == 1
