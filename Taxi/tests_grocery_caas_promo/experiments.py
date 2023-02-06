import pytest

# pylint: disable=invalid-name
GROCERY_DISCOUNTS_LABELS_HEADERS = {
    'X-YaTaxi-Session': 'taxi:1',
    'X-Yandex-UID': '1',
}

GROCERY_DISCOUNTS_LABELS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_discounts_labels',
    consumers=['grocery-discounts-provider'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'user_id',
                    'arg_type': 'string',
                    'value': '1',
                },
                'type': 'eq',
            },
            'title': 'good discount for first customer',
            'value': {'labels': ['from_user_id']},
        },
        {
            'predicate': {
                'init': {
                    'arg_name': 'geo_id',
                    'arg_type': 'string',
                    'value': '3',
                },
                'type': 'eq',
            },
            'title': 'good discount for first customer',
            'value': {'labels': ['from_geo_id']},
        },
    ],
    default_value={'labels': []},
    is_config=True,
)
