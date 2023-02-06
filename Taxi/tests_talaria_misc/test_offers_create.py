import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple

import pytest

FREE_PASS_TYPE = 0
SUPER_PASS_TYPE = 1


DEFAULT_START_TIME = datetime.datetime.fromisoformat(
    '2022-04-05 00:00:00+00:00',
)


def make_free_pass_config(
        pass_id: str,
        life_time_sec: int = 3600,
        ride_time_sec: int = 3600,
        pass_type: int = FREE_PASS_TYPE,
        is_free_trial: int = 0,
        price: int = 1000,
):
    return {
        'freePassId': pass_id,
        'periodInSeconds': life_time_sec,
        'price': str(price),
        'currency': 'ils',
        'isForTargetUser': 0,
        'originalPrice': 897000,
        'unlockingCents': 0,
        'maxRidingTimeSeconds': ride_time_sec,
        'limitPerDay': 3,
        'totalLimit': 3,
        'region': 'il',
        'city': -1,
        'totalRidingTimeSeconds': 0,
        'type': pass_type,
        'isFreeTrial': is_free_trial,
        'reservationInSeconds': 300,
        'trialingTimeInSecond': 604800,
        'tieredPricing': [
            {'percentOff': 0, 'ridingTime': 15},
            {'percentOff': 20, 'ridingTime': 120},
        ],
    }


def make_pass(
        pass_id: str,
        start_at: datetime.datetime,
        usage_ride_time_sec: int = 0,
        life_time_sec: int = 3600,
        ride_time_sec: int = 3600,
        pass_type: int = FREE_PASS_TYPE,
        is_free_trial: int = 0,
        price: int = 1000,
        has_subscription: int = 0,
):
    timestamp_start_at = start_at.timestamp()
    return {
        'id': 'eb981b19-3259-40d1-8b79-184d10d22e28',
        'expireAt': timestamp_start_at + life_time_sec,
        'isActive': 1,
        'isExceededLimit': 0,
        'startAt': timestamp_start_at,
        'hasFreeTrial': 0,
        'freePassId': 'sf_1_hour',
        'periodInSeconds': life_time_sec,
        'price': str(price),
        'currency': 'ils',
        'isForTargetUser': 0,
        'originalPrice': 897000,
        'unlockingCents': 100,
        'maxRidingTimeSeconds': ride_time_sec,
        'limitPerDay': 3,
        'totalLimit': 3,
        'region': 'il',
        'city': -1,
        'totalRidingTimeSeconds': ride_time_sec,
        'totalUsageTimeSeconds': usage_ride_time_sec,
        'type': pass_type,
        'isFreeTrial': is_free_trial,
        'isAutoReload': has_subscription,
        'reservationInSeconds': 300,
        'trialingTimeInSecond': 604800,
        'tieredPricing': [
            {'percentOff': 0, 'ridingTime': 15},
            {'percentOff': 20, 'ridingTime': 120},
        ],
    }


def make_free_passes_response(
        result: int = 0,
        free_passes: List[Dict[str, Any]] = None,
        current_free_pass: Dict[str, Any] = None,
        super_passes: List[Dict[str, Any]] = None,
        current_super_pass: Dict[str, Any] = None,
        is_shown_free_trial_pass: int = 0,
):
    return {
        'result': result,
        'items': free_passes if free_passes else [],
        'freePass': current_free_pass,
        'superItems': super_passes if super_passes else [],
        'premiumFreePass': current_super_pass,
        'isShownFreeTrialPass': is_shown_free_trial_pass,
    }


