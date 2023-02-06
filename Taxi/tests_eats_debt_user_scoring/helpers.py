import collections


def make_debt(
        order_id='test_order',
        reason_code='technical_debt',
        debt=None,
        total=None,
) -> dict:
    if debt is None:
        debt = []
    if total is None:
        total = []
    return {
        'id': order_id,
        'reason': {'code': reason_code, 'metadata': {}},
        'metadata': {},
        'service': 'eats',
        'debtors': ['eats/yandex_uid/12345'],
        'version': 1,
        'invoice': {
            'id': order_id,
            'transactions_installation': 'eda',
            'originator': 'eats_payments',
        },
        'collection': {
            'strategy': {'kind': 'null', 'metadata': {}},
            'installed_at': '2021-09-01T00:00:00+03:00',
        },
        'transactions_params': {},
        'currency': 'RUB',
        'items_by_payment_type': {'debt': debt, 'total': total},
        'created_at': '2021-09-01T00:00:00+03:00',
        'updated_at': '2021-09-01T00:00:00+03:00',
    }


def make_debt_item(item_id, amount) -> dict:
    return {'item_id': item_id, 'amount': amount}


def make_counters(counter_list):
    payment_method_count = collections.defaultdict(int)
    for item in counter_list:
        payment_method_count[item['payment_method']] += item['orders_count']
    return [
        {
            'value': v,
            'first_order_at': '2021-08-19T13:04:05+0000',
            'last_order_at': '2021-08-19T13:04:05+0000',
            'properties': [{'name': 'payment_method', 'value': k}],
        }
        for k, v in payment_method_count.items()
    ]
