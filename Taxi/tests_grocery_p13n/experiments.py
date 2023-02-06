import pytest

# pylint: disable=invalid-name

GROCERY_DISCOUNTS_LABELS = pytest.mark.experiments3(
    name='grocery_discounts_labels',
    match={'predicate': {'type': 'true'}, 'enabled': True},
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
        {
            'predicate': {
                'init': {
                    'arg_name': 'has_parcels',
                    'arg_type': 'bool',
                    'value': True,
                },
                'type': 'eq',
            },
            'title': 'discount for a customer with pacels in depot',
            'value': {'labels': ['has_parcels_label']},
        },
    ],
    default_value={'labels': []},
    is_config=True,
)


CASHBACK_EXPERIMENT_RUSSIA = pytest.mark.experiments3(
    name='grocery_cashback',
    consumers=['grocery-p13n/discounts', 'grocery-p13n/cashback-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                    'value': 'RUS',
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)

CASHBACK_CHARGE_ENABLED = pytest.mark.experiments3(
    name='grocery_cashback_charge_enabled',
    consumers=['grocery-p13n/cashback-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)

CASHBACK_CHARGE_DISABLED = pytest.mark.experiments3(
    name='grocery_cashback_charge_enabled',
    consumers=['grocery-p13n/cashback-info'],
    clauses=[],
    default_value={'enabled': False},
    is_config=True,
)

GROCERY_DISCOUNTS_SURGE_ENABLED = pytest.mark.experiments3(
    name='grocery_discounts_surge_enabled',
    match={'predicate': {'type': 'true'}, 'enabled': True},
    consumers=['grocery-p13n/discounts'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)

GROCERY_DISCOUNTS_SURGE_DISABLED = pytest.mark.experiments3(
    name='grocery_discounts_surge_enabled',
    match={'predicate': {'type': 'true'}, 'enabled': True},
    consumers=['grocery-p13n/discounts'],
    clauses=[],
    default_value={'enabled': False},
    is_config=False,
)

PAYMENT_METHOD_DISCOUNT_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_payment_method_discount',
    consumers=['grocery-p13n/discounts'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=False,
)


def markdown_discounts_exp_(enabled):
    return pytest.mark.experiments3(
        name='grocery_enable_markdown_discounts',
        consumers=['grocery-p13n/discounts'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': False},
        is_config=True,
    )


MARKDOWN_DISCOUNTS_ENABLED = markdown_discounts_exp_(True)
MARKDOWN_DISCOUNTS_DISABLED = markdown_discounts_exp_(False)


def antifraud_check_exp_(enabled, cache_enabled=False):
    return pytest.mark.experiments3(
        name='grocery_enable_discount_antifraud',
        consumers=['grocery-antifraud'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enable': enabled, 'cache_enable': cache_enabled},
            },
        ],
        default_value={'enable': False},
        is_config=True,
    )


ANTIFRAUD_CHECK_ENABLED = antifraud_check_exp_(True)
ANTIFRAUD_CHECK_WITH_CACHE_ENABLED = antifraud_check_exp_(True, True)
ANTIFRAUD_CHECK_DISABLED = antifraud_check_exp_(False)


def check_labels_for_discounts(request, labels):
    assert set(
        request.json['common_conditions'].get('experiments', {}),
    ) == set(labels)


def generate_labels_experiment(name, is_config, labels):
    return pytest.mark.experiments3(
        name=name,
        consumers=['grocery-discounts-provider'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'labels': labels},
            },
        ],
        default_value={'labels': []},
        is_config=is_config,
    )
