import typing

import pytest


class MyTestCase(typing.NamedTuple):
    wind_reservation_response_file: str = 'wind_reservation_response.json'
    wind_reservation_error_result_code: typing.Optional[int] = None
    wind_unauthorized_error: bool = False
    has_mobile_paymethod_id: bool = False
    payment_method: typing.Dict = {
        'type': 'card',
        'id': 'card-xebc57db7ebf81bdb07c8d5d2',
    }
    app_name: str = 'iphone'
    response_status_code: int = 200


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(), id='success_card_payment_method'),
        pytest.param(
            MyTestCase(
                has_mobile_paymethod_id=True,
                payment_method={'type': 'applepay', 'id': 'token'},
                app_name='iphone',
            ),
            id='success_applepay_payment_method',
        ),
        pytest.param(
            MyTestCase(
                has_mobile_paymethod_id=True,
                payment_method={'type': 'googlepay', 'id': 'token'},
                app_name='android',
            ),
            id='success_googlepay_payment_method',
        ),
        pytest.param(
            MyTestCase(wind_unauthorized_error=True),
            id='wind_unauthorized_error',
        ),
        pytest.param(
            MyTestCase(
                wind_reservation_error_result_code=-215,
                response_status_code=400,
            ),
            id='wind_reservation_error_board_is_reserved',
        ),
        pytest.param(
            MyTestCase(
                wind_reservation_error_result_code=-211,
                response_status_code=400,
            ),
            id='wind_reservation_error_board_is_in_riding',
        ),
        pytest.param(
            MyTestCase(
                wind_reservation_error_result_code=-305,
                response_status_code=400,
            ),
            id='wind_reservation_error_negative_user_balance',
        ),
    ],
)
@pytest.mark.servicetest
async def test_response_offers_book(
        case,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    board_id = '4c963198-3e5f-49c3-85fe-e0a690f15f69'

    @mockserver.json_handler('/wind-pd/pf/v1/user')
    def _mock_wind_get_user(request):
        return load_json('wind_pd_pf_v1_user_response_default.json')[0]

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_no_ride_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation')
    def _mock_wind_boards_reservation(request):
        assert request.json == {
            'boardId': board_id,
            'paymentData': {
                'yandex_uid': 'yandex_uid',
                'payment_method': case.payment_method,
                'antifraud_data': {
                    'yandex_login_id': 'login_id',
                    'user_ip': '1.2.3.4',
                },
            },
        }

        if (
                case.wind_unauthorized_error
                and _mock_wind_boards_reservation.times_called == 0
        ):
            return mockserver.make_response(status=401)

        resp = load_json(case.wind_reservation_response_file)
        if case.wind_reservation_error_result_code:
            resp['result'] = case.wind_reservation_error_result_code
        return resp

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        # PUT
        if case.has_mobile_paymethod_id:
            assert request.query == {'service': 'scooters'}
            assert request.json == {
                'flows': [
                    {
                        'flow_type': 'order',
                        'payment_method': case.payment_method,
                    },
                ],
            }
            return mockserver.make_response(status=200)

        # GET
        assert request.query == {'service': 'scooters', 'flow': 'order'}
        return {
            'flows': [
                {'flow_type': 'ride', 'payment_method': case.payment_method},
            ],
        }

    @mockserver.json_handler(
        (
            '/stq-agent/queues/api/add/'
            'talaria_payments_notify_billing_about_ride'
        ),
    )
    def _mock_stq(request):
        assert request.json['task_id'] == 'c3d24aadf038'
        kwargs = request.json['kwargs']
        kwargs.pop('log_extra')
        assert kwargs == {
            'yandex_uid': 'yandex_uid',
            'personal_phone_id': '123',
            'wind_ride_id': 'c3d24aadf038',
        }
        return {}

    req_body = {'offer_id': board_id}
    if case.has_mobile_paymethod_id:
        req_body['mobile_paymethod_id'] = case.payment_method['id']

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/offers/book',
        json=req_body,
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123', app_name=case.app_name),
        },
    )

    assert response.status_code == case.response_status_code
    assert _mock_last_payment_methods.times_called == 1

    if case.wind_reservation_error_result_code:
        assert _mock_stq.times_called == 0
    else:
        assert _mock_stq.times_called == 1

    if case.wind_unauthorized_error:
        assert _mock_wind_get_user.times_called == 2
        assert _mock_wind_boards_reservation.times_called == 2
    else:
        assert _mock_wind_get_user.times_called == 1
        assert _mock_wind_boards_reservation.times_called == 1


