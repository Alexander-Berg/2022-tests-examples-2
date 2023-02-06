# pylint: disable=too-many-arguments,too-many-lines,protected-access
# pylint: disable=redefined-outer-name, too-many-locals
import datetime
import uuid

from aiohttp import web
import pytest

from taxi import discovery
from taxi.clients import support_chat

from support_info import constants
from support_info.api import callcenter


NOW = datetime.datetime(2018, 6, 15, 12, 34)


def _dummy_uuid4():
    return uuid.UUID(int=0, version=4)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    STARTRACK_SUPPORT_AVAILABLE_EMAILS=[
        'support@taxi.yandex.ru',
        'approved@email.com',
    ],
    STARTRACK_SUPPORT_AVAILABLE_QUEUES=['SUPPORT', 'APPROVED_QUEUE'],
)
@pytest.mark.parametrize(
    [
        'data',
        'headers',
        'order_proc_data',
        'order_data',
        'expected_support_chat_request',
        'expected_create_ticket',
        'expected_metadata',
        'expected_hidden_comment_begins',
    ],
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": "SSDFSA"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_11"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Дополнительно"
                    },
                    "id": 12152,
                    "slug": "add_info"
                },
                "value": "Стандартное обращение"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Email"
                    },
                    "id": 12149,
                    "slug": "user_email"
                },
                "value": "devnull@yandex.ru"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_9"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Дата и примерное время подачи такси"
                    },
                    "id": 12150,
                    "slug": "datetime"
                },
                "value": "2342"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона с которого звонили"
                    },
                    "id": 12146,
                    "slug": "caller_phone"
                },
                "value": "+79250325272"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_7"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Имя"
                    },
                    "id": 12147,
                    "slug": "name"
                },
                "value": null
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "eeeeeeee"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "+79250325272"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_2"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Кто обращается"
                    },
                    "id": 12136,
                    "slug": "role"
                },
                "value": "Клиент"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_3"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Решено самостоятельно"
                    },
                    "id": 12143,
                    "slug": "solved"
                },
                "value": "Нет"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_1"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Контактный центр"
                    },
                    "id": 12135,
                    "slug": "callcenter"
                },
                "value": "Аудиотеле"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
                constants.DUMP_META_IN_HEADERS: 'True',
                constants.META_TOP_FIELDS_HEADER: 'caller_phone,order_id,etc',
            },
            {
                '_id': 'SSDFSA',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {'_id': 'SSDFSA'},
            {
                'owner': {
                    'id': '+79250325272',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'request_id': 'request_1',
                'message': {
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'yandex',
                    },
                    'metadata': {'order_id': 'SSDFSA'},
                },
                'metadata': {
                    'user_application': 'yandex',
                    'owner_phone': '+79250325272',
                },
            },
            None,
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'add_info',
                        'value': 'Стандартное обращение',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'amount_cashback',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'amount_charity',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'baby_seat_services',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'callcenter',
                        'value': 'Аудиотеле',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'caller_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cancel_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'claim',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cost_paid_supply',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_use_value',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_used',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'created',
                        'value': '2018-06-15T12:34:00+0000',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_complete_rides',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_phone_type',
                        'value': 'uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone_id',
                        'value': '539eb65be7e5b1f53980dfa9',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'datetime',
                        'value': '2342',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'dif_ordercost_surge_surgecharge',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'door_to_door',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_arrived',
                        'value': False,
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
                        'field_name': 'final_ride_duration',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_transaction_status',
                        'value': 'no_transactions',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'fixed_price_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_compensation',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_refund',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'moved_to_cash_by_antifraud',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multipoints',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multiorder',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_cost',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'SSDFSA',
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
                        'field_name': 'order_tips',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_cancel_tag',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_supply',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_decisions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type_changed_to_cash',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'point_b_changed',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'role',
                        'value': 'Клиент',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'several_ride_transactions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'solved',
                        'value': 'Нет',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'success_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'surge_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff_currency',
                        'value': 'RUB',
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
                        'field_name': 'user_email',
                        'value': 'devnull@yandex.ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'general',
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
                        'field_name': 'waiting_time_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'waiting_time_raw_minutes',
                        'value': 0.0,
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            'caller_phone: +79250325272\norder_id: SSDFSA',
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": "SSDFSA"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_11"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Дополнительно"
                    },
                    "id": 12152,
                    "slug": "add_info"
                },
                "value": "Стандартное обращение"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Email"
                    },
                    "id": 12149,
                    "slug": "user_email"
                },
                "value": "test@TESS.RU"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_9"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Дата и примерное время подачи такси"
                    },
                    "id": 12150,
                    "slug": "datetime"
                },
                "value": "2342"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона с которого звонили"
                    },
                    "id": 12146,
                    "slug": "caller_phone"
                },
                "value": "+79250325272"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_7"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Имя"
                    },
                    "id": 12147,
                    "slug": "name"
                },
                "value": null
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "-"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "+79250325272"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_2"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Кто обращается"
                    },
                    "id": 12136,
                    "slug": "role"
                },
                "value": "Клиент"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_3"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Решено самостоятельно"
                    },
                    "id": 12143,
                    "slug": "solved"
                },
                "value": "Нет"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_1"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Контактный центр"
                    },
                    "id": 12135,
                    "slug": "callcenter"
                },
                "value": "Аудиотеле"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {
                '_id': 'SSDFSA',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {'_id': 'SSDFSA'},
            None,
            {
                'comment': None,
                'queue': 'SUPPORT',
                'summary': (
                    'Телефонное обращение в службу поддержки ' 'Яндекс.Такси'
                ),
                'description': '-',
                'unique': 'request_1',
                'tags': ['email_task'],
                'custom_fields': {
                    'emailFrom': 'test@TESS.RU',
                    'emailTo': ['support@taxi.yandex.ru'],
                    'emailCreatedBy': 'support@taxi.yandex.ru',
                    'OrderId': 'SSDFSA',
                    'CallCenterName': 'Аудиотеле',
                    'CallRecivedFromPhone': '+79250325272',
                    'userPhone': '+79250325272',
                    'userEmail': 'test@TESS.RU',
                    'country': 'rus',
                    'coupon': 'False',
                    'couponUsed': 'False',
                    'orderCost': '0',
                    'pointBChanged': 'False',
                    'userType': 'general',
                    'waitingCost': '0',
                },
            },
            None,
            None,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": "order_id"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "text"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "+79250325272"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "caller_phone"
                },
                "value": "+7901"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '539eb65be7e5b1f53980dfa8',
                    'user_id': 'user_id',
                    'user_locale': 'ru',
                    'city': 'Москва',
                    'performer': {
                        'car_number': 'car_number',
                        'phone': ['+791234', '+75678'],
                        'clid': '100500',
                        'uuid': 'driver_uuid',
                        'db_id': 'db_id',
                        'taxi_alias': {'id': 'alias_id'},
                        'tariff': {'class': 'ultima'},
                    },
                    'coupon': {'id': '123', 'valid': True, 'value': 10},
                    'request': {'comment': 'precomment'},
                    'cashback_cost': 10.0,
                },
                'performer': {'driver_id': 'clid_uuid'},
            },
            {'_id': 'order_id', 'payment_tech': {'type': 'applepay'}},
            {
                'owner': {
                    'id': '+79250325272',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'request_id': 'request_1',
                'message': {
                    'text': 'text',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'yandex',
                    },
                    'metadata': {
                        'driver_id': 'clid_uuid',
                        'park_db_id': 'db_id',
                        'order_id': 'order_id',
                        'order_alias_id': 'alias_id',
                        'driver_uuid': 'driver_uuid',
                    },
                },
                'metadata': {
                    'user_application': 'yandex',
                    'owner_phone': '+79250325272',
                },
            },
            None,
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'amount_cashback',
                        'value': 10.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'amount_charity',
                        'value': 15.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'baby_seat_services',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'caller_phone',
                        'value': '+7901',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cancel_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'car_number',
                        'value': 'car_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'claim',
                        'value': 'text',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': '100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cost_paid_supply',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_use_value',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_used',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'created',
                        'value': '2018-06-15T12:34:00+0000',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_app_version',
                        'value': '3.85.1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_complete_rides',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_phone_type',
                        'value': 'yandex',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_id',
                        'value': 'user_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone_id',
                        'value': '539eb65be7e5b1f53980dfa8',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_platform',
                        'value': 'android',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'dif_ordercost_surge_surgecharge',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'discount_ya_plus',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'door_to_door',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_arrived',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_id',
                        'value': 'clid_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_late_time',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+791234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': 'driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_waiting_time',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_ride_duration',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_transaction_status',
                        'value': 'no_transactions',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'fixed_price_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_compensation',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_refund',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'moved_to_cash_by_antifraud',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multipoints',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multiorder',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_alias_id',
                        'value': 'alias_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_cost',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_disp_status',
                        'value': 'some_reason',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'order_id',
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
                        'field_name': 'order_tips',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_cancel_tag',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_supply',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'db_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_driver_profile_id',
                        'value': 'db_id_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'park_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_phone',
                        'value': '+79123',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_decisions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type',
                        'value': 'applepay',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type_changed_to_cash',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_car_number',
                        'value': 'car_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_clid',
                        'value': '100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_phone',
                        'value': '+791234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_uuid',
                        'value': 'driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_db_id',
                        'value': 'db_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_driver_profile_id',
                        'value': 'db_id_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_name',
                        'value': 'park_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_phone',
                        'value': '+79123',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_taximeter_version',
                        'value': '7.07',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'point_b_changed',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'precomment',
                        'value': 'precomment',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'several_ride_transactions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'success_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'surge_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff',
                        'value': 'ultima',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '7.07',
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
                        'field_name': 'user_locale',
                        'value': 'ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip',
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
                        'field_name': 'priority_list',
                        'value': {
                            'Дезинфекция машины': 2,
                            'Поездки с музыкой': 2,
                        },
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": "order_id"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "text"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "-"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "caller_phone"
                },
                "value": "+79250325273"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '539eb65be7e5b1f53980dfa9',
                    'user_id': 'user_id1',
                    'user_locale': 'en',
                    'city': 'Москва',
                    'performer': {
                        'car_number': 'car_number',
                        'phone': ['+791234', '+75678'],
                        'clid': '100500',
                        'uuid': 'driver_uuid',
                        'db_id': 'db_id',
                        'taxi_alias': {'id': 'alias_id_1'},
                        'tariff': {'class': 'ultima'},
                    },
                    'coupon': {
                        'id': '123',
                        'was_used': True,
                        'valid': True,
                        'value': 10,
                    },
                    'nz': 'erevan',
                    'request': {'comment': 'precomment'},
                    'cashback_cost': 10.0,
                },
            },
            {'_id': 'order_id', 'payment_tech': {'type': 'corp'}},
            {
                'owner': {
                    'id': '+79250325273',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'request_id': 'request_1',
                'message': {
                    'text': 'text',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325273',
                        'platform': 'yandex',
                    },
                    'metadata': {
                        'driver_uuid': 'driver_uuid',
                        'order_id': 'order_id',
                        'order_alias_id': 'alias_id_1',
                        'park_db_id': 'db_id',
                    },
                },
                'metadata': {
                    'user_application': 'yandex',
                    'owner_phone': '+79250325273',
                },
            },
            None,
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'amount_cashback',
                        'value': 10.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'amount_charity',
                        'value': 15.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'baby_seat_services',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'caller_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cancel_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'car_number',
                        'value': 'car_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'claim',
                        'value': 'text',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': '100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cost_paid_supply',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'arm',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_use_value',
                        'value': 10,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_used',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'created',
                        'value': '2018-06-15T12:34:00+0000',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_app_version',
                        'value': '3.8.1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_complete_rides',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_phone_type',
                        'value': 'uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_id',
                        'value': 'user_id1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone_id',
                        'value': '539eb65be7e5b1f53980dfa9',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_platform',
                        'value': 'iphone',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'dif_ordercost_surge_surgecharge',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'discount_ya_plus',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'door_to_door',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_arrived',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_late_time',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+791234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': 'driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_waiting_time',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_ride_duration',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_transaction_status',
                        'value': 'no_transactions',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'fixed_price_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_compensation',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_refund',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'moved_to_cash_by_antifraud',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multipoints',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multiorder',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_alias_id',
                        'value': 'alias_id_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_cost',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_disp_status',
                        'value': 'some_reason',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'order_id',
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
                        'field_name': 'order_tips',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_cancel_tag',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_supply',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'db_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_driver_profile_id',
                        'value': 'db_id_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'park_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_phone',
                        'value': '+79123',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_decisions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type',
                        'value': 'corp',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type_changed_to_cash',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_car_number',
                        'value': 'car_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_clid',
                        'value': '100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_phone',
                        'value': '+791234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_uuid',
                        'value': 'driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_db_id',
                        'value': 'db_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_driver_profile_id',
                        'value': 'db_id_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_name',
                        'value': 'park_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_phone',
                        'value': '+79123',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_taximeter_version',
                        'value': '7.07',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'point_b_changed',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'precomment',
                        'value': 'precomment',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'several_ride_transactions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'success_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'surge_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff',
                        'value': 'ultima',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '7.07',
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
                        'field_name': 'user_locale',
                        'value': 'en',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'corp',
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
                        'field_name': 'zone',
                        'value': 'erevan',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'priority_list',
                        'value': {
                            'Дезинфекция машины': 2,
                            'Поездки с музыкой': 2,
                        },
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": null
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "text"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "+79250325273"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "caller_phone"
                },
                "value": "-"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {},
            {},
            {
                'owner': {
                    'id': '+79250325273',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'request_id': 'request_1',
                'message': {
                    'text': 'text',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325273',
                        'platform': 'yandex',
                    },
                    'metadata': {},
                },
                'metadata': {
                    'user_application': 'yandex',
                    'owner_phone': '+79250325273',
                },
            },
            None,
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'claim',
                        'value': 'text',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": null
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "text"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Email"
                    },
                    "id": 12149,
                    "slug": "user_email"
                },
                "value": "devnull@yandex.ru"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "devnull@yandex.ru"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "caller_phone"
                },
                "value": "devnull@yandex.ru"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
                'YaTaxi-queue': 'APPROVED_QUEUE',
                'YaTaxi-emailTo': 'Approved@email.com',
                'YaTaxi-summary': '\\u042d\\u0442\\u043e summary',
                'YaTaxi-tags': 'best_of_the_best_tags,  \\u042d,pulya',
                constants.DUMP_META_IN_HEADERS: 'True',
                constants.META_TOP_FIELDS_HEADER: 'caller_phone,claim',
            },
            {},
            {},
            None,
            {
                'comment': (
                    'caller_phone: devnull@yandex.ru\n'
                    'claim: text\n'
                    'user_email: devnull@yandex.ru\n'
                    'request_id: request_1'
                ),
                'queue': 'APPROVED_QUEUE',
                'summary': 'Это summary',
                'description': 'text',
                'unique': 'request_1',
                'tags': [
                    'best_of_the_best_tags',
                    'Э',
                    'pulya',
                    'cc_task_nophone',
                ],
                'custom_fields': {
                    'emailFrom': 'devnull@yandex.ru',
                    'emailTo': ['approved@email.com'],
                    'emailCreatedBy': 'approved@email.com',
                    'userEmail': 'devnull@yandex.ru',
                    'CallRecivedFromPhone': 'devnull@yandex.ru',
                },
            },
            None,
            'caller_phone: devnull@yandex.ru\nclaim: text',
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Кто обратился?"
                    },
                    "id": 12147,
                    "slug": "requester"
                },
                "value": "client"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_11"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Тема обращения клиента:"
                    },
                    "id": 12148,
                    "slug": "client_subject_id"
                },
                "value": "64412"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона:"
                    },
                    "id": 12149,
                    "slug": "user_phone"
                },
                "value": "+79250325272"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_9"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Комментарий:"
                    },
                    "id": 12150,
                    "slug": "claim"
                },
                "value": "мне оторвали ногу"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
                'YaTaxi-form-type': 'ar_form',
            },
            None,
            None,
            {
                'owner': {
                    'id': 'ar_form+79250325272',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'request_id': 'request_1',
                'message': {
                    'text': 'мне оторвали ногу',
                    'sender': {
                        'role': 'sms_client',
                        'id': 'ar_form+79250325272',
                        'platform': 'yandex',
                    },
                    'metadata': {},
                },
                'metadata': {
                    'user_application': 'yandex',
                    'owner_phone': '+79250325272',
                },
            },
            None,
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'claim',
                        'value': 'мне оторвали ногу',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'client_subject_id',
                        'value': '64412',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'requester',
                        'value': 'client',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                ],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'sms_autoreply_task'},
                    {'change_type': 'add', 'tag': 'sms_task'},
                ],
            },
            None,
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "db id таксопарка"
                    },
                    "id": 12151,
                    "slug": "db_id"
                },
                "value": 100500
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Страна"
                    },
                    "id": 12144,
                    "slug": "city"
                },
                "value": "Москва"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": ""
                    },
                    "id": 12144,
                    "slug": "city"
                },
                "value": "Москва"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Клид"
                    },
                    "id": 12149,
                    "slug": "clid"
                },
                "value": "clid"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "почта куда будут приходить письма с трекера"
                    },
                    "id": 12145,
                    "slug": "park_email"
                },
                "value": "parkmail@parkmail.mail"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Название парка"
                    },
                    "id": 12145,
                    "slug": "database"
                },
                "value": "Парк Нейм"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "тип диспетчерской"
                    },
                    "id": 12145,
                    "slug": "product"
                },
                "value": "Тип Продукта"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Парк ID"
                    },
                    "id": 12145,
                    "slug": "db_id"
                },
                "value": "1331221"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "eeeeeeee"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'X-FORM-ID': '4432',
                'YaTaxi-FIELD-db_ID': (
                    '\\u041b\\u044f \\u043f\\u0430\\u0446\\u0430\\u043d\\u044b'
                ),
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {},
            {},
            None,
            {
                'comment': None,
                'queue': 'SUPPORT',
                'summary': (
                    'Телефонное обращение в службу поддержки ' 'Яндекс.Такси'
                ),
                'description': 'eeeeeeee',
                'unique': 'request_1_4432',
                'tags': ['cc_task_nophone'],
                'custom_fields': {
                    'city': 'Москва',
                    'clid': 'clid',
                    'parkDbId': 'Ля пацаны',
                    'parkName': 'Парк Нейм',
                    'parkEmail': 'parkmail@parkmail.mail',
                    'emailFrom': 'parkmail@parkmail.mail',
                    'emailTo': ['support@taxi.yandex.ru'],
                    'emailCreatedBy': 'support@taxi.yandex.ru',
                },
            },
            None,
            None,
        ),
    ],
)
async def test_callcenter_form(
        support_info_client,
        support_info_app,
        territories_mock,
        patch_aiohttp_session,
        order_archive_mock,
        response_mock,
        mock_st_create_ticket,
        mock_get_user_phones,
        mock_get_users,
        mock_personal,
        mock_driver_profiles,
        mock_driver_trackstory,
        mock_driver_priority,
        mock_persey_payments,
        mock_taxi_fleet,
        data,
        headers,
        order_proc_data,
        order_data,
        expected_support_chat_request,
        expected_create_ticket,
        expected_metadata,
        expected_hidden_comment_begins,
):
    if order_proc_data:
        order_archive_mock.set_order_proc(order_proc_data)

    chatterbox_url = discovery.find_service('chatterbox').url
    support_chat_url = discovery.find_service('support_chat').url
    archive_api_url = support_info_app.settings.ARCHIVE_API_URL

    if (
            expected_create_ticket
            and headers.get(constants.DUMP_META_IN_HEADERS) == 'True'
    ):
        assert expected_create_ticket['comment'] is not None
        if expected_hidden_comment_begins is not None:
            assert expected_create_ticket['comment'].startswith(
                expected_hidden_comment_begins,
            )
    elif (
        expected_create_ticket
        and not headers.get(constants.DUMP_META_IN_HEADERS) == 'True'
    ):
        assert expected_create_ticket['comment'] is None

    @patch_aiohttp_session(support_chat_url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        assert url == support_chat_url + '/v1/chat'
        assert kwargs['json'] == expected_support_chat_request
        return response_mock(json={'id': 'chat_id'})

    @patch_aiohttp_session(archive_api_url, 'POST')
    def _dummy_archive_api_request(method, url, **kwargs):
        assert url == archive_api_url + '/archive/order'
        if order_data:
            return response_mock(json={'doc': order_data})
        return response_mock(status=404)

    @patch_aiohttp_session(chatterbox_url, 'POST')
    def _dummy_chatterbox_request(method, url, **kwargs):
        assert url == chatterbox_url + '/v1/tasks'
        meta = kwargs['json'].pop('metadata')
        if constants.DUMP_META_IN_HEADERS in headers:
            hidden = kwargs['json'].pop('hidden_comment')
            assert hidden and 'None' not in hidden
            if expected_hidden_comment_begins is not None:
                assert hidden.startswith(expected_hidden_comment_begins)
        assert kwargs['json'] == {'external_id': 'chat_id', 'type': 'chat'}
        assert (
            sorted(meta['update_meta'], key=lambda x: x['field_name'])
            == sorted(
                expected_metadata['update_meta'],
                key=lambda x: x['field_name'],
            )
        )
        assert sorted(meta['update_tags'], key=lambda x: x['tag']) == sorted(
            expected_metadata['update_tags'], key=lambda x: x['tag'],
        )
        return response_mock(json={'id': 'task_id'})

    response = await support_info_client.post(
        '/v1/webhook/forms/callcenter', data=data, headers=headers,
    )
    assert response.status == 200

    if expected_create_ticket is not None:
        create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
        assert create_ticket_kwargs == expected_create_ticket


@pytest.mark.parametrize(
    ['data', 'expected_error_text'],
    (
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "db id таксопарка"
                    },
                    "id": 12151,
                    "slug": "db_id"
                },
                "value": 100500
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438--\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            '{\'claim\': [\'Missing data for required field.\']}',
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Claim text field"
                    },
                    "id": 12153,
                    "slug": "claim"
                },
                "value": "Claim text"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438--\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            'There is no phone or email in fields',
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Claim text field"
                    },
                    "id": 12153,
                    "slug": "claim"
                },
                "value": null
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438--\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            '{\'claim\': [\'Field may not be null.\']}',
        ),
    ),
)
async def test_callcenter_form_fail(
        support_info_client, data, expected_error_text,
):
    response = await support_info_client.post(
        '/v1/webhook/forms/callcenter',
        data=data,
        headers={
            'x-delivery-id': 'request_1',
            'Content-type': (
                'multipart/form-data; '
                'boundary=f329de09cd544a86a5cf95375c2e0438'
            ),
        },
    )
    assert response.status == 400
    assert await response.json() == {
        'error': expected_error_text,
        'status': 'error',
    }