class MyTestCase(NamedTuple):
    wind_board_response_file: str = 'wind_board_id_response.json'
    response_file: str = 'offers_create_response.json'
    payment_methods: List[Dict] = [
        {'account_id': 'card', 'card': 'card-xebc57db7ebf81bdb07c8d5d2'},
    ]
    last_payment_methods_error: bool = False


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(), id='success_card_payment_method'),
        pytest.param(
            MyTestCase(payment_methods=[{'account_id': 'mobile_payment'}]),
            id='success_mobile_payment_method',
        ),
        pytest.param(
            MyTestCase(payment_methods=[]), id='no_payment_methods_ok',
        ),
        pytest.param(MyTestCase(last_payment_methods_error=True), id='error'),
    ],
)
@pytest.mark.servicetest
async def test_200_response_offers_create(
        case,
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler(
        '/wind/pf/v1/boards/36f95a1c-1085-4e92-82bd-34a7d9a36cb1',
    )
    def _mock_wind_boards_id_response(request):
        return load_json(case.wind_board_response_file)

    @mockserver.json_handler('/wind/pf/v1/freePasses')
    def _mock_wind_free_passes(request):
        return {}

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        assert request.query == {'service': 'scooters'}
        assert request.json == {
            'flows': [
                {
                    'flow_type': 'order',
                    'payment_method': {
                        'type': 'card',
                        'id': 'card-xebc57db7ebf81bdb07c8d5d2',
                    },
                },
            ],
        }
        if case.last_payment_methods_error:
            return mockserver.make_response(status=400, json={})
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_no_ride_response.json')

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/offers/create',
        json={
            'vehicle_numbers': ['36f95a1c-1085-4e92-82bd-34a7d9a36cb1'],
            'insurance_type': 'standart',
            'user_position': [37.50838996967984, 55.735838906048528],
            'payment_methods': case.payment_methods,
            'destinations': [],
        },
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            **default_pa_headers('123'),
        },
    )

    if case.last_payment_methods_error:
        assert response.status_code == 500
        assert response.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }
    else:
        assert response.status_code == 200
        assert response.json() == load_json(case.response_file)
        assert _mock_wind_boards_id_response.times_called == 1

        no_or_mobile_payment = (
            not case.payment_methods
            or case.payment_methods[0]['account_id'] == 'mobile_payment'
        )
        assert (
            _mock_last_payment_methods.times_called == 0
            if no_or_mobile_payment
            else 1
        )


