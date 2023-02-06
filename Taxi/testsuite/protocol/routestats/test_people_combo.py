import pytest

from protocol.routestats import utils


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
)
@pytest.mark.experiments3(filename='exp3_people_combo_order.json')
@pytest.mark.experiments3(filename='exp3_people_combo_order_inner.json')
@pytest.mark.translations(
    tariff={
        'routestats.combo_inner.money.selector.tooltip': {
            'ru': 'Уже есть один',
        },
        'routestats.combo_outer.money.selector.tooltip': {
            'ru': 'Будет еще один',
        },
    },
)
def test_people_combo(taxi_protocol, load_json, load, mockserver):
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
        pass

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta.json')

    ticket = load('tvm2_ticket_2020659_13')
    request = load_json('request.json')
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )

    assert response.status_code == 200

    response = response.json()

    assert {'combo_inner', 'combo_outer'} == set(
        i['type'] for i in response['alternatives']['options']
    )

    combo_inner = [
        i
        for i in response['internal_data']['alternatives']
        if i['type'] == 'combo_inner'
    ][0]
    combo_outer = [
        i
        for i in response['internal_data']['alternatives']
        if i['type'] == 'combo_outer'
    ][0]

    # base econom price is 2144,
    # default discounts are 20% (inner) and 30% (outer)
    assert '1501' == combo_inner['service_levels_data'][0]['final_price']
    assert '1715' == combo_outer['service_levels_data'][0]['final_price']