@pytest.mark.config(
    STARTRACK_SUPPORT_AVAILABLE_EMAILS=[
        'support@taxi.yandex.ru',
        'approved@email.com',
    ],
)
def test_got_unapproved_email(support_info_app):
    with pytest.raises(web.HTTPBadRequest) as exc:
        callcenter._get_call_center_email(
            headers={'YaTaxi-emailTo': 'UNapproved@email.com'},
            config=support_info_app.config,
        )
    assert exc.value.text == (
        'Email=unapproved@email.com ' 'is not available for sending'
    )


@pytest.mark.config(
    STARTRACK_SUPPORT_AVAILABLE_QUEUES=['SUPPORT', 'APPROVED_QUEUE'],
)
def test_got_unapproved_queue(support_info_app):

    with pytest.raises(web.HTTPBadRequest) as exc:
        callcenter._get_queue(
            headers={'YaTaxi-queue': 'UNAPPROVED_QUEUE'},
            config=support_info_app.config,
        )
    assert exc.value.text == (
        'Queue=UNAPPROVED_QUEUE ' 'is not available for sending'
    )


@pytest.mark.parametrize(
    'fields,expected_phone',
    [
        (
            {'user_phone': '+79250325272', 'caller_phone': '123'},
            '+79250325272',
        ),
        ({'user_phone': '89250325272', 'caller_phone': '123'}, '+79250325272'),
        ({'user_phone': '-', 'caller_phone': '89250325272'}, '+79250325272'),
        (
            {'user_phone': 'asdf', 'caller_phone': '+3801231231234'},
            '+3801231231234',
        ),
        (
            {'user_phone': '3801231231234', 'caller_phone': '123'},
            '+3801231231234',
        ),
        ({'user_phone': '79250325272', 'caller_phone': '123'}, '+79250325272'),
        ({'user_phone': '123', 'caller_phone': '123'}, '+123'),
    ],
)
async def test_user_phone_cleaning(
        territories_mock, support_info_app, fields, expected_phone,
):
    class MockRequest:
        def __init__(self, app):
            self.app = app

        def __getitem__(self, item):
            return ''

    request = MockRequest(support_info_app)
    phone = await callcenter._get_user_phone(request, fields)
    assert phone == expected_phone


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SUPPORT_INFO_META_DRIVER_TAGS_CONDITIONS=[
        {
            'external_tag': 'test_tag',
            'tags': ['test_tag'],
            'name': 'driver_tag_name_1',
        },
    ],
    SUPPORT_INFO_META_USER_TAGS_CONDITIONS=[
        {
            'external_tag': 'test_tag',
            'tags': ['test_tag'],
            'name': 'user_tag_name_1',
        },
    ],
)
@pytest.mark.parametrize('raise_support_chat_409', [False, True])
@pytest.mark.parametrize(
    [
        'data',
        'hidden_comment',
        'order_proc_data',
        'order_data',
        'expected_support_chat_request',
        'expected_metadata',
        'expected_create_ticket',
    ],
    [
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'uber',
                'country': 'aze',
            },
            True,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            {
                'owner': {
                    'id': '+79250325272_request_1',
                    'role': 'sms_client',
                    'platform': 'uber_android',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'uber_android',
                    },
                },
                'metadata': {
                    'user_application': 'uber_android',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'aze',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'uber_android',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'uber',
            },
            False,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            {
                'owner': {
                    'id': '+79250325272_request_1',
                    'role': 'sms_client',
                    'platform': 'uber_android',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'uber_android',
                    },
                },
                'metadata': {
                    'user_application': 'uber_android',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'uber_android',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325273',
                'request_id': 'request_1',
                'user_platform': 'yandex',
                'order_id': '1',
                'country': 'rus',
            },
            True,
            {
                '_id': '1',
                'order': {
                    'user_phone_id': '539eb65be7e5b1f53980dfa9',
                    'user_id': 'user_id1',
                    'user_locale': 'en',
                    'city': 'Москва',
                    'performer': {
                        'car_number': 'car_number',
                        'phone': ['+791234', '+75678'],
                        'clid': '100500',
                        'uuid': 'driver_uuid',
                        'db_id': 'db_id',
                        'taxi_alias': {'id': 'alias_id_1'},
                        'tariff': {'class': 'ultima'},
                    },
                    'coupon': {
                        'id': '123',
                        'was_used': True,
                        'valid': True,
                        'value': 10,
                    },
                    'nz': 'erevan',
                    'request': {'comment': 'precomment'},
                    'cashback_cost': 10.0,
                },
            },
            {'_id': 'order_id', 'payment_tech': {'type': 'corp'}},
            {
                'owner': {
                    'id': '+79250325273_request_1',
                    'role': 'sms_client',
                    'platform': 'android',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {
                        'order_id': 'order_id',
                        'driver_uuid': 'driver_uuid',
                        'order_alias_id': 'alias_id_1',
                        'park_db_id': 'db_id',
                    },
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325273',
                        'platform': 'android',
                    },
                },
                'metadata': {
                    'user_application': 'android',
                    'owner_phone': '+79250325273',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'amount_cashback',
                        'value': 10.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'amount_charity',
                        'value': 15.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'baby_seat_services',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cancel_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'car_number',
                        'value': 'car_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': '100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'cost_paid_supply',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'arm',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_use_value',
                        'value': 10,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'coupon_used',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'created',
                        'value': '2018-06-15T12:34:00+0000',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_app_version',
                        'value': '3.8.1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_complete_rides',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_phone_type',
                        'value': 'uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_id',
                        'value': 'user_id1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_phone_id',
                        'value': '539eb65be7e5b1f53980dfa9',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'customer_user_platform',
                        'value': 'iphone',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'dif_ordercost_surge_surgecharge',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'discount_ya_plus',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'door_to_door',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_arrived',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_late_time',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+791234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': 'driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_waiting_time',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_ride_duration',
                        'value': 0.0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'final_transaction_status',
                        'value': 'no_transactions',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'fixed_price_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_compensation',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'is_refund',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'moved_to_cash_by_antifraud',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multipoints',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'multiorder',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_alias_id',
                        'value': 'alias_id_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_cost',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_disp_status',
                        'value': 'some_reason',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_distance_raw',
                        'value': 0,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'order_id',
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
                        'field_name': 'order_tips',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_cancel_tag',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'paid_supply',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'db_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_driver_profile_id',
                        'value': 'db_id_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'park_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_phone',
                        'value': '+79123',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_decisions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type',
                        'value': 'corp',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type_changed_to_cash',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_car_number',
                        'value': 'car_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_clid',
                        'value': '100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_phone',
                        'value': '+791234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_driver_uuid',
                        'value': 'driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_db_id',
                        'value': 'db_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_driver_profile_id',
                        'value': 'db_id_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_name',
                        'value': 'park_name',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_park_phone',
                        'value': '+79123',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'performer_taximeter_version',
                        'value': '7.07',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'yandex',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'point_b_changed',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'precomment',
                        'value': 'precomment',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'several_ride_transactions',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'priority_list',
                        'value': {
                            'Дезинфекция машины': 2,
                            'Поездки с музыкой': 2,
                        },
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'success_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'surge_order_flg',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff',
                        'value': 'ultima',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff_currency',
                        'value': 'RUB',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '7.07',
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
                        'field_name': 'user_locale',
                        'value': 'en',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'android',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'corp',
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
                        'field_name': 'zone',
                        'value': 'erevan',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            {
                'user_platform': 'yandex',
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325274',
                'request_id': 'request_1',
                'metadata': {
                    'user_phone': '+79250325274',
                    'user_platform': 'yandex',
                    'user_email': 'some@email',
                    'message_text': 'eeeeeeee',
                    'order_id': '1',
                    'country': 'rus',
                },
            },
            True,
            {
                '_id': '1',
                'order': {
                    'user_phone_id': '539eb65be7e5b1f53980dfaa',
                    'user_id': 'user_id1',
                    'user_locale': 'en',
                    'city': 'Москва',
                    'performer': {
                        'car_number': 'car_number',
                        'phone': ['+791234', '+75678'],
                        'clid': '100500',
                        'uuid': 'driver_uuid',
                        'db_id': 'db_id',
                        'taxi_alias': {'id': 'alias_id_1'},
                        'tariff': {'class': 'ultima'},
                    },
                    'coupon': {
                        'id': '123',
                        'was_used': True,
                        'valid': True,
                        'value': 10,
                    },
                    'nz': 'erevan',
                    'request': {'comment': 'precomment'},
                },
            },
            {'_id': 'order_id', 'payment_tech': {'type': 'corp'}},
            None,
            None,
            {
                'queue': 'SUPPORT',
                'summary': 'Телефонное обращение в службу поддержки',
                'description': 'eeeeeeee',
                'tags': ['email_task'],
                'comment': (
                    'user_phone: +79250325274\nuser_platform: yandex\n'
                    'user_email: some@email\nmessage_text: eeeeeeee\n'
                    'order_id: order_id\ncountry: arm\n'
                    'paid_cancel_tag: False\ntransactions: \n'
                    'corp_client_id: \ndriver_phone: +791234\n'
                    'taximeter_version: 7.07\ndriver_license: driver_license\n'
                    'driver_name: \ndriver_locale: \n'
                    'driver_uuid: driver_uuid\n'
                    'performer_driver_phone: +791234\n'
                    'performer_taximeter_version: 7.07\n'
                    'performer_driver_license: driver_license\n'
                    'performer_driver_name: \n'
                    'performer_driver_locale: \n'
                    'performer_driver_uuid: driver_uuid\n'
                    'park_driver_profile_id: db_id_driver_uuid\n'
                    'performer_park_driver_profile_id: db_id_driver_uuid\n'
                    'priority_list: {\'Дезинфекция машины\': 2,'
                    ' \'Поездки с музыкой\': 2}\n'
                    'clid: 100500\n'
                    'performer_clid: 100500\n'
                    'park_phone: +79123\npark_name: park_name\npark_email: \n'
                    'park_city: \npark_country: \n'
                    'performer_park_phone: +79123\n'
                    'performer_park_name: park_name\n'
                    'performer_park_email: \n'
                    'performer_park_city: \n'
                    'performer_park_country: \n'
                    'park_db_id: db_id\n'
                    'car_number: car_number\n'
                    'performer_park_db_id: db_id\n'
                    'performer_car_number: car_number\n'
                    'order_alias_id: alias_id_1\n'
                    'tariff: ultima\ntariff_id: \ntariff_currency: RUB\n'
                    'user_locale: en\ncity: москва\n'
                    'order_date: -\norder_time: -\ntaximeter_cost: \n'
                    'driver_cost: \ndisp_cost: \norder_currency: RUB\n'
                    'order_pre_distance_raw: 0\norder_pre_time_raw: 0\n'
                    'order_pre_time_raw_minutes: 0.0\nsurge: \ncalc_way: \n'
                    'amount_cashback: 0\n'
                    'waiting_time_raw: 0\nwaiting_time_raw_minutes: 0.0\n'
                    'waiting: Нет\nwaiting_bool: False\nwaiting_cost: 0\n'
                    'point_b_changed: False\nsuccess_order_flg: False\n'
                    'coupon_use_value: 10\npaid_supply: False\norder_cost: 0\n'
                    'fixed_price_order_flg: False\n'
                    'dif_ordercost_surge_surgecharge: 0.0\n'
                    'surge_order_flg: False\ncost_paid_supply: 0\n'
                    'precomment: precomment\npoint_a: \npoints_b: \n'
                    'coupon: True\ncoupon_used: True\nfixed_price: \n'
                    'zone: erevan\ndiscount_ya_plus: False\npoint_a_city: \n'
                    'multiorder: False\n'
                    'order_distance_raw: 0\ncancel_distance_raw: 0\n'
                    'final_ride_duration: 0\ndriver_late_time: 0.0\n'
                    'driver_waiting_time: 0\n'
                    'moved_to_cash_by_antifraud: False\n'
                    'payment_type_changed_to_cash: False\n'
                    'time_request: 0.0\n'
                    'transportation_animals: False\n'
                    'baby_seat_services: False\ndoor_to_door: False\n'
                    'created: 2018-06-15T12:34:00+0000\npayment_type: corp\n'
                    'order_tips: False\n'
                    'final_transaction_status: no_transactions\n'
                    'payment_decisions: False\n'
                    'is_refund: False\nis_compensation: False\n'
                    'several_ride_transactions: False\n'
                    'multipoints: False\n'
                    'driver_arrived: False\n'
                    'customer_user_id: user_id1\n'
                    'customer_app_version: 3.8.1\n'
                    'customer_user_platform: iphone\n'
                    'customer_phone_type: yandex\n'
                    'customer_user_phone_id: 539eb65be7e5b1f53980dfaa\n'
                    'customer_user_phone: +79250325274\n'
                    'customer_complete_rides: 0\n'
                    'customer_taxi_staff: True\n'
                    'amount_charity: 15.0\n'
                    'order_disp_status: some_reason\n'
                    'user_type: corp'
                ),
                'custom_fields': {
                    'userPhone': '+79250325274',
                    'userPlatform': 'yandex',
                    'userEmail': 'some@email',
                    'OrderId': 'order_id',
                    'country': 'arm',
                    'driverPhone': '+791234',
                    'taximeterVersion': '7.07',
                    'driverLicense': 'driver_license',
                    'DriverUuid': 'driver_uuid',
                    'clid': '100500',
                    'ParkPhone': '+79123',
                    'parkName': 'park_name',
                    'parkDbId': 'db_id',
                    'carNumber': 'car_number',
                    'tariff': 'ultima',
                    'city': 'москва',
                    'waitingCost': '0',
                    'pointBChanged': 'False',
                    'orderCost': '0',
                    'preComment': 'precomment',
                    'coupon': 'True',
                    'couponUsed': 'True',
                    'paymentType': 'corp',
                    'brand': 'yandex',
                    'userType': 'corp',
                    'emailFrom': 'some@email',
                    'emailTo': ['support@taxi.yandex.ru'],
                    'emailCreatedBy': 'support@taxi.yandex.ru',
                },
                'unique': 'request_1',
            },
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'uber',
                'country': 'rus',
                'zone': 'moscow',
            },
            False,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            {
                'owner': {
                    'id': '+79250325272_request_1',
                    'role': 'sms_client',
                    'platform': 'uber_android',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'uber_android',
                    },
                },
                'metadata': {
                    'user_application': 'uber_android',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'uber',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'uber_android',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'zone',
                        'value': 'moscow',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'unknown_platform',
                'metadata': {
                    'country': 'rus',
                    'zone': 'moscow',
                    'message_text': 'eeeeeeee',
                    'user_phone': '+79250325272',
                    'request_id': 'request_1',
                    'extra_meta_field': 'extra_meta_field_value',
                },
                'tags': ['extra_tag_1', 'extra_tag_2', 'non-call-center-tag'],
            },
            False,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            {
                'owner': {
                    'id': '+79250325272_',
                    'role': 'sms_client',
                    'platform': 'unknown_platform',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'unknown_platform',
                    },
                },
                'metadata': {
                    'user_application': 'unknown_platform',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'extra_meta_field',
                        'value': 'extra_meta_field_value',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'yandex',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'unknown_platform',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'zone',
                        'value': 'moscow',
                    },
                ],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'extra_tag_1'},
                    {'change_type': 'add', 'tag': 'extra_tag_2'},
                    {'change_type': 'add', 'tag': 'non-call-center-tag'},
                    {'change_type': 'add', 'tag': 'sms_task'},
                ],
            },
            None,
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'unknown_platform',
                'country': 'rus',
                'zone': 'moscow',
            },
            False,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            {
                'owner': {
                    'id': '+79250325272_request_1',
                    'role': 'sms_client',
                    'platform': 'unknown_platform',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'unknown_platform',
                    },
                },
                'metadata': {
                    'user_application': 'unknown_platform',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'yandex',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'unknown_platform',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'zone',
                        'value': 'moscow',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            None,
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'unknown_platform',
                'metadata': {
                    'country': 'rus',
                    'zone': 'moscow',
                    'message_text': 'eeeeeeee',
                    'user_phone': '+79250325272',
                    'request_id': 'request_1',
                    'extra_meta_field': 'extra_meta_field_value',
                },
                'tags': ['extra_tag_1', 'extra_tag_2'],
            },
            False,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            {
                'owner': {
                    'id': '+79250325272_request_1',
                    'role': 'sms_client',
                    'platform': 'unknown_platform',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'unknown_platform',
                    },
                },
                'metadata': {
                    'user_application': 'unknown_platform',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'extra_meta_field',
                        'value': 'extra_meta_field_value',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'yandex',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'unknown_platform',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'zone',
                        'value': 'moscow',
                    },
                ],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'extra_tag_1'},
                    {'change_type': 'add', 'tag': 'extra_tag_2'},
                    {'change_type': 'add', 'tag': 'sms_task'},
                ],
            },
            None,
        ),
        (
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'unknown_platform',
                'metadata': {
                    'country': 'rus',
                    'zone': 'moscow',
                    'message_text': 'eeeeeeee',
                    'user_phone': '+79250325272',
                    'request_id': 'request_1',
                    'extra_meta_field': 'extra_meta_field_value',
                    'user_email': 'test@test.ru',
                },
                'tags': ['extra_tag_1', 'extra_tag_2'],
            },
            False,
            {
                '_id': '1',
                'order': {'user_phone_id': '539eb65be7e5b1f53980dfa9'},
            },
            {},
            None,
            None,
            {
                'comment': None,
                'custom_fields': {
                    'brand': 'yandex',
                    'country': 'rus',
                    'emailCreatedBy': 'support@taxi.yandex.ru',
                    'emailFrom': 'test@test.ru',
                    'emailTo': ['support@taxi.yandex.ru'],
                    'userEmail': 'test@test.ru',
                    'userPhone': '+79250325272',
                    'userPlatform': 'unknown_platform',
                },
                'description': 'eeeeeeee',
                'queue': 'SUPPORT',
                'summary': 'Телефонное обращение в службу поддержки',
                'tags': ['extra_tag_1', 'extra_tag_2', 'email_task'],
                'unique': 'request_1',
            },
        ),
        pytest.param(
            {
                'message_text': 'eeeeeeee',
                'user_phone': '+79250325272',
                'request_id': 'request_1',
                'user_platform': 'unknown_platform',
                'metadata': {
                    'country': 'rus',
                    'zone': 'moscow',
                    'message_text': 'eeeeeeee',
                    'user_phone': '+79250325272',
                    'user_phone_id': '539eb65be7e5b1f53980dfa9',
                    'driver_license': 'driver_license',
                    'request_id': 'request_1',
                    'extra_meta_field': 'extra_meta_field_value',
                },
                'tags': ['extra_tag_1', 'extra_tag_2'],
            },
            False,
            {},
            {},
            {
                'owner': {
                    'id': '+79250325272_request_1',
                    'role': 'sms_client',
                    'platform': 'unknown_platform',
                },
                'request_id': 'request_1',
                'message': {
                    'metadata': {},
                    'text': 'eeeeeeee',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325272',
                        'platform': 'unknown_platform',
                    },
                },
                'metadata': {
                    'user_application': 'unknown_platform',
                    'owner_phone': '+79250325272',
                },
            },
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'extra_meta_field',
                        'value': 'extra_meta_field_value',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'message_text',
                        'value': 'eeeeeeee',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'phone_type',
                        'value': 'yandex',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_platform',
                        'value': 'unknown_platform',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325272',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone_id',
                        'value': '539eb65be7e5b1f53980dfa9',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_tag_name_1',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'driver_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_tag_name_1',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'zone',
                        'value': 'moscow',
                    },
                ],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'extra_tag_1'},
                    {'change_type': 'add', 'tag': 'extra_tag_2'},
                    {'change_type': 'add', 'tag': 'sms_task'},
                ],
            },
            None,
            marks=[
                pytest.mark.config(
                    SUPPORT_INFO_EXTERNAL_META_QUERIES=True,
                    SUPPORT_INFO_CHATTERBOX_TAGS_SEARCH=False,
                ),
            ],
        ),
    ],
)
async def test_fos_form(
        support_info_client,
        support_info_app,
        territories_mock,
        mock_st_create_ticket,
        mock_personal,
        monkeypatch,
        patch_aiohttp_session,
        order_archive_mock,
        mock_get_user_phones,
        mock_get_users,
        response_mock,
        mock_get_tags,
        mockserver,
        mock_driver_profiles,
        mock_driver_trackstory,
        mock_driver_priority,
        mock_persey_payments,
        mock_taxi_fleet,
        data,
        hidden_comment,
        order_proc_data,
        order_data,
        expected_support_chat_request,
        expected_metadata,
        expected_create_ticket,
        raise_support_chat_409,
):
    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)

    chatterbox_url = discovery.find_service('chatterbox').url
    support_chat_url = discovery.find_service('support_chat').url
    archive_api_url = support_info_app.settings.ARCHIVE_API_URL

    if order_proc_data:
        order_archive_mock.set_order_proc(order_proc_data)

    mock_get_tags(
        response={'tags': ['test_tag', 'grade_for_branding', 'silver']},
        tags_service='driver-tags',
    )

    mock_get_tags(
        response={
            'entities': [
                {'entity_type': 'user_phone_id', 'tags': ['test_tag']},
            ],
        },
        tags_service='passenger-tags',
    )

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve_bulk')
    def _mock_user_api(request):
        return {
            'items': [
                {
                    'id': '5fb68e9f15a2887e0a040177',
                    'phone': '+70000000000',
                    'type': 'yandex',
                },
            ],
        }

    @patch_aiohttp_session(support_chat_url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        if raise_support_chat_409:
            raise support_chat.ConflictError
        assert url == support_chat_url + '/v1/chat'
        assert kwargs['json'] == expected_support_chat_request
        return response_mock(json={'id': 'chat_id'})

    @patch_aiohttp_session(archive_api_url, 'POST')
    def _dummy_archive_api_request(method, url, **kwargs):
        assert url == archive_api_url + '/archive/order'
        if order_data:
            return response_mock(json={'doc': order_data})
        return response_mock(status=404)

    @patch_aiohttp_session(chatterbox_url, 'POST')
    def _dummy_chatterbox_request(method, url, **kwargs):
        assert url == chatterbox_url + '/v1/tasks'
        meta = kwargs['json'].pop('metadata')
        if hidden_comment:
            assert kwargs['json'].pop('hidden_comment')

        assert kwargs['json'] == {'external_id': 'chat_id', 'type': 'chat'}
        assert (
            sorted(meta['update_meta'], key=lambda x: x['field_name'])
            == sorted(
                expected_metadata['update_meta'],
                key=lambda x: x['field_name'],
            )
        )
        assert sorted(meta['update_tags'], key=lambda x: x['tag']) == sorted(
            expected_metadata['update_tags'], key=lambda x: x['tag'],
        )
        return response_mock(json={'id': 'task_id'})

    headers = {}
    if hidden_comment:
        headers[constants.DUMP_META_IN_HEADERS] = 'True'
    response = await support_info_client.post(
        '/v1/forms/fos', json=data, headers=headers,
    )
    assert response.status == 200

    if expected_create_ticket is not None:
        create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
        assert create_ticket_kwargs == expected_create_ticket


@pytest.mark.config(
    STARTRACK_SUPPORT_AVAILABLE_EMAILS=[
        'support@taxi.yandex.ru',
        'approved@email.com',
    ],
    STARTRACK_SUPPORT_AVAILABLE_QUEUES=['SUPPORT', 'APPROVED_QUEUE'],
)
@pytest.mark.parametrize(
    [
        'data',
        'headers',
        'order_proc_data',
        'order_data',
        'expected_support_chat_request',
        'expected_create_ticket',
        'expected_metadata',
        'ticket_type',
    ],
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "db id таксопарка"
                    },
                    "id": 12151,
                    "slug": "db_id"
                },
                "value": 100500
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Страна"
                    },
                    "id": 12144,
                    "slug": "city"
                },
                "value": "Москва"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": ""
                    },
                    "id": 12144,
                    "slug": "city"
                },
                "value": "Москва"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Клид"
                    },
                    "id": 12149,
                    "slug": "clid"
                },
                "value": "clid"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "почта куда будут приходить письма с трекера"
                    },
                    "id": 12145,
                    "slug": "park_email"
                },
                "value": "parkmail@parkmail.mail"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Название парка"
                    },
                    "id": 12145,
                    "slug": "database"
                },
                "value": "Парк Нейм"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "тип диспетчерской"
                    },
                    "id": 12145,
                    "slug": "product"
                },
                "value": "Тип Продукта"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Парк ID"
                    },
                    "id": 12145,
                    "slug": "db_id"
                },
                "value": "1331221"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "eeeeeeee"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="file";'
            'filename="my.txt"\r\n'
            'Content-Type: text/plain \r\n\r\n'
            'TEXT PLAIN\r\n\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="file";'
            'filename="my.txt"\r\n'
            'Content-Type: text/plain \r\n\r\n'
            'TEXT PLAIN TEXT\r\n\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'X-FORM-ID': '4432',
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {},
            {},
            None,
            {
                'comment': None,
                'queue': 'SUPPORT',
                'summary': (
                    'Телефонное обращение в службу поддержки ' 'Яндекс.Такси'
                ),
                'description': 'eeeeeeee',
                'unique': 'request_1_4432',
                'tags': ['cc_task_nophone'],
                'custom_fields': {
                    'city': 'Москва',
                    'clid': 'clid',
                    'parkDbId': '1331221',
                    'parkName': 'Парк Нейм',
                    'parkEmail': 'parkmail@parkmail.mail',
                    'emailFrom': 'parkmail@parkmail.mail',
                    'emailTo': ['support@taxi.yandex.ru'],
                    'emailCreatedBy': 'support@taxi.yandex.ru',
                },
            },
            None,
            'startrack',
        ),
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "ID заказа"
                    },
                    "id": 12151,
                    "slug": "order_id"
                },
                "value": null
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "text"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "user_phone"
                },
                "value": "+79250325273"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Номер телефона, на который заказывали такси"
                    },
                    "id": 12145,
                    "slug": "caller_phone"
                },
                "value": "-"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="file";'
            'filename="my1.txt"\r\n'
            'Content-Type: text/plain \r\n\r\n'
            'TEXT PLAIN\r\n\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="file";'
            'filename="my2.txt"\r\n'
            'Content-Type: text/plain \r\n\r\n'
            'TEXT PLAIN TEXT\r\n\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'X-FORM-ID': '4432',
                'x-delivery-id': 'request_1',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
            {},
            {},
            {
                'owner': {
                    'id': '+79250325273',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'request_id': 'request_1_4432',
                'message': {
                    'text': 'text',
                    'sender': {
                        'role': 'sms_client',
                        'id': '+79250325273',
                        'platform': 'yandex',
                    },
                    'metadata': {
                        'attachments': [
                            {
                                'id': 'my1.txt',
                                'name': 'my1.txt',
                                'source': 'mds',
                            },
                            {
                                'id': 'my2.txt',
                                'name': 'my2.txt',
                                'source': 'mds',
                            },
                        ],
                    },
                },
                'metadata': {
                    'user_application': 'yandex',
                    'owner_phone': '+79250325273',
                },
            },
            None,
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'claim',
                        'value': 'text',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79250325273',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'request_id',
                        'value': 'request_1_4432',
                    },
                ],
                'update_tags': [{'change_type': 'add', 'tag': 'sms_task'}],
            },
            'chatterbox',
        ),
    ],
)
async def test_callcenter_form_with_file(
        support_info_client,
        support_info_app,
        territories_mock,
        patch_aiohttp_session,
        order_archive_mock,
        response_mock,
        mock_st_create_ticket,
        data,
        headers,
        order_proc_data,
        order_data,
        expected_support_chat_request,
        expected_create_ticket,
        expected_metadata,
        ticket_type,
):
    chatterbox_url = discovery.find_service('chatterbox').url
    support_chat_url = discovery.find_service('support_chat').url
    archive_api_url = support_info_app.settings.ARCHIVE_API_URL
    startrack_attachments_url = (
        'http://test-startrack-url/issues/SUPPORT-1/attachments'
    )

    @patch_aiohttp_session(support_chat_url + '/v1/chat', 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        assert kwargs['json'] == expected_support_chat_request
        return response_mock(json={'id': 'chat_id'})

    @patch_aiohttp_session(archive_api_url, 'POST')
    def _dummy_archive_api_request(method, url, **kwargs):
        assert url == archive_api_url + '/archive/order'
        if order_data:
            return response_mock(json={'doc': order_data})
        return response_mock(status=404)

    @patch_aiohttp_session(chatterbox_url, 'POST')
    def _dummy_chatterbox_request(method, url, **kwargs):
        assert url == chatterbox_url + '/v1/tasks'
        meta = kwargs['json'].pop('metadata')
        if constants.DUMP_META_IN_HEADERS in headers:
            hidden = kwargs['json'].pop('hidden_comment')
            assert hidden and 'None' not in hidden
        assert kwargs['json'] == {'external_id': 'chat_id', 'type': 'chat'}
        assert (
            sorted(meta['update_meta'], key=lambda x: x['field_name'])
            == sorted(
                expected_metadata['update_meta'],
                key=lambda x: x['field_name'],
            )
        )
        assert sorted(meta['update_tags'], key=lambda x: x['tag']) == sorted(
            expected_metadata['update_tags'], key=lambda x: x['tag'],
        )
        return response_mock(json={'id': 'task_id'})

    @patch_aiohttp_session(support_chat_url + '/v1/chat/attach_file', 'POST')
    def _dummy_attach_file_request(method, url, **kwargs):
        return response_mock(
            json={'attachment_id': kwargs['params']['filename']},
        )

    @patch_aiohttp_session(startrack_attachments_url, 'POST')
    def _dummy_attachments_request(method, url, params, data, **kwargs):
        assert params['filename'] == 'my.txt'
        assert len(data._fields) == 1
        return response_mock(json={'id': 'string', 'name': 'my.txt'})

    response = await support_info_client.post(
        '/v1/webhook/forms/callcenter', data=data, headers=headers,
    )
    assert response.status == 200
    if ticket_type == 'startrack':
        assert len(_dummy_attachments_request.calls) == 2
    else:
        assert not _dummy_attachments_request.calls

    if expected_create_ticket is not None:
        create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
        assert create_ticket_kwargs == expected_create_ticket


@pytest.mark.config(
    STARTRACK_SUPPORT_AVAILABLE_EMAILS=[
        'support@taxi.yandex.ru',
        'approved@email.com',
    ],
    STARTRACK_SUPPORT_AVAILABLE_QUEUES=['SUPPORT', 'APPROVED_QUEUE'],
)
@pytest.mark.parametrize(
    ['data', 'headers'],
    [
        (
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_10"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "db id таксопарка"
                    },
                    "id": 12151,
                    "slug": "db_id"
                },
                "value": 100500
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Страна"
                    },
                    "id": 12144,
                    "slug": "city"
                },
                "value": "Москва"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": ""
                    },
                    "id": 12144,
                    "slug": "city"
                },
                "value": "Москва"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_8"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Клид"
                    },
                    "id": 12149,
                    "slug": "clid"
                },
                "value": "clid"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "почта куда будут приходить письма с трекера"
                    },
                    "id": 12145,
                    "slug": "park_email"
                },
                "value": "parkmail@parkmail.mail"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_5"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Название парка"
                    },
                    "id": 12145,
                    "slug": "database"
                },
                "value": "Парк Нейм"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "тип диспетчерской"
                    },
                    "id": 12145,
                    "slug": "product"
                },
                "value": "Тип Продукта"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_6"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Парк ID"
                    },
                    "id": 12145,
                    "slug": "db_id"
                },
                "value": "1331221"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="field_4"\r\n\r\n'
            """
            {
                "question": {
                    "label": {
                        "ru": "Содержание обращения"
                    },
                    "id": 12144,
                    "slug": "claim"
                },
                "value": "eeeeeeee"
            }\r\n"""
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="file";'
            'filename="my.txt"\r\n'
            'Content-Type: text/plain \r\n\r\n'
            'TEXT PLAIN\r\n\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="file";'
            'filename="my.txt"\r\n'
            'Content-Type: text/plain \r\n\r\n'
            'TEXT PLAIN TEXT\r\n\r\n'
            '--f329de09cd544a86a5cf95375c2e0438\r\n'
            'Content-Disposition: form-data;name="noop";filename=""\r\n\r\n'
            'content\r\n'
            '--f329de09cd544a86a5cf95375c2e0438--\r\n',
            {
                'X-FORM-ID': '4432',
                'x-delivery-id': 'duplicate',
                'Content-type': (
                    'multipart/form-data; '
                    'boundary=f329de09cd544a86a5cf95375c2e0438'
                ),
            },
        ),
    ],
)
async def test_callcenter_conflict(
        support_info_client,
        support_info_app,
        territories_mock,
        mock_st_create_ticket,
        patch_aiohttp_session,
        response_mock,
        data,
        headers,
):
    startrack_attachments_url = (
        'http://test-startrack-url/issues/SUPPORT-1/attachments'
    )

    startrack_unique_url = 'http://test-startrack-url/issues/_findByUnique'

    @patch_aiohttp_session(startrack_unique_url, 'POST')
    def _dummy_get_by_unique_request(method, url, params, data, **kwargs):
        assert params == {'unique': 'duplicate_4432'}
        return response_mock(json={'key': 'SUPPORT-1'})

    @patch_aiohttp_session(startrack_attachments_url, 'POST')
    def _dummy_attachments_request(method, url, params, data, **kwargs):
        assert params['filename'] == 'my.txt'
        assert len(data._fields) == 1
        assert 'SUPPORT-1' in url
        return response_mock(json={'id': 'string', 'name': 'my.txt'})

    response = await support_info_client.post(
        '/v1/webhook/forms/callcenter', data=data, headers=headers,
    )
    assert response.status == 200
    assert len(_dummy_attachments_request.calls) == 2
