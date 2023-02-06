def debt_info(id_, invoice_id, debtors):
    return {
        'id': id_,
        'metadata': {'zone': 'moscow'},
        'service': 'eats',
        'debtors': debtors,
        'currency': 'RUB',
        'version': 3,
        'items_by_payment_type': {'debt': [], 'total': []},
        'collection': {
            'installed_at': '2021-01-01T00:00:00+00:00',
            'strategy': {'kind': 'null', 'metadata': {}},
        },
        'transactions_params': {},
        'invoice': {
            'id': invoice_id,
            'originator': 'eats_payments',
            'transactions_installation': 'eda',
        },
        'reason': {'code': 'some_code', 'metadata': {'from': 'admin'}},
        'created_at': '2021-03-08T00:00:00+00:00',
        'updated_at': '2021-03-09T00:00:00+00:00',
    }
