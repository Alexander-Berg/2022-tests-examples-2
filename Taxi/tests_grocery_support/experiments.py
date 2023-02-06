import copy

import pytest

from . import consts


CANCELMATRIX_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_cancel_reasons',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': '',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'predicate': {
                                    'init': {
                                        'value': 'canceled',
                                        'arg_name': 'order_status',
                                        'arg_type': 'string',
                                    },
                                    'type': 'eq',
                                },
                            },
                            'type': 'not',
                        },
                        {
                            'init': {
                                'value': 'pickup',
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'groups': [
                    {
                        'name': 'pickup',
                        'description': 'pickup',
                        'reasons': [
                            {
                                'name': 'out_of_stock',
                                'description': 'Отсутсвует товар',
                                'compensations': [
                                    {
                                        'type': 'promocode',
                                        'promocode_type': 'percent',
                                        'promocode_value': 10,
                                    },
                                    {
                                        'promocode_value': 300,
                                        'type': 'promocode',
                                        'promocode_type': 'fixed',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

CANCELMATRIX_COURIER = pytest.mark.experiments3(
    name='grocery_support_cancel_reasons',
    consumers=['grocery-support', 'grocery-support/bulk'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'bulk clause',
            'predicate': {
                'init': {
                    'value': True,
                    'arg_name': 'is_bulk',
                    'arg_type': 'bool',
                },
                'type': 'eq',
            },
            'value': {
                'groups': [
                    {
                        'name': 'service',
                        'description': 'courier_name',
                        'reasons': [
                            {
                                'name': 'technical_problems',
                                'description': 'Технические проблемы',
                                'compensations': [
                                    {
                                        'promocode_value': 40,
                                        'type': 'promocode',
                                        'promocode_type': 'percent',
                                    },
                                    {
                                        'promocode_value': 300,
                                        'type': 'promocode',
                                        'promocode_type': 'fixed',
                                    },
                                ],
                            },
                            {
                                'name': 'grocery_problems',
                                'description': 'Проблемы на лавке',
                                'compensations': [{'type': 'refund'}],
                            },
                        ],
                    },
                ],
            },
        },
        {
            'title': '',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'predicate': {
                                    'init': {
                                        'value': 'canceled',
                                        'arg_name': 'order_status',
                                        'arg_type': 'string',
                                    },
                                    'type': 'eq',
                                },
                            },
                            'type': 'not',
                        },
                        {
                            'init': {
                                'value': 'courier',
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'groups': [
                    {
                        'name': 'courier',
                        'description': 'courier_name',
                        'reasons': [
                            {
                                'name': 'out_of_stock',
                                'description': 'Отсутсвует товар',
                                'compensations': [
                                    {
                                        'promocode_value': 10,
                                        'type': 'promocode',
                                        'promocode_type': 'percent',
                                    },
                                    {
                                        'promocode_value': 300,
                                        'type': 'promocode',
                                        'promocode_type': 'fixed',
                                    },
                                ],
                            },
                            {
                                'name': 'cant_wait',
                                'description': 'Не хочет ждать',
                                'compensations': [{'type': 'refund'}],
                            },
                        ],
                    },
                ],
            },
        },
    ],
    is_config=True,
)

INFORMERS_CONFIG = pytest.mark.experiments3(
    name='grocery_support_informers_options',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': '',
            'predicate': {'type': 'true'},
            'value': {
                'courier_search_delay': 5,
                'courier_search_promocode_info': {
                    'delay': 10,
                    'compensation': {
                        'type': 'promocode',
                        'promocode_type': 'percent',
                        'promocode_value': 15,
                    },
                },
                'delivery_delay': 10,
                'delivery_promocode_info': {
                    'delay': 10,
                    'compensation': {
                        'type': 'promocode',
                        'promocode_type': 'percent',
                        'promocode_value': 15,
                    },
                },
            },
        },
    ],
    is_config=True,
)

EMPTY_PROMOCODE_INFORMERS_CONFIG = pytest.mark.experiments3(
    name='grocery_support_informers_options',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': '',
            'predicate': {'type': 'true'},
            'value': {'courier_search_delay': 5, 'delivery_delay': 10},
        },
    ],
    is_config=True,
)


LATE_ORDERS_MANUAL_PROACTIVE_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_late_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'delay': 5,
                },
                'auto_proactive_info': {
                    'compensations_info': [
                        {
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'percent',
                                'promocode_value': 15,
                            },
                            'delay': 10,
                        },
                    ],
                    'can_process_automatically': True,
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

PROACTIVE_SUPPORT_EXPENSIVE_ORDERS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_expensive_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'price_limit': consts.PRICE_LIMIT,
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

PROACTIVE_SUPPORT_VIP_ORDERS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_vip_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'vip_options': [
                        {
                            'vip_type': 'slivki',
                            'phone_id_tag': 'lavka_support_slivki',
                        },
                    ],
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

PROACTIVE_SUPPORT_FIRST_ORDERS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_first_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'order_count': consts.FIRST_ORDER_COUNT,
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

PROACTIVE_SUPPORT_FIRST_ORDERS_DELAYED_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_first_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'order_count': consts.FIRST_ORDER_COUNT,
                    'delay': consts.CREATION_DELAY,
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

PROACTIVE_SUPPORT_FIRST_ORDERS_EXPERIMENT_WITH_FLOW = pytest.mark.experiments3(
    name='grocery_support_proactive_first_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'manual_proactive_info': {
            'delay': 5,
            'order_count': 1,
            'tickets_options': {
                'ticket_tags': ['lavka_first_orders_TESTING'],
                'ticket_queue': 'LAVKA',
                'max_tickets_count': 10,
                'create_chatterbox_ticket': False,
                'creating_tickets_enabled': False,
            },
        },
    },
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'predicate': {
                                    'init': {
                                        'set': [
                                            'market_native_ios',
                                            'market_native_android',
                                            'market_old_ios',
                                            'market_old_android',
                                            'lavket_ios',
                                            'lavket_android',
                                            'lavket_desktop',
                                        ],
                                        'arg_name': 'application',
                                        'set_elem_type': 'string',
                                    },
                                    'type': 'in_set',
                                },
                            },
                            'type': 'not',
                        },
                        {
                            'init': {
                                'set': [
                                    'grocery_flow_v1',
                                    'grocery_flow_v2',
                                    'grocery_flow_v3',
                                ],
                                'arg_name': 'order_flow_version',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'order_count': consts.FIRST_ORDER_COUNT,
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

PROACTIVE_SUPPORT_CANCELED_ORDERS_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_support_proactive_canceled_orders',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Russia',
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {
                'manual_proactive_info': {
                    'tickets_options': {
                        'creating_tickets_enabled': True,
                        'max_tickets_count': 100,
                        'ticket_queue': consts.TICKET_QUEUE,
                        'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                        'create_chatterbox_ticket': True,
                    },
                    'cancel_reasons': [
                        {
                            'type': 'dispatch_failure',
                            'message': 'performer_not_found',
                        },
                    ],
                    'task_ttl': 1,
                },
                'auto_proactive_info': {
                    'compensations_info': [
                        {
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'fixed',
                                'promocode_value': 15,
                            },
                            'cancel_reason': {
                                'type': 'failure',
                                'message': 'reserve_failed',
                            },
                        },
                        {
                            'compensation': {
                                'type': 'promocode',
                                'promocode_type': 'fixed',
                                'promocode_value': 15,
                            },
                            'cancel_reason': {
                                'type': 'failure',
                                'message': 'technical_issues',
                            },
                            'issuance_freeze_duration': {'hours': 12},
                        },
                    ],
                    'can_process_automatically': True,
                },
            },
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

LATE_ORDER_SITUATIONS = pytest.mark.experiments3(
    name='grocery_support_late_order_situations',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': '',
            'predicate': {'type': 'true'},
            'value': {'situation_codes': ['test_code']},
        },
    ],
    is_config=True,
)

