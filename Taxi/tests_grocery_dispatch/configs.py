import pytest

ASSEMBLING_ETA = 5


DISPATCH_CLAIM_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_claim',
    consumers=['grocery_dispatch/dispatch'],
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
                'logistic_group': 'ya_eats_group',
                'requirement_meta_group': 'lavka',
                'taxi_class': 'express',
                'taxi_classes': ['lavka'],
            },
        },
        {
            'title': 'other',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'taxi_dispatch',
                    'arg_name': 'dispatch_option',
                    'arg_type': 'string',
                },
            },
            'value': {
                'claim_kind': 'delivery_service',
                'requirement_type': 'performer_group',
                'logistic_group': 'ya_eats_group',
                'requirement_meta_group': 'lavka',
                'taxi_class': 'express',
                'taxi_classes': ['lavka'],
            },
        },
    ],
    is_config=True,
)

DISPATCH_CLAIM_CONFIG_DEFAULT = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_claim',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'claim_kind': 'platform_usage',
        'taxi_class': 'express',
        'taxi_classes': ['lavka'],
    },
    is_config=True,
)

DISPATCH_CLAIM_CONFIG_CARGO = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_claim',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'claim_kind': 'delivery_service',
        'taxi_class': 'cargo',
        'taxi_classes': ['cargo'],
        'cargo_loaders': 1,
    },
    is_config=True,
)

DISPATCH_CLAIM_CONFIG_PULL_DISPATCH = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_claim',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'create-accepted',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'create_accepted',
                    'arg_name': 'create_handler_type',
                    'arg_type': 'string',
                },
            },
            'value': {
                'claim_kind': 'platform_usage',
                'taxi_class': 'lavka',
                'taxi_classes': ['lavka'],
            },
        },
        {
            'title': 'pedestrian',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'default_dispatch',
                    'arg_name': 'dispatch_option',
                    'arg_type': 'string',
                },
            },
            'value': {
                'claim_kind': 'platform_usage',
                'taxi_class': 'lavka',
                'taxi_classes': ['lavka'],
            },
        },
        {
            'title': 'other',
            'predicate': {'type': 'true'},
            'value': {
                'claim_kind': 'delivery_service',
                'taxi_class': 'express',
                'taxi_classes': ['courier'],
            },
        },
    ],
    is_config=True,
)

DISPATCH_GENERAL_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_general',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': ASSEMBLING_ETA,
                'accept_language': 'ru',
                'skip_door_to_door': False,
                'skip_client_notify': True,
                'skip_emergency_notify': False,
                'comment': 'Лавка',
                'user_name': 'Клиент',
                'depot_name': 'ЯндексЛавка',
                'emergency_contact_name': 'Поддержка Лавки',
                'emergency_contact_phone': '+79991234567',
                'depot_skip_confirmation': True,
                'use_depot_cache_coordinates': False,
                'user_skip_confirmation': True,
                'use_time_intervals_perfect': True,
                'use_time_intervals_strict': True,
                'use_time_intervals_endpoint': True,
                'time_intervals_endpoint_perfect_span': 10,
                'time_intervals_endpoint_strict_span': 15,
                'send_items_weight': True,
                'send_items_size': True,
                'add_postal_code_field_to_user_address': True,
            },
        },
    ],
    is_config=True,
)

MODELER_DECISION_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_modeler_decision',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'ld_modeler_th': 60,
                'primary_modeler_name': 'ld',
                'shadow_modeler_names': ['local'],
            },
        },
    ],
    is_config=True,
)

MODELER_DECISION_CONFIG_DISABLED = pytest.mark.experiments3(
    name='grocery_dispatch_modeler_decision',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always disabled',
            'predicate': {'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)

ETA_THRESHOLD_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_eta_modeler_threshold',
    consumers=['grocery_dispatch/depots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'eta': 600, 'overwrite_db_value': True},
    is_config=True,
)

MODELER_ORDERS_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_modeler_orders_options',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'included_statuses': ['idle', 'scheduled', 'rescheduling', 'matching'],
        'excluded_dispatch_types': [],
    },
    is_config=True,
)

DISPATCH_PRIORITY_CONFIG = pytest.mark.experiments3(
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_dispatch_priority',
    default_value={'dispatches': ['cargo_sync']},
    is_config=True,
)

