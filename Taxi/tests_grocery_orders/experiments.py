import pytest

from . import consts

TIPS_EXPERIMENT = pytest.mark.experiments3(
    name='lavka_tips_proposals',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Trsitero disabled',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'tristero_flow_v1',
                    'arg_name': 'order_flow_version',
                    'arg_type': 'string',
                },
            },
            'value': {},
        },
        {
            'title': 'Rover and Pickup disabled',
            'predicate': {
                'init': {
                    'predicate': {
                        'init': {
                            'set': ['eats_dispatch', 'courier'],
                            'arg_name': 'delivery_type',
                            'set_elem_type': 'string',
                        },
                        'type': 'in_set',
                    },
                },
                'type': 'not',
            },
            'value': {},
        },
        {
            'title': 'Always enabled ISR',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'ISR',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {'arg_name': 'payment_method_type'},
                            'type': 'not_null',
                        },
                    ],
                },
            },
            'value': {'tips_proposals': consts.ISR_TIPS_PROPOSALS},
        },
        {
            'title': 'Always enabled RUS',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {'arg_name': 'payment_method_type'},
                            'type': 'not_null',
                        },
                    ],
                },
            },
            'value': {'tips_proposals': consts.RUS_TIPS_PROPOSALS},
        },
    ],
    is_config=True,
)

MAPPED_TANKER_KEY = 'mapped_tanker_key'
RUS_CARD_MAPPED_TANKER_KEY = 'rus_card_mapped_tanker_key'
PAYMENTS_CLIENT_MAPPINGS_EXP = pytest.mark.experiments3(
    name='grocery_payments_client_mappings',
    consumers=['grocery-orders/payments_client_mappings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'RUS card',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'RUS',
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
                        {
                            'init': {
                                'value': 'not_enough_funds',
                                'arg_name': 'payment_error_code',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {'error_code': RUS_CARD_MAPPED_TANKER_KEY},
        },
    ],
    default_value={'error_code': MAPPED_TANKER_KEY},
    is_config=True,
)


def available_payment_types(payment_types):
    return pytest.mark.experiments3(
        name='grocery_orders_available_payment_types',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'payment_types': payment_types},
            },
        ],
        is_config=True,
    )


TRACKING_PAYMENTS_ERROR = pytest.mark.experiments3(
    name='grocery_tracking_payment_errors_enabled',
    consumers=['grocery-orders/submit'],
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


def available_payment_types_ext(
        countries_payment_types, default_payment_types,
):
    clauses = []
    for country_iso3, payment_types in countries_payment_types.items():
        clauses.append(
            {
                'title': country_iso3,
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': country_iso3,
                        'arg_name': 'country_iso3',
                        'arg_type': 'string',
                    },
                },
                'value': {'payment_types': payment_types},
            },
        )
    return pytest.mark.experiments3(
        name='grocery_orders_available_payment_types',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=clauses,
        default_value={'payment_types': default_payment_types},
        is_config=True,
    )


def set_simultaneous_orders_limit(experiments3, lim):
    experiments3.add_config(
        name='grocery_orders_simultaneous_orders_limit',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'total_limit': lim},
            },
        ],
    )


PAYMENT_TIMEOUT = pytest.mark.experiments3(
    name='grocery_orders_payment_timeout',
    consumers=['grocery-orders/submit'],
    default_value={'timeout_seconds': consts.PAYMENT_TIMEOUT_SECONDS},
    is_config=True,
)

CORRECT_INFO = pytest.mark.experiments3(
    name='grocery_orders_correct_info',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'allowed_radius': 100},
        },
    ],
    is_config=True,
)

WMS_RESERVE_TIMEOUT = pytest.mark.experiments3(
    name='grocery_orders_wms_reserve_timeout',
    consumers=['grocery-orders/submit'],
    default_value={'timeout_seconds': consts.WMS_RESERVE_TIMEOUT_SECONDS},
    is_config=True,
)

LAVKA_PROMOCODE_CONFIG = pytest.mark.experiments3(
    name='lavka_compensation_promocodes',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'equal 10',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 10,
                    'arg_name': 'promocode_value',
                    'arg_type': 'int',
                },
            },
            'value': {'series': {'percent': 'PERCENT_SERIES_10'}},
        },
        {
            'title': 'equal 20',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 20,
                    'arg_name': 'promocode_value',
                    'arg_type': 'int',
                },
            },
            'value': {'series': {'percent': 'PERCENT_SERIES_20'}},
        },
        {
            'title': 'Use new promocode flow',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 1337,
                    'arg_name': 'promocode_value',
                    'arg_type': 'int',
                },
            },
            'value': {
                'series': {'percent': 'FARADAY_SERIES'},
                'use_new_flow': True,
            },
        },
        {
            'title': 'less 100',
            'predicate': {
                'type': 'lte',
                'init': {
                    'value': 100,
                    'arg_name': 'promocode_value',
                    'arg_type': 'int',
                },
            },
            'value': {'series': {'fixed': 'FIXED_SERIES_100'}},
        },
        {
            'title': 'less 300',
            'predicate': {
                'type': 'lte',
                'init': {
                    'value': 300,
                    'arg_name': 'promocode_value',
                    'arg_type': 'int',
                },
            },
            'value': {'series': {'fixed': 'FIXED_SERIES_300'}},
        },
        {
            'title': 'Always enabled = default',
            'predicate': {'type': 'true'},
            'value': {'series': {'percent': 'PERCENT_SERIES'}},
        },
    ],
    is_config=True,
)


def antifraud_check_experiment(enabled, cache_enabled=False):
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


EDIT_ADDRESS = pytest.mark.experiments3(
    name='grocery_orders_enable_edit_address',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'statuses': ['created', 'assembling', 'assembled'],
            },
        },
    ],
    default_value={},
    is_config=True,
)

GOAL_RESERVATION = pytest.mark.experiments3(
    name='grocery_orders_goal_reservation',
    consumers=['grocery-orders/submit'],
    default_value={'goal_reserve_enabled': True, 'goal_release_enabled': True},
    is_config=True,
)
