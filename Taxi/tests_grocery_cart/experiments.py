# pylint: disable=too-many-lines, invalid-name
import pytest

GROCERY_ORDERS_WEIGHT_EXP = pytest.mark.experiments3(
    name='grocery_orders_weight',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Take netto',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '+79672529051',
                                'arg_name': 'personal_phone_id',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {
                'use_max': False,
                'weight': 'netto',
                'use_default': False,
                'default_weight': 1000,
            },
        },
        {
            'title': 'Take brutto',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '+79672529052',
                                'arg_name': 'personal_phone_id',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {
                'use_max': False,
                'weight': 'brutto',
                'use_default': False,
                'default_weight': 1000,
            },
        },
        {
            'title': 'Take max',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '+79672529053',
                                'arg_name': 'personal_phone_id',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {
                'use_max': True,
                'weight': 'brutto',
                'use_default': False,
                'default_weight': 1000,
            },
        },
        {
            'title': 'Take default',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '+79672529054',
                                'arg_name': 'personal_phone_id',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {
                'use_max': False,
                'weight': 'default',
                'use_default': False,
                'default_weight': 1000,
            },
        },
        {
            'title': 'Check use default',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '+79672529055',
                                'arg_name': 'personal_phone_id',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {
                'use_max': False,
                'weight': 'brutto',
                'use_default': True,
                'default_weight': 1000,
            },
        },
    ],
    default_value={},
    is_config=True,
)


def _get_pickup_exp(payload):
    return pytest.mark.experiments3(
        name='lavka_selloncogs',
        consumers=['internal:overlord-catalog:special-categories'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': payload,
            },
        ],
        default_value={'enabled': False},
        is_config=True,
    )


def _get_parcel_exp(payload):
    return pytest.mark.experiments3(
        name='lavka_parcel',
        consumers=['internal:overlord-catalog:special-categories'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': payload,
            },
        ],
        default_value={'enabled': False},
        is_config=True,
    )


def get_rover_zones_exp(enabled, default_value=False):
    return pytest.mark.experiments3(
        name='use_rover_depot_zones',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': default_value},
        is_config=True,
    )


def _get_parcel_sizes_exp(payload):
    return pytest.mark.experiments3(
        name='lavka_parcel_sizes',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': payload,
            },
        ],
        default_value={'enabled': False},
        is_config=True,
    )


def _get_delivery_types_exp(payload):
    return pytest.mark.experiments3(
        name='lavka_available_delivery_types',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'markdown',
                'is_signal': False,
                'is_paired_signal': False,
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': 1,
                                    'arg_name': 'has_markdown',
                                    'arg_type': 'int',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
                'value': {'delivery_types': ['pickup']},
            },
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': payload,
            },
        ],
        default_value={'enabled': False},
        is_config=True,
    )


GROCERY_ORDER_CYCLE_ENABLED = pytest.mark.experiments3(
    name='grocery_order_cycle_enabled',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Not matched by region_id',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 12,
                                'arg_name': 'region_id',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'Not matched by depot_id',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': '12345',
                                'arg_name': 'depot_id',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'Only parcels',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_parcel',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 0,
                                'arg_name': 'has_store',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'pickup',
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 213,
                                'arg_name': 'region_id',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': '0',
                                'arg_name': 'depot_id',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'Bad flow version for has parcel and markdown',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_markdown',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_parcel',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'FlowVersionV2 for has_parcel',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 1,
                    'arg_name': 'has_parcel',
                    'arg_type': 'int',
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'FlowVersionV1 for pickup and has_markdown',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'pickup',
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_markdown',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'FlowVersionV3 for pickup',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'pickup',
                    'arg_name': 'delivery_type',
                    'arg_type': 'string',
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'Exchange currency flow',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'card_issuer_country',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 'ISR',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 'card',
                                'arg_name': 'payment_method_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'No flow version for eats_dispatch',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'eats_dispatch',
                    'arg_name': 'delivery_type',
                    'arg_type': 'string',
                },
            },
            'value': {'enabled': False},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)

GROCERY_ORDER_CYCLE_DISABLED = pytest.mark.experiments3(
    name='grocery_order_cycle_enabled',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': False},
    is_config=True,
)

