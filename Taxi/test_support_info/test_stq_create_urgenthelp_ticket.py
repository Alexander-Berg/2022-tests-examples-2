# pylint: disable=redefined-outer-name
import datetime

import pytest

from support_info import stq_task


NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(
    zendesk_forms={
        'urgenthelp_ticket.subject': {
            'en': 'Need urgent help',
            'ru': 'Надо ургентхелп',
        },
        'urgenthelp_ticket.body': {
            'en': 'Please call {phone!s}',
            'ru': 'Надо позвонить на {phone!s}',
        },
    },
)
@pytest.mark.parametrize(
    'task_id, owner_id, phone, metadata, order, order_proc, '
    'expected_create_chat, expected_tasks',
    [
        (
            '123_urgenthelp',
            '5d84f4a63934cf8f37562ffe',
            '+79000000000',
            {'source': 'app', 'locale': 'en'},
            {},
            {},
            {
                'data': None,
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'request_id': '123_urgenthelp',
                    'owner': {
                        'id': '5d84f4a63934cf8f37562ffe',
                        'role': 'client',
                        'platform': 'yandex',
                    },
                    'message': {
                        'text': 'Please call +79000000000',
                        'sender': {
                            'id': '5d84f4a63934cf8f37562ffe',
                            'role': 'client',
                            'platform': 'yandex',
                        },
                        'metadata': {'source': 'urgenthelp'},
                    },
                    'metadata': {
                        'user_application': 'yandex',
                        'owner_phone': '+79000000000',
                    },
                },
            },
            {
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'type': 'chat',
                    'external_id': '5cf82c4f629526419ea4486d',
                    'metadata': {
                        'update_meta': [
                            {
                                'change_type': 'set',
                                'field_name': 'locale',
                                'value': 'en',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'urgenthelp_source',
                                'value': 'app',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'ticket_subject',
                                'value': 'Need urgent help',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+79000000000',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'newest_message_id',
                                'value': 'some_message_id',
                            },
                        ],
                        'update_tags': [
                            {'change_type': 'add', 'tag': 'urgenthelp_task'},
                        ],
                    },
                },
            },
        ),
        (
            '123_urgenthelp',
            '5d84f4a63934cf8f37562ffe',
            '+79000000000',
            {
                'source': 'app',
                'phone': '+79000000000',
                'locale': 'ru',
                'orderid': '1',
                'driver_id': 'some_driver_id',
                'driver_uuid': 'some_driver_uuid',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_db_id',
                'user_platform': 'iphone',
            },
            {'_id': '1'},
            {
                '_id': '1',
                'order': {
                    'coupon': {
                        'id': 'coup_id',
                        'was_used': True,
                        'valid': True,
                        'value': 10,
                    },
                    'cost': 100,
                    'user_phone_id': '539eb65be7e5b1f53980dfa8',
                },
            },
            {
                'data': None,
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'request_id': '123_urgenthelp',
                    'owner': {
                        'id': '5d84f4a63934cf8f37562ffe',
                        'role': 'client',
                        'platform': 'iphone',
                    },
                    'message': {
                        'text': 'Надо позвонить на +79000000000',
                        'sender': {
                            'id': '5d84f4a63934cf8f37562ffe',
                            'role': 'client',
                            'platform': 'iphone',
                        },
                        'metadata': {
                            'driver_id': 'some_driver_id',
                            'driver_uuid': 'some_driver_uuid',
                            'order_alias_id': 'some_alias_id',
                            'order_id': '1',
                            'park_db_id': 'some_db_id',
                            'source': 'urgenthelp',
                        },
                    },
                    'metadata': {
                        'user_application': 'iphone',
                        'owner_phone': '+79000000000',
                    },
                },
            },
            {
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'type': 'chat',
                    'external_id': '5cf82c4f629526419ea4486d',
                    'metadata': {
                        'update_meta': [
                            {
                                'change_type': 'set',
                                'field_name': 'locale',
                                'value': 'ru',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_id',
                                'value': 'some_driver_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_uuid',
                                'value': 'some_driver_uuid',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_alias_id',
                                'value': 'some_alias_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'park_db_id',
                                'value': 'some_db_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_platform',
                                'value': 'iphone',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_id',
                                'value': '1',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'urgenthelp_source',
                                'value': 'app',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+79000000000',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'ticket_subject',
                                'value': 'Надо ургентхелп',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'paid_cancel_tag',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'tariff_currency',
                                'value': 'RUB',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'country',
                                'value': 'rus',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_currency',
                                'value': 'RUB',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_pre_distance_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_pre_time_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_pre_time_raw_minutes',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'amount_cashback',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_time_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_time_raw_minutes',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting',
                                'value': 'Нет',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_bool',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_cost',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'point_b_changed',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'success_order_flg',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'coupon_use_value',
                                'value': 10,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'paid_supply',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_cost',
                                'value': 90,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'fixed_price_order_flg',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': (
                                    'dif_ordercost_surge_surgecharge'
                                ),
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'surge_order_flg',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'cost_paid_supply',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'coupon',
                                'value': True,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'coupon_used',
                                'value': True,
                            },
                            {
                                'change_type': 'set',
                                'field_name': (
                                    'difference_fact_coupon_and_cost'
                                ),
                                'value': -90,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'multiorder',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_distance_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'cancel_distance_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'final_ride_duration',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_late_time',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_waiting_time',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'moved_to_cash_by_antifraud',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'payment_type_changed_to_cash',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'time_request',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'transportation_animals',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'baby_seat_services',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'door_to_door',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'created',
                                'value': '2018-06-15T12:34:00+0000',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_tips',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'final_transaction_status',
                                'value': 'no_transactions',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'payment_decisions',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'is_refund',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'is_compensation',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'several_ride_transactions',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'multipoints',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_arrived',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'customer_phone_type',
                                'value': 'yandex',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'customer_user_phone_id',
                                'value': '539eb65be7e5b1f53980dfa8',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'customer_user_phone',
                                'value': '+79000000000',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'customer_complete_rides',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'amount_charity',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_type',
                                'value': 'general',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'newest_message_id',
                                'value': 'some_message_id',
                            },
                        ],
                        'update_tags': [
                            {'change_type': 'add', 'tag': 'urgenthelp_task'},
                        ],
                    },
                },
            },
        ),
        (
            '123_urgenthelp',
            '539eb65be7e5b1f53980dfa8',
            '+79000000001',
            {
                'source': 'app',
                'phone': '+79000000001',
                'locale': 'fr',
                'orderId': '1',
                'driver_id': 'some_driver_id',
                'driver_uuid': 'some_driver_uuid',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_db_id',
                'user_platform': 'iphone',
            },
            {'_id': '1'},
            {
                '_id': '1',
                'order': {
                    'user_phone_id': '5d84f4a63934cf8f37562ffe',
                    'cashback_cost': 15,
                },
            },
            {
                'data': None,
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'request_id': '123_urgenthelp',
                    'owner': {
                        'id': '539eb65be7e5b1f53980dfa8',
                        'role': 'client',
                        'platform': 'iphone',
                    },
                    'message': {
                        'text': 'Please call +79000000001',
                        'sender': {
                            'id': '539eb65be7e5b1f53980dfa8',
                            'role': 'client',
                            'platform': 'iphone',
                        },
                        'metadata': {
                            'driver_id': 'some_driver_id',
                            'driver_uuid': 'some_driver_uuid',
                            'order_alias_id': 'some_alias_id',
                            'order_id': '1',
                            'park_db_id': 'some_db_id',
                            'source': 'urgenthelp',
                        },
                    },
                    'metadata': {
                        'user_application': 'iphone',
                        'owner_phone': '+79000000001',
                    },
                },
            },
            {
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'type': 'chat',
                    'external_id': '5cf82c4f629526419ea4486d',
                    'metadata': {
                        'update_meta': [
                            {
                                'change_type': 'set',
                                'field_name': 'locale',
                                'value': 'fr',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_id',
                                'value': 'some_driver_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_uuid',
                                'value': 'some_driver_uuid',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_alias_id',
                                'value': 'some_alias_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'park_db_id',
                                'value': 'some_db_id',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_platform',
                                'value': 'iphone',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_id',
                                'value': '1',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'urgenthelp_source',
                                'value': 'app',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+79000000001',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'ticket_subject',
                                'value': 'Need urgent help',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'paid_cancel_tag',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'tariff_currency',
                                'value': 'RUB',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'country',
                                'value': 'rus',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_currency',
                                'value': 'RUB',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_pre_distance_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_pre_time_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_pre_time_raw_minutes',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'amount_cashback',
                                'value': 15,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_time_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_time_raw_minutes',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting',
                                'value': 'Нет',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_bool',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'waiting_cost',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'point_b_changed',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'success_order_flg',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'coupon_use_value',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'paid_supply',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_cost',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'fixed_price_order_flg',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': (
                                    'dif_ordercost_surge_surgecharge'
                                ),
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'surge_order_flg',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'cost_paid_supply',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'coupon',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'coupon_used',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'multiorder',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_distance_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'cancel_distance_raw',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'final_ride_duration',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_late_time',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_waiting_time',
                                'value': 0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'moved_to_cash_by_antifraud',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'payment_type_changed_to_cash',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'time_request',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'transportation_animals',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'baby_seat_services',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'door_to_door',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'created',
                                'value': '2018-06-15T12:34:00+0000',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'order_tips',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'final_transaction_status',
                                'value': 'no_transactions',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'payment_decisions',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'is_refund',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'is_compensation',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'several_ride_transactions',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'multipoints',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'driver_arrived',
                                'value': False,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'amount_charity',
                                'value': 0.0,
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'newest_message_id',
                                'value': 'some_message_id',
                            },
                        ],
                        'update_tags': [
                            {'change_type': 'add', 'tag': 'urgenthelp_task'},
                        ],
                    },
                },
            },
        ),
    ],
)
async def test_create_urgenthelp_ticket(
        support_info_app_stq,
        patch_support_chat_create_chat,
        patch_chatterbox_tasks,
        mockserver,
        patch_get_order_by_id,
        patch_order_proc_retrieve,
        mock_get_user_phones,
        mock_persey_payments,
        mock_taxi_fleet,
        task_id,
        owner_id,
        phone,
        metadata,
        order,
        order_proc,
        expected_create_chat,
        expected_tasks,
):
    patch_get_order_by_id(order)
    patch_order_proc_retrieve(order_proc)

    @mockserver.json_handler('/user-api/user_phones', prefix=True)
    def _patch_request(request):
        return {'phone': metadata.get('phone')}

    mock_chat_create = patch_support_chat_create_chat(
        {
            'id': '5cf82c4f629526419ea4486d',
            'newest_message_id': 'some_message_id',
        },
    )
    mock_chatterbox_tasks = patch_chatterbox_tasks({'id': 'some_id'})
    await stq_task.create_urgenthelp_ticket(
        support_info_app_stq, task_id, owner_id, phone, metadata,
    )
    create_chat_calls = mock_chat_create.calls
    assert create_chat_calls[0]['kwargs'] == expected_create_chat

    tasks_calls = mock_chatterbox_tasks.calls
    assert tasks_calls[0]['kwargs'] == expected_tasks
