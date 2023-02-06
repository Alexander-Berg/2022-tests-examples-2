import pytest


@pytest.mark.parametrize(
    [
        'wind_create_ride_response_file',
        'wind_create_board_id_response_file',
        'wind_info_ride_id_started_response_file',
        'wind_info_ride_id_locked_response_file',
        'response_status_code',
    ],
    [
        (
            'wind_create_start_ride_response.json',
            'wind_booked_board_id_response.json',
            'wind_info_ride_id_started_response.json',
            'wind_info_ride_id_locked_response.json',
            200,
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.config(
    TALARIA_MISC_POLLING_SETTINGS={
        'wind_polling_status_timeout_ms': 5000,
        'wind_polling_status_interval_ms': 1000,
    },
)
async def test_200_response_create_ride(
        wind_create_ride_response_file,
        wind_create_board_id_response_file,
        wind_info_ride_id_started_response_file,
        wind_info_ride_id_locked_response_file,
        response_status_code,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/boardRides')
    def _mock_wind_boards_create_ride_response(request):
        return load_json(wind_create_ride_response_file)

    @mockserver.json_handler('/wind/pf/v1/boards/A0000111')
    def _mock_wind_boards_id_response(request):
        return load_json(wind_create_board_id_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/cbca7e8d5b83')
    def _mock_wind_get_info_ride_id_response(request):
        # emulate delay for pooling status
        if _mock_wind_get_info_ride_id_response.times_called < 2:
            return load_json(wind_info_ride_id_locked_response_file)
        return load_json(wind_info_ride_id_started_response_file)

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/tag/evolve',
        json={'session_id': 'A0000111', 'tag_name': 'old_state_riding'},
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.status_code == response_status_code
    assert _mock_wind_boards_create_ride_response.times_called == 1
    assert _mock_wind_boards_id_response.times_called == 1
    assert _mock_wind_get_info_ride_id_response.times_called == 3


@pytest.mark.parametrize(
    [
        'wind_create_ride_response_file',
        'wind_create_board_id_response_file',
        'wind_info_ride_id_locked_response_file',
        'failed_start_ride_expected_response',
    ],
    [
        (
            'wind_create_start_ride_response.json',
            'wind_booked_board_id_response.json',
            'wind_info_ride_id_locked_response.json',
            'failed_start_ride_expected_response.json',
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.config(
    TALARIA_MISC_POLLING_SETTINGS={
        'wind_polling_status_timeout_ms': 200,
        'wind_polling_status_interval_ms': 100,
    },
)
async def test_400_response_failed_create_ride_and_cancel(
        wind_create_ride_response_file,
        wind_create_board_id_response_file,
        wind_info_ride_id_locked_response_file,
        failed_start_ride_expected_response,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/boardRides')
    def _mock_wind_boards_create_ride_response(request):
        return load_json(wind_create_ride_response_file)

    @mockserver.json_handler('/wind/pf/v1/boards/A0000111')
    def _mock_wind_boards_id_response(request):
        return load_json(wind_create_board_id_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation/cbca7e8d5b83')
    def _mock_wind_cancel_ride_response(request):
        return load_json(wind_create_board_id_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/cbca7e8d5b83')
    def _mock_wind_get_info_ride_id_response(request):
        return load_json(wind_info_ride_id_locked_response_file)

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/tag/evolve',
        json={'session_id': 'A0000111', 'tag_name': 'old_state_riding'},
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.status_code == 400
    assert response.json() == load_json(failed_start_ride_expected_response)
    assert _mock_wind_boards_create_ride_response.times_called == 1
    assert _mock_wind_cancel_ride_response.times_called == 1


async def test_401_response_create_ride(
        taxi_talaria_misc, x_latitude, x_longitude,
):
    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/tag/evolve',
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
        },
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.config(
    TALARIA_MISC_POLLING_SETTINGS={
        'wind_polling_status_timeout_ms': 5000,
        'wind_polling_status_interval_ms': 1000,
    },
)
async def test_unlock_failed(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/boardRides')
    def _mock_wind_boards_create_ride_response(request):
        return load_json('wind_create_start_ride_response.json')

    @mockserver.json_handler('/wind/pf/v1/boards/A0000111')
    def _mock_wind_boards_id_response(request):
        return load_json('wind_booked_board_id_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation/cbca7e8d5b83')
    def _mock_wind_cancel_ride_response(request):
        return load_json('wind_booked_board_id_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/cbca7e8d5b83')
    def _mock_wind_get_info_ride_id_response(request):
        response = load_json('wind_info_ride_id_started_response.json')
        response['ride']['isUnlockFailed'] = 1
        return response

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/tag/evolve',
        json={'session_id': 'A0000111', 'tag_name': 'old_state_riding'},
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.status_code == 400
    assert _mock_wind_boards_create_ride_response.times_called == 1
    assert _mock_wind_cancel_ride_response.times_called == 1
    assert _mock_wind_get_info_ride_id_response.times_called == 2
