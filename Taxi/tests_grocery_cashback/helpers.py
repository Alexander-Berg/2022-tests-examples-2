import copy
import decimal

from . import models

OTHER_PAYLOAD = {
    'payload_version': 'v1',
    'items': [{'type': 'other', 'amount': '666'}],
}


def create_payload(products):
    payload = copy.deepcopy(OTHER_PAYLOAD)

    items = payload['items']

    for product in products:
        items.append(
            {
                'type': 'product',
                'item_id': product.item_id,
                'quantity': product.quantity,
            },
        )

    return payload


def create_other_payload(amount):
    return {
        'payload_version': 'v1',
        'items': [{'type': 'other', 'amount': amount}],
    }


def make_transaction_items(products):
    items = []

    for product in products:
        items.append(
            models.TransactionItem(
                product.item_id, product.quantity, product.amount,
            ),
        )

    return items


def get_order_amount(products):
    amount = decimal.Decimal(OTHER_PAYLOAD['items'][0]['amount'])

    for product in products:
        amount += decimal.Decimal(product.amount)

    return str(amount)


def make_invoice_id(compensation_id):
    return f'compensation:{compensation_id}'


def make_reward_compensation_id(order_id):
    return f'tracking_game_reward_{order_id}'
