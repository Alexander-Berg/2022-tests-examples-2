import typing

DEFAULT_EXTERNAL_PAYMENT_ID = 'c964a582b3b4b3dcd514ab1914a7d2a8'

DEFAULT_TRANSACTION = {
    'created': '2020-08-14T17:39:50.265000+03:00',
    'external_payment_id': DEFAULT_EXTERNAL_PAYMENT_ID,
    'cleared': '2020-08-14T17:39:50.265000+03:00',
    'fiscal_receipt_url': (
        'https://trust.yandex.ru/checks/abc/receipts/def?mode=mobile'
    ),
    'held': '2020-08-14T17:40:01.053000+03:00',
    'initial_sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
    'operation_id': 'foo:12345',
    'payment_method_id': '123',
    'payment_type': 'card',
    'refunds': [],
    'status': 'hold_success',
    'sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
    'technical_error': False,
    'terminal_id': '57000176',
    'updated': '2020-08-14T17:40:01.053000+03:00',
}

DEFAULT_OPERATION = {
    'created': '2020-08-14T17:39:49.663000+03:00',
    'id': 'create:12345',
    'status': 'done',
    'sum_to_pay': [
        {
            'items': [{'amount': '5.00', 'item_id': 'big_mac'}],
            'payment_type': 'card',
        },
    ],
}


def make_refund(refund_sum: typing.List[dict], operation_id: str, **kwargs):
    return {
        'created': '2020-08-14T17:39:50.265000+03:00',
        'updated': '2020-08-14T17:39:50.265000+03:00',
        'sum': refund_sum,
        'status': 'refund_success',
        'operation_id': operation_id,
        **kwargs,
    }


def make_transactions_item(
        item_id: str,
        commission_category: typing.Optional[int] = None,
        amount: typing.Optional[str] = None,
        quantity: typing.Optional[str] = None,
        price: typing.Optional[str] = None,
        calc_amount: bool = False,
        fiscal_receipt_info: typing.Optional[dict] = None,
        product_id: typing.Optional[str] = None,
) -> dict:
    item: typing.Dict[str, typing.Any] = {
        'item_id': item_id,
        'product_id': 'burger' if product_id is None else product_id,
    }
    if commission_category is not None:
        item['commission_category'] = commission_category
    if fiscal_receipt_info is not None:
        item['fiscal_receipt_info'] = fiscal_receipt_info
    if amount is not None:
        item['amount'] = amount
    else:
        assert (
            quantity and price
        ), 'Either amount or both quantity and price should be present'
        item['quantity'] = quantity
        item['price'] = price
        # transactions returns amount in retrieve response
        if calc_amount:
            item['amount'] = f'{float(quantity) * float(price):.2f}'
    return item


def make_transaction(**extra) -> dict:
    return {**DEFAULT_TRANSACTION, **extra}


def make_db_row(
        item_id: str,
        order_id: str = 'test_order',
        place_id: str = '100500',
        balance_client_id='123456',
        item_type: str = 'product',
) -> dict:
    return {
        'order_id': order_id,
        'item_id': item_id,
        'place_id': place_id,
        'balance_client_id': balance_client_id,
        'type': item_type,
    }


def make_transactions_payment_items(
        payment_type: str, items: typing.List[dict],
) -> dict:
    return {'payment_type': payment_type, 'items': items}


def make_operation(**extra) -> dict:
    return {**DEFAULT_OPERATION, **extra}


def make_callback_transaction(status: str, **extra) -> dict:
    return {
        'external_payment_id': DEFAULT_EXTERNAL_PAYMENT_ID,
        'payment_type': 'card',
        'status': status,
        **extra,
    }
