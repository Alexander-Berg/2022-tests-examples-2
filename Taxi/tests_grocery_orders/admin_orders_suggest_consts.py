HEADER = {'Accept-Language': 'ru', 'X-Remote-IP': '127.0.0.1'}
VIP_TYPE = 'slivki'

ORDER_HISTORY_DB_VALUES = [
    [
        ('status_change', {'to': 'draft'}),
        ('status_change', {'to': 'reserving'}),
        ('state_change', {'to': {'wms_reserve_status': 'success'}}),
        (
            'state_change',
            {
                'to': {
                    'hold_money_status': 'success',
                    'wms_reserve_status': 'success',
                },
            },
        ),
        (
            'payment_status_change',
            {
                'to_operation_info': {
                    'operation_type': 'create',
                    'status': 'success',
                    'operation_id': '123',
                },
            },
        ),
        ('status_change', {'to': 'reserved'}),
        (
            'admin_action',
            {
                'to_action_type': 'correct',
                'admin_info': {'x_yandex_login': 'super_admin_777'},
                'status': 'success',
            },
        ),
        (
            'order_correcting_status',
            {
                'to_order_correcting': 'correcting_checked',
                'correcting_result': 'success',
                'correcting_items': [
                    {'item_id': 'some_item_id', 'quantity': '3'},
                ],
                'correcting_type': 'remove',
            },
        ),
        ('status_change', {'to': 'assembling'}),
        (
            'dispatch_status_change',
            {
                'to_dispatch_status': 'created',
                'to_dispatch_cargo_status': 'new',
            },
        ),
        (
            'dispatch_status_change',
            {
                'to_dispatch_status': 'accepted',
                'to_dispatch_cargo_status': 'accepted',
                'to_dispatch_delivery_eta': 14,
            },
        ),
        (
            'state_change',
            {
                'to': {
                    'assembling_status': 'assembled',
                    'hold_money_status': 'success',
                    'wms_reserve_status': 'success',
                },
            },
        ),
        (
            'state_change',
            {
                'to': {
                    'assembling_status': 'assembled',
                    'hold_money_status': 'success',
                    'close_money_status': 'success',
                    'wms_reserve_status': 'success',
                },
            },
        ),
        ('status_change', {'to': 'assembled'}),
        ('status_change', {'to': 'delivering'}),
        (
            'dispatch_status_change',
            {
                'to_dispatch_status': 'accepted',
                'to_dispatch_cargo_status': 'performer_draft',
                'to_dispatch_delivery_eta': 14,
            },
        ),
        (
            'dispatch_status_change',
            {
                'to_dispatch_status': 'accepted',
                'to_dispatch_cargo_status': 'performer_draft',
                'to_dispatch_delivery_eta': 14,
            },
        ),
        (
            'dispatch_status_change',
            {
                'to_dispatch_status': 'accepted',
                'to_dispatch_cargo_status': 'performer_draft',
                'to_dispatch_delivery_eta': 14,
            },
        ),
        (
            'dispatch_status_change',
            {
                'to_dispatch_status': 'accepted',
                'to_dispatch_cargo_status': 'performer_draft',
                'to_dispatch_delivery_eta': 14,
            },
        ),
        ('status_change', {'to': 'pending_cancel'}),
        ('status_change', {'to': 'closed'}),
        (
            'items_refund',
            {
                'to_refund_type': 'partial',
                'refunded_items': [
                    {'item_id': 'some_random_item', 'quantity': '100500'},
                ],
            },
        ),
        (
            'admin_action',
            {
                'to_action_type': 'partial_refund',
                'admin_info': {'x_yandex_login': 'super_admin_777'},
            },
        ),
        (
            'admin_action',
            {
                'to_action_type': 'promocode',
                'admin_info': {'x_yandex_login': 'super_admin_777'},
                'status': 'fail',
            },
        ),
        (
            'create_cashback',
            {
                'compensation_id': 'a2ace908-5d18-4764-8593-192a1b535514',
                'compensation_source': 'admin_compensation',
                'compensation_value': 120,
                'status': 'success',
            },
        ),
    ],
    [
        ('status_change', {'to': 'draft'}),
        ('status_change', {'to': 'reserving'}),
        ('state_change', {'to': {'wms_reserve_status': 'success'}}),
        (
            'payment_status_change',
            {
                'to_operation_info': {
                    'operation_type': 'create',
                    'status': 'fail',
                    'operation_id': '123',
                    'errors': [
                        {
                            'payment_type': 'applepay',
                            'error_reason_code': 'not_enough_funds',
                        },
                    ],
                },
            },
        ),
        (
            'state_change',
            {
                'to': {
                    'hold_money_status': 'failed',
                    'wms_reserve_status': 'success',
                },
            },
        ),
        (
            'admin_action',
            {
                'to_action_type': 'cancel',
                'admin_info': {'x_yandex_login': 'super_admin_777'},
            },
        ),
        ('status_change', {'to': 'pending_cancel'}),
        (
            'state_change',
            {
                'to': {
                    'hold_money_status': 'failed',
                    'close_money_status': 'success',
                    'wms_reserve_status': 'success',
                },
            },
        ),
        (
            'state_change',
            {
                'to': {
                    'hold_money_status': 'failed',
                    'close_money_status': 'success',
                    'wms_reserve_status': 'success',
                },
            },
        ),
        ('status_change', {'to': 'canceled'}),
        ('items_refund', {'to_refund_type': 'full'}),
        (
            'create_cashback',
            {
                'compensation_id': 'a2ace908-5d18-4764-8593-192a1b535514',
                'compensation_source': 'admin_compensation',
                'compensation_value': 120,
                'status': 'fail',
            },
        ),
    ],
]

