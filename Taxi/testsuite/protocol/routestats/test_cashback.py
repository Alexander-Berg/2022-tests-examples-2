import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils

USER_WITH_PLUS = '7c5cea02692a49a5b5e277e4582af45b'
USER_WITH_CASHBACK_PLUS = '7c5c00000000000000000000582af45b'
USER_WITH_DISABLED_NEW_SUBSCRIPTION = '7c5c00000001111111100000582af45b'


def floats_equal(p1, p2, epsilon):
    """
    In price calculations there is some rounding issue,
    so we are just checking that prices match with some error margin.
    """
    return abs(p1 - p2) < epsilon


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cashback_for_plus_availability',
    consumers=['protocol/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.user_experiments('fixed_price', 'ya_plus')
@pytest.mark.parametrize(
    'user, modifier_expected',
    [
        (USER_WITH_PLUS, True),
        (USER_WITH_CASHBACK_PLUS, False),
        (USER_WITH_DISABLED_NEW_SUBSCRIPTION, False),
    ],
    ids=['old_plus', 'cashback_plus', 'disabled_new_subscription'],
)
@ORDER_OFFERS_SAVE_SWITCH
def test_ya_plus_switch_to_cashback(
        local_services_fixed_price,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        user,
        modifier_expected,
        mock_order_offers,
        order_offers_save_enabled,
):
    request = load_json('simple_request.json')
    request['id'] = user

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    offer = utils.get_offer(
        content['offer'], db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1

    if not modifier_expected:
        assert 'price_modifiers' not in offer
        assert 'discount' not in content['service_levels'][0]
        return

    price_modifiers = offer['price_modifiers']
    assert len(price_modifiers) == 1
    modifier = price_modifiers['items'][0]

    assert 'discount' in content['service_levels'][0]
    assert modifier['reason'] == 'ya_plus'
    assert modifier['pay_subventions'] is False
    assert modifier['tariff_categories'] == ['econom']
    assert modifier['type'] == 'multiplier'
    assert floats_equal(float(modifier['value']), 0.9, 0.01)


@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.parametrize(
    'user, modifier_expected',
    [
        (USER_WITH_PLUS, True),
        (USER_WITH_CASHBACK_PLUS, True),
        (USER_WITH_DISABLED_NEW_SUBSCRIPTION, False),
    ],
    ids=['old_plus', 'cashback_plus', 'disabled_new_subscription'],
)
def test_ya_plus_switch_to_cashback_no_cashback_availability_exp(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        user,
        modifier_expected,
):
    request = load_json('simple_request.json')
    request['id'] = user

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    offer = utils.get_offer(content['offer'], db)

    if not modifier_expected:
        assert 'price_modifiers' not in offer
        assert 'discount' not in content['service_levels'][0]
        return

    price_modifiers = offer['price_modifiers']
    assert len(price_modifiers) == 1
    modifier = price_modifiers['items'][0]

    assert 'discount' in content['service_levels'][0]
    assert modifier['reason'] == 'ya_plus'
    assert modifier['pay_subventions'] is False
    assert modifier['tariff_categories'] == ['econom']
    assert modifier['type'] == 'multiplier'
    assert floats_equal(float(modifier['value']), 0.9, 0.01)
