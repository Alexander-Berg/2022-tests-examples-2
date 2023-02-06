import datetime

DEFAULT_ITEMS = [
    {
        'amount': '100',
        'item_id': '1',
        'product_id': 'eda_107819207_ride',
        'fiscal_receipt_info': {'vat': 'nds_20', 'title': 'Hamburger x2'},
    },
    {
        'amount': '100',
        'item_id': '2',
        'product_id': 'eda_107819207_ride',
        'fiscal_receipt_info': {'vat': 'nds_10', 'title': 'Cola x0.5'},
    },
    {
        'amount': '0',
        'item_id': '4',
        'product_id': 'eda_107819207_ride',
        'fiscal_receipt_info': {'vat': 'nds_0', 'title': 'Air x1'},
    },
]

COMPOSITE_ITEMS = [
    {
        'amount': '1',
        'item_id': '1',
        'product_id': 'eda_107819207_ride',
        'fiscal_receipt_info': {'vat': 'nds_20', 'title': 'Hamburger x2'},
    },
    {
        'amount': '50',
        'item_id': '2',
        'product_id': 'eda_107819207_ride',
        'fiscal_receipt_info': {'vat': 'nds_10', 'title': 'Cola x0.5'},
    },
    {
        'amount': '0',
        'item_id': '4',
        'product_id': 'eda_107819207_ride',
        'fiscal_receipt_info': {'vat': 'nds_0', 'title': 'Air x1'},
    },
]


def default_sum_to_pay(
        items=None, payment_type='card', complement_amount=None,
):
    if items is None:
        items = DEFAULT_ITEMS
    sum_to_pay = [{'items': items, 'payment_type': payment_type}]
    if complement_amount:
        sum_to_pay.append(
            {
                'items': [
                    {
                        'amount': complement_amount,
                        'item_id': '1',
                        'product_id': 'eda_107819207_ride',
                    },
                ],
                'payment_type': 'personal_wallet',
            },
        )
    return sum_to_pay


DEFAULT_INVOICE_RETRIEVE_RESPONSE = {
    'id': 'invoice_01',
    'operation_info': {
        'originator': 'processing',
        'priority': 1,
        'version': 2,
    },
    'service': 'restaurants',
    'status': 'cleared',
    'sum_to_pay': [{'items': DEFAULT_ITEMS, 'payment_type': 'card'}],
    'yandex_uid': '123456789',
    'transactions': [
        dict(
            terminal_id='deprecated_terminal_id',
            external_payment_id='deprecated_trust_id',
            payment_type='card',
            status='hold_fail',
            # unused required fields
            created=datetime.datetime.now().isoformat(),
            updated=datetime.datetime.now().isoformat(),
            sum=[],
            initial_sum=[],
            refunds=[],
        ),
        dict(
            terminal_id='terminal_id',
            external_payment_id='trust_id',
            payment_type='card',
            status='clear_success',
            # unused required fields
            created=datetime.datetime.now().isoformat(),
            updated=datetime.datetime.now().isoformat(),
            sum=[],
            initial_sum=[],
            refunds=[],
        ),
    ],
    # unused required fields
    'cleared': [],
    'currency': 'RUB',
    'debt': [],
    'held': [],
    'invoice_due': '2020-07-27T21:20:00+03:00',
    'created': '2020-07-27T21:20:00+03:00',
    'operations': [],
    'payment_types': ['card'],
}


COMPOSITE_INVOICE_RETRIEVE_RESPONSE = {
    'id': 'order_pending_composite',
    'operation_info': {
        'originator': 'processing',
        'priority': 1,
        'version': 2,
    },
    'service': 'restaurants',
    'status': 'cleared',
    'sum_to_pay': default_sum_to_pay(
        items=DEFAULT_ITEMS, complement_amount='200',
    ),
    'yandex_uid': '123456789',
    # never mind
    'cleared': [],
    'currency': 'RUB',
    'debt': [],
    'held': [],
    'invoice_due': '2020-07-27T21:20:00+03:00',
    'created': '2020-07-27T21:20:00+03:00',
    'operations': [],
    'payment_types': ['card', 'personal_wallet'],
    'transactions': [
        dict(
            terminal_id='deprecated_terminal_id',
            external_payment_id='deprecated_trust_id',
            payment_type='card',
            status='hold_fail',
            # unused required fields
            created=datetime.datetime.now().isoformat(),
            updated=datetime.datetime.now().isoformat(),
            sum=[],
            initial_sum=[],
            refunds=[],
        ),
        dict(
            terminal_id='deprecated_complement_terminal_id',
            external_payment_id='deprecated_complement_trust_id',
            payment_type='personal_wallet',
            status='hold_fail',
            # unused required fields
            created=datetime.datetime.now().isoformat(),
            updated=datetime.datetime.now().isoformat(),
            sum=[],
            initial_sum=[],
            refunds=[],
        ),
        dict(
            terminal_id='terminal_id',
            external_payment_id='trust_id',
            payment_type='card',
            status='clear_success',
            # unused required fields
            created=datetime.datetime.now().isoformat(),
            updated=datetime.datetime.now().isoformat(),
            sum=[],
            initial_sum=[],
            refunds=[],
        ),
        dict(
            terminal_id='complement_terminal_id',
            external_payment_id='complement_trust_id',
            payment_type='personal_wallet',
            status='clear_success',
            # unused required fields
            created=datetime.datetime.now().isoformat(),
            updated=datetime.datetime.now().isoformat(),
            sum=[],
            initial_sum=[],
            refunds=[],
        ),
    ],
}


DEFAULT_INVOICE_UPDATE_REQUEST = {
    'id': 'order_pending',
    'originator': 'processing',
    'operation_id': 'refund_2',
    'items_by_payment_type': default_sum_to_pay(),
    'version': 2,
}

COMPOSITE_INVOICE_UPDATE_REQUEST = {
    'id': 'order_pending_composite',
    'originator': 'processing',
    'operation_id': 'refund_2',
    'items_by_payment_type': default_sum_to_pay(
        items=COMPOSITE_ITEMS, complement_amount='149',
    ),
    'version': 2,
    'wallet_payload': {
        'service_id': '645',
        'cashback_service': 'qr_restaurant',
        'amount': '149',
        'cashback_type': 'transaction',
        'has_plus': 'True',
        'order_id': 'order_pending_composite',
        'base_amount': '200',
    },
}
