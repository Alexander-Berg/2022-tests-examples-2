import pytest

from tests_grocery_communications import consts

OPENED_DEPOT_NOTIFICATION_INTENT = 'depot_opened_notification'
CANCEL_NOTIFICATION_INTENT = 'grocery_order_cycle_cancel'
MONEY_CANCEL_NOTIFICATION_INTENT = 'grocery_money_cancellation_intent'
ORDER_STATUS_NOTIFICATION_INTENT = 'grocery_order_cycle_common'
COMPENSATION_NOTIFICATION_INTENT = 'grocery_order_cycle_compensation'
ADMIN_COMPENSATION_NOTIFICATION_INTENT = 'grocery_admin_compensation'
ADMIN_PRESET_MESSAGE_INTENT = 'grocery_admin_preset_message'
ADMIN_CUSTOM_MESSAGE_INTENT = 'grocery_admin_custom_message'
RECEIPT_NOTIFICATION_INTENT = 'grocery_receipts'
SMS_ONLY_INTENT = 'grocery_support_on_order'

GROCERY_COMMUNICATIONS_OPEN_DEPOT_NOTIFICATION_INFO = pytest.mark.experiments3(
    name='grocery_communications_open_depot_notification_info',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Israel',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'ISR',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': {
                'push_text': 'החנות נפתחה!',
                'push_title': 'בצע את ההזמנה הראשונה!',
                'sms_text': 'החנות נפתחה',
            },
        },
        {
            'title': 'Russia',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': {
                'push_text': 'Лавка открылась!',
                'push_title': 'Сделайте первый заказ!',
                'sms_text': 'Лавка открылась',
            },
        },
        {
            'title': 'France',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'FRA',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': {
                'push_text': 'Le magasin est ouvert!',
                'push_title': 'Faites la première commande!',
                'sms_text': 'Le magasin est ouvert',
            },
        },
        {
            'title': 'Other',
            'predicate': {'type': 'true'},
            'value': {
                'push_text': 'The shop has opened!',
                'push_title': 'Make your first order!',
                'sms_text': 'The shop has opened',
            },
        },
    ],
    is_config=True,
)


GROCERY_COMMUNICATIONS_ORDERS_SUPPORT_NOTIFICATIONS_EXPERIMENT = (
    pytest.mark.experiments3(
        name='grocery_communications_orders_support_notifications',
        consumers=['grocery-communications'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'available_tanker_keys': [
                        'support_test_notification',
                        'test_tanker_key',
                    ],
                    'intent': 'test_intent',
                    'keyset': 'grocery_communications',
                    'send_sms_keys': ['test_tanker_key'],
                },
            },
        ],
        is_config=True,
    )
)


GROCERY_NEED_TO_HANDLE_OPENED_DEPOT_OFF = pytest.mark.experiments3(
    name='grocery_need_to_handle_opened_depot',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Off (item_id)',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': '666777-123',
                    'arg_name': 'item_id',
                    'arg_type': 'string',
                },
            },
            'value': {'enabled': False},
        },
        {
            'title': 'Off (batch_number)',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 5,
                    'arg_name': 'batch_number',
                    'arg_type': 'int',
                },
            },
            'value': {'enabled': False},
        },
        {
            'title': 'On',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)

GROCERY_ORDER_NOTIFICATION_OPTIONS = pytest.mark.experiments3(
    name='grocery_order_notification_options',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always True',
            'predicate': {'type': 'true'},
            'value': {'ignore_list': ['delivered', 'compensation']},
        },
    ],
    is_config=True,
)

GROCERY_RECEIPT_VIA_MAIL = pytest.mark.experiments3(
    name='grocery_communications_send_receipts_options',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'receipt_notification_type': 'receipt_via_email',
                'retry_interval': {'hours': 24},
                'error_after': {'hours': 48},
                'intent': 'custom_intent',
            },
        },
    ],
    is_config=True,
)

GROCERY_COMMUNICATIONS_INTENTS_CONFIG = pytest.mark.config(
    GROCERY_COMMUNICATIONS_INTENTS={
        'intents': [
            {
                'notification_type': 'order_cycle_common',
                'intent': ORDER_STATUS_NOTIFICATION_INTENT,
            },
            {
                'notification_type': 'order_cycle_cancel',
                'intent': CANCEL_NOTIFICATION_INTENT,
            },
            {
                'notification_type': 'order_cycle_money_fail',
                'intent': MONEY_CANCEL_NOTIFICATION_INTENT,
            },
            {
                'notification_type': 'order_cycle_compensation',
                'intent': COMPENSATION_NOTIFICATION_INTENT,
            },
            {
                'notification_type': 'admin_compensation',
                'intent': ADMIN_COMPENSATION_NOTIFICATION_INTENT,
            },
            {
                'notification_type': 'admin_preset_message',
                'intent': ADMIN_PRESET_MESSAGE_INTENT,
            },
            {
                'notification_type': 'admin_custom_message',
                'intent': ADMIN_CUSTOM_MESSAGE_INTENT,
            },
            {
                'notification_type': 'depot_opened',
                'intent': OPENED_DEPOT_NOTIFICATION_INTENT,
            },
            {
                'notification_type': 'receipts',
                'intent': RECEIPT_NOTIFICATION_INTENT,
            },
            {'notification_type': 'sms_only', 'intent': SMS_ONLY_INTENT},
        ],
    },
)