EXPECTED_ORDER_HISTORY_VALUES = [
    [
        ('status_change', {'status': 'draft'}),
        ('status_change', {'status': 'reserving'}),
        ('state_change', {'state': {'wms_reserve_status': 'success'}}),
        ('state_change', {'state': {'hold_money_status': 'success'}}),
        (
            'payment_status_change',
            {
                'payment_operation_info': {
                    'type': 'create',
                    'status': 'success',
                    'id': '123',
                },
            },
        ),
        ('status_change', {'status': 'reserved'}),
        (
            'admin_action',
            {
                'admin_action': {
                    'type': 'correct',
                    'admin_info': {'x_ya_login': 'super_admin_777'},
                    'status': 'success',
                },
            },
        ),
        (
            'order_correcting_status',
            {
                'correcting_info': {
                    'status': 'correcting_checked',
                    'result': 'success',
                    'correcting_items': [
                        {'item_id': 'some_item_id', 'quantity': '3'},
                    ],
                    'correcting_type': 'remove',
                },
            },
        ),
        ('status_change', {'status': 'assembling'}),
        ('dispatch_status_change', {'dispatch_status': 'created'}),
        ('dispatch_status_change', {'dispatch_status': 'accepted'}),
        ('state_change', {'state': {'assembling_status': 'assembled'}}),
        ('state_change', {'state': {'close_money_status': 'success'}}),
        ('status_change', {'status': 'assembled'}),
        ('status_change', {'status': 'delivering'}),
        ('dispatch_status_change', {'dispatch_status': 'accepted'}),
        ('status_change', {'status': 'pending_cancel'}),
        ('status_change', {'status': 'closed'}),
        (
            'items_refund',
            {
                'refund_info': {
                    'type': 'partial',
                    'refunded_items': [
                        {'item_id': 'some_random_item', 'quantity': '100500'},
                    ],
                },
            },
        ),
        (
            'admin_action',
            {
                'admin_action': {
                    'type': 'partial_refund',
                    'admin_info': {'x_ya_login': 'super_admin_777'},
                },
            },
        ),
        (
            'admin_action',
            {
                'admin_action': {
                    'type': 'promocode',
                    'admin_info': {'x_ya_login': 'super_admin_777'},
                    'status': 'fail',
                },
            },
        ),
        (
            'create_cashback',
            {
                'cashback_info': {
                    'compensation_id': 'a2ace908-5d18-4764-8593-192a1b535514',
                    'compensation_source': 'admin_compensation',
                    'compensation_value': 120,
                    'status': 'success',
                },
            },
        ),
    ],
    [
        ('status_change', {'status': 'draft'}),
        ('status_change', {'status': 'reserving'}),
        ('state_change', {'state': {'wms_reserve_status': 'success'}}),
        (
            'payment_status_change',
            {
                'payment_operation_info': {
                    'type': 'create',
                    'status': 'fail',
                    'id': '123',
                    'errors': [
                        {
                            'payment_type': 'applepay',
                            'error_reason_code': 'not_enough_funds',
                        },
                    ],
                },
            },
        ),
        ('state_change', {'state': {'hold_money_status': 'failed'}}),
        (
            'admin_action',
            {
                'admin_action': {
                    'type': 'cancel',
                    'admin_info': {'x_ya_login': 'super_admin_777'},
                },
            },
        ),
        ('status_change', {'status': 'pending_cancel'}),
        ('state_change', {'state': {'close_money_status': 'success'}}),
        ('status_change', {'status': 'canceled'}),
        ('items_refund', {'refund_info': {'type': 'full'}}),
        (
            'create_cashback',
            {
                'cashback_info': {
                    'compensation_id': 'a2ace908-5d18-4764-8593-192a1b535514',
                    'compensation_source': 'admin_compensation',
                    'compensation_value': 120,
                    'status': 'fail',
                },
            },
        ),
    ],
]