DISPATCH_PRIORITY_CONFIG_FULL = pytest.mark.experiments3(
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_dispatch_priority',
    clauses=[
        {
            'title': 'ручное переназначение на конкретного курьера',
            'value': {'dispatches': ['cargo_forced_performer']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'bool',
                'init': {'arg_name': 'has_forced_performer'},
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'forced_order_batch',
            'value': {'dispatches': ['cargo_forced_performer']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'bool',
                'init': {'arg_name': 'has_forced_order_to_batch'},
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'Товары с тегом hot c истекшим таймаутом',
            'value': {'dispatches': ['cargo_sync']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'pending_timeout_exceeded',
                                'arg_name': 'dispatch_intent',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'Фоллбек по объему посылки',
            'value': {'dispatches': ['cargo_taxi']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 50625,
                                'arg_name': 'order_volume',
                                'arg_type': 'double',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'set': ['88119', '78299', '383017', '408554'],
                                'arg_name': 'depot_id',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'фоллбек по весу Россия',
            'value': {'dispatches': ['cargo_taxi']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 25000,
                                'arg_name': 'order_weight',
                                'arg_type': 'double',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'фоллбек по весу Израиль',
            'value': {'dispatches': ['cargo_taxi']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 10000,
                                'arg_name': 'order_weight',
                                'arg_type': 'double',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'set': ['298283', '396798'],
                                'arg_name': 'depot_id',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'фоллбек по моделеру все',
            'value': {'dispatches': ['cargo_taxi']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {'arg_name': 'modeler_decision'},
                            'type': 'bool',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'фоллбек по времени',
            'value': {'dispatches': ['cargo_taxi']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'cargo_taxi_intent',
                                'arg_name': 'dispatch_intent',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'Товары с тегом hot',
            'value': {'dispatches': ['pending']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'hot',
                                'arg_name': 'item_tags',
                                'set_elem_type': 'string',
                            },
                            'type': 'contains',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'UD по depot_id',
            'value': {'dispatches': ['cargo_united_dispatch']},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['pedestrian'],
                                'arg_name': 'delivery_type',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'value': 25000,
                                            'arg_name': 'order_weight',
                                            'arg_type': 'double',
                                        },
                                        'type': 'lt',
                                    },
                                    {
                                        'init': {'arg_name': 'order_weight'},
                                        'type': 'is_null',
                                    },
                                    {
                                        'init': {
                                            'value': 25000,
                                            'arg_name': 'order_weight',
                                            'arg_type': 'double',
                                        },
                                        'type': 'lt',
                                    },
                                ],
                            },
                            'type': 'any_of',
                        },
                        {
                            'init': {
                                'set': ['404224'],
                                'arg_name': 'depot_id',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
            },
            'is_tech_group': False,
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
    ],
    default_value={'dispatches': ['cargo_sync']},
    is_config=True,
)

DISPATCH_PRIORITY_CONFIG_TAXI = pytest.mark.experiments3(
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_dispatch_priority',
    default_value={'dispatches': ['cargo_taxi']},
    is_config=True,
)

DISPATCH_PRIORITY_CONFIG_UNITED_DISPATCH = pytest.mark.experiments3(
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='grocery_dispatch_priority',
    default_value={'dispatches': ['cargo_united_dispatch']},
    is_config=True,
)

DISPATCH_PRIORITY_CONFIG_SYNC = pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'dispatches': ['cargo_sync']},
    is_config=True,
)

DISPATCH_PRIORITY_CONFIG_TEST = pytest.mark.experiments3(
    name='grocery_dispatch_priority',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'dispatches': ['test']},
    is_config=True,
)

DISPATCH_COMMENT_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_comments',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'For pedestrian',
            'predicate': {
                'init': {'arg_name': 'use_pull_dispatch'},
                'type': 'bool',
            },
            'value': {
                'leave_under_door': 'leave_under_door_comment',
                'meet_outside': 'meet_outside_comment',
                'no_door_call': 'no_door_call_comment',
                'user_name': 'client_name_comment',
                'additional_phone_code': 'additional_phone_code_comment',
            },
        },
        {
            'title': 'For taxi',
            'predicate': {'type': 'true'},
            'value': {
                'leave_under_door': 'leave_under_door_comment_taxi',
                'meet_outside': 'meet_outside_comment',
                'no_door_call': 'no_door_call_comment',
                'user_name': 'client_name_comment',
                'additional_phone_code': 'additional_phone_code_comment',
            },
        },
    ],
    is_config=True,
)

CARGO_DISPATCHES_THR_ONE_DAY = pytest.mark.config(
    GROCERY_DISPATCH_CARGO_DISPATCHES_THR_SECONDS=86400,
)

