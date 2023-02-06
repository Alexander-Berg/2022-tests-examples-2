import pytest


@pytest.mark.parametrize(
    [
        'wind_cancel_booking_response_file',
        'wind_booked_board_response_file',
        'wind_board_id_response_file',
        'response_file',
        'response_status_code',
    ],
    [
        (
            'wind_cancel_booking_response.json',
            'wind_booked_board_response.json',
            'wind_board_id_with_book_response.json',
            'succes_tag_evolve_response.json',
            200,
        ),
        (
            'wind_error_canceling_booking.json',
            'wind_booked_board_response.json',
            'wind_board_id_with_book_response.json',
            'failed_tag_evolve_response.json',
            400,
        ),
    ],
)
@pytest.mark.servicetest
async def test_200_response_cancel_booking(
        wind_cancel_booking_response_file,
        wind_booked_board_response_file,
        wind_board_id_response_file,
        response_file,
        taxi_talaria_misc,
        response_status_code,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation/d3046c5e335a')
    def _mock_wind_boards_cancel_reservation_response(request):
        return load_json(wind_cancel_booking_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/d3046c5e335a')
    def _mock_wind_get_info_ride_id_response(request):
        return load_json(wind_booked_board_response_file)

    @mockserver.json_handler('/wind/pf/v1/boards/A0000111')
    def _mock_wind_get_board_id_response(request):
        return load_json(wind_board_id_response_file)

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/tag/evolve',
        json={'session_id': 'A0000111', 'tag_name': 'old_state_reservation'},
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.json() == load_json(response_file)
    assert response.status_code == response_status_code
    assert _mock_wind_boards_cancel_reservation_response.times_called == 1
    assert _mock_wind_get_info_ride_id_response.times_called == 1
    assert _mock_wind_get_board_id_response.times_called == 1


async def test_401_response_cancel_booking(
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
