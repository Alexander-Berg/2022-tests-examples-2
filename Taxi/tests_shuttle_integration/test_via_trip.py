import datetime

import pytest


TEST_DETAILS_RESPONSE = {
    'trip_id': 'trip_id_0',
    'trip_details': {
        'trip_status': 'FINISHED',
        'pickup': {'lat': 60.002, 'lng': 30.002},
        'dropoff': {'lat': 60.008, 'lng': 30.008},
        'pickup_eta': 1652787004,
        'dropoff_eta': 1652787104,
        'vehicle_info': {
            'license_plate': 'A666MP77',
            'color': 'black',
            'model': 'a1',
            'vfh_id': '2331',
            'current_location': {'lat': 60.001, 'lng': 30.001},
        },
        'driver_info': {
            'id': 'dbid0_uuid0',
            'first_name': 'ivan',
            'last_name': 'ivanovich',
        },
    },
}

TEST_BOOK_RESPONSE = {'trip_id': 'trip_id_1', 'trip_status': 'ASSIGNED'}

TEST_CANCEL_RESPONSE = {'trip_id': 'trip_id_2', 'trip_status': 'CANCELED'}

TEST_BOARD_RESPONSE: dict = {}

TEST_REQUEST_RESPONSE = {
    'trips': [
        {
            'trip_id': 'trip_id_4',
            'trip_type': 'shared',
            'pickup': {'lat': 55.734452, 'lng': 37.643129},
            'pickup_eta': 1652786951,
            'pickup_distance': 10,
            'pickup_walking_time_sec': 30,
            'dropoff': {'lat': 55.733419, 'lng': 37.641628},
            'dropoff_eta': 1652787001,
            'cost': 35 * 2,
        },
    ],
}

MT_TST = 'mt_tst'
MT_TST_API_KEY = 'mt_tst_api_key'