DISPATCH_GENERAL_CONFIG_DEPOT_COORDS = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_general',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': 5,
                'accept_language': 'ru',
                'skip_door_to_door': False,
                'skip_client_notify': True,
                'skip_emergency_notify': False,
                'comment': 'Лавка',
                'user_name': 'Клиент',
                'depot_name': 'ЯндексЛавка',
                'emergency_contact_name': 'Поддержка Лавки',
                'emergency_contact_phone': '+79991234567',
                'depot_skip_confirmation': True,
                'use_depot_cache_coordinates': True,
                'user_skip_confirmation': True,
                'use_time_intervals_perfect': True,
                'use_time_intervals_strict': True,
                'use_time_intervals_endpoint': True,
                'time_intervals_endpoint_perfect_span': 10,
                'time_intervals_endpoint_strict_span': 15,
                'send_items_weight': True,
                'send_items_size': True,
            },
        },
    ],
    is_config=True,
)

DISPATCH_RESCHEDULE_MANUAL_DEFAULT = pytest.mark.experiments3(
    name='grocery_dispatch_reschedule',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'check_period': 300, 'failure_count': 1, 'enabled': True},
    is_config=True,
)

CARGO_AUTH_TOKEN_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_lavka_cargo_auth_token_key',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'always on',
            'predicate': {'type': 'true'},
            'value': {'token_key': 'b2b-taxi-auth-grocery-fra'},
        },
    ],
    is_config=True,
)

DISPATCH_GENERAL_CONFIG_LEAVE_UNDER_DOOR = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_general',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': 5,
                'accept_language': 'ru',
                'skip_door_to_door': False,
                'skip_client_notify': True,
                'skip_emergency_notify': False,
                'comment': 'Лавка',
                'user_name': 'Клиент',
                'depot_name': 'ЯндексЛавка',
                'emergency_contact_name': 'Поддержка Лавки',
                'emergency_contact_phone': '+79991234567',
                'depot_skip_confirmation': True,
                'use_depot_cache_coordinates': False,
                'user_skip_confirmation': True,
                'use_time_intervals_perfect': True,
                'use_time_intervals_strict': True,
                'use_time_intervals_endpoint': True,
                'time_intervals_endpoint_perfect_span': 10,
                'time_intervals_endpoint_strict_span': 15,
                'send_items_weight': True,
                'send_items_size': True,
                'send_lavka_leave_at_the_door': True,
            },
        },
    ],
    is_config=True,
)

DISPATCH_GENERAL_CONFIG_MODIFIER_AGE_CHECK = pytest.mark.experiments3(
    name='grocery_dispatch_cargo_general',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': 5,
                'accept_language': 'ru',
                'skip_door_to_door': False,
                'skip_client_notify': True,
                'skip_emergency_notify': False,
                'comment': 'Лавка',
                'user_name': 'Клиент',
                'depot_name': 'ЯндексЛавка',
                'emergency_contact_name': 'Поддержка Лавки',
                'emergency_contact_phone': '+79991234567',
                'depot_skip_confirmation': True,
                'use_depot_cache_coordinates': False,
                'user_skip_confirmation': True,
                'use_time_intervals_perfect': True,
                'use_time_intervals_strict': True,
                'use_time_intervals_endpoint': True,
                'time_intervals_endpoint_perfect_span': 10,
                'time_intervals_endpoint_strict_span': 15,
                'send_items_weight': True,
                'send_items_size': True,
                'send_lavka_leave_at_the_door': False,
                'send_modifier_age_check': True,
            },
        },
    ],
    is_config=True,
)

DISPATCH_WATCHDOG_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_watchdog',
    consumers=['grocery_dispatch/dispatch_watchdog'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'interval': 60,
        'is_enabled': True,
        'reschedule_options': {},
    },
    is_config=True,
)

DISPATCH_PENDING_RESCHEDULE_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_pending_reschedule',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'reschedule_options': {'dispatch_intent': 'pending_timeout_exceeded'},
    },
    is_config=True,
)

DISPATCH_BATCHING_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_disable_batching',
    consumers=['grocery_dispatch/dispatch'],
    clauses=[
        {
            'title': 'Disable fragile for batching',
            'predicate': {
                'init': {
                    'arg_name': 'item_tags',
                    'set_elem_type': 'string',
                    'value': 'fragile',
                },
                'type': 'contains',
            },
            'value': {'disable_batching': True},
        },
        {
            'title': 'Hot first in batch',
            'predicate': {
                'init': {
                    'arg_name': 'item_tags',
                    'set_elem_type': 'string',
                    'value': 'hot',
                },
                'type': 'contains',
            },
            'value': {'place_first_in_batch': True},
        },
    ],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'disable_batching': False},
    is_config=True,
)

DISPATCH_DEPOT_ADDRESS_CONFIG = pytest.mark.experiments3(
    name='grocery_dispatch_depot_address',
    consumers=['grocery_dispatch/depots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'use_depot_cache_coordinates': True},
    is_config=True,
)
