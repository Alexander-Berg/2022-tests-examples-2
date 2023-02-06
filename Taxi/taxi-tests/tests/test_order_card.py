import re

import pytest

from taxi_tests import utils

GET_PRICE_RE = re.compile(r'(\d+)(?:[,.](\d+))?')

MAX_CARD_PAYMENT = 800
PAYMENT_TYPE_ERROR_MSG = 'Appropriate payment_type was not set in time'
DEBT_ERROR_MSG = 'Has not find \'debt\' in \'payment_statuses_filter\' in time'


def test_card_success(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card()
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    response = client.set_destinations([[37.642743, 55.734684]])
    fixed_price_cost = _get_fixed_price_cost(response, client.selected_class)
    client.order('speed-300,wait-0')
    data = client.wait_for_order_status()
    cost = data['cost']
    assert abs(cost - fixed_price_cost) < 1
    client.wait_for_basket_status('cleared')
    cleared_cost = client.get_card_payments('cleared')
    assert abs(cost - cleared_cost) < 1


@pytest.mark.skip(reason='TAXIBACKEND-41364')
@pytest.mark.parametrize(
    'billing_response,transaction_status,payment_type',
    [('ok', 'cleared', 'card'), ('fail', 'cancelled', 'cash')],
)
def test_card_accept(
        billing_response,
        transaction_status,
        payment_type,
        client_maker,
        taximeter_control,
):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card(rules={'pay': billing_response})
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    response = client.set_destinations([[37.900479, 55.414348]])
    fixed_price_cost = _get_fixed_price_cost(response, client.selected_class)
    assert fixed_price_cost > MAX_CARD_PAYMENT + 100
    client.order('manual_control-1')
    response = client.wait_for_order_status('driving')
    client.taximeter = taximeter_control.find_by_phone(
        response['driver']['phone'],
    )
    client.taximeter.move(client.source['geopoint'])
    client.taximeter.requestconfirm('waiting')
    client.taximeter.requestconfirm('transporting')
    client.wait_for_basket_status(transaction_status)
    for obj in utils.wait_for(100, PAYMENT_TYPE_ERROR_MSG):
        data = client.taxiontheway()
        if data['payment']['type'] == payment_type:
            break
        obj['payment_type'] = data['payment']['type']
    client.taximeter.move(client.destinations[-1]['geopoint'])
    client.taximeter.requestconfirm('complete', cost=fixed_price_cost)
    data = client.wait_for_order_status()
    assert data['payment']['type'] == payment_type
    assert abs(data['cost'] - fixed_price_cost) < 1
    baskets = client.get_baskets()
    assert baskets, 'no transactions at all'
    assert baskets[0]['status'] == transaction_status

    if transaction_status == 'cleared':
        cleared_cost = client.get_card_payments('cleared')
        assert cleared_cost == MAX_CARD_PAYMENT


def test_card_hold_error(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card(rules={'pay': 'manual'})
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    response = client.set_destinations([[37.642743, 55.734684]])
    fixed_price_cost = _get_fixed_price_cost(response, client.selected_class)
    client.order('speed-300,wait-0')
    data = client.wait_for_order_status()
    assert abs(data['cost'] - fixed_price_cost) < 1
    basket = client.wait_for_basket_status('holding')
    client.set_basket_status(basket, 'cancelled')

    for _ in utils.wait_for(100, DEBT_ERROR_MSG):
        data = client.launch()
        if 'debt' in data.get('payment_statuses_filter', ()):
            break


def _get_fixed_price_cost(response, tariff_class):
    for cls_info in response['service_levels']:
        if cls_info['class'] == tariff_class:
            assert response.get('is_fixed_price') or cls_info.get(
                'is_fixed_price',
            )
            price_match = GET_PRICE_RE.search(cls_info['description'])
            return float(
                '{}.{}'.format(
                    price_match.group(1), price_match.group(2) or '0',
                ),
            )
    return None
