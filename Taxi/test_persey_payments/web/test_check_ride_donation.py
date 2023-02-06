import pytest


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'request_uid',
        'x_request_application',
        'request_params',
        'country_code',
        'persey_core_status_code',
        'exp_resp',
        'exp_resp_status',
    ],
    [
        (
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'ru',
            200,
            {
                'subs_info': {
                    'mod': {
                        'value': 10,
                        'repr': {
                            'currency_code': 'RUB',
                            'amount': '10 $SIGN$$CURRENCY$',
                            'amount_number': '10',
                            'currency_sign': '₽',
                        },
                    },
                    'goal': {'fund_id': 'friends'},
                },
                'is_subscribed': True,
            },
            200,
        ),
        (
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'not RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'ru',
            200,
            {'is_subscribed': True},
            200,
        ),
        (
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            None,
            500,
            {
                'subs_info': {
                    'mod': {
                        'value': 10,
                        'repr': {
                            'currency_code': 'RUB',
                            'amount': '10 $SIGN$$CURRENCY$',
                            'amount_number': '10',
                            'currency_sign': '₽',
                        },
                    },
                    'goal': {'fund_id': 'friends'},
                },
                'is_subscribed': True,
            },
            200,
        ),
        (
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            None,
            404,
            {
                'subs_info': {
                    'mod': {
                        'value': 10,
                        'repr': {
                            'currency_code': 'RUB',
                            'amount': '10 $SIGN$$CURRENCY$',
                            'amount_number': '10',
                            'currency_sign': '₽',
                        },
                    },
                    'goal': {'fund_id': 'friends'},
                },
                'is_subscribed': True,
            },
            200,
        ),
        (
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'de',
            200,
            {'is_subscribed': True},
            200,
        ),
        (
            'no_subs_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'ru',
            200,
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': True},
            200,
        ),
        (
            'no_subs_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'de',
            200,
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': False},
            200,
        ),
        pytest.param(
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'ru',
            200,
            {
                'code': 'ROUNDUPS_DISABLED',
                'message': (
                    'Roundups are disabled for brand=eats, '
                    'application=android'
                ),
            },
            403,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'eats': ['ios']},
            ),
        ),
        pytest.param(
            'phonish_uid',
            'app_name=ios,app_brand=yataxi',
            {
                'order_id': 'no_matter',
                'payment_tech_type': 'card',
                'ride_cost': '6',
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'lavka',
            },
            'ru',
            200,
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': True},
            200,
            marks=[
                pytest.mark.config(
                    PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                        'lavka': ['ios:exp3'],
                    },
                ),
                pytest.mark.client_experiments3(
                    consumer='persey-payments/ride_subs',
                    experiment_name='persey_payments_allow_app',
                    args=[
                        {
                            'name': 'yandex_uid',
                            'type': 'string',
                            'value': 'phonish_uid',
                        },
                        {
                            'name': 'application',
                            'type': 'string',
                            'value': 'ios',
                        },
                        {'name': 'brand', 'type': 'string', 'value': 'lavka'},
                    ],
                    value={'allowed': True},
                ),
            ],
        ),
        pytest.param(
            'phonish_uid',
            'app_name=android,app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'ru',
            200,
            {
                'subs_info': {
                    'mod': {
                        'value': 10,
                        'repr': {
                            'currency_code': 'RUB',
                            'amount': '10 $SIGN$$CURRENCY$',
                            'amount_number': '10',
                            'currency_sign': '₽',
                        },
                    },
                    'goal': {'fund_id': 'friends'},
                },
                'is_subscribed': True,
            },
            200,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={
                    'eats': ['ios', 'android'],
                },
            ),
        ),
        pytest.param(
            'phonish_uid',
            'app_brand=yataxi',
            {
                'currency_code': 'RUB',
                'delivery_position_lon': 1,
                'delivery_position_lat': 2,
                'brand': 'eats',
            },
            'ru',
            200,
            {
                'subs_info': {
                    'mod': {
                        'value': 10,
                        'repr': {
                            'currency_code': 'RUB',
                            'amount': '10 $SIGN$$CURRENCY$',
                            'amount_number': '10',
                            'currency_sign': '₽',
                        },
                    },
                    'goal': {'fund_id': 'friends'},
                },
                'is_subscribed': True,
            },
            200,
            marks=pytest.mark.config(
                PERSEY_PAYMENTS_ESTIMATE_APPLICATION={'eats': ['ios']},
            ),
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        mock_geo,
        x_request_application,
        request_uid,
        request_params,
        country_code,
        persey_core_status_code,
        exp_resp,
        exp_resp_status,
):
    mock_geo(country_code, persey_core_status_code)

    response = await taxi_persey_payments_web.get(
        '/4.0/persey-payments/v1/charity/ride_donation/check',
        params=request_params,
        headers={
            'X-Yandex-UID': request_uid,
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-Request-Application': x_request_application,
            'X-Request-Language': 'ru',
        },
    )

    assert response.status == exp_resp_status
    assert await response.json() == exp_resp
