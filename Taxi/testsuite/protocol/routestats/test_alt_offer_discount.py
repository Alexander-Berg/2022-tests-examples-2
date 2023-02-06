import base64

import bson
import pytest

from protocol.routestats import utils


def _get_discount(response, alternative_name):
    options = response['alternatives']['options']
    assert any(e['type'] == alternative_name for e in options)
    for e in response['internal_data']['alternatives']:
        if e['type'] == alternative_name:
            return e


def _check_alternative(response, alternative_name, price, db):
    options = response['alternatives']['options']
    assert any(e['type'] == alternative_name for e in options)

    discount = _get_discount(response, alternative_name)
    assert str(price) == discount['service_levels_data'][0]['final_price']

    offer = utils.get_offer(discount['offer_id'], db)
    assert offer['prices'][0]['price'] == float(price)


@pytest.mark.parametrize('prepare_altoffer', [False, True])
@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
)
@pytest.mark.experiments3(filename='exp3_alt_offer_discount.json')
@pytest.mark.translations(
    tariff={
        'routestats.perfect_chain.money.selector.tooltip': {
            'ru': 'Придется подождать',
        },
    },
)
def test_base(
        taxi_protocol, load_json, load, mockserver, db, prepare_altoffer,
):
    _EXPECTED_PERFECT_CHAIN_PRICE = 1501

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        res = utils.get_surge_calculator_response(request, 1)
        for class_info in res['classes']:
            if class_info['name'] == 'econom':
                class_info['explicit_antisurge'] = {'value': 0.3}
                class_info['value_smooth_b'] = 1.0
                break
        return res

    @mockserver.json_handler('/personal_wallet/v1/balances')
    def _mock_balances(request):
        return {
            'balances': [
                {
                    'wallet_id': 'wallet_id/some_number_value',
                    'currency': 'RUB',
                    'is_new': True,
                    'balance': '60',
                    'payment_orders': [],
                },
            ],
            'available_deposit_payment_methods': [],
        }

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        return load_json('pdp_response.json')

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        pin_extra = request.json['pin']['extra']
        assert len(pin_extra['alt_offer_discount_ids']) == 2

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta.json')

    ticket = load('tvm2_ticket_2020659_13')
    request = load_json('request.json')
    if prepare_altoffer:
        request['feature_flags'] = {'prepare_altoffers': ['perfect_chain']}
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )
    assert response.status_code == 200
    response = response.json()

    if not prepare_altoffer:
        _check_alternative(
            response, 'perfect_chain', _EXPECTED_PERFECT_CHAIN_PRICE, db,
        )
        assert 'prepared_altoffers' not in response['internal_data']
    else:
        # altoffer was not saved
        offer_id = _get_discount(response, 'perfect_chain')['offer_id']
        assert not utils.get_offer('offer_id', db)

        prepared_altoffer = response['internal_data']['prepared_altoffers'][0]
        assert prepared_altoffer['alternative_type'] == 'perfect_chain'
        offer = bson.BSON(
            base64.b64decode(prepared_altoffer['serialized_doc']),
        ).decode()
        assert offer['prices'][0]['price'] == _EXPECTED_PERFECT_CHAIN_PRICE
        assert offer['_id'] == offer_id

    assert all(
        e['type'] != 'not_so_cool_chain'
        for e in response['alternatives']['options']
    )
