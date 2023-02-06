import typing

import pytest


class MyTestCase(typing.NamedTuple):
    wind_booked_board_id_response_file: str = 'wind_booked_board_id_response.json'  # noqa: E501
    wind_info_ride_id_riding_response_file: str = 'wind_info_ride_id_riding_response.json'  # noqa: E501
    wind_info_ride_id_finished_response_file: str = 'wind_info_ride_id_finished_response.json'  # noqa: E501
    wind_update_ride_info_response_file: str = 'wind_info_ride_id_finished_response.json'  # noqa: E501
    wind_update_ride_info_error_result_code: typing.Optional[int] = None
    wait_for_status_after_finish_times_called: int = 2
    update_helmet_status_times_called: int = 0
    response_file: typing.Optional[str] = None
    response_status_code: int = 200


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(), id='200_response_finish_ride'),
        pytest.param(
            MyTestCase(
                wind_info_ride_id_riding_response_file='wind_ride_id_response_helmet_needs_to_be_returned.json',  # noqa: E501
                response_file='response_helmet_needs_to_be_returned.json',
                response_status_code=400,
            ),
            id='400_response_finish_ride_helmet_needs_to_be_returned',
        ),
        pytest.param(
            MyTestCase(
                wind_info_ride_id_riding_response_file='wind_ride_id_response_helmet_needs_to_be_returned.json',  # noqa: E501
                update_helmet_status_times_called=1,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='config3_talaria_finish_ride_settings.json',
                )
            ),
            id='200_response_ok_update_helmet_status',
        ),
        pytest.param(
            MyTestCase(
                wind_update_ride_info_error_result_code=-310,
                response_file='response_parking_error.json',
                response_status_code=400,
            ),
            id='400_response_finish_ride_parking_error_one',
        ),
        pytest.param(
            MyTestCase(
                wind_update_ride_info_error_result_code=-306,
                response_file='response_parking_error.json',
                response_status_code=400,
            ),
            id='400_response_finish_ride_parking_error_two',
        ),
        pytest.param(
            MyTestCase(
                wait_for_status_after_finish_times_called=20,
                response_status_code=500,
            ),
            id='500_response_failed_finish_ride_and_cancel',
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
async def test_finsh_ride(
        case,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/boards/A0000111')
    def _mock_wind_boards_id_response(request):
        return load_json(case.wind_booked_board_id_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation/A0000111')
    def _mock_wind_cancel_ride_response(request):
        return load_json(case.wind_booked_board_id_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/cbca7e8d5b83')
    def _mock_wind_get_info_ride_id_response(request):
        if request.method == 'GET':
            # emulate delay for polling status
            if (
                    _mock_wind_get_info_ride_id_response.times_called
                    < case.wait_for_status_after_finish_times_called
            ):
                return load_json(case.wind_info_ride_id_riding_response_file)
            return load_json(case.wind_info_ride_id_finished_response_file)
        if request.method == 'PUT':
            resp = load_json(case.wind_update_ride_info_response_file)
            if case.wind_update_ride_info_error_result_code:
                resp['result'] = case.wind_update_ride_info_error_result_code
            return resp
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/wind/pf/v1/boardRides/cbca7e8d5b83/helmet')
    def _mock_wind_update_helmet_status(request):
        return load_json(case.wind_info_ride_id_riding_response_file)

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
    assert response.status_code == case.response_status_code
    if case.response_file:
        assert response.json() == load_json(case.response_file)
    assert _mock_wind_boards_id_response.times_called == 1
    assert _mock_wind_get_info_ride_id_response.times_called > 0
    assert _mock_wind_cancel_ride_response.times_called == 0
    assert (
        _mock_wind_update_helmet_status.times_called
        == case.update_helmet_status_times_called
    )


async def test_401_response_finsh_ride(
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
