import json

import pytest

from protocol.routestats import utils


@pytest.fixture(autouse=True)
def mock_routestats_deps(mockserver, load_json):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        res = utils.get_surge_calculator_response(request, 1)
        return res

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        pass

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

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta.json')


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
)
@pytest.mark.experiments3(
    name='full_auction',
    consumers=['protocol/routestats'],
    match={
        'predicate': {
            'type': 'contains',
            'init': {
                'value': 'econom',
                'arg_name': 'tariff_classes',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    clauses=[
        {
            'title': 'Econom as auction',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
def test_full_auction(taxi_protocol, load_json, load, mockserver):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        request_data = json.loads(request.get_data())
        assert request_data['calc_additional_prices']['full_auction'] is True
        return load_json('pdp_response.json')

    response = taxi_protocol.post(
        'internal/routestats',
        json=load_json('request.json'),
        headers={'X-Ya-Service-Ticket': load('tvm2_ticket_2020659_13')},
    )

    assert _mock_v2_prepare.times_called == 1
    assert response.status_code == 200

    response = response.json()

    service_levels_data = response['internal_data']['service_levels_data']
    for service_level_data in service_levels_data:
        if service_level_data['class'] != 'econom':
            continue
        # base econom price is 2144, we override it with value from
        # additional_prices.full_auction.price, which is 1501
        assert service_level_data['final_price'] == '1501'
