import pytest


TEMPLATE_ID = 'rsa-template-id'

URL_TEMPLATE = 'https://receipts.com?id={}'

HEAD_HTML = 'head html'

RECEIPT_PARAMS = pytest.mark.experiments3(
    name='grocery_receipts_params_rsa',
    consumers=['grocery-invoices/stq'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'template_id': TEMPLATE_ID,
                'url_template': URL_TEMPLATE,
                'head_html': HEAD_HTML,
            },
        },
    ],
    is_config=True,
)
