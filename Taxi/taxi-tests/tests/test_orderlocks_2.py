import re

import pytest
import requests

from taxi_tests import utils

GET_PRICE_RE = re.compile(r'(\d+)(?:[,.](\d+))?')
PAID_ERROR_MSG = f'Order has not been paid in time'
DEBT_ERROR_MSG = 'Has not find \'debt\' in \'payment_statuses_filter\' in time'


def order_paymentstatus(client):
    request = {
        'orderid': client.order_id,
        'format_currency': True,
        'id': client.user_id,
    }
    response = client.protocol.paymentstatuses(request, session=client.session)
    assert len(response['orders']) == 1
    return response['orders'][0]


@pytest.mark.skip(reason='TAXIBACKEND-41364')
def test_card_success(client_maker, taximeter_control):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card()
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    response = client.set_destinations([[37.642743, 55.734684]])
    fixed_price_cost = _get_fixed_price_cost(response, client.selected_class)

    client.order('manual_control-1')
    response = client.wait_for_order_status('driving')
    taximeter = taximeter_control.find_by_phone(response['driver']['phone'])
    taximeter.move(client.source['geopoint'])

    order_payment_status = order_paymentstatus(client)
    assert order_payment_status['can_be_paid_by_card'] is False
    assert order_payment_status['payment']['cardid'].startswith('card-')
    assert order_payment_status['payment']['status'] == 'paid'

    taximeter.requestconfirm('waiting')
    taximeter.requestconfirm('transporting')
    client.wait_for_basket_status(('holded', 'cleared'))
    taximeter.move(client.destinations[-1]['geopoint'])
    taximeter.requestconfirm('complete', cost=fixed_price_cost)

    data = client.wait_for_order_status()

    cost = data['cost']
    assert abs(cost - fixed_price_cost) < 1
    client.wait_for_basket_status('cleared')
    cleared_cost = client.get_card_payments('cleared')
    assert abs(cost - cleared_cost) < 1

    order_payment_status = order_paymentstatus(client)
    assert order_payment_status['can_be_paid_by_card'] is False
    assert order_payment_status['payment']['cardid'].startswith('card-')
    assert order_payment_status['payment']['status'] == 'paid'


def test_card_hold_fail(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card(rules={'pay': 'manual'})
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    response = client.set_destinations([[37.642743, 55.734684]])
    fixed_price_cost = _get_fixed_price_cost(response, client.selected_class)
    client.order('speed-300,wait-0,card_hold_fail')
    data = client.wait_for_order_status()
    assert abs(data['cost'] - fixed_price_cost) < 1
    basket = client.wait_for_basket_status('holding')
    client.set_basket_status(basket, 'cancelled')

    for _ in utils.wait_for(100, DEBT_ERROR_MSG):
        data = client.launch()
        if 'debt' in data.get('payment_statuses_filter', ()):
            break


def test_card_technical_error(client_maker):
    client = client_maker()
    client.init_phone(phone='random')
    client.add_card(rules={'pay': 'manual'})
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    client.set_destinations([[37.642743, 55.734684]])
    client.order('speed-300,wait-0,card_hold_tech_error')
    basket = client.wait_for_basket_status('holding')
    client.wait_for_order_status()
    order_payment_status = order_paymentstatus(client)
    assert order_payment_status['payment']['status'] == 'processing'

    client.set_basket_status(
        basket,
        'cancelled',
        extra={
            'status_code': 'payment_gateway_technical_error',
            'payment_resp_code': 'payment_gateway_technical_error',
            'status_desc': 'http 500 Processing error',
        },
    )

    for _ in utils.wait_for(60, PAID_ERROR_MSG):
        order_payment_status = order_paymentstatus(client)
        if order_payment_status['payment']['status'] == 'paid':
            break


def test_concurrent_orders_with_same_phone(client_maker):
    def create_client_and_order():
        client = client_maker()
        client.init_phone(phone='+79998887767')
        client.add_card()
        client.launch()
        client.paymentmethods()
        client.set_source([37.58799716246824, 55.73452861215414])
        client.set_destinations([[37.642743, 55.734684]])
        client.order('speed-300,wait-0, same_phone')
        return client

    clients = [create_client_and_order() for _ in range(3)]
    for client in clients:
        client.wait_for_order_status()
        client.wait_for_basket_status('cleared')
        order_payment_status = order_paymentstatus(client)
        assert order_payment_status['payment']['status'] == 'paid'


def test_orders_same_device(client_maker):
    client = client_maker()

    client.init_phone(phone='random')
    client.add_card()
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    client.set_destinations([[37.642743, 55.734684]])
    client.order('speed-300,wait-0,same_device')

    client.init_phone(phone='random')
    client.add_card()
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    client.set_destinations([[37.642743, 55.734684]])
    try:
        client.order('speed-300,wait-0,sd2')
    except requests.HTTPError as exc:
        assert exc.response.status_code == 429
    else:
        assert False


def test_orders_same_card(client_maker):
    card = {
        'auth_type': 'token',
        'name': '',
        'expiration_year': '2023',
        'proto': 'fake',
        'type': 'card',
        'expired': 0,
        'system': 'VISA',
        'number': '411111****1112',
        'expiration_month': '10',
        'currency': 'RUB',
        'binding_ts': 1484049109.142617,
        'service_labels': [],
        'holder': 'yyy',
        'id': 'x2222',
        'region_id': '225',
    }

    def create_and_order():
        client = client_maker()
        client.init_phone(phone='random')
        client.add_card(card=card)
        client.launch()
        client.paymentmethods()
        client.set_source([37.58799716246824, 55.73452861215414])
        client.set_destinations([[37.642743, 55.734684]])
        client.order('speed-300,wait-0,same_card')
        return client

    clients = [create_and_order() for _ in range(3)]

    for client in clients:
        client.wait_for_order_status()
        client.wait_for_basket_status('cleared')
        order_payment_status = order_paymentstatus(client)
        assert order_payment_status['payment']['cardid'].startswith('card-')
        assert order_payment_status['payment']['status'] == 'paid'


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
