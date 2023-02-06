import datetime
from typing import Optional

import pytest


VOUCHER = 'voucher'
PERCENT_OFF = 'percentOff'
FREE_UNLOCK = 'freeUnlock'

DEFAULT_EXPIRE_TIME = datetime.datetime.fromisoformat(
    '2022-04-15 00:00:00+00:00',
)


def build_coupon(
        coupon_id: str,
        coupon_type: str = VOUCHER,
        discount: Optional[str] = '100',
        expire_at: datetime.datetime = DEFAULT_EXPIRE_TIME,
):
    return {
        'couponId': coupon_id,
        'currency': 'ils',
        'descText': '1 free unlock for E-Scooter!',
        'discount': discount,
        'expireAt': int(expire_at.timestamp()),
        'startAt': 0,
        'title': 'Free Unlock',
        'type': coupon_type,
    }


@pytest.mark.parametrize(
    [
        'wind_board_response_file',
        'wind_riding_response_file',
        'wind_user_response_file',
        'board_riding_mock_called_time',
        'board_id_mock_called_time',
        'response_file',
    ],
    [
        (
            'wind_board_id_response.json',
            'wind_riding_id_response.json',
            'wind_get_user_no_ride_response.json',
            0,
            0,
            'sessions_current_no_ride_response.json',
        ),
        (
            'wind_board_id_without_helmet.json',
            'wind_riding_id_without_helmet_response.json',
            'wind_get_user_with_current_ride_response.json',
            1,
            1,
            'sessions_current_with_ride_without_helmet.json',
        ),
        (
            'wind_board_id_response.json',
            'wind_riding_id_response.json',
            'wind_get_user_with_current_ride_response.json',
            1,
            1,
            'sessions_current_with_ride.json',
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.config(
    TALARIA_MISC_DRIVER_LICENSE_VERIFICATION_URL='http://verification.url',
)
async def test_200_response_sessions_current(
        wind_board_response_file,
        wind_riding_response_file,
        wind_user_response_file,
        board_riding_mock_called_time,
        board_id_mock_called_time,
        response_file,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json(wind_user_response_file)

    @mockserver.json_handler(
        '/wind/pf/v1/boards/36f95a1c-1085-4e92-82bd-34a7d9a36cb1',
    )
    def _mock_wind_boards_id_response(request):
        return load_json(wind_board_response_file)

    @mockserver.json_handler('/wind/pf/v1/boardRides/7e3e6703c7cc')
    def _mock_wind_boards_rides_response(request):
        return load_json(wind_riding_response_file)

    response = await taxi_talaria_misc.get(
        '4.0/scooters/external/sessions/current',
        headers={
            'x-lat': x_latitude,
            'x-long': x_longitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )
    response_data = response.json()

    expected_response_data = load_json(response_file)
    expected_response_data['server_time'] = response_data['server_time']

    assert response.status_code == 200
    assert response_data == expected_response_data
    assert (
        _mock_wind_boards_id_response.times_called == board_id_mock_called_time
    )
    assert (
        _mock_wind_boards_rides_response.times_called
        == board_riding_mock_called_time
    )
    assert _mock_wind_pf_user.times_called == 1


async def test_401_response_sessions_current(
        taxi_talaria_misc, x_latitude, x_longitude,
):
    response = await taxi_talaria_misc.get(
        '4.0/scooters/external/sessions/current',
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
        },
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.parametrize(
    'coupons,expected_coupons,expected_offer_promo_title',
    [
        pytest.param(None, [], None, id='coupons_are_missing'),
        pytest.param([], [], None, id='coupons_are_missing_too'),
        pytest.param(
            [build_coupon(coupon_id='id')],
            [
                {
                    'expire_at': '2022-04-15T00:00:00+00:00',
                    'id': 'id',
                    'start_at': '1970-01-01T00:00:00+00:00',
                    'subtitle': {
                        'items': [
                            {'text': 'Expire ', 'type': 'text'},
                            {'text': '03:00, Apr 15, 2022', 'type': 'text'},
                        ],
                    },
                    'title': {
                        'items': [
                            {'text': '1 $SIGN$$CURRENCY$', 'type': 'text'},
                            {'text': ' discount', 'type': 'text'},
                        ],
                    },
                    'type': 'voucher',
                },
            ],
            {
                'items': [
                    {'text': '1 $SIGN$$CURRENCY$', 'type': 'text'},
                    {'text': ' discount', 'type': 'text'},
                ],
            },
            id=VOUCHER,
        ),
        pytest.param(
            [
                build_coupon(
                    coupon_id='id', coupon_type=PERCENT_OFF, discount='20',
                ),
            ],
            [
                {
                    'expire_at': '2022-04-15T00:00:00+00:00',
                    'id': 'id',
                    'start_at': '1970-01-01T00:00:00+00:00',
                    'title': {
                        'items': [
                            {'text': '20', 'type': 'text'},
                            {'text': '% discount', 'type': 'text'},
                        ],
                    },
                    'type': 'percent_off',
                },
            ],
            {
                'items': [
                    {'text': '20', 'type': 'text'},
                    {'text': '% discount', 'type': 'text'},
                ],
            },
            id=PERCENT_OFF,
        ),
        pytest.param(
            [build_coupon(coupon_id='id', coupon_type=FREE_UNLOCK)],
            [
                {
                    'expire_at': '2022-04-15T00:00:00+00:00',
                    'id': 'id',
                    'start_at': '1970-01-01T00:00:00+00:00',
                    'title': {
                        'items': [{'text': 'Free unlock', 'type': 'text'}],
                    },
                    'type': 'free_unlock',
                },
            ],
            {'items': [{'text': 'Free unlock', 'type': 'text'}]},
            id=FREE_UNLOCK,
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'talaria.coupons.voucher.title': {
            'en': '%(voucher_discount)s discount',
        },
        'talaria.coupons.voucher.subtitle': {'en': 'Expire %(expire_at)s'},
        'talaria.coupons.percent_off.title': {
            'en': '%(percent_discount)s% discount',
        },
        'talaria.coupons.free_unlock.title': {'en': 'Free unlock'},
        'talaria.coupons.offer_promo_title.voucher': {
            'en': '%(voucher_discount)s discount',
        },
        'talaria.coupons.offer_promo_title.percent_off': {
            'en': '%(percent_discount)s% discount',
        },
        'talaria.coupons.offer_promo_title.free_unlock': {'en': 'Free unlock'},
        'talaria.coupons.offer_promo_title.common': {
            'en': 'You will get discount',
        },
    },
)
@pytest.mark.config(
    TALARIA_MISC_DRIVER_LICENSE_VERIFICATION_URL='http://verification.url',
)
@pytest.mark.now('2022-04-05T00:00:00.000000+0000')
async def test_discounts(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
        coupons,
        expected_coupons,
        expected_offer_promo_title,
):
    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        json = load_json('wind_get_user_no_ride_response.json')
        json['user']['coupons'] = coupons
        return json

    response = await taxi_talaria_misc.get(
        '4.0/scooters/external/sessions/current',
        headers={
            'x-lat': x_latitude,
            'x-long': x_longitude,
            'x-yataxi-scooters-tag': 'wind',
            'timezone-offset': '10800',
            **default_pa_headers('123'),
        },
    )
    response_data = response.json()
    assert response_data['discounts']['coupons'] == expected_coupons
    if expected_offer_promo_title:
        assert (
            response_data['discounts']['offer_promo_title']
            == expected_offer_promo_title
        )
    else:
        assert 'offer_promo_title' not in response_data['discounts']


@pytest.mark.parametrize(
    'card_should_be_migrated',
    [
        pytest.param(False, id='no_cards_migration_exp'),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='config3_talaria_wind_cards_migration_disabled.json',  # noqa: E501
                )
            ),
            id='cards_migration_exp_disabled',
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='config3_talaria_wind_cards_migration_enabled.json',  # noqa: E501
                ),
                pytest.mark.pgsql(
                    'talaria_misc', files=['users_with_card_migrated_at.sql'],
                ),
            ),
            id='user_card_is_already_migrated',
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='config3_talaria_wind_cards_migration_enabled.json',  # noqa: E501
                ),
                pytest.mark.pgsql(
                    'talaria_misc', files=['users_no_card_migrated_at.sql'],
                ),
            ),
            id='user_card_should_be_migrated',
        ),
    ],
)
@pytest.mark.config(
    TALARIA_MISC_DRIVER_LICENSE_VERIFICATION_URL='http://verification.url',
)
async def test_cards_migration(
        taxi_talaria_misc,
        mockserver,
        stq,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
        card_should_be_migrated,
):
    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_no_ride_response.json')

    response = await taxi_talaria_misc.get(
        '4.0/scooters/external/sessions/current',
        headers={
            'x-lat': x_latitude,
            'x-long': x_longitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers(),
        },
    )

    assert response.status_code == 200
    if card_should_be_migrated:
        assert stq.talaria_payments_transfer_wind_cards.times_called == 1
        stq_args = stq.talaria_payments_transfer_wind_cards.next_call()
        assert stq_args['id'] == 'wind_user_id'
        assert stq_args['kwargs']['users'] == [
            {
                'login_id': 'login_id',
                'yandex_uid': 'yandex_uid',
                'wind_user_id': 'wind_user_id',
            },
        ]
    else:
        assert stq.talaria_payments_transfer_wind_cards.times_called == 0


