import json

import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


@pytest.fixture
def ordercommit_services(mockserver, load_binary):
    class context:
        surge_value = 1
        experiments = ['forced_surge']

    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route.protobuf'),
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        data = json.loads(request.get_data())
        assert data['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'
        assert data['payment_type'] == 'cash'
        assert data['tariffs'] == ['econom'] or data['tariffs'] == ['pool']
        assert data['experiments'] == context.experiments
        assert data['client'] == {
            'name': 'iphone',
            'version': [3, 61, 4830],
            'platform_version': [10, 1, 1],
        }
        assert data['orders_complete'] == 83
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': context.surge_value,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
                {
                    'name': 'pool',
                    'value': context.surge_value,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    return context


@pytest.mark.parametrize(
    'order_id,expected_code',
    [('fixed_price_0_no_offer', 200), ('fixed_price_1_pool_no_offer', 200)],
)
@pytest.mark.filldb(order_proc='pending')
@pytest.mark.user_experiments(
    'fixed_price_cpp', 'calc_info_cpp', 'get_experiments_cpp',
)
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize('url', ('3.0/ordercommit', 'internal/ordercommit'))
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_ordercommit_fixed_price(
        taxi_protocol,
        ordercommit_services,
        order_id,
        expected_code,
        db,
        url,
        pricing_data_preparer,
        individual_tariffs_switch_on,
):
    pricing_data_preparer.set_locale('ru')
    ordercommit_services.experiments = ['fixed_price']
    response = taxi_protocol.post(
        url,
        json={'id': 'b300bda7d41b4bae8d58dfa93221ef16', 'orderid': order_id},
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        proc = db.order_proc.find_one({'_id': order_id})
        assert proc is not None
        assert proc['commit_state'] == 'done'