ADMIN_INFO_STATUSES = [
    (
        'closed',
        'canceled',
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'pickuped',
        'order_finished',
    ),
    (
        'canceled',
        None,
        None,
        'success',
        'success',
        None,
        None,
        'pickuped',
        'order_canceled',
    ),
    (
        'closed',
        'delivering',
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'pickuped',
        'order_finished',
    ),
    (
        'delivering',
        'closed',
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'ready_for_delivery_confirmation',
        'finishing_in_progress',
    ),
    (
        'closed',
        'closed',
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'ready_for_delivery_confirmation',
        'order_finished',
    ),
    (
        'delivering',
        'canceled',
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'ready_for_delivery_confirmation',
        'canceling_in_progress',
    ),
    (
        'canceled',
        'canceled',
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'ready_for_delivery_confirmation',
        'order_canceled',
    ),
    (
        'delivering',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'ready_for_delivery_confirmation',
        'performer_arrived_to_client',
    ),
    (
        'delivering',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'pickuped',
        'performer_took_the_order',
    ),
    (
        'delivering',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'ready_for_pickup_confirmation',
        'performer_arrived_to_depot',
    ),
    (
        'delivering',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'performer_found',
        'performer_found',
    ),
    (
        'delivering',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'performer_draft',
        'performer_lookup',
    ),
    (
        'assembled',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'accepted',
        'order_assembled',
    ),
    (
        'assembling',
        None,
        'success',
        'success',
        'success',
        None,
        None,
        'accepted',
        'order_assembling_started',
    ),
    (
        'reserving',
        None,
        'success',
        None,
        'success',
        'assembled',
        'delivering',
        'accepted',
        'payment_awaiting',
    ),
    (
        'reserving',
        None,
        'failed',
        'success',
        'success',
        'assembled',
        'delivering',
        'accepted',
        'wms_reservation_failed',
    ),
    (
        'reserving',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'accepted',
        'payment_success',
    ),
    (
        'reserving',
        None,
        'success',
        'failed',
        'success',
        'assembled',
        'delivering',
        'accepted',
        'payment_failed',
    ),
    (
        'checked_out',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'delivering',
        'accepted',
        'order_created',
    ),
    (
        'canceled',
        None,
        'success',
        'success',
        'failed',
        'assembled',
        'delivering',
        'accepted',
        'payment_failed',
    ),
    (
        'canceled',
        None,
        'success',
        'success',
        'success',
        'failed',
        'delivering',
        'accepted',
        'order_assembling_failed',
    ),
    (
        'canceled',
        None,
        'success',
        'success',
        'success',
        'assembled',
        'failed',
        'accepted',
        'dispatch_failed',
    ),
]