@pytest.mark.experiments3(filename='config3_talaria_debts_settings.json')
@pytest.mark.parametrize(
    'debt_status,balance',
    [
        pytest.param('no_funds', -100, id='debt_without_payment'),
        pytest.param(
            'waiting',
            -100,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_pending_debts.sql'],
                ),
            ),
            id='debt_with_panding_payment',
        ),
        pytest.param(
            'no_funds',
            -100,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_failed_debts.sql'],
                ),
            ),
            id='debt_with_failed_payment',
        ),
        pytest.param(None, -5, id='too_small_debt'),
    ],
)
async def test_debts(
        taxi_talaria_misc,
        mockserver,
        wind_user_auth_mock,
        load_json,
        x_latitude,
        x_longitude,
        default_pa_headers,
        debt_status,
        balance,
):
    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        resp = load_json('wind_get_user_no_ride_response.json')
        if debt_status:
            resp['user']['balance'] = balance
        return resp

    response = await taxi_talaria_misc.get(
        '4.0/scooters/external/sessions/current',
        headers={
            'x-lat': x_latitude,
            'x-long': x_longitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    if debt_status:
        debt = data['user']['billing']['debt']
        assert debt['status'] == debt_status
        assert debt['amount'] == abs(balance)
    else:
        assert 'billing' not in data['user']


@pytest.mark.experiments3(
    filename='config3_talaria_skip_book_screen_enabled.json',
)
@pytest.mark.config(
    TALARIA_MISC_DRIVER_LICENSE_VERIFICATION_URL='http://verification.url',
)
async def test_sessions_current_book_skip_enabled(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_with_current_ride_response.json')

    @mockserver.json_handler(
        '/wind/pf/v1/boards/36f95a1c-1085-4e92-82bd-34a7d9a36cb1',
    )
    def _mock_wind_boards_id_response(request):
        return load_json('wind_board_id_response.json')

    @mockserver.json_handler('/wind/pf/v1/boardRides/7e3e6703c7cc')
    def _mock_wind_boards_rides_response(request):
        return load_json('wind_riding_id_response.json')

    response = await taxi_talaria_misc.get(
        '4.0/scooters/external/sessions/current',
        headers={
            'x-lat': x_latitude,
            'x-long': x_longitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )
    response_data = response.json()

    expected_response_data = load_json('sessions_current_with_ride.json')
    expected_response_data['server_time'] = response_data['server_time']
    expected_response_data['sessions'][0]['segment']['session'][
        'current_performing'
    ] = 'old_state_riding'

    assert response.status_code == 200
    assert response_data == expected_response_data
    assert _mock_wind_boards_id_response.times_called == 1
    assert _mock_wind_boards_rides_response.times_called == 1
    assert _mock_wind_pf_user.times_called == 1
