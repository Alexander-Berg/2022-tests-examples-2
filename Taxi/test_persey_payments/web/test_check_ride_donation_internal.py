import pytest


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    ['request_params', 'zalogin_response', 'exp_resp', 'exp_resp_status'],
    [
        (
            {
                'uid': '10000',
                'currency_code': 'RUB',
                'payment_type': 'card',
                'brand': 'eats',
                'app': 'android',
            },
            'zalogin_resp_portal.json',
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
            {
                'uid': '10000',
                'currency_code': 'RUB',
                'payment_type': 'cash',
                'brand': 'eats',
                'app': 'android',
            },
            'zalogin_resp_portal.json',
            {'is_subscribed': True},
            200,
        ),
        (
            {
                'uid': '10000',
                'currency_code': 'RUB',
                'payment_type': 'card',
                'brand': 'eats',
                'app': 'android',
            },
            'zalogin_resp_no_bound.json',
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': True},
            200,
        ),
        (
            {
                'uid': '10000',
                'currency_code': 'RUB',
                'payment_type': 'cash',
                'brand': 'eats',
                'app': 'android',
            },
            'zalogin_resp_no_bound.json',
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': False},
            200,
        ),
        (
            {
                'uid': '10000',
                'currency_code': 'USD',
                'payment_type': 'card',
                'brand': 'eats',
                'app': 'android',
            },
            'zalogin_resp_no_bound.json',
            {'is_subscribed': False, 'nonzero_donation_if_subscribes': False},
            200,
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        mock_geo,
        request_params,
        exp_resp,
        exp_resp_status,
        mock_zalogin,
        zalogin_response,
):
    zalogin_mock = mock_zalogin('10000', zalogin_response)

    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donation/check', params=request_params,
    )

    assert response.status == exp_resp_status
    assert await response.json() == exp_resp
    assert zalogin_mock.has_calls
