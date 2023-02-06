import pytest


TEMPLATE_ID = 'france-template-id'

COMPANY = {
    'name': 'name',
    'address': 'address',
    'email': 'email',
    'siret_number': 'siret_number',
    'rcs_number': 'rcs_number',
    'tva_number': 'tva_number',
}

RECEIPT_CONFIG = {
    'payment_title': 'receipt-payment-title',
    'refund_title': 'receipt-refund-title',
}

URL_TEMPLATE = 'https://receipts.com?id={}'

HEAD_HTML = 'head html'

RECEIPT_PARAMS = pytest.mark.experiments3(
    name='grocery_receipts_params_france',
    consumers=['grocery-invoices/stq'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'template_id': TEMPLATE_ID,
                'company': COMPANY,
                'receipt': RECEIPT_CONFIG,
                'url_template': URL_TEMPLATE,
                'head_html': HEAD_HTML,
            },
        },
    ],
    is_config=True,
)
