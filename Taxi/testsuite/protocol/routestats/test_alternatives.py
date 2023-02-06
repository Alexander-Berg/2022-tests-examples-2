import json

import pytest


@pytest.mark.config(PERSONAL_WALLET_ENABLED=True)
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.parametrize(
    'has_plus_promo, params',
    (
        pytest.param(True, {}, id='success_alternative_offer'),
        pytest.param(
            False,
            {'with_personal_wallet_complement'},
            id='no_offer_because_personal_wallet_complement',
        ),
        pytest.param(
            False,
            {'with_cash'},
            id='no_offer_because_incompatible_main_payment_type',
        ),
        pytest.param(
            False,
            {'disable_plus_promo'},
            id='no_offer_because_no_promo_plus_experiment',
        ),
        pytest.param(
            False,
            {'disable_client_capability'},
            id='no_offer_because_no_client_capabilty',
        ),
        pytest.param(
            False,
            {'disable_personal_wallet'},
            id='no_offer_because_no_personal_wallet',
        ),
        pytest.param(
            False,
            {'no_cashback_plus'},
            id='no_offer_because_no_cashback_plus',
        ),
        pytest.param(
            False, {'empty_wallet'}, id='no_offer_because_empty_wallet',
        ),
        pytest.param(
            False,
            {'no_additional_data'},
            id='no_offer_because_no_pdp_additional_data',
        ),
        pytest.param(
            False,
            {'invalid_additional_data'},
            id='no_offer_because_invalid_pdp_additional_data',
        ),
        pytest.param(
            False,
            {'with_no_drivers'},
            id='no_offer_because_no_drivers_in_tariffs',
        ),
        pytest.param(
            False,
            {'with_paid_supply'},
            id='no_offer_because_paid_supply_in_tariffs',
        ),
        pytest.param(
            False,
            {'little_personal_wallet'},
            id='no_offer_because_no_enough_personal_wallet_money',
        ),
    ),
)
def test_alternative_plus_promo(
        local_services_fixed_price,
        mockserver,
        taxi_protocol,
        experiments3,
        load_json,
        db,
        has_plus_promo,
        params,
):
    if 'disable_personal_wallet' not in params:
        experiments3.add_experiments_json(
            load_json('exp3_personal_wallet.json'),
        )
    if 'disable_plus_promo' not in params:
        experiments3.add_experiments_json(load_json('exp3_plus_promo.json'))

    @mockserver.json_handler('/personal_wallet/v1/balances')
    def _mock_balances(request):
        balance = '111'
        if 'empty_wallet' in params:
            balance = '0'
        elif 'little_personal_wallet' in params:
            balance = '11'

        return {
            'balances': [
                {
                    'wallet_id': 'wallet_id/some_number_value',
                    'currency': 'RUB',
                    'is_new': True,
                    'balance': balance,
                    'payment_orders': [],
                },
            ],
            'available_deposit_payment_methods': [],
        }

    if 'with_no_drivers' in params:

        @mockserver.json_handler('/driver-eta/eta')
        def mock_driver_eta(request):
            response = load_json('driver_eta.json')
            response['classes']['econom']['found'] = False
            del response['classes']['econom']['estimated_time']
            del response['classes']['econom']['estimated_distance']
            return response

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_pricing_data_preparer(request):
        has_plus_promo_request = not any(
            [
                'disable_client_capability' in params,
                'disable_plus_promo' in params,
                'disable_personal_wallet' in params,
                'empty_wallet' in params,
                'with_personal_wallet_complement' in params,
                'with_cash' in params,
                'no_cashback_plus' in params,
            ],
        )

        body = json.loads(request.get_data())
        assert (
            body['calc_additional_prices']['plus_promo']
            == has_plus_promo_request
        )

        response = load_json('pdp_response.json')
        user_prices = response['categories']['business']['user']
        if not has_plus_promo_request or 'no_additional_data' in params:
            del user_prices['additional_prices']['plus_promo']
        elif 'invalid_additional_data' in params:
            del user_prices['additional_prices']['plus_promo']['meta'][
                'tariff_to_business'
            ]
        elif 'with_paid_supply' in params:
            user_prices['additional_prices']['paid_supply'] = {
                'meta': {},
                'modifications': {'for_fixed': [], 'for_taximeter': []},
                'price': {'total': 345.0},
            }

        return response

    request = load_json('request.json')
    if 'disable_client_capability' in params:
        del request['supported']
    if 'with_personal_wallet_complement' in params:
        request['payment']['complements'] = [
            {'type': 'personal_wallet', 'payment_method_id': 'wallet_id'},
        ]
    if 'with_cash' in params:
        request['payment'] = {'type': 'cash'}
    if 'no_cashback_plus' in params:
        db.users.update(
            {'_id': request['id']}, {'$unset': {'has_cashback_plus': 0}},
        )

    response = taxi_protocol.post(
        '3.0/routestats',
        request,
        headers={
            'User-Agent': (
                'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
            ),
        },
    )
    assert response.status_code == 200
    data = response.json()

    promo_plus_alternative = None
    for alternative in data.get('alternatives', {}).get('options', []):
        if alternative['type'] == 'plus_promo':
            promo_plus_alternative = alternative
            break

    assert bool(promo_plus_alternative) is has_plus_promo
