import uuid

import pytest
import requests

from taxi_tests import utils

CASH_PAID_ERROR_MSG = 'Client %s from clients %s did not paid cash in time'
OLD_ORDERS_ERROR_MSG = 'Old order was not finished in time'
NEW_ORDER_ERROR_MSG = 'Order was not started in time'


@pytest.mark.skip(reason='TAXIBACKEND-41364')
def test_2_cards_one_fails(client_maker, taximeter_control):
    clients = _create_clients(client_maker)
    for client in clients:
        response = client.wait_for_order_status('driving')
        client.taximeter = taximeter_control.find_by_phone(
            response['driver']['phone'],
        )
        client.taximeter.move(client.source['geopoint'])
        client.taximeter.requestconfirm('waiting')
        client.taximeter.requestconfirm('transporting')

    for client in clients:
        client.wait_for_order_status('transporting')

    for client in clients:
        if client.pay_ok:
            client.wait_for_basket_status(('holded', 'cleared'))
        else:
            basket = client.wait_for_basket_status('holding')
            client.set_basket_status(basket, 'cancelled')

    for client in clients:
        for _ in utils.wait_for(
                1000, CASH_PAID_ERROR_MSG % (str(client), str(clients)),
        ):
            response = client.taxiontheway()
            if response['payment']['type'] == 'cash':
                break

    for client in clients:
        client.taximeter.move(client.destinations[-1]['geopoint'])
        client.taximeter.requestconfirm('complete', cost=300)

    for client in clients:
        data = client.wait_for_order_status()
        assert data['cost'] == 300
        assert data['payment']['type'] == 'cash'

        if client.pay_ok:
            client.wait_for_basket_status(('resized', 'refunded'))
        else:
            client.wait_for_basket_status('cancelled')
        assert client.get_card_payments() == 0

    for client in clients:
        _check_can_make_more_orders(client)


def _start_order(client, manual_control=True):
    client.launch()
    client.paymentmethods()
    client.set_source([37.58799716246824, 55.73452861215414])
    client.set_destinations([[37.642743, 55.734684]])
    data = client.order('manual_control-1' if manual_control else '')
    assert data['status'] == 'search'


def _random_card(card_template, persistent_id):
    card_id = str(uuid.uuid4())

    card_data = next(iter(card_template.values()))
    card_data['id'] = card_id
    card_data['service_labels'] = ['taxi:persistent_id:%s' % persistent_id]
    card_data['persistent_id'] = persistent_id

    return card_data


def _create_clients(client_maker):
    persistent_id = uuid.uuid4().hex
    clients = []
    for pay_ok in (True, False):
        client = client_maker()
        clients.append(client)
        client.init_phone(phone='random')
        client.pay_ok = pay_ok
        card = _random_card(
            client.billing.default_paymnet_methods, persistent_id,
        )
        rules = None if pay_ok else {'pay': 'manual'}
        client.add_card(card, rules=rules)
        _start_order(client)
    return clients


def _check_can_make_more_orders(client):
    for obj in utils.wait_for(120, OLD_ORDERS_ERROR_MSG, sleep=10):
        request = {
            'filter': ['need_cvn', 'debt'],
            'format_currency': True,
            'id': client.user_id,
        }
        response = client.protocol.paymentstatuses(
            request, session=client.session,
        )
        if not response['orders']:
            break
        obj['orders'] = response['orders']

    for obj in utils.wait_for(120, NEW_ORDER_ERROR_MSG, sleep=15):
        try:
            _start_order(client, manual_control=False)
        except requests.HTTPError as exc:
            obj['error'] = exc
        else:
            break

    response = client.taxiontheway(cancel=True)
    assert response['status'] == 'cancelled'