async def test_401_response_offers_create(
        taxi_talaria_misc, x_latitude, x_longitude,
):
    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/offers/create',
        json={
            'vehicle_numbers': ['36f95a1c-1085-4e92-82bd-34a7d9a36cb1'],
            'insurance_type': 'standart',
            'payment_methods': [
                {
                    'account_id': 'card',
                    'card': 'card-xebc57db7ebf81bdb07c8d5d2',
                },
            ],
            'destinations': [],
        },
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
        },
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.translations(
    client_messages={
        'talaria.passes.free_passes.item.tariff.title': {
            'en': '%(tariff_price)s/min',
        },
        'talaria.passes.free_passes.item.tariff.subtitle': {'en': 'Unlimited'},
        'talaria.passes.free_passes.item.tariff.purchase_subtitle': {
            'en': '%(tariff_price)s/min',
        },
        'talaria.passes.free_passes.group.title': {
            'en': '%(group_duration)sh time passes',
        },
        'talaria.passes.free_passes.item.free_pass.title': {'en': '%(price)s'},
        'talaria.passes.free_passes.item.free_pass.subtitle': {
            'en': '%(ride_duration_min)s min',
        },
        'talaria.passes.free_passes.item.free_pass.purchase_subtitle': {
            'en': '%(ride_duration_min)s min for %(price)s',
        },
        'talaria.passes.free_passes.group.required.title': {
            'en': 'Ride options',
        },
        'talaria.passes.free_passes.entrypoint.tariff.title': {
            'en': '%(tariff_price_unlock)s + %(tariff_price)s/min',
        },
        'talaria.passes.free_passes.entrypoint.tariff.subtitle': {
            'en': 'More options',
        },
        'talaria.passes.free_passes.entrypoint.free_pass.title': {
            'en': '%(ride_duration_min)s min ride',
        },
        'talaria.passes.free_passes.entrypoint.free_pass.subtitle': {
            'en': 'Valid until %(expire_at)s',
        },
        'talaria.passes.current.free_pass.title': {
            'en': '%(ride_duration_min)s min ride pass',
        },
        'talaria.passes.current.free_pass.description.riding_time_left': {
            'en': 'Ride up to %(riding_time_left_min)s minutes',
        },
        'talaria.passes.current.free_pass.description.expired_at': {
            'en': 'Use until %(full_expire_at)s',
        },
        'talaria.passes.super_passes.item.super_pass.hour.title': {
            'en': 'Hourly',
        },
        'talaria.passes.super_passes.item.super_pass.subtitle': {
            'en': 'Most popular option',
        },
        'talaria.passes.super_passes.item.super_pass.subtitle.discount': {
            'en': (
                'Save %(super_pass_discount)s'
                ' per %(super_pass_discount_period)s'
            ),
        },
        'talaria.passes.super_passes.item.super_pass.caption': {
            'en': '%(price)s',
        },
        'talaria.passes.super_passes.item.super_pass.day.title': {
            'en': 'Daily',
        },
        'talaria.passes.super_passes.item.super_pass.month.title': {
            'en': 'Month',
        },
        'talaria.passes.super_passes.item.super_pass.quarter.title': {
            'en': 'Quarter',
        },
        'talaria.passes.super_passes.item.super_pass.annual.title': {
            'en': 'Annual',
        },
        'talaria.passes.super_passes.entrypoint.has_not_active.title': {
            'en': 'Subscribe and save up to 20%',
        },
        'talaria.passes.super_passes.entrypoint.has_not_active.subtitle': {
            'en': 'Monthly and quarterly',
        },
        'talaria.passes.super_passes.entrypoint.has_active.title': {
            'en': '%(life_time_period_adjective)s subscription active',
        },
        'talaria.passes.super_passes.entrypoint.has_active.subtitle': {
            'en': 'See more',
        },
        'talaria.passes.free_passes.entrypoint.super_pass.title': {
            'en': 'Free unlock + %(tariff_price)s/min',
        },
        'talaria.passes.current.super_pass.subscription.renew_info': {
            'en': 'Renew on %(expire_at)s',
        },
        'talaria.passes.current.super_pass.subscription.cancellation_info': {
            'en': 'Your subscription will be cancelled from %(expire_at)s',
        },
        'talaria.passes.current.super_pass'
        '.description.free_reservation_time': {
            'en': 'Free %(free_reservation_time_min)s min reservation time',
        },
        'talaria.passes.current.super_pass.description.discounts': {
            'en': (
                '%(ride_discount_percent)s% off for rides '
                'longer than %(ride_discount_start_period)s min'
            ),
        },
        'talaria.passes.current.super_pass.description.free_trial': {
            'en': 'Free %(trial_period_days)s days trial',
        },
        'talaria.passes.current.super_pass.description.unlimited_lock': {
            'en': 'Free and unlimited unlock',
        },
        'talaria.passes.super_passes.item.super_pass.purchase_subtitle': {
            'en': '%(price)s / %(life_time_period)s',
        },
        'talaria.passes.free_passes.entrypoint.both_passes.title': {
            'en': '%(ride_duration_min)s min ride',
        },
        'talaria.passes.period.adjective.hour': {'en': 'Hourly'},
        'talaria.passes.current.super_pass.title': {
            'en': '%(life_time_period_adjective)s subscription',
        },
        'talaria.passes.current.super_pass.subtitle': {
            'en': '%(price)s / %(life_time_period)s',
        },
    },
)
@pytest.mark.parametrize(
    'free_pass_resp, expected_pass',
    [
        pytest.param(make_free_passes_response(), None, id='empty_resp'),
        pytest.param(
            make_free_passes_response(
                current_free_pass=make_pass('id', start_at=DEFAULT_START_TIME),
            ),
            'current_free_pass.json',
            id='curre_free_pass',
        ),
        pytest.param(
            make_free_passes_response(
                current_free_pass=make_pass(
                    'id', start_at=DEFAULT_START_TIME, usage_ride_time_sec=122,
                ),
            ),
            'current_using_free_pass.json',
            id='current_using_free_pass',
        ),
        pytest.param(
            make_free_passes_response(
                free_passes=[
                    make_free_pass_config('id1'),
                    make_free_pass_config('id2', life_time_sec=86400),
                ],
            ),
            'group_passes.json',
            id='group_passes',
        ),
        pytest.param(
            make_free_passes_response(
                super_passes=[
                    make_free_pass_config(
                        'id1',
                        price=0,
                        pass_type=SUPER_PASS_TYPE,
                        is_free_trial=1,
                    ),
                    make_free_pass_config(
                        'id2',
                        price=1900,
                        life_time_sec=2592000,
                        pass_type=SUPER_PASS_TYPE,
                    ),
                    make_free_pass_config(
                        'id3',
                        price=4900,
                        life_time_sec=7776000,
                        pass_type=SUPER_PASS_TYPE,
                    ),
                    make_free_pass_config(
                        'id3',
                        price=17900,
                        life_time_sec=31104000,
                        pass_type=SUPER_PASS_TYPE,
                    ),
                ],
            ),
            'super_passes.json',
            id='super_passes',
        ),
        pytest.param(
            make_free_passes_response(
                current_super_pass=make_pass(
                    'id',
                    start_at=DEFAULT_START_TIME,
                    pass_type=SUPER_PASS_TYPE,
                    has_subscription=1,
                ),
            ),
            'current_super_pass.json',
            id='current_super_passes',
        ),
        pytest.param(
            make_free_passes_response(
                current_free_pass=make_pass('id', start_at=DEFAULT_START_TIME),
                current_super_pass=make_pass(
                    'id',
                    start_at=DEFAULT_START_TIME,
                    pass_type=SUPER_PASS_TYPE,
                    has_subscription=1,
                ),
            ),
            'both_passes.json',
            id='both_passes',
        ),
    ],
)
@pytest.mark.now('2022-04-05T00:00:00.000000+0000')
async def test_free_passes(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
        free_pass_resp,
        expected_pass,
):
    @mockserver.json_handler(
        '/wind/pf/v1/boards/36f95a1c-1085-4e92-82bd-34a7d9a36cb1',
    )
    def _mock_wind_boards_id_response(request):
        return load_json('wind_board_id_response.json')

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/wind/pf/v1/freePasses')
    def _mock_wind_free_passes(request):
        return free_pass_resp

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_no_ride_response.json')

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/offers/create',
        json={
            'vehicle_numbers': ['36f95a1c-1085-4e92-82bd-34a7d9a36cb1'],
            'insurance_type': 'standart',
            'payment_methods': [
                {
                    'account_id': 'card',
                    'card': 'card-xebc57db7ebf81bdb07c8d5d2',
                },
            ],
            'destinations': [],
        },
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            'timezone-offset': '10800',
            **default_pa_headers('123'),
        },
    )
    assert response.status_code == 200
    data = response.json()
    if expected_pass:
        assert data['passes'] == load_json(expected_pass)
    else:
        assert 'passes' not in data