SPECIFIC_ORDER_TIMEZONE = 'Europe/Moscow'

SPECIFIC_ORDER = {
    'order_id': 'specific_order_id',
    'status': 'delivering',
    'desired_status': 'delivering',
    'client_price': '102',
    'depot_id': '12345',
    'bound_sessions': ['specific_bound_sessions'],
    'session': 'specific_session',
    'yandex_uid': 'specific_yandex_uid',
    'personal_phone_id': 'specific_personal_phone_id',
    'phone_id': 'specific_phone_id',
    'eats_user_id': 'specific_eats_user_id',
    'taxi_user_id': 'specific_taxi_user_id',
    'eats_order_id': 'specific_eats_order_id',
    'cart_id': '32d82a0f-7da0-459c-ba24-12ec11f30c99',
    'cart_version': 119,
    'short_order_id': 'specific_short_order_id',
    'order_version': 33,
    'assembling_status': 'assembled',
    'close_money_status': 'success',
    'hold_money_status': 'success',
    'wms_reserve_status': 'success',
    'doorcode': '119kk',
    'doorcode_extra': 'doorcode_extra',
    'doorbell_name': 'doorbell_name',
    'building_name': 'building_name',
    'left_at_door': False,
    'meet_outside': True,
    'no_door_call': True,
    'postal_code': 'SE16 3LR',
    'delivery_common_comment': 'comment',
    'place_id': 'yamaps...',
    'floor': '22',
    'flat': '89',
    'house': '12',
    'street': 'specific_street',
    'city': 'specific_city',
    'country': 'speceific_country',
    'app_info': 'specific_app_info',
    'cancel_reason_type': 'failure',
    'cancel_reason_message': 'specific cancel reason message',
    'currency': 'specific_currency',
    'grocery_flow_version': 'grocery_flow_v1',
    'dispatch_id': 'specific_dispatch_id',
    'dispatch_status': 'delivering',
    'dispatch_cargo_status': 'accepted',
    'dispatch_courier_name': 'specific_courier',
    'dispatch_delivery_eta': 15,
    'dispatch_status_meta': {
        'cargo_dispatch': {
            'batch_claim_ids': [
                '5218f37445de4fa890924f90f1165a95',
                '5920adbc7a0f45489445e938ccfd6367',
            ],
            'batch_order_num': 0,
            'dispatch_in_batch': True,
            'dispatch_delivery_type': 'courier',
        },
    },
    'created': '2020-05-25T17:20:45+00:00',
    'updated': '2020-05-25T17:35:45+00:00',
    'finished': '2020-05-25T17:43:45+00:00',
    'comment': 'specific_comment',
    'tips': 1.23,
    'tips_status': 'pending',
    'order_revision': 1,
    'billing_flow': 'grocery_payments',
    'timezone': SPECIFIC_ORDER_TIMEZONE,
    'locale': 'ru',
    'edit_status': 'success',
    'vip_type': VIP_TYPE,
    'push_notification_enabled': True,
    'personal_email_id': 'personal_email_id',
}

SPECIFIC_FEEDBACK = {
    'feedback_status': 'submitted',
    'evaluation': 5,
    'feedback_options': ['Качество продуктов'],
    'feedback_comment': 'Свежая еда',
}