MOCK_NOW = datetime.datetime(2022, 5, 17, 11, 28, 21)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'method, url, request_body, expected_response, expected_mock_call',
    [
        (
            'get',
            '/via-trip/v1/trips/details?trip_id=trip_id_0',
            None,
            TEST_DETAILS_RESPONSE,
            'booking_information',
        ),
        (
            'post',
            '/via-trip/v1/trips/book',
            {'trip_id': 'trip_id_1'},
            TEST_BOOK_RESPONSE,
            'booking_create',
        ),
        (
            'post',
            '/via-trip/v1/trips/cancel',
            {'trip_id': 'trip_id_2'},
            TEST_CANCEL_RESPONSE,
            'booking_cancel',
        ),
        (
            'post',
            '/via-trip/v1/trips/board',
            {'trip_id': 'trip_id_3'},
            TEST_BOARD_RESPONSE,
            'confirm_boarding',
        ),
        (
            'post',
            '/via-trip/v1/trips/request',
            {
                'origin': {'lat': 37.25, 'lng': 50.49},
                'destination': {'lat': 37.25, 'lng': 50.49},
                'passenger_info': {
                    'first_name': '111111',
                    'last_name': 'surname',
                    'passenger_id': 'd1cf6a92-26ef-11ea-979b-02426df27c46',
                    'phone_number': '+99000',
                },
                'passenger_count': 2,
                'trip_properties': ['trip_properties_0'],
            },
            TEST_REQUEST_RESPONSE,
            'trip_planner_search',
        ),
    ],
)
async def test_via_trip(
        taxi_shuttle_integration,
        mockserver,
        method,
        url,
        request_body,
        expected_response,
        expected_mock_call,
):
    shuttle_control_prefix = '/shuttle-control/internal/shuttle-control/v1'

    mock_call = None

    @mockserver.json_handler(
        shuttle_control_prefix + '/service/booking/information',
    )
    def _mock_booking_information(request):
        nonlocal mock_call
        assert mock_call is None
        mock_call = 'booking_information'

        assert dict(request.args) == {
            'booking_id': 'trip_id_0',
            'service_id': MT_TST,
        }
        return {
            'booking_id': 'trip_id_0',
            'status': {'status': 'finished'},
            'shuttle': {
                'shuttle_id': 'Pmp80rQ23L4wZYxd',
                'vehicle_info': {
                    'car_number': 'A666MP77',
                    'color': 'black',
                    'model': 'a1',
                    'vfh_id': '2331',
                },
                'driver_info': {
                    'park_id': 'dbid0',
                    'driver_profile_id': 'uuid0',
                    'first_name': 'ivan',
                    'last_name': 'ivanovich',
                },
                'position': [30.001, 60.001],
                'is_at_stop': False,
            },
            'route': {
                'route_id': 'gkZxnYQ73QGqrKyz',
                'pickup_stop': {
                    'stop_id': 'stop__123',
                    'position': [30.002, 60.002],
                },
                'dropoff_stop': {
                    'stop_id': 'stop__5',
                    'position': [30.008, 60.008],
                },
            },
            'pickup_eta': {
                'time_seconds': 101,
                'distance_meters': 50,
                'timestamp': (
                    MOCK_NOW + datetime.timedelta(seconds=103)
                ).isoformat() + '+0000',
            },
            'dropoff_eta': {
                'time_seconds': 201,
                'distance_meters': 60,
                'timestamp': (
                    MOCK_NOW + datetime.timedelta(seconds=203)
                ).isoformat() + '+0000',
            },
        }

    @mockserver.json_handler(
        shuttle_control_prefix + '/service/booking/create',
    )
    def _mock_booking_create(request):
        nonlocal mock_call
        assert mock_call is None
        mock_call = 'booking_create'

        assert dict(request.args) == {'service_id': MT_TST}
        assert request.json == {'offer_id': 'trip_id_1'}
        return {'booking_id': 'trip_id_1', 'status': {'status': 'created'}}

    @mockserver.json_handler(
        shuttle_control_prefix + '/service/booking/cancel',
    )
    def _mock_booking_cancel(request):
        nonlocal mock_call
        assert mock_call is None
        mock_call = 'booking_cancel'

        assert dict(request.args) == {'service_id': MT_TST}
        assert request.json == {'booking_id': 'trip_id_2'}
        return {
            'booking_id': 'trip_id_2',
            'status': {
                'status': 'cancelled',
                'cancel_reason': 'by_driver_stop',
            },
        }

    @mockserver.json_handler(
        shuttle_control_prefix + '/service/confirm-boarding',
    )
    def _mock_confirm_boarding(request):
        nonlocal mock_call
        assert mock_call is None
        mock_call = 'confirm_boarding'

        assert dict(request.args) == {'service_id': MT_TST}
        assert request.json == {'booking_id': 'trip_id_3'}
        return {}

    @mockserver.json_handler(shuttle_control_prefix + '/trip-planner/search')
    def _mock_trip_planner_search(request):
        nonlocal mock_call
        assert mock_call is None
        mock_call = 'trip_planner_search'

        assert dict(request.args) == {'service_id': MT_TST}
        assert request.json == {
            'external_confirmation_code': '1111',
            'external_passenger_id': 'd1cf6a92-26ef-11ea-979b-02426df27c46',
            'route': [[50.49, 37.25], [50.49, 37.25]],
            'passengers_count': 2,
        }
        return {
            'service_available': True,
            'trips': [
                {
                    'id': 'trip_id_4',
                    'price': {
                        'per_seat': {'amount': 35, 'currency': 'RUB'},
                        'total': {'amount': 35 * 2, 'currency': 'RUB'},
                    },
                    'shuttle': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'pickup_eta': {
                            'distance_meters': 200,
                            'time_seconds': 50,
                        },
                    },
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'segment': {
                            'pickup': {
                                'id': 'stop__2',
                                'position': [37.643129, 55.734452],
                            },
                            'dropoff': {
                                'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                                'position': [37.641628, 55.733419],
                            },
                            'route_info': {
                                'distance_meters': 200,
                                'time_seconds': 50,
                            },
                        },
                    },
                    'walk_to_pickup': {
                        'distance_meters': 10,
                        'time_seconds': 30,
                    },
                    'walk_from_dropoff': {
                        'distance_meters': 40,
                        'time_seconds': 60,
                    },
                },
            ],
        }

    headers = {'X-API-Key': MT_TST_API_KEY}
    if method == 'get':
        response = await taxi_shuttle_integration.get(url, headers=headers)
    else:  # method == 'post'
        response = await taxi_shuttle_integration.post(
            url, request_body, headers=headers,
        )

    assert response.status_code == 200
    assert response.json() == expected_response

    assert mock_call == expected_mock_call


@pytest.mark.parametrize(
    'method, url, body_or_get_params, client_url_postfix, error_code',
    [
        (
            'post',
            '/via-trip/v1/trips/board',
            {'trip_id': 'trip_id_0'},
            '/service/confirm-boarding',
            404,
        ),
        (
            'post',
            '/via-trip/v1/trips/board',
            {'trip_id': 'trip_id_0'},
            '/service/confirm-boarding',
            409,
        ),
        (
            'get',
            '/via-trip/v1/trips/detail',
            '?trip_id=trip_id_0',
            '/service/booking/information',
            404,
        ),
    ],
)
async def test_via_trip_client_error(
        taxi_shuttle_integration,
        mockserver,
        method,
        url,
        body_or_get_params,
        client_url_postfix,
        error_code,
):
    shuttle_control_prefix = '/shuttle-control/internal/shuttle-control/v1'

    @mockserver.json_handler(shuttle_control_prefix + client_url_postfix)
    def _mock_client(request):
        return mockserver.make_response(
            json={'code': str(error_code), 'message': 'error'},
            status=error_code,
        )

    headers = {'X-API-Key': MT_TST_API_KEY}
    if method == 'get':
        response = await taxi_shuttle_integration.get(
            url + (body_or_get_params or ''), headers=headers,
        )
    else:  # method == 'post'
        response = await taxi_shuttle_integration.post(
            url, body_or_get_params or {}, headers=headers,
        )
    assert response.status_code == error_code