@pytest.mark.translations(
    client_messages={'talaria.offer.free_pass.title': {'en': 'Title'}},
)
@pytest.mark.now('2022-04-05T00:00:00.000000+0000')
async def test_title_subtitle_override(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
):
    @mockserver.json_handler(
        '/wind/pf/v1/boards/36f95a1c-1085-4e92-82bd-34a7d9a36cb1',
    )
    def _mock_wind_boards_id_response(request):
        return load_json('wind_board_id_response.json')

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/wind/pf/v1/freePasses')
    def _mock_wind_free_passes(request):
        return make_free_passes_response(
            result=0,
            current_free_pass=make_pass('id', start_at=DEFAULT_START_TIME),
        )

    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_user(request):
        return load_json('wind_get_user_no_ride_response.json')

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/offers/create',
        json={
            'vehicle_numbers': ['36f95a1c-1085-4e92-82bd-34a7d9a36cb1'],
            'insurance_type': 'standart',
            'payment_methods': [
                {
                    'account_id': 'card',
                    'card': 'card-xebc57db7ebf81bdb07c8d5d2',
                },
            ],
            'destinations': [],
        },
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            'timezone-offset': '10800',
            **default_pa_headers('123'),
        },
    )
    assert response.status_code == 200
    data = response.json()
    offer = data['offers'][0]
    assert offer['title'] == 'Title'
    assert offer['subtitle'] == ''


@pytest.mark.parametrize(
    'expected_title, has_coupon',
    [
        pytest.param(
            None,
            False,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_has_auto_promocodes.sql'],
                ),
            ),
            id='used_promocode',
        ),
        pytest.param('Free unlock', False, id='promocode_is_available'),
        pytest.param(
            'Free unlock',
            True,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_has_auto_promocodes.sql'],
                ),
            ),
            id='has_coupon',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_talaria_auto_coupon_apply.json')
@pytest.mark.translations(
    client_messages={'talaria.offer.title': {'en': 'Free unlock'}},
)
@pytest.mark.now('2022-04-05T00:00:00.000000+0000')
async def test_free_unlock_coupon(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
        x_latitude,
        x_longitude,
        expected_title,
        has_coupon,
):
    @mockserver.json_handler(
        '/wind/pf/v1/boards/36f95a1c-1085-4e92-82bd-34a7d9a36cb1',
    )
    def _mock_wind_boards_id_response(request):
        return load_json('wind_board_id_response.json')

    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def _mock_last_payment_methods(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/wind/pf/v1/freePasses')
    def _mock_wind_free_passes(request):
        return {}

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

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/offers/create',
        json={
            'vehicle_numbers': ['36f95a1c-1085-4e92-82bd-34a7d9a36cb1'],
            'insurance_type': 'standart',
            'payment_methods': [
                {
                    'account_id': 'card',
                    'card': 'card-xebc57db7ebf81bdb07c8d5d2',
                },
            ],
            'destinations': [],
        },
        headers={
            'x-long': x_longitude,
            'x-lat': x_latitude,
            'x-yataxi-scooters-tag': 'wind',
            'timezone-offset': '10800',
            **default_pa_headers('123'),
        },
    )
    assert response.status_code == 200
    data = response.json()
    offer = data['offers'][0]
    if expected_title is not None:
        assert offer['title'] == expected_title
        # assert offer['']
    else:
        assert 'title' not in offer
    assert 'subtitle' not in offer
