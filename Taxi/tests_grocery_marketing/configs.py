import pytest

GROCERY_MARKETING_HANDLE_STATUS_CHANGE = pytest.mark.experiments3(
    name='grocery_marketing_handle_status_change',
    consumers=['grocery-marketing/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Israel all off',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 131,
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                },
            },
            'value': {'enabled': False, 'send_adjust': False},
        },
        {
            'title': 'Russia all on',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 213,
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                },
            },
            'value': {'enabled': True, 'send_adjust': True},
        },
        {
            'title': 'Other',
            'predicate': {'type': 'true'},
            'value': {'enabled': True, 'send_adjust': False},
        },
    ],
    is_config=True,
)


def add_is_adjust_order_config(experiments3, enabled):
    experiments3.add_config(
        name='grocery_marketing_is_adjust_order',
        consumers=['grocery-marketing/common'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )


GROCERY_MARKETING_IS_ADJUST_ORDER = pytest.mark.experiments3(
    name='grocery_marketing_is_adjust_order',
    consumers=['grocery-marketing/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)

GROCERY_MARKETING_OPENED_DEPOT_PROCESSING = pytest.mark.experiments3(
    name='grocery_marketing_opened_depot_processing',
    consumers=['grocery-marketing/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'batch_size': 2, 'delay_minutes_count': 10},
        },
    ],
    is_config=True,
)
