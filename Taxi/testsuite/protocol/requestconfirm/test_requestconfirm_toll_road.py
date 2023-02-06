import json

import pytest

from protocol.ordercommit import order_commit_common
from protocol.requestconfirm import test_requestconfirm_cashback
from protocol.requestconfirm.test_requestconfirm import PricingCompleteData


def check_toll_road_cost(proc, expected_toll_road):
    toll_road_price = None
    expected_total_price = proc['order']['cost']
    if expected_toll_road:
        assert proc['order']['toll_road'] == expected_toll_road
        if not expected_toll_road['hidden']:
            toll_road_price = expected_toll_road['toll_road_price']
            assert (
                proc['order']['current_prices']['toll_road_price']
                == expected_toll_road['toll_road_price']
            )
        expected_total_price += expected_toll_road['toll_road_price']
    else:
        assert 'toll_road' not in proc['order']['current_prices']
    order_commit_common.check_current_prices(
        proc,
        'final_cost',
        expected_total_price,
        toll_road_price=toll_road_price,
    )


@pytest.mark.parametrize(
    'norway_toll_road_cost, gepard_toll_road_cost',
    [
        pytest.param(None, None, id='no_toll_road'),
        pytest.param(15, None, id='only_norway'),
        pytest.param(None, 15, id='only_gepard'),
        pytest.param(15, 16, id='both_but_use_norway'),
    ],
)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_ENABLED_REQUESTCONFIRM=True)
@pytest.mark.experiments3(filename='exp3.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_toll_road_cases(
        taxi_protocol,
        db,
        norway_toll_road_cost,
        gepard_toll_road_cost,
        mockserver,
):
    toll_road = None
    if norway_toll_road_cost:
        toll_road = {'toll_road_price': norway_toll_road_cost, 'hidden': True}
    elif gepard_toll_road_cost:
        toll_road = {'toll_road_price': gepard_toll_road_cost, 'hidden': False}

    @mockserver.json_handler(
        '/current_prices_calculator/v1/internal/current_prices',
    )
    def mock_current_prices_calculator(request):
        req = json.loads(request.get_data())
        if norway_toll_road_cost or gepard_toll_road_cost:
            assert req['toll_road']
        else:
            assert not req.get('toll_road')
        response = {
            'user_total_price': '1000',
            'user_total_display_price': '1000',
            'user_ride_display_price': '1000',
            'cost_breakdown': [
                {'type': 'card', 'amount': '100'},
                {'type': 'personal_wallet', 'amount': '20'},
            ],
            'kind': 'taximeter',
        }
        if toll_road and not toll_road['hidden']:
            response['toll_road_price'] = str(toll_road['toll_road_price'])
        return response

    test_requestconfirm_cashback.setup_order_proc(
        db, False, False, 'card', True, False,
    )
    test_requestconfirm_cashback.setup_order_proc_metas(db, None, None, None)
    final_cost_meta = {'driver': {}, 'user': {}}
    if norway_toll_road_cost:
        final_cost_meta['driver'][
            'norway_toll_road_payment_price'
        ] = norway_toll_road_cost
        final_cost_meta['user'][
            'norway_toll_road_payment_price'
        ] = norway_toll_road_cost
    if gepard_toll_road_cost:
        final_cost_meta['driver'][
            'gepard_toll_road_payment_price'
        ] = gepard_toll_road_cost
        final_cost_meta['user'][
            'gepard_toll_road_payment_price'
        ] = gepard_toll_road_cost

    pricing_complete_data = PricingCompleteData()
    pricing_complete_data.set_final_cost(driver_cost=1000, user_cost=1000)
    pricing_complete_data.set_final_cost_meta(final_cost_meta)
    test_requestconfirm_cashback.make_request(
        taxi_protocol,
        test_requestconfirm_cashback.CALC_METHOD_FIXED_PRICE,
        pricing_complete_data=pricing_complete_data,
    )

    proc = db.order_proc.find_one(test_requestconfirm_cashback.ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    check_toll_road_cost(proc, toll_road)