DEFERRED_NOTIFICATIONS_SETTINGS = pytest.mark.experiments3(
    name='grocery_communications_deferred_notifications_settings',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assigned_courier': {
                    'processing_type': 'prioritization',
                    'delay_time': {'minutes': 5},
                    'priority_policy': [
                        {
                            'notification_type': 'courier_picked_up_order',
                            'priority': 1,
                        },
                        {
                            'notification_type': 'courier_is_late',
                            'priority': 2,
                        },
                    ],
                },
                'status_change': {
                    'processing_type': 'prioritization',
                    'delay_time': {'seconds': 15},
                    'priority_policy': [
                        {
                            'priority': 1,
                            'notification_type': 'ready_for_pickup',
                        },
                        {'priority': 2, 'notification_type': 'accepted'},
                        {'priority': 3, 'notification_type': 'assembling'},
                        {'priority': 4, 'notification_type': 'common_failure'},
                        {'priority': 5, 'notification_type': 'money_failure'},
                        {
                            'priority': 6,
                            'notification_type': 'ready_for_dispatch',
                        },
                        {'priority': 7, 'notification_type': 'delivering'},
                        {'priority': 8, 'notification_type': 'delivered'},
                        {'priority': 9, 'notification_type': 'compensation'},
                    ],
                },
                'order_edited': {
                    'processing_type': 'push_with_chat',
                    'delay_time': {'minutes': 5},
                },
            },
        },
    ],
    is_config=True,
)

OPTIONAL_NOTIFICATIONS_SETTINGS = pytest.mark.experiments3(
    name='grocery_communications_optional_notifications_settings',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Push and chat',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'value': (
                                    'processing_v1_compensation_notification'
                                ),
                                'arg_name': 'handler_name',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'mobileweb_yango_iphone',
                                'arg_name': 'application',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {
                'notification_types': 'push_and_chat',
                'chat_options': {'maximal_push_availability': 'unknown'},
            },
        },
        {
            'title': 'Chat instead push',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'value': (
                                    'processing_v1_compensation_notification'
                                ),
                                'arg_name': 'handler_name',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'mobileweb_yango_android',
                                'arg_name': 'application',
                                'arg_type': 'string',
                            },
                        },
                    ],
                },
            },
            'value': {
                'notification_types': 'chat',
                'chat_options': {'maximal_push_availability': 'no'},
            },
        },
        {
            'title': 'Default',
            'predicate': {'type': 'true'},
            'value': {'notification_types': 'push'},
        },
    ],
    is_config=True,
)

GROCERY_MESSENGER_SUPPORT = pytest.mark.experiments3(
    name='grocery_messenger_support',
    consumers=['grocery-communications'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [
            {'name': 'yangodeli_iphone', 'version_range': {'from': '1.8.4'}},
            {'name': 'yangodeli_android', 'version_range': {'from': '1.8.4'}},
        ],
    },
    clauses=[
        {
            'title': 'Iphone',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'yangodeli_iphone',
                    'arg_name': 'application',
                    'arg_type': 'string',
                },
            },
            'value': {
                'chatId': 'chat-id',
                'enabled': True,
                'supportChatUrlRegexp': 'some-url',
                'supportChatOrderIdQueryParam': 'chat-order-id',
            },
        },
        {
            'title': 'Android',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'yangodeli_android',
                    'arg_name': 'application',
                    'arg_type': 'string',
                },
            },
            'value': {
                'chatId': 'chat-id',
                'enabled': False,
                'supportChatUrlRegexp': 'some-url',
                'supportChatOrderIdQueryParam': 'chat-order-id',
            },
        },
    ],
    is_config=False,
)

GROCERY_COMMUNICATIONS_TRACKING_DEEPLINK_PREFIX = pytest.mark.config(
    GROCERY_COMMUNICATIONS_TRACKING_DEEPLINK_PREFIX={
        'deeplink_prefixes': [
            {
                'applications': [consts.APP_IPHONE],
                'prefix': consts.LAVKA_TRACKING_DEEPLINK_PREFIX,
            },
            {
                'applications': [
                    consts.YANGO_ANDROID,
                    consts.YANGO_IPHONE,
                    consts.DELI_ANDROID,
                    consts.DELI_IPHONE,
                ],
                'prefix': consts.YANGODELI_TRACKING_DEEPLINK_PREFIX,
            },
        ],
    },
)