GROCERY_PARCEL_PAID_DELIVERY = pytest.mark.experiments3(
    name='grocery_parcel_paid_delivery',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Enable in one region_id',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'value': 213,
                                'arg_name': 'region_id',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': '0',
                                'arg_name': 'depot_id',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)

GROCERY_ORDER_FLOW_VERSION_CONFIG_PROD = pytest.mark.experiments3(
    name='grocery_order_flow_version',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Only parcels',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_parcel',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 0,
                                'arg_name': 'has_store',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'any_of',
                            'init': {
                                'predicates': [
                                    {
                                        'type': 'is_null',
                                        'init': {
                                            'arg_name': 'has_paid_delivery',
                                        },
                                    },
                                    {
                                        'type': 'eq',
                                        'init': {
                                            'value': 0,
                                            'arg_name': 'has_paid_delivery',
                                            'arg_type': 'int',
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'tristero_flow_v1'},
        },
        {
            'title': 'Only goal reward',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_goal_reward',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 0,
                                'arg_name': 'has_parcel',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 0,
                                'arg_name': 'has_store',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'any_of',
                            'init': {
                                'predicates': [
                                    {
                                        'type': 'is_null',
                                        'init': {
                                            'arg_name': 'has_paid_delivery',
                                        },
                                    },
                                    {
                                        'type': 'eq',
                                        'init': {
                                            'value': 0,
                                            'arg_name': 'has_paid_delivery',
                                            'arg_type': 'int',
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'integration_no_payment_flow_v1'},
        },
    ],
    default_value={},
    is_config=True,
)

GROCERY_ORDER_FLOW_VERSION_CONFIG = pytest.mark.experiments3(
    name='grocery_order_flow_version',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Not matched by region_id',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 12,
                                'arg_name': 'region_id',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'grocery_flow_v3'},
        },
        {
            'title': 'Not matched by depot_id',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': '12345',
                                'arg_name': 'depot_id',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'grocery_flow_v3'},
        },
        {
            'title': 'Only parcels',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_parcel',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 0,
                                'arg_name': 'has_store',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'pickup',
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 213,
                                'arg_name': 'region_id',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': '0',
                                'arg_name': 'depot_id',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'any_of',
                            'init': {
                                'predicates': [
                                    {
                                        'type': 'is_null',
                                        'init': {
                                            'arg_name': 'has_paid_delivery',
                                        },
                                    },
                                    {
                                        'type': 'eq',
                                        'init': {
                                            'value': 0,
                                            'arg_name': 'has_paid_delivery',
                                            'arg_type': 'int',
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'tristero_flow_v1'},
        },
        {
            'title': 'Bad flow version for has parcel and markdown',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_markdown',
                                'arg_type': 'int',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_parcel',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'blahblah_version'},
        },
        {
            'title': 'FlowVersionV2 for has_parcel',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 1,
                    'arg_name': 'has_parcel',
                    'arg_type': 'int',
                },
            },
            'value': {'flow_version': 'grocery_flow_v2'},
        },
        {
            'title': 'FlowVersionV1 for pickup and has_markdown',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {'type': 'true', 'init': {}},
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'pickup',
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 1,
                                'arg_name': 'has_markdown',
                                'arg_type': 'int',
                            },
                        },
                    ],
                },
            },
            'value': {'flow_version': 'grocery_flow_v1'},
        },
        {
            'title': 'FlowVersionV3 for pickup',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'pickup',
                    'arg_name': 'delivery_type',
                    'arg_type': 'string',
                },
            },
            'value': {'flow_version': 'grocery_flow_v3'},
        },
    ],
    default_value={},
    is_config=True,
)

ENABLED_PICKUP_EXP = _get_pickup_exp({'enabled': True})
ENABLED_PARCEL_EXP = _get_parcel_exp({'enabled': True})
ENABLED_PARCEL_SIZES_EXP = _get_parcel_sizes_exp({'enabled': True})
DELIVERY_TYPES_EXP = _get_delivery_types_exp(
    {'delivery_types': ['eats_dispatch', 'pickup']},
)


