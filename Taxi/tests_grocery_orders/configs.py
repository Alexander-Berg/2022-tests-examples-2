import pytest


FORMATTER_CONFIGS = pytest.mark.config(
    GROCERY_LOCALIZATION_GROCERY_LOCALIZATIONS_KEYSET='grocery_localizations',
    GROCERY_LOCALIZATION_CURRENCIES_KEYSET='currencies',
    GROCERY_LOCALIZATION_CURRENCY_FORMAT={
        '__default__': {'precision': 2, 'rounding': '0.01'},
        'RUB': {'precision': 2, 'rounding': '0.01'},
        'GBP': {'precision': 2, 'rounding': '0.01'},
        'ILS': {'precision': 2, 'rounding': '0.01'},
    },
)

TRANSLATIONS_MARK = pytest.mark.translations(
    grocery_localizations={
        'decimal_separator': {'ru': ',', 'en': '.', 'fr': ',', 'he': '.'},
        'price_with_sign.default': {
            'ru': '$VALUE$$SIGN$',
            'en': '$VALUE$$SIGN$',
            'fr': '$VALUE$$SIGN$',
            'he': '$VALUE$$SIGN$',
        },
        'price_with_sign.gbp': {
            'ru': '$SIGN$$VALUE$',
            'en': '$SIGN$$VALUE$',
            'fr': '$SIGN$$VALUE$',
            'he': '$SIGN$$VALUE$',
        },
    },
    currencies={
        'currency_sign.eur': {'ru': '€', 'en': '€', 'fr': '€', 'he': '€'},
        'currency_sign.gbp': {'ru': '£', 'en': '£', 'fr': '£', 'he': '£'},
        'currency_sign.ils': {'ru': '₪', 'en': '₪', 'fr': '₪', 'he': '₪'},
        'currency_sign.rub': {'ru': '₽', 'en': '₽', 'fr': '₽', 'he': '₽'},
        'currency_sign.zar': {'ru': 'R', 'en': 'R', 'fr': 'R', 'he': 'R'},
    },
)


def add_feedback_comments_config(experiments3, evaluation_comments):
    experiments3.add_config(
        name='lavka_order_feedback_comments',
        consumers=['grocery-orders/feedback'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': f'{value} stars',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': evaluation,
                        'arg_name': 'evaluation',
                        'arg_type': 'int',
                    },
                },
                'value': value,
            }
            for evaluation, value in evaluation_comments.items()
        ],
    )


def add_lavka_dispatch_options(experiments3, dispatch_option):
    experiments3.add_config(
        name='lavka_dispatch_options',
        consumers=['grocery-orders/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'dispatch_option': dispatch_option},
            },
        ],
    )


def set_billing_flow(experiments3, billing_flow='grocery_payments'):
    experiments3.add_config(
        name='grocery_billing_flow',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'billing_flow': billing_flow},
            },
        ],
    )


def set_billing_settings_version(experiments3, settings_version):
    experiments3.add_config(
        name='grocery_billing_settings_version',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'version': settings_version},
            },
        ],
    )


def event_policy_config(names, value):
    return pytest.mark.experiments3(
        name='grocery_processing_events_policy',
        consumers=[
            'grocery-orders/processing-policy',
            'grocery-processing/policy',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Dispatch approve',
                'predicate': {
                    'init': {
                        'set': names,
                        'arg_name': 'name',
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
                'value': value,
            },
        ],
        is_config=True,
    )


def set_has_parcel_wms_tags(experiments3, parcel_tags):
    experiments3.add_config(
        name='grocery_orders_wms_tags',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Parcels tag',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'has_parcel',
                        'arg_type': 'int',
                        'value': 1,
                    },
                },
                'value': {'tags': parcel_tags},
            },
        ],
        default_value={'tags': []},
    )


def set_user_orders_count(experiments3, user_orders_count, count_tags):
    experiments3.add_config(
        name='grocery_orders_wms_tags',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'One wms tag',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'user_orders_completed',
                        'arg_type': 'int',
                        'value': user_orders_count,
                    },
                },
                'value': {'tags': count_tags},
            },
        ],
        default_value={'tags': []},
    )


SPECIAL_ITEM_ID = 'prohibited-item-id'