@pytest.mark.experiments3(
    filename='config3_talaria_skip_book_screen_enabled.json',
)
async def test_offers_book_skip_enabled(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    board_id = '4c963198-3e5f-49c3-85fe-e0a690f15f69'

    @mockserver.json_handler('/wind-pd/pf/v1/user')
    def _mock_wind_get_user(request):
        return load_json('wind_pd_pf_v1_user_response_default.json')[0]

    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation')
    def _mock_wind_boards_reservation(request):
        assert request.json == {
            'boardId': board_id,
            'paymentData': {
                'yandex_uid': 'yandex_uid',
                'payment_method': {
                    'type': 'card',
                    'id': 'card-xebc57db7ebf81bdb07c8d5d2',
                },
                'antifraud_data': {
                    'yandex_login_id': 'login_id',
                    'user_ip': '1.2.3.4',
                },
            },
        }

        return load_json('wind_reservation_response.json')

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        assert request.query == {'service': 'scooters', 'flow': 'order'}
        return {
            'flows': [
                {
                    'flow_type': 'ride',
                    'payment_method': {
                        'type': 'card',
                        'id': 'card-xebc57db7ebf81bdb07c8d5d2',
                    },
                },
            ],
        }

    @mockserver.json_handler(f'/wind/pf/v1/boards/{board_id}')
    def _mock_wind_boards_id_response(request):
        return load_json('wind_booked_board_id_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides')
    def _mock_wind_boards_create_ride_response(request):
        return load_json('wind_create_start_ride_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/c3d24aadf038')
    def _mock_wind_get_info_ride_id_response(request):
        return load_json('wind_info_ride_id_started_response.json')

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_no_ride_response.json')

    req_body = {'offer_id': board_id}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/offers/book',
        json=req_body,
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.status_code == 200
    assert _mock_last_payment_methods.times_called == 1
    assert _mock_wind_get_user.times_called == 1
    assert _mock_wind_boards_reservation.times_called == 1
    assert _mock_wind_boards_id_response.times_called == 1
    assert _mock_wind_boards_create_ride_response.times_called == 1
    assert _mock_wind_get_info_ride_id_response.times_called >= 1


async def test_401_response_offers_book(
        taxi_talaria_misc, x_latitude, x_longitude,
):
    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/offers/book',
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
        },
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.parametrize(
    'has_coupon, stq_times_call',
    [
        pytest.param(False, 1, id='coupon_apply'),
        pytest.param(True, 0, id='user_has_coupon'),
        pytest.param(
            False,
            0,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_has_auto_promocodes.sql'],
                ),
            ),
            id='coupon_limit_exited',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_talaria_auto_coupon_apply.json')
async def test_auto_promocode(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
        has_coupon,
        stq_times_call,
):
    board_id = '4c963198-3e5f-49c3-85fe-e0a690f15f69'

    @mockserver.json_handler('/wind-pd/pf/v1/user')
    def _mock_wind_get_user(request):
        return load_json('wind_pd_pf_v1_user_response_default.json')[0]

    @mockserver.json_handler('/wind/pf/v1/boardRides/reservation')
    def _mock_wind_boards_reservation(request):
        assert request.json == {
            'boardId': board_id,
            'paymentData': {
                'yandex_uid': 'yandex_uid',
                'payment_method': {
                    'type': 'card',
                    'id': 'card-xebc57db7ebf81bdb07c8d5d2',
                },
                'antifraud_data': {
                    'yandex_login_id': 'login_id',
                    'user_ip': '1.2.3.4',
                },
            },
        }

        return load_json('wind_reservation_response.json')

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        assert request.query == {'service': 'scooters', 'flow': 'order'}
        return {
            'flows': [
                {
                    'flow_type': 'ride',
                    'payment_method': {
                        'type': 'card',
                        'id': 'card-xebc57db7ebf81bdb07c8d5d2',
                    },
                },
            ],
        }

    @mockserver.json_handler(f'/wind/pf/v1/boards/{board_id}')
    def _mock_wind_boards_id_response(request):
        return load_json('wind_booked_board_id_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides')
    def _mock_wind_boards_create_ride_response(request):
        return load_json('wind_create_start_ride_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/c3d24aadf038')
    def _mock_wind_get_info_ride_id_response(request):
        return load_json('wind_info_ride_id_started_response.json')

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        response = load_json('wind_get_user_no_ride_response.json')
        if has_coupon:
            response['user']['coupons'] = [
                {
                    'couponId': 'coupon_id',
                    'currency': 'ils',
                    'descText': '1 free unlock for E-Scooter!',
                    'discount': '100',
                    'expireAt': 101203123,
                    'startAt': 0,
                    'title': 'Free Unlock',
                    'type': 'freeUnlock',
                },
            ]
        return response

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/talaria_misc_auto_promocode_apply',
    )
    def _mock_auto_promocode_apply(request):
        return {}

    req_body = {'offer_id': board_id}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/api/yandex/offers/book',
        json=req_body,
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    assert response.status_code == 200
    assert _mock_auto_promocode_apply.times_called == stq_times_call