def eats_payments_flow(experiments3, enabled=True):
    experiments3.add_config(
        name='eats_payments_grocery',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': enabled},
    )


def _get_substitute_uncrossed_price_exp(*, enabled, default_value=False):
    return pytest.mark.experiments3(
        name='substitute_uncrossed_price',
        is_config=True,
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': default_value},
    )


SUBSTITUTE_UNCROSSED_PRICE = _get_substitute_uncrossed_price_exp(enabled=True)

SERVICE_TOKEN_FROM_CONFIG = 'config-service-token'
DEFAULT_SERVICE_TOKEN_FROM_CONFIG = 'config-service-token-default'


def grocery_service_token(experiments3, order_flow_version, country_iso3):
    experiments3.add_config(
        name='grocery_service_token',
        consumers=['grocery-cart/order-cycle'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'title',
                'is_signal': False,
                'is_paired_signal': False,
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': country_iso3,
                                    'arg_name': 'country_iso3',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'value': order_flow_version,
                                    'arg_name': 'order_flow_version',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
                'value': {'token': SERVICE_TOKEN_FROM_CONFIG},
            },
        ],
        default_value={'token': DEFAULT_SERVICE_TOKEN_FROM_CONFIG},
    )


def grocery_cashback_percent(experiments3, enabled=True, value='10'):
    experiments3.add_experiment(
        name='grocery_cashback_percent',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled, 'value': value},
            },
        ],
    )


CASHBACK_GROCERY_ORDER_ENABLED = pytest.mark.experiments3(
    name='grocery_order_cycle_cashback',
    consumers=['grocery-cart'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)

PROMOCODE_CHOOSE_ORDER_ENABLED_CYCLE = pytest.mark.experiments3(
    name='grocery_order_cycle_enabled',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Eats promocode',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'eats',
                                'arg_name': 'promocode_source',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {'enabled': False},
        },
    ],
    default_value={'enabled': True},
    is_config=True,
)

PROMOCODE_CHOOSE_ORDER_CYCLE = pytest.mark.experiments3(
    name='grocery_order_flow_version',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Taxi promocode',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'taxi',
                                'arg_name': 'promocode_source',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {'flow_version': 'grocery_flow_v1'},
        },
        {
            'title': 'No promocode',
            'predicate': {'type': 'true'},
            'value': {'flow_version': 'grocery_flow_v3'},
        },
    ],
    default_value={},
    is_config=True,
)


def add_lavka_cart_prices_config(
        experiments3,
        currency_min_value,
        precision,
        minimum_total_cost,
        minimum_item_price,
        promocode_rounding_value,
):
    experiments3.add_config(
        name='lavka_cart_prices',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'currency_min_value': currency_min_value,
                    'currency_precision': precision,
                    'minimum_total_cost': minimum_total_cost,
                    'minimum_item_price': minimum_item_price,
                    'promocode_rounding_value': promocode_rounding_value,
                },
            },
        ],
        default_value={},
    )


ITEMS_PRICING_ENABLED = pytest.mark.config(
    GROCERY_CART_ITEMS_PRICING_ENABLED=True,
)

GROCERY_PRICE_RISE_MAP = pytest.mark.experiments3(
    name='grocery_price_rise_map',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': 'wms_depot_id',
                },
                'type': 'eq',
            },
            'value': {
                'products_map': [
                    {'products_ids': ['item_id_1'], 'rise_coef': '3'},
                ],
            },
        },
    ],
    is_config=False,
)

DO_NOT_APPLY_PROMO = pytest.mark.experiments3(
    name='do_not_apply_promo',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'exclude_18_plus': True,
                'exclude_items_id': ['medicine_id'],
            },
        },
    ],
    default_value={},
    is_config=True,
)


MARKDOWN_DISCOUNTS_ENABLED = pytest.mark.experiments3(
    name='grocery_enable_markdown_discounts',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)