NO_MULTIORDER_GOODS_EXPERIMENT = pytest.mark.experiments3(
    name='no_multiorder_goods',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'multiple_dispatch_prohibited': True,
                'forcefully_ban_multiorder': False,
                'goods-to-exclude': [SPECIAL_ITEM_ID],
            },
        },
    ],
    default_value={},
    is_config=True,
)

GROCERY_PAYMENT_METHOD_VALIDATION = pytest.mark.experiments3(
    name='grocery_payment_method_validation',
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

GROCERY_DISPATCH_FLOW_EXPERIMENT = pytest.mark.experiments3(
    name='grocery_dispatch_flow',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'dispatch_flow': 'grocery_dispatch'},
        },
    ],
    is_config=True,
)

DISPATCH_SUPPLY_CONFIG = pytest.mark.experiments3(
    name='grocery_orders_dispatch_supply',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'taxi fallback',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 1,
                    'arg_name': 'is_taxi_fallback',
                    'arg_type': 'int',
                },
            },
            'value': {'supply_type': 'taxi'},
        },
        {
            'title': 'rover',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'rover',
                    'arg_name': 'delivery_type',
                    'arg_type': 'string',
                },
            },
            'value': {'supply_type': 'rover'},
        },
        {
            'title': 'for delivery_zone = pedestrian',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'pedestrian',
                    'arg_name': 'delivery_zone_type',
                    'arg_type': 'string',
                },
            },
            'value': {'supply_type': 'pedestrian'},
        },
        {
            'title': 'other',
            'predicate': {'type': 'true'},
            'value': {'supply_type': 'taxi'},
        },
    ],
    is_config=True,
)

DISPATCH_CLAIM_CONFIG = pytest.mark.experiments3(
    name='grocery_orders_dispatch_claim',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'pedestrian',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'pedestrian',
                    'arg_name': 'supply_type',
                    'arg_type': 'string',
                },
            },
            'value': {
                'claim_kind': 'platform_usage',
                'requirement_type': 'performer_group',
                'requirement_meta_group': 'lavka',
                'taxi_class': 'express',
                'taxi_classes': ['lavka'],
            },
        },
        {
            'title': 'rover',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'rover',
                    'arg_name': 'supply_type',
                    'arg_type': 'string',
                },
            },
            'value': {
                'claim_kind': 'delivery_service',
                'requirement_type': 'performer_group',
                'requirement_meta_group': 'lavka',
                'taxi_class': 'express',
                'taxi_classes': ['courier'],
                'assign_rover': True,
            },
        },
        {
            'title': 'other',
            'predicate': {'type': 'true'},
            'value': {
                'claim_kind': 'delivery_service',
                'requirement_type': 'performer_group',
                'requirement_meta_group': 'lavka',
                'taxi_class': 'express',
                'taxi_classes': ['courier'],
            },
        },
    ],
    is_config=True,
)


def handle_paid_delivery(experiments3, enabled):
    experiments3.add_config(
        name='lavka_handle_paid_delivery',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )


ASSEMBLING_ETA = 5
DISPATCH_GENERAL_CONFIG = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': ASSEMBLING_ETA,
                'cancel_minutes_threshold': 4,
            },
        },
    ],
    is_config=True,
)

USE_DYNAMIC_DELIVERY_ETA = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'use_dynamic_delivery_eta': True},
        },
    ],
    is_config=True,
)

GROCERY_ORDERS_SUBMIT_LIMIT = pytest.mark.experiments3(
    name='grocery_orders_submit_limit',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': False},
        },
    ],
    is_config=True,
)

GROCERY_ORDERS_ENABLED_WMS_TAGS = pytest.mark.experiments3(
    name='grocery_orders_enable_wms_tags',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true', 'init': {}},
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)

PASS_PAYMENT_METHOD_CHECKOUT_ENABLED = pytest.mark.config(
    GROCERY_ORDERS_PASS_PAYMENT_TO_CART_ENABLED=True,
)

PASS_PAYMENT_METHOD_CHECKOUT_ENABLED_EATS_CYCLE = pytest.mark.config(
    GROCERY_ORDERS_PASS_PAYMENT_TO_CART_ENABLED_EATS_CYCLE=True,
)

GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE = pytest.mark.config(
    GROCERY_ORDERS_ENABLE_CART_COMMIT_IN_SETSTATE=False,
)


def set_feedback_processing_rules(
        experiments3,
        evaluation_threshold,
        creating_tickets_enabled,
        ticket_queue,
        ticket_tags,
        create_chatterbox_ticket,
        macro_id=7,
):
    evaluation_set = list(range(1, evaluation_threshold + 1))
    experiments3.add_config(
        name='grocery_feedback_processing_rules',
        consumers=['grocery-orders/feedback-ticket'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Init chat enabled for special kwargs',
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'not',
                                'init': {
                                    'predicate': {
                                        'type': 'bool',
                                        'init': {'arg_name': 'has_comment'},
                                    },
                                },
                            },
                            {
                                'type': 'in_set',
                                'init': {
                                    'arg_name': 'evaluation',
                                    'set': [4, 5],
                                    'set_elem_type': 'int',
                                },
                            },
                            {
                                'type': 'contains',
                                'init': {
                                    'arg_name': 'feedback_options',
                                    'set_elem_type': 'string',
                                    'value': 'Качество продуктов',
                                },
                            },
                        ],
                    },
                },
                'value': {
                    'init_chat': True,
                    'macro_id': macro_id,
                    'creating_tickets_enabled': False,
                    'ticket_queue': ticket_queue,
                    'ticket_tags': ticket_tags,
                    'create_chatterbox_ticket': create_chatterbox_ticket,
                },
            },
            {
                'title': 'Creating tickets enabled for special kwargs',
                'predicate': {
                    'type': 'any_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'bool',
                                'init': {'arg_name': 'has_comment'},
                            },
                            {
                                'type': 'in_set',
                                'init': {
                                    'arg_name': 'evaluation',
                                    'set': evaluation_set,
                                    'set_elem_type': 'int',
                                },
                            },
                            {
                                'type': 'not_null',
                                'init': {'arg_name': 'feedback_options'},
                            },
                        ],
                    },
                },
                'value': {
                    'init_chat': False,
                    'creating_tickets_enabled': creating_tickets_enabled,
                    'ticket_queue': ticket_queue,
                    'ticket_tags': ticket_tags,
                    'create_chatterbox_ticket': create_chatterbox_ticket,
                },
            },
            {
                'title': 'Tickets creation disabled',
                'predicate': {'type': 'true'},
                'value': {
                    'init_chat': False,
                    'creating_tickets_enabled': False,
                    'ticket_queue': ticket_queue,
                    'ticket_tags': ticket_tags,
                    'create_chatterbox_ticket': create_chatterbox_ticket,
                },
            },
        ],
    )


GROCERY_ORDERS_WMS_SET_COURIER_WITH_PROCESSING = pytest.mark.config(
    GROCERY_ORDERS_WMS_SET_COURIER_WITH_PROCESSING=True,
)

GROCERY_ORDERS_ENABLE_CORRECTING_INSTEAD_CANCEL = pytest.mark.experiments3(
    name='grocery_orders_enable_correcting_instead_cancel',
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

GROCERY_ORDERS_WMS_PAUSE_DELAY = pytest.mark.config(
    GROCERY_ORDERS_WMS_PAUSE_DELAY=60,
)

CORRECTING_ENABLED = pytest.mark.experiments3(
    name='grocery_admin_correct_order',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True, 'addition_enabled': True},
        },
    ],
    is_config=True,
)

GROCERY_ITEMS_CORRECTION_TICKET_PARAMETERS = pytest.mark.experiments3(
    name='grocery_items_correction_ticket_parameters',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true', 'init': {}},
            'value': {
                'ticket_tags': ['lavka_testing_correcting'],
                'ticket_queue': 'LAVKA',
                'evaluation_threshold': 4,
                'create_chatterbox_ticket': False,
                'creating_tickets_enabled': True,
            },
        },
    ],
    is_config=True,
)

SUBMIT_RETRY_AFTER = 25
GROCERY_ORDERS_SUBMIT_RETRY_AFTER = pytest.mark.config(
    GROCERY_ORDERS_SUBMIT_RETRY_AFTER=SUBMIT_RETRY_AFTER,
)
