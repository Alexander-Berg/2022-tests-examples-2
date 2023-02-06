import pytest


TEMPLATE_ID = 'great-britain-template-id'

COMPANY = {
    'name': 'great-britain-name',
    'address': 'great-britain-address',
    'email': 'great-britain-email',
    'description': 'great-britain-description',
    'registered_address': 'great-britain-registered_address',
    'business_address': 'great-britain-business_address',
}

URL_TEMPLATE = 'https://receipts.com?id={}'

HEAD_HTML = 'head html'

RECEIPT_PARAMS = pytest.mark.experiments3(
    name='grocery_receipts_params_great_britain',
    consumers=['grocery-invoices/stq'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'template_id': TEMPLATE_ID,
                'company': COMPANY,
                'url_template': URL_TEMPLATE,
                'head_html': HEAD_HTML,
            },
        },
    ],
    is_config=True,
)