TIPS_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_tips_proposals',
    is_config=True,
    consumers=['grocery-tips-shared/tips'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Выкл для tristero',
            'enabled': True,
            'extension_method': 'replace',
            'predicate': {
                'init': {
                    'arg_name': 'order_flow_version',
                    'set': ['tristero_flow_v1'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {},
        },
        {
            'title': 'Выкл для pickup',
            'enabled': True,
            'extension_method': 'replace',
            'predicate': {
                'init': {
                    'arg_name': 'delivery_type',
                    'set': ['pickup'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {},
        },
        {
            'title': 'Always enabled RUS',
            'predicate': {'type': 'true'},
            'value': {
                'tips_proposals': ['49', '99', '149'],
                'tips_proposals_v2': [
                    {'amount': '49', 'amount_type': 'absolute'},
                    {'amount': '99', 'amount_type': 'absolute'},
                    {'amount': '149', 'amount_type': 'absolute'},
                ],
            },
        },
    ],
    default_value={},
)


def set_tips_payment_flow(experiments3, flow='with_order'):
    experiments3.add_config(
        name='grocery_tips_payment_flow',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'flow': flow},
            },
        ],
    )


def set_service_fee(experiments3, amount):
    experiments3.add_config(
        name='grocery_service_fee',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'amount': amount},
            },
        ],
    )


def set_checkout_discounts_apply_flow(experiments3, flow: str):
    experiments3.add_config(
        name='grocery_checkout_discounts_apply_flow',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'flow': flow},
            },
        ],
    )


ENABLE_BUNDLE_DISCOUNT_V2 = pytest.mark.experiments3(
    name='grocery_enable_combo_products',
    consumers=['grocery-cart'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True, 'enabled_combo_v2': True},
        },
    ],
    default_value={'enabled': False, 'enabled_combo_v2': True},
    is_config=False,
)


def set_delivery_conditions(
        experiments3, min_eta, max_eta, delivery, surge=True,
):
    experiments3.add_config(
        name='grocery-surge-delivery-conditions',
        consumers=['grocery-surge-client/surge'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'data': [
                        {
                            'payload': {
                                'surge': surge,
                                'min_eta_minutes': str(min_eta),
                                'max_eta_minutes': str(max_eta),
                                'delivery_conditions': [
                                    {
                                        'order_cost': '0',
                                        'delivery_cost': delivery['cost'],
                                    },
                                    {
                                        'order_cost': delivery[
                                            'next_threshold'
                                        ],
                                        'delivery_cost': delivery['next_cost'],
                                    },
                                ],
                            },
                            'timetable': [
                                {
                                    'to': '00:00',
                                    'from': '00:00',
                                    'day_type': 'everyday',
                                },
                            ],
                        },
                    ],
                    'enabled': True,
                },
            },
        ],
    )


def set_heavy_cart_settings(experiments3, is_heavy_cart_enabled, threshold=7):
    experiments3.add_experiment(
        name='grocery_heavy_cart_settings',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': is_heavy_cart_enabled,
                    'gross-weight-threshold': threshold,
                    'image-link': 'some-link',
                },
            },
        ],
        default_value={},
    )


EXCHANGE_CURRENCY_CHOOSE_ORDER_CYCLE = pytest.mark.experiments3(
    name='grocery_order_flow_version',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Exchange currency',
            'predicate': {'type': 'true'},
            'value': {'flow_version': 'exchange_currency'},
        },
    ],
    default_value={},
    is_config=True,
)


def grocery_api_enable_newbie_scoring(experiments3, enabled=True):
    experiments3.add_config(
        name='grocery_cart_newbie_scoring',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'mobileweb_android enabled',
                'predicate': {
                    'init': {
                        'arg_name': 'application',
                        'arg_type': 'string',
                        'value': 'mobileweb_android',
                    },
                    'type': 'eq',
                },
                'value': {'enabled': enabled},
            },
        ],
    )


def set_exchanger_currency_settings(
        experiments3, to_currency_precision='0.0001', empty_exp=False,
):
    value = {
        'currency_from': 'RUB',
        'currency_to': 'ILS',
        'to_currency_precision': str(to_currency_precision),
    }

    if empty_exp is True:
        value = {}

    experiments3.add_config(
        name='grocery_exchange_currency_settings',
        consumers=['grocery-cart/order-cycle'],
        default_value={'settings': value},
    )


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
