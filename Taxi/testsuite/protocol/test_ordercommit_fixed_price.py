from datetime import datetime
from datetime import timedelta
import json

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_MATCH_SWITCH

ORDER_ID = 'fixed_price'
USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_fixed_price_positive(taxi_protocol, db):
    """
        Tests everything works
    """
    order_proc_after = check_order_proc_before_and_get_after(db, taxi_protocol)
    check_order_proc_after(order_proc_after)


@pytest.mark.order_experiments('fixed_price')
@pytest.mark.parametrize(
    'enable_preorder_fixprice',
    [
        True,
        # False # Disabled because there is no way to detect experiment change
    ],
    ids=[
        'preorder fixprice is allowed',
        # 'preorder fixprice is not allowed'
    ],
)
def test_ordercommit_fixed_price_preorder(
        taxi_protocol,
        db,
        experiments3,
        enable_preorder_fixprice,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    """
        Tests everything works
    """
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='preorder_fixprice',
        consumers=['protocol/ordercommit'],
        clauses=[
            {
                'title': '',
                'value': {'enabled': enable_preorder_fixprice},
                'predicate': {'type': 'true'},
            },
        ],
    )
    taxi_protocol.invalidate_caches()

    setup_preorder(db, datetime.now())

    order_proc_after = check_order_proc_before_and_get_after(db, taxi_protocol)
    if not enable_preorder_fixprice:
        assert order_proc_after['order'].get('fixed_price') is None
    else:
        check_order_proc_after(order_proc_after)


def check_order_proc_before_and_get_after(db, taxi_protocol):
    order_proc_before = db.order_proc.find_one({'_id': ORDER_ID})
    assert 'fixed_price' not in order_proc_before['order']

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert response.status_code == 200

    return db.order_proc.find_one({'_id': ORDER_ID})


def check_order_proc_after(order_proc_after):
    fixed_price_expected = {
        'destination': [37.5, 55.7],
        'max_distance_from_b': 500,
        'price': 250.0,
        'price_original': 250,
        'show_price_in_taximeter': True,
    }

    fixed_price = order_proc_after['order'].get('fixed_price')
    assert fixed_price == dict(
        paid_supply_info={'distance': 4567, 'time': 456},
        **fixed_price_expected,
    )

    current_prices = order_proc_after['order'].get('current_prices')
    assert current_prices['user_total_price'] == fixed_price_expected['price']
    assert (
        current_prices['user_total_display_price']
        == fixed_price_expected['price']
    )
    assert current_prices['kind'] == 'fixed'


def setup_preorder(db, now):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.preorder_request_id': 'preorder_id'}},
    )
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.due': now + timedelta(seconds=2000)}},
    )
    order = db.order_proc.find_one({'_id': ORDER_ID})
    offer_id = order['order']['request']['offer']
    db.order_offers.update(
        {'_id': offer_id}, {'$set': {'due': now + timedelta(seconds=2020)}},
    )


@pytest.mark.order_experiments('fixed_price')
def test_ordercommit_fixed_price_wrong_offer(
        taxi_protocol, mockserver, db, pricing_data_preparer,
):
    """
        Tests if offer is not found
        then 406 exception thrown
    """
    pricing_data_preparer.set_locale('ru')

    order_before = db.order_proc.find_one({'_id': ORDER_ID})
    assert 'fixed_price' not in order_before['order']

    result = db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.offer': 'wrong_id'}},
    )
    assert result['nModified'] == 1

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == 406
    json = response.json()
    assert json['error'] == {'code': 'PRICE_CHANGED'}


@pytest.mark.order_experiments('fixed_price')
@ORDER_OFFERS_MATCH_SWITCH
def test_ordercommit_fixed_price_wrong_offer_new_pricing(
        taxi_protocol,
        mockserver,
        db,
        load_json,
        mock_order_offers,
        order_offers_match_enabled,
):
    """
        Tests if offer is not found
        then 406 exception thrown
    """
    order_before = db.order_proc.find_one({'_id': ORDER_ID})
    assert 'fixed_price' not in order_before['order']

    result = db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.offer': 'wrong_id'}},
    )
    assert result['nModified'] == 1
    result = db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.is_delayed': True}},
    )
    assert result['nModified'] == 1

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        data = json.loads(request.get_data())
        assert data.get('is_delayed') is True
        assert 'zone' in data and data['zone']
        pdp_response = load_json('pdp_v2_prepare_response.json')
        return pdp_response

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert response.status_code == 406
    json_response = response.json()
    assert json_response['error'] == {'code': 'PRICE_CHANGED'}

    assert mock_new_pricing.has_calls

    assert mock_order_offers.mock_match_offer.times_called == (
        1 if order_offers_match_enabled else 0
    )


@pytest.mark.config(PERSONAL_WALLET_ENABLED=True)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
@pytest.mark.order_experiments('fixed_price')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='personal_wallet',
    consumers=['protocol/ordercommit'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_ordercommit_fixed_price_pass_complements_in_pdp(
        taxi_protocol, mockserver, db, load_json,
):
    """
        Tests that wallet is passed to pdp
    """
    result = db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.offer': 'wrong_id'}},
    )
    assert result['nModified'] == 1
    result = db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.is_delayed': True}},
    )
    assert result['nModified'] == 1

    complements = [{'type': 'personal_wallet', 'payment_method_id': 'w/123'}]
    result = db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.payment.complements': complements}},
    )
    assert result['nModified'] == 1

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        data = json.loads(request.get_data())

        assert data['user_info']['payment_info']['complements'] == {
            'personal_wallet': {'balance': 20, 'method_id': 'w/123'},
        }

        pdp_response = load_json('pdp_v2_prepare_response.json')
        return pdp_response

    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return {
            'balances': [
                {'balance': '20', 'currency': 'RUB', 'wallet_id': 'w/123'},
            ],
        }

    taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )

    assert mock_balances.has_calls
    assert mock_new_pricing.has_calls


@pytest.mark.order_experiments('fixed_price')
@ORDER_OFFERS_MATCH_SWITCH
def test_ordercommit_fixed_price_unauthorized_offer(
        taxi_protocol,
        mockserver,
        db,
        experiments3,
        load_json,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_match_enabled,
):
    """
        Tests that price recalculates for unauthroized offer.
        It's different, so PRICE_CHANGED error returns.
    """
    pricing_data_preparer.set_locale('ru')

    order = db.order_proc.find_one({'_id': ORDER_ID})
    offer_id = order['order']['request']['offer']
    db.order_offers.update({'_id': offer_id}, {'$set': {'authorized': False}})

    response = taxi_protocol.post(
        '3.0/ordercommit', json={'id': USER_ID, 'orderid': ORDER_ID},
    )
    assert 406 == response.status_code
    json = response.json()
    assert json['error'] == {'code': 'PRICE_CHANGED'}

    assert mock_order_offers.mock_match_offer.times_called == (
        1 if order_offers_match_enabled else 0
    )