GROCERY_PROCESSING_EVENTS_POLICY = pytest.mark.experiments3(
    name='grocery_processing_events_policy',
    consumers=['grocery-processing/policy'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'save_informer',
            'predicate': {
                'init': {
                    'set': ['save_informer'],
                    'arg_name': 'name',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'error_after': {'minutes': 3},
                'retry_interval': {'seconds': 30},
                'stop_retry_after': {'minutes': 6},
            },
        },
        {
            'title': 'compensations',
            'predicate': {
                'init': {
                    'set': [
                        'compensation_notification',
                        'compensation_promocode',
                        'compensation_cashback',
                        'compensation_refund',
                        'compensation_partial_refund',
                        'apology_notification',
                    ],
                    'arg_name': 'name',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'error_after': {'minutes': 1},
                'retry_interval': {'seconds': 10},
                'stop_retry_after': {'minutes': 6},
            },
        },
    ],
    is_config=True,
)


GROCERY_SUPPORT_ALLOWED_ACTIONS_EXPIRATION_TIMES = pytest.mark.experiments3(
    name='grocery_support_allowed_actions_expiration_times',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': '',
            'predicate': {'type': 'true'},
            'value': {
                'refund_time': 24,
                'correct_add_time': 24,
                'cancel_time': 12,
                'compensation_time': 12,
            },
        },
    ],
    is_config=True,
)


GROCERY_SUPPORT_PROACTIVE_OPTIONS = pytest.mark.experiments3(
    name='grocery_support_proactive_options',
    consumers=['grocery-support'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'full_price > 1100',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'full_price',
                                'arg_type': 'double',
                                'value': 1100,
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'arg_name': 'total_completed_orders_count',
                                'arg_type': 'int',
                                'value': 1,
                            },
                            'type': 'lt',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'proactive_enabled': True,
                'max_duration_in_status': 5,
                'tickets_options': {
                    'creating_tickets_enabled': True,
                    'max_tickets_count': 100,
                    'ticket_queue': consts.TICKET_QUEUE,
                    'ticket_tags': copy.deepcopy(consts.TICKET_TAGS),
                    'create_chatterbox_ticket': True,
                },
            },
        },
        {
            'title': 'Proactive disabled',
            'predicate': {'type': 'true'},
            'value': {'proactive_enabled': False},
        },
    ],
    is_config=True,
)
