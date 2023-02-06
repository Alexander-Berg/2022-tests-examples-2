# pylint: disable=too-many-arguments, too-many-branches, too-many-lines
# pylint: disable=no-member, redefined-outer-name, unused-variable
import datetime
import json

import bson
import pytest

from taxi import discovery
from taxi.clients import support_chat
from taxi.clients import support_info

from chatterbox import stq_task


NOW = datetime.datetime(2019, 12, 16, 0)
TRANSLATE = {
    'errors.exist_chat_chatterbox': {
        'en': 'go to {ticket} chatterbox',
        'ru': 'Тикет {ticket} в Крутилке',
    },
}
UUID = '00000000000040008000000000000000'


@pytest.fixture
def mock_get_chat(monkeypatch, mock):
    def _wrap(chat_type):
        @mock
        async def get_chat(*args, **kwargs):
            chat = {
                'id': 'some_id',
                'type': chat_type,
                'status': {'is_open': True, 'is_visible': True},
                'metadata': {'last_message_from_user': True},
            }
            return chat

        monkeypatch.setattr(
            support_chat.SupportChatApiClient, 'get_chat', get_chat,
        )
        return mock_get_chat

    return _wrap


@pytest.fixture
def mock_get_additional_meta(monkeypatch, mock):
    @mock
    async def _dummy_get_additional_meta(**kwargs):
        metadata = kwargs['data']['metadata'].copy()
        if metadata.get('user_phone'):
            if metadata['user_phone'] == 'missing_user_phone':
                return {'metadata': metadata, 'status': 'no_data'}
            if metadata['user_phone'] == 'user_phone_task_exists':
                user_phone_id = 'task_exists'
            elif metadata['user_phone'] == 'user_phone_task_broken':
                user_phone_id = 'task_broken'
            elif metadata['user_phone'] == 'user_phone_task_closed':
                user_phone_id = 'task_closed'
            elif metadata['user_phone'] == 'user_phone_race_task':
                user_phone_id = 'race_task'
            else:
                user_phone_id = 'phone_id'
            metadata.update({'user_phone_id': user_phone_id})
            if 'use_last_order' in kwargs['data']:
                metadata.update(
                    {
                        'customer_user_id': 'some_user_id',
                        'user_locale': 'ru',
                        'user_platform': 'android',
                        'city': 'moscow',
                        'country': 'rus',
                    },
                )
        if metadata.get('driver_uuid'):
            if metadata['driver_uuid'] == 'missing_uuid':
                return {'metadata': metadata, 'status': 'no_data'}
            if metadata['driver_uuid'] == 'driver_uuid_task_exists':
                unique_driver_id = 'task_exists'
            elif metadata['driver_uuid'] == 'driver_uuid_task_broken':
                unique_driver_id = 'task_broken'
            else:
                unique_driver_id = 'some_unique_driver_id'
            metadata.update(
                {
                    'park_db_id': 'some_park_id',
                    'driver_license': 'some_driver_license',
                    'driver_name': 'Швабрэ Старая Пристарая',
                    'driver_phone': '+70000000000',
                    'driver_locale': 'ru',
                    'taximeter_version': '0.1.2',
                    'clid': 'some_clid',
                    'park_name': 'Лещ',
                    'park_city': 'moscow',
                    'park_country': 'rus',
                    'car_number': '123XYZ',
                    'unique_driver_id': unique_driver_id,
                },
            )
        if metadata.get('order_id'):
            metadata.update(
                {
                    'car_number': '123XYZ',
                    'city': 'moscow',
                    'country': 'rus',
                    'clid': 'some_clid',
                    'coupon': False,
                    'coupon_used': False,
                    'driver_id': 'some_driver_id',
                    'order_alias_id': 'some_alias_id',
                    'park_db_id': 'some_park_id',
                    'payment_type': 'cash',
                    'precomment': 'ahaha',
                    'tariff': 'econom',
                    'customer_user_id': 'some_user_id',
                    'user_platform': 'android',
                    'user_locale': 'ru',
                },
            )
        else:
            assert 'use_last_order' in kwargs['data']
        if kwargs['data'].get('applications'):
            if 'vezet' not in kwargs['data']['applications'][0]:
                metadata.update(
                    {'user_platform': kwargs['data']['applications'][0]},
                )
        return {'metadata': metadata, 'status': 'ok'}

    monkeypatch.setattr(
        support_info.SupportInfoApiClient,
        'get_additional_meta',
        _dummy_get_additional_meta,
    )
    return _dummy_get_additional_meta


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_DEFAULT_LINES={
        'client_support': 'first',
        'driver_support': 'driver_first',
        'eats_support': 'eats_first',
        'restapp_support': 'restapp_first',
        'whatsapp_support': 'first',
        'telegram_support': 'telegram',
    },
    CHATTERBOX_SOURCE_TYPE_MAPPING={
        'client_support': 'client',
        'driver_support': 'driver',
        'eats_support': 'client_eats',
        'restapp_support': 'restapp',
        'whatsapp_support': 'whatsapp',
        'telegram_support': 'telegram',
    },
    CHATTERBOX_PREDISPATCH=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
    },
    ALLOWED_MULTICHAT_SERVICES=['restapp'],
    CHATTERBOX_CHAT_INIT={
        'whatsapp_taxi_test': {
            'bot_id': 'whatsapp_bot',
            'default_platform': 'yandex',
            'fields': [
                {
                    'checks': ['not-empty'],
                    'id': 'user_phone',
                    'metadata': True,
                    'tanker': 'chat_init.user_phone',
                    'type': 'phone',
                },
                {
                    'checks': ['not-empty'],
                    'id': 'template_name',
                    'metadata': True,
                    'options': [
                        {
                            'tanker': 'chat_init.template_1',
                            'value': 'infobip_test_hsm_1',
                        },
                    ],
                    'tanker': 'chat_init.template_choose',
                    'type': 'select',
                },
            ],
            'owner_id': 'user_phone_id',
            'owner_role': 'whatsapp_client',
        },
        'telegram_taxi': {
            'bot_id': 'telegram_bot',
            'default_platform': 'yandex',
            'fields': [
                {
                    'checks': ['not-empty'],
                    'id': 'user_phone',
                    'metadata': True,
                    'tanker': 'chat_init.user_phone',
                    'type': 'phone',
                },
            ],
            'owner_id': 'user_phone_id',
            'owner_role': 'telegram_client',
        },
        'client': {
            'owner_id': 'user_phone_id',
            'owner_role': 'client',
            'default_platform': 'yandex',
            'fields': [
                {
                    'id': 'platform',
                    'checks': ['not-empty'],
                    'tanker': 'chat_init.platform',
                    'type': 'select',
                    'options': [
                        {'tanker': 'platform.yandex', 'value': 'yandex'},
                        {'tanker': 'platform.uber', 'value': 'uber'},
                        {'tanker': 'platform.yango', 'value': 'yango'},
                        {'tanker': 'platform.vezet', 'value': 'vezet'},
                    ],
                },
                {
                    'id': 'user_phone',
                    'tanker': 'chat_init.user_phone',
                    'type': 'phone',
                    'checks': ['not-empty'],
                    'metadata': True,
                },
                {
                    'id': 'order_id',
                    'tanker': 'chat_init.order_id',
                    'type': 'string',
                    'checks': [],
                    'metadata': True,
                },
                {
                    'id': 'message',
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'checks': ['not-empty'],
                },
            ],
        },
        'driver': {
            'owner_id': 'unique_driver_id',
            'owner_role': 'driver',
            'default_platform': 'taximeter',
            'permission': 'driver_init_permission',
            'fields': [
                {
                    'tanker': 'chat_init.driver_uuid',
                    'type': 'string',
                    'id': 'driver_uuid',
                    'checks': ['not-empty'],
                    'metadata': True,
                },
                {
                    'tanker': 'chat_init.order_id',
                    'type': 'string',
                    'id': 'order_id',
                    'checks': [],
                    'metadata': True,
                },
                {
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'id': 'message',
                    'checks': ['not-empty'],
                },
            ],
        },
        'client_eats': {
            'owner_id': 'user_uid',
            'owner_role': 'eats_client',
            'fields': [
                {
                    'tanker': 'chat_init.user_uid',
                    'type': 'string',
                    'id': 'user_uid',
                    'checks': ['not-empty'],
                    'metadata': True,
                    'save_as': 'some_field',
                },
                {
                    'tanker': 'chat_init.eats_order_id',
                    'type': 'string',
                    'id': 'eats_order_id',
                    'checks': [],
                    'metadata': True,
                },
                {
                    'tanker': 'chat_init.order_type',
                    'type': 'string',
                    'id': 'order_type',
                    'checks': [],
                    'metadata': True,
                },
                {
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'id': 'message',
                    'checks': ['not-empty'],
                },
            ],
        },
        'restapp': {
            'owner_id': 'restapp_partner_id',
            'owner_role': 'restapp_client',
            'fields': [
                {
                    'tanker': 'chat_init.restapp_partner_id',
                    'type': 'string',
                    'id': 'restapp_partner_id',
                    'checks': ['not-empty'],
                    'metadata': True,
                    'save_as': 'user_id',
                },
                {
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'id': 'message',
                    'checks': ['not-empty'],
                },
                {'id': 'ticket_subject', 'metadata': True},
            ],
        },
    },
    CHATTERBOX_CREATE_CHAT_METADATA_FIELDS_MAP={
        'client': {
            'fields_map': {
                'user_id': 'customer_user_id',
                'user_locale': 'user_locale',
                'user_application': 'user_platform',
                'user_country': 'country',
            },
            'required': [
                'user_id',
                'user_locale',
                'user_application',
                'user_country',
            ],
        },
        'driver': {
            'fields_map': {
                'db': 'park_db_id',
                'driver_uuid': 'driver_uuid',
                'user_locale': 'driver_locale',
                'user_country': 'park_country',
            },
            'required': ['db', 'driver_uuid', 'user_locale', 'user_country'],
            'defaults': {'user_application': 'taximeter'},
        },
        'restapp_client': {
            'fields_map': {'user_id': 'user_id'},
            'required': ['user_id'],
        },
        'eats_client': {
            'fields_map': {'chat_meta': 'task_meta'},
            'defaults': {'chat_meta': 'some_meta'},
        },
        'whatsapp_client': {
            'fields_map': {
                'contact_point_id': 'contact_point_id',
                'template_name': 'template_name',
                'user_application': 'user_platform',
                'user_country': 'country',
                'user_id': 'customer_user_id',
                'user_locale': 'user_locale',
                'user_phone_pd_id': 'user_phone_pd_id',
            },
            'required': [
                'user_id',
                'user_locale',
                'user_application',
                'user_country',
                'user_phone_pd_id',
                'contact_point_id',
                'template_name',
            ],
        },
        'telegram_client': {
            'fields_map': {
                'contact_point_id': 'contact_point_id',
                'user_application': 'user_platform',
                'user_phone_pd_id': 'user_phone_pd_id',
            },
            'required': [
                'user_application',
                'user_phone_pd_id',
                'contact_point_id',
            ],
        },
    },
    GET_ORDER_META_FROM_EATS_SUPPORT_MISC=True,
    CHATTERBOX_WHATSAPP_TEMPLATES={
        'infobip_test_hsm_1': {
            'default_params': [],
            'locale': 'ru_RU',
            'params': [],
            'text': 'Hello',
        },
    },
)
@pytest.mark.parametrize(
    [
        'url',
        'login',
        'chat_type',
        'expected_task_status',
        'data',
        'expected_status',
        'expected_meta',
        'expected_create_chat',
        'expected_create_new_chat',
    ],
    [
        (
            '/v2/tasks/init/whatsapp_taxi_test/',
            'superuser',
            'whatsapp_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'user_phone': '+79999999999',
                'platform': 'yandex',
                'template_name': 'infobip_test_hsm_1',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'android',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'template_name': 'infobip_test_hsm_1',
                'contact_point_id': 'whatsapp_bot',
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello',
                'owner_id': 'phone_id_whatsapp_bot',
                'owner_role': 'whatsapp_client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'android',
                    'contact_point_id': 'whatsapp_bot',
                    'user_phone_pd_id': 'phone_pd_id_1',
                    'template_name': 'infobip_test_hsm_1',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/telegram_taxi/',
            'superuser',
            'telegram_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'user_phone': '+79999999999',
                'platform': 'yandex',
                'message': 'hello telegram',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'user_platform': 'android',
                'customer_user_id': 'some_user_id',
                'ml_request_id': UUID,
                'user_locale': 'ru',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'new',
                'contact_point_id': 'telegram_bot',
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'hello telegram',
                'owner_id': 'phone_id_telegram_bot',
                'owner_role': 'telegram_client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_application': 'android',
                    'contact_point_id': 'telegram_bot',
                    'user_phone_pd_id': 'phone_pd_id_1',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'platform': 'yandex',
                'message_metadata': {'encrypt_key': '123'},
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': {'encrypt_key': '123'},
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            'in_progress',
            {
                'request_id': 'request_id',
                'macro_id': 123,
                'user_phone': '+79999999999',
                'platform': 'yandex',
                'order_id': 'some_order_id',
            },
            200,
            {
                'request_id': 'request_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'user_phone_id': 'phone_id',
                'phone_type': 'yandex',
                'order_id': 'some_order_id',
                'car_number': '123XYZ',
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': 'user_phone_task_closed',
                'platform': 'yandex',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'task_closed',
                'user_phone': 'user_phone_task_closed',
                'user_phone_pd_id': 'phone_pd_id_2',
                'phone_type': 'yandex',
                'some': 'meta',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'reopened',
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'task_closed',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'yandex',
            },
            200,
            {
                'user_phone': 'user_phone_task_broken',
                'user_phone_pd_id': 'phone_pd_id_4',
                'phone_type': 'yandex',
                'user_phone_id': 'task_broken',
                'request_id': 'request_id',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'yandex',
            },
            200,
            {
                'user_phone': 'user_phone_task_broken',
                'user_phone_pd_id': 'phone_pd_id_4',
                'phone_type': 'yandex',
                'user_phone_id': 'task_broken',
                'request_id': 'request_id',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
            None,
        ),
        (
            '/v2/tasks/init_with_tvm/client/',
            'superuser',
            'client_support',
            'new',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'yandex',
            },
            200,
            {
                'user_phone': 'user_phone_task_broken',
                'user_phone_pd_id': 'phone_pd_id_4',
                'phone_type': 'yandex',
                'user_phone_id': 'task_broken',
                'request_id': 'request_id',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'vezet',
            },
            406,
            {},
            None,
            None,
        ),
        (
            '/v2/tasks/init/client/',
            'superuser',
            'client_support',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_exists',
                'platform': 'yandex',
            },
            409,
            None,
            None,
            None,
        ),
        (
            '/v2/tasks/init/driver/',
            'superuser',
            'driver_support',
            'in_progress',
            {
                'request_id': 'another_request_id',
                'message': 'Hello!',
                'driver_uuid': 'some_driver_uuid',
                'platform': 'uberdriver',
            },
            200,
            {
                'request_id': 'another_request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'status_before_assign': 'new',
                'ml_request_id': UUID,
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'another_request_id',
                'platform': 'uberdriver',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/driver/',
            'driver_init',
            'driver_support',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
            },
            200,
            {
                'request_id': 'request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'status_before_assign': 'new',
                'ml_request_id': UUID,
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'driver_init',
                'message_sender_role': 'support',
                'message_text': 'Hello again!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'request_id',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            None,
        ),
        (
            '/v2/tasks/init/driver/',
            'superuser',
            'driver_support',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'missing_uuid',
            },
            424,
            None,
            None,
            None,
        ),
        (
            '/v2/tasks/init/driver/',
            'superuser',
            'driver_support',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_broken',
            },
            200,
            {
                'driver_uuid': 'driver_uuid_task_broken',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'task_broken',
                'request_id': 'request_id',
                'status_before_assign': 'new',
                'ml_request_id': UUID,
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
            None,
        ),
        (
            '/v2/tasks/init_with_tvm/driver/',
            'superuser',
            'driver_support',
            'new',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_broken',
            },
            200,
            {
                'driver_uuid': 'driver_uuid_task_broken',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'task_broken',
                'request_id': 'request_id',
                'ml_request_id': UUID,
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
            None,
        ),
        (
            '/v2/tasks/init/driver/',
            'superuser',
            'driver_support',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_exists',
            },
            409,
            None,
            None,
            None,
        ),
        (
            '/v2/tasks/init/client_eats/',
            'superuser',
            'eats_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_uid': 'user_uid',
                'order_type': 'lavka',
                'eats_order_id': '12345',
            },
            200,
            {
                'country_code': 'RU',
                'currency': 'RUB',
                'eater_id': 'eater_id',
                'eater_name': 'Иван Иванович',
                'eats_order_id': '12345',
                'is_blocked_user': False,
                'is_canceled': True,
                'is_first_order': False,
                'is_promocode_used': False,
                'ml_request_id': UUID,
                'order_delay_minutes': 2,
                'order_delivered_at': '2020-01-20T18:02:42+0700',
                'order_promised_at': '2020-01-20T18:00:00+0700',
                'order_total_amount': 777,
                'order_type': 'lavka',
                'request_id': 'some_request_id',
                'status_before_assign': 'new',
                'user_uid': 'user_uid',
                'some_field': 'user_uid',
                'task_meta': 'grocery_meta',
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'metadata': {'chat_meta': 'grocery_meta'},
                'owner_id': 'user_uid',
                'owner_role': 'eats_client',
                'platform': None,
                'request_id': 'some_request_id',
            },
            None,
        ),
        (
            '/v2/tasks/init/client_eats/',
            'superuser',
            'eats_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_uid': 'user_uid',
                'platform': 'some_platform',
            },
            200,
            {
                'ml_request_id': UUID,
                'request_id': 'some_request_id',
                'status_before_assign': 'new',
                'user_uid': 'user_uid',
                'some_field': 'user_uid',
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'metadata': {'chat_meta': 'some_meta'},
                'owner_id': 'user_uid',
                'owner_role': 'eats_client',
                'platform': 'some_platform',
                'request_id': 'some_request_id',
            },
            None,
        ),
        (
            '/v2/tasks/init/restapp/',
            'superuser',
            'restapp_support',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'restapp_partner_id': 'task_exists',
                'platform': 'restapp_app',
                'ticket_subject': 'Проблема с выплатами от Яндекс.Еды',
            },
            200,
            {
                'ml_request_id': UUID,
                'request_id': 'some_request_id',
                'status_before_assign': 'new',
                'restapp_partner_id': 'task_exists',
                'user_id': 'task_exists',
                'ticket_subject': 'Проблема с выплатами от Яндекс.Еды',
                'deadline': datetime.datetime(2019, 12, 20, 3, 0),
            },
            None,
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'metadata': {'user_id': 'task_exists'},
                'owner_id': 'task_exists',
                'owner_role': 'restapp_client',
                'platform': 'restapp_app',
                'request_id': 'some_request_id',
            },
        ),
        (
            '/v2/tasks/init/driver/',
            'some_init',
            'driver_support',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_broken',
            },
            403,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_task(
        cbox,
        mock_chat_create,
        mock_chat_create_new,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        url,
        login,
        chat_type,
        expected_task_status,
        data,
        expected_status,
        expected_meta,
        expected_create_chat,
        expected_create_new_chat,
        mock_uuid_uuid4,
        mock_personal,
        patch_aiohttp_session,
        response_mock,
        patch_auth,
):
    if login:
        patch_auth(login=login)
    mock_chat_get_history({'messages': []})
    mock_get_chat(chat_type)

    grocery_orders_service = discovery.find_service('grocery-orders')

    @patch_aiohttp_session(grocery_orders_service.url)
    def mock_grocery_orders(method, url, **kwargs):
        assert method == 'post'
        assert (
            url
            == grocery_orders_service.url
            + '/internal/v1/get-chatterbox-order-meta/'
        )
        return response_mock(
            text=json.dumps(
                {
                    'is_canceled': True,
                    'currency': 'RUB',
                    'task_meta': 'grocery_meta',
                },
            ),
        )

    await cbox.post(url, data=data)
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data['status'] == expected_task_status

        task = await cbox.app.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(cbox.body_data['id'])},
        )
        assert task['status'] == expected_task_status
        assert task['support_admin'] == login
        assert 'support_init' in task['tags']
        assert task['meta_info'] == expected_meta
        assert not task.get('inner_comments')

        if expected_create_chat is None:
            assert not mock_chat_create.calls
        else:
            create_chat_call = mock_chat_create.calls[0]['kwargs']
            create_chat_call.pop('log_extra')
            assert create_chat_call == expected_create_chat

        if expected_create_new_chat is None:
            assert not mock_chat_create_new.calls
        else:
            create_chat_call = mock_chat_create_new.calls[0]['kwargs']
            create_chat_call.pop('log_extra')
            assert create_chat_call == expected_create_new_chat

        # try double request
        await cbox.post(url, data=data)
        assert cbox.status == 200
        assert bson.ObjectId(cbox.body_data['id']) == task['_id']
        assert cbox.body_data['status'] == expected_task_status

    elif expected_status == 409:
        assert cbox.body_data == {
            'message': 'Тикет existing_task_id в Крутилке',
            'next_frontend_action': 'open_task',
            'task_id': 'existing_task_id',
            'status': 'Chat already opened',
        }


@pytest.mark.config(
    CHATTERBOX_PREDISPATCH=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
    },
)
@pytest.mark.parametrize(
    [
        'url',
        'expected_task_status',
        'data',
        'expected_status',
        'expected_meta',
        'expected_create_chat',
    ],
    [
        (
            '/v1/tasks/init/client/',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'message_metadata': {'encrypt_key': '123'},
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': {'encrypt_key': '123'},
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
        ),
        (
            '/v1/tasks/init/client/',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'order_id': 'some_order_id',
            },
            200,
            {
                'request_id': 'request_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'user_phone_id': 'phone_id',
                'phone_type': 'yandex',
                'order_id': 'some_order_id',
                'car_number': '123XYZ',
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello again!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
        ),
        (
            '/v1/tasks/init/client/',
            'in_progress',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': 'user_phone_task_closed',
                'phone_type': 'yandex',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'task_closed',
                'user_phone': 'user_phone_task_closed',
                'user_phone_pd_id': 'phone_pd_id_2',
                'phone_type': 'yandex',
                'some': 'meta',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'reopened',
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'task_closed',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
        ),
        (
            '/v1/tasks/init/client/',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'missing_user_phone',
                'phone_type': 'yandex',
            },
            424,
            None,
            None,
        ),
        (
            '/v1/tasks/init/client/',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'phone_type': 'yandex',
            },
            200,
            {
                'user_phone': 'user_phone_task_broken',
                'user_phone_pd_id': 'phone_pd_id_4',
                'phone_type': 'yandex',
                'user_phone_id': 'task_broken',
                'request_id': 'request_id',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
        ),
        (
            '/v1/tasks/init/client/',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'yandex',
            },
            200,
            {
                'user_phone': 'user_phone_task_broken',
                'user_phone_pd_id': 'phone_pd_id_4',
                'phone_type': 'yandex',
                'user_phone_id': 'task_broken',
                'request_id': 'request_id',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
        ),
        (
            '/v1/tasks/init_with_tvm/client/',
            'new',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'yandex',
            },
            200,
            {
                'user_phone': 'user_phone_task_broken',
                'user_phone_pd_id': 'phone_pd_id_4',
                'phone_type': 'yandex',
                'user_phone_id': 'task_broken',
                'request_id': 'request_id',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'ml_request_id': UUID,
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
        ),
        (
            '/v1/tasks/init/client/',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_broken',
                'platform': 'vezet',
            },
            406,
            {},
            None,
        ),
        (
            '/v1/tasks/init/client/',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'user_phone': 'user_phone_task_exists',
                'phone_type': 'yandex',
            },
            409,
            None,
            None,
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_client_task(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        url,
        expected_task_status,
        data,
        expected_status,
        expected_meta,
        expected_create_chat,
        mock_uuid_uuid4,
        mock_personal,
):
    mock_chat_get_history({'messages': []})
    mock_get_chat('client_support')
    await cbox.post(url, data=data)
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data['status'] == expected_task_status

        task = await cbox.app.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(cbox.body_data['id'])},
        )
        assert task['status'] == expected_task_status
        assert task['support_admin'] == 'superuser'
        assert 'support_init' in task['tags']
        assert task['meta_info'] == expected_meta
        assert not task.get('inner_comments')

        if expected_create_chat is None:
            assert not mock_chat_create.calls
        else:
            create_chat_call = mock_chat_create.calls[0]['kwargs']
            create_chat_call.pop('log_extra')
            assert create_chat_call == expected_create_chat

        # try double request
        await cbox.post(url, data=data)
        assert cbox.status == 200
        assert bson.ObjectId(cbox.body_data['id']) == task['_id']
        assert cbox.body_data['status'] == expected_task_status

    elif expected_status == 409:
        assert cbox.body_data == {
            'message': 'Тикет existing_task_id в Крутилке',
            'next_frontend_action': 'open_task',
            'task_id': 'existing_task_id',
            'status': 'Chat already opened',
        }


@pytest.mark.config(
    CHATTERBOX_CHAT_INIT={
        'client': {
            'owner_id': 'user_phone_id',
            'owner_role': 'client',
            'fields': [
                {
                    'id': 'platform',
                    'checks': ['not-empty'],
                    'tanker': 'chat_init.platform',
                    'type': 'select',
                    'options': [
                        {'tanker': 'platform.yandex', 'value': 'yandex'},
                        {'tanker': 'platform.uber', 'value': 'uber'},
                        {'tanker': 'platform.yango', 'value': 'yango'},
                        {'tanker': 'platform.vezet', 'value': 'vezet'},
                    ],
                },
                {
                    'id': 'user_phone',
                    'tanker': 'chat_init.user_phone',
                    'type': 'phone',
                    'checks': ['not-empty'],
                },
                {
                    'id': 'order_id',
                    'tanker': 'chat_init.order_id',
                    'type': 'string',
                    'checks': [],
                },
                {
                    'id': 'message',
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'checks': ['not-empty'],
                },
            ],
        },
        'driver': {
            'owner_id': 'unique_driver_id',
            'owner_role': 'driver',
            'permission': 'driver_init_permission',
            'fields': [
                {
                    'tanker': 'chat_init.driver_uuid',
                    'type': 'string',
                    'id': 'driver_uuid',
                    'checks': ['not-empty'],
                },
                {
                    'tanker': 'chat_init.order_id',
                    'type': 'string',
                    'id': 'order_id',
                    'checks': [],
                },
                {
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'id': 'message',
                    'checks': ['not-empty'],
                },
            ],
        },
        'some_type': {
            'owner_id': 'some_id',
            'owner_role': 'some_role',
            'permission': 'some_init_permission',
            'fields': [
                {
                    'tanker': 'chat_init.some_field',
                    'type': 'phone',
                    'id': 'some_field',
                    'checks': ['not-empty'],
                },
                {
                    'tanker': 'chat_init.order_id',
                    'type': 'string',
                    'id': 'order_id',
                    'checks': [],
                },
                {
                    'tanker': 'chat_init.message',
                    'type': 'text',
                    'id': 'message',
                    'checks': ['not-empty'],
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    ('login', 'expected_result'),
    [
        (
            'superuser',
            {
                'chat_types': [
                    {
                        'fields': [
                            {
                                'checks': ['not-empty'],
                                'id': 'platform',
                                'label': 'platform',
                                'options': [
                                    {'label': 'yandex', 'value': 'yandex'},
                                    {'label': 'uber', 'value': 'uber'},
                                    {'label': 'yango', 'value': 'yango'},
                                    {'label': 'vezet', 'value': 'vezet'},
                                ],
                                'type': 'select',
                            },
                            {
                                'checks': ['not-empty'],
                                'id': 'user_phone',
                                'label': 'user_phone',
                                'type': 'phone',
                            },
                            {
                                'checks': [],
                                'id': 'order_id',
                                'label': 'order_id',
                                'type': 'string',
                            },
                            {
                                'checks': ['not-empty'],
                                'id': 'message',
                                'label': 'message',
                                'type': 'text',
                            },
                        ],
                        'id': 'client',
                        'label': 'client',
                    },
                    {
                        'fields': [
                            {
                                'checks': ['not-empty'],
                                'id': 'driver_uuid',
                                'label': 'driver_uuid',
                                'type': 'string',
                            },
                            {
                                'checks': [],
                                'id': 'order_id',
                                'label': 'order_id',
                                'type': 'string',
                            },
                            {
                                'checks': ['not-empty'],
                                'id': 'message',
                                'label': 'message',
                                'type': 'text',
                            },
                        ],
                        'id': 'driver',
                        'label': 'driver',
                    },
                    {
                        'fields': [
                            {
                                'checks': ['not-empty'],
                                'id': 'some_field',
                                'label': 'some_field',
                                'type': 'phone',
                            },
                            {
                                'checks': [],
                                'id': 'order_id',
                                'label': 'order_id',
                                'type': 'string',
                            },
                            {
                                'checks': ['not-empty'],
                                'id': 'message',
                                'label': 'message',
                                'type': 'text',
                            },
                        ],
                        'id': 'some_type',
                        'label': 'some_type',
                    },
                ],
            },
        ),
        (
            'driver_init',
            {
                'chat_types': [
                    {
                        'fields': [
                            {
                                'checks': ['not-empty'],
                                'id': 'driver_uuid',
                                'label': 'driver_uuid',
                                'type': 'string',
                            },
                            {
                                'checks': [],
                                'id': 'order_id',
                                'label': 'order_id',
                                'type': 'string',
                            },
                            {
                                'checks': ['not-empty'],
                                'id': 'message',
                                'label': 'message',
                                'type': 'text',
                            },
                        ],
                        'id': 'driver',
                        'label': 'driver',
                    },
                ],
            },
        ),
        (
            'some_init',
            {
                'chat_types': [
                    {
                        'fields': [
                            {
                                'checks': ['not-empty'],
                                'id': 'some_field',
                                'label': 'some_field',
                                'type': 'phone',
                            },
                            {
                                'checks': [],
                                'id': 'order_id',
                                'label': 'order_id',
                                'type': 'string',
                            },
                            {
                                'checks': ['not-empty'],
                                'id': 'message',
                                'label': 'message',
                                'type': 'text',
                            },
                        ],
                        'id': 'some_type',
                        'label': 'some_type',
                    },
                ],
            },
        ),
    ],
)
async def test_get_init_task(cbox, patch_auth, login, expected_result):
    patch_auth(login=login)
    await cbox.query('/v1/tasks/init/')
    assert cbox.status == 200
    assert cbox.body_data == expected_result


@pytest.mark.config(CHATTERBOX_PREDISPATCH=True)
@pytest.mark.parametrize(
    [
        'url',
        'expected_task_status',
        'data',
        'expected_status',
        'expected_meta',
        'expected_create_chat',
    ],
    [
        (
            '/v1/tasks/init/driver/',
            'in_progress',
            {
                'request_id': 'another_request_id',
                'message': 'Hello!',
                'driver_uuid': 'some_driver_uuid',
                'platform': 'uberdriver',
                'message_metadata': {'encrypt_key': '123'},
            },
            200,
            {
                'request_id': 'another_request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'status_before_assign': 'new',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': {'encrypt_key': '123'},
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'another_request_id',
                'platform': 'uberdriver',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
        ),
        (
            '/v1/tasks/init/driver/',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'platform': 'taximeter',
            },
            200,
            {
                'request_id': 'request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'status_before_assign': 'new',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello again!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'request_id',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
        ),
        (
            '/v1/tasks/init/driver/',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'missing_uuid',
            },
            424,
            None,
            None,
        ),
        (
            '/v1/tasks/init/driver/',
            'in_progress',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_broken',
            },
            200,
            {
                'driver_uuid': 'driver_uuid_task_broken',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'task_broken',
                'request_id': 'request_id',
                'status_before_assign': 'new',
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
        ),
        (
            '/v1/tasks/init_with_tvm/driver/',
            'new',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_broken',
            },
            200,
            {
                'driver_uuid': 'driver_uuid_task_broken',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'task_broken',
                'request_id': 'request_id',
                'recently_used_macro_ids': ['1', '2'],
            },
            None,
        ),
        (
            '/v1/tasks/init/driver/',
            None,
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'driver_uuid_task_exists',
            },
            409,
            None,
            None,
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_driver_task(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_chat_order_meta,
        url,
        expected_task_status,
        data,
        expected_status,
        expected_meta,
        expected_create_chat,
):
    mock_chat_get_history({'messages': []})
    mock_get_chat('driver_support')
    await cbox.post(url, data=data)
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data['status'] == expected_task_status

        task = await cbox.app.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(cbox.body_data['id'])},
        )
        assert task['status'] == expected_task_status
        assert task['support_admin'] == 'superuser'
        assert 'support_init' in task['tags']

        assert 'ml_request_id' in task['meta_info']
        task['meta_info'].pop('ml_request_id')
        assert task['meta_info'] == expected_meta
        assert not task.get('inner_comments')

        if expected_create_chat is None:
            assert not mock_chat_create.calls
        else:
            create_chat_call = mock_chat_create.calls[0]['kwargs']
            create_chat_call.pop('log_extra')
            assert create_chat_call == expected_create_chat

        # try double request
        await cbox.post(url, data=data)
        assert cbox.status == 200
        assert bson.ObjectId(cbox.body_data['id']) == task['_id']
        assert cbox.body_data['status'] == expected_task_status

    elif expected_status == 409:
        assert cbox.body_data == {
            'message': 'Тикет existing_task_id в Крутилке',
            'next_frontend_action': 'open_task',
            'status': 'Chat already opened',
            'task_id': 'existing_task_id',
        }


@pytest.mark.config(
    CHATTERBOX_PREDISPATCH=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
    },
)
@pytest.mark.parametrize(
    'url, data, expected_status, expected_meta, '
    'expected_create_chat, init_status, expected_ticket_status, '
    'chat_ticket_status, ask_csat',
    [
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'new',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'new',
            'in_progress',
            'open',
            None,
        ),
        (
            '/v1/tasks/init_with_tvm/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'new',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'new',
            'new',
            'open',
            None,
        ),
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'waiting',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'waiting',
            'waiting',
            'pending',
            None,
        ),
        (
            '/v1/tasks/init_with_tvm/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'waiting',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'waiting',
            'waiting',
            'pending',
            None,
        ),
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'closed',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'closed',
            'closed',
            'solved',
            False,
        ),
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'closed_with_csat',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'status_before_assign': 'new',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'closed',
            'closed',
            'solved',
            True,
        ),
        (
            '/v1/tasks/init_with_tvm/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'closed_with_csat',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'closed',
            'closed',
            'solved',
            True,
        ),
        (
            '/v1/tasks/init_with_tvm/client/',
            {
                'request_id': 'some_request_id',
                'macro_id': 321,
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'closed_with_csat',
            },
            424,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            '/v1/tasks/init_with_tvm/client/',
            {
                'request_id': 'some_request_id',
                'macro_id': 123,
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'closed_with_csat',
            },
            200,
            {
                'request_id': 'some_request_id',
                'user_phone_id': 'phone_id',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'phone_type': 'yandex',
                'customer_user_id': 'some_user_id',
                'user_locale': 'ru',
                'user_platform': 'iphone',
                'city': 'moscow',
                'country': 'rus',
                'antifraud_rules': ['taxi_free_trips'],
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'some_request_id',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            'closed',
            'closed',
            'solved',
            True,
        ),
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
                'status': 'unknown',
            },
            400,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_client_task_in_status(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_personal,
        patch,
        url,
        data,
        expected_status,
        expected_meta,
        expected_create_chat,
        init_status,
        expected_ticket_status,
        chat_ticket_status,
        ask_csat,
):

    mock_chat_get_history({'messages': []})
    mock_get_chat('client_support')
    await cbox.post(url, data=data)
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data['status'] == expected_ticket_status

        task = await cbox.app.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(cbox.body_data['id'])},
        )
        assert task['status'] == expected_ticket_status
        tags = task['tags']
        assert 'support_init' in tags
        assert 'init_in_{}_status'.format(init_status) in tags

        assert 'ml_request_id' in task['meta_info']
        task['meta_info'].pop('ml_request_id')
        assert task['meta_info'] == expected_meta
        assert not task.get('inner_comments')

        if expected_create_chat is None:
            assert not mock_chat_create.calls
        else:
            create_chat_call = mock_chat_create.calls[0]['kwargs']
            create_chat_call.pop('log_extra')
            assert create_chat_call == expected_create_chat

        if chat_ticket_status in ('pending', 'solved'):
            chat_update_meta = mock_chat_add_update.calls[1]['kwargs'][
                'update_metadata'
            ]
            assert chat_update_meta['ticket_status'] == chat_ticket_status
            if chat_ticket_status == 'solved':
                assert chat_update_meta['ask_csat'] == ask_csat

        @patch('taxi.clients.support_chat.SupportChatApiClient.search')
        async def _search(*args, **kwargs):
            return {
                'chats': [
                    {
                        'id': task['external_id'],
                        'metadata': {'chatterbox_id': str(task['_id'])},
                    },
                ],
            }

        await cbox.post(url, data=data)
        assert cbox.status == 409

    elif cbox.status == 400:
        assert cbox.body_data == {
            'message': 'Creating chat in status unknown is not allowed',
            'status': 'bad_status',
        }


@pytest.mark.config(CHATTERBOX_PREDISPATCH=True)
@pytest.mark.parametrize(
    'url, data, expected_status, expected_meta, '
    'expected_create_chat, expected_ticket_status',
    [
        (
            '/v1/tasks/init/driver/',
            {
                'request_id': 'another_request_id',
                'message': 'Hello!',
                'driver_uuid': 'some_driver_uuid',
                'status': 'new',
            },
            200,
            {
                'request_id': 'another_request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'status_before_assign': 'new',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'another_request_id',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            'in_progress',
        ),
        (
            '/v1/tasks/init_with_tvm/driver/',
            {
                'request_id': 'another_request_id',
                'message': 'Hello!',
                'driver_uuid': 'some_driver_uuid',
                'status': 'new',
            },
            200,
            {
                'request_id': 'another_request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'another_request_id',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            'new',
        ),
        (
            '/v1/tasks/init/driver/',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'status': 'closed',
                'platform': 'uberdriver',
            },
            200,
            {
                'request_id': 'request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'status_before_assign': 'new',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello again!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'request_id',
                'platform': 'uberdriver',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            'closed',
        ),
        (
            '/v1/tasks/init_with_tvm/driver/',
            {
                'request_id': 'request_id',
                'message': 'Hello again!',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'status': 'closed',
                'platform': 'uberdriver',
            },
            200,
            {
                'request_id': 'request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Hello again!',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'request_id',
                'platform': 'uberdriver',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            'closed',
        ),
        (
            '/v1/tasks/init_with_tvm/driver/',
            {
                'request_id': 'request_id',
                'macro_id': 321,
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'status': 'closed',
                'platform': 'uberdriver',
            },
            424,
            None,
            None,
            None,
        ),
        (
            '/v1/tasks/init_with_tvm/driver/',
            {
                'request_id': 'request_id',
                'macro_id': 123,
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'status': 'closed',
                'platform': 'uberdriver',
            },
            200,
            {
                'request_id': 'request_id',
                'park_db_id': 'some_park_id',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'some_order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'user_locale': 'ru',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'recently_used_macro_ids': ['1', '2'],
            },
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'request_id',
                'platform': 'uberdriver',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            'closed',
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_driver_task_in_status(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_chat_order_meta,
        patch,
        url,
        data,
        expected_status,
        expected_meta,
        expected_create_chat,
        expected_ticket_status,
):
    mock_chat_get_history({'messages': []})
    mock_get_chat('driver_support')
    await cbox.post(url, data=data)
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data['status'] == expected_ticket_status

        task = await cbox.app.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(cbox.body_data['id'])},
        )
        assert task['status'] == expected_ticket_status
        assert task['support_admin'] == 'superuser'
        assert 'support_init' in task['tags']

        assert 'ml_request_id' in task['meta_info']
        task['meta_info'].pop('ml_request_id')
        assert task['meta_info'] == expected_meta
        assert not task.get('inner_comments')
        if expected_create_chat is None:
            assert not mock_chat_create.calls
        else:
            create_chat_call = mock_chat_create.calls[0]['kwargs']
            create_chat_call.pop('log_extra')
            assert create_chat_call == expected_create_chat

        @patch('taxi.clients.support_chat.SupportChatApiClient.search')
        async def _search(*args, **kwargs):
            return {
                'chats': [
                    {
                        'id': task['external_id'],
                        'metadata': {'chatterbox_id': str(task['_id'])},
                    },
                ],
            }

        await cbox.post(url, data=data)
        assert cbox.status == 409


@pytest.mark.parametrize(
    'data, expected_code, expected_args, expected_kwargs',
    [
        ({'order_id': 'test_id'}, 400, None, None),
        ({'macro_ids': [123, 456]}, 400, None, None),
        (
            {'order_id': 'test_id', 'macro_ids': [123, 456]},
            200,
            ['test_id', [123, 456], None],
            {},
        ),
        (
            {
                'order_id': 'test_id',
                'macro_ids': [123, 456],
                'tags': ['proactivity'],
            },
            200,
            ['test_id', [123, 456], ['proactivity']],
            {},
        ),
        (
            {
                'order_id': 'test_id',
                'macro_ids': [123, 456],
                'tags': ['proactivity'],
                'status': 'closed_with_csat',
            },
            200,
            ['test_id', [123, 456], ['proactivity']],
            {'status': 'closed_with_csat'},
        ),
    ],
)
async def test_customer_care_request(
        cbox, stq, data, expected_code, expected_args, expected_kwargs,
):
    await cbox.post('/v1/tasks/init/customer_care/', data=data)
    assert cbox.status == expected_code
    if expected_code == 200:
        call = stq.chatterbox_customer_care_init_task.next_call()
        assert call['args'] == expected_args
        assert 'request_id' in call['kwargs']
        assert isinstance(call['kwargs']['request_id'], str)
        call['kwargs'].pop('request_id')
        call['kwargs'].pop('log_extra')
        assert call['kwargs'] == expected_kwargs
    else:
        assert not stq.chatterbox_customer_care_init_task.has_calls


async def test_customer_care_disabled(cbox):
    assert not await stq_task.customer_care_init(
        cbox.app, 'order_id', [123, 456],
    )


@pytest.mark.parametrize(
    'data, expected_code, expected_args, expected_kwargs',
    [
        ({'order_id': 'test_id'}, 400, None, None),
        ({'macro_ids': [123, 456]}, 400, None, None),
        (
            {'order_id': 'test_id', 'macro_ids': [123, 456]},
            200,
            ['test_id', [123, 456], None],
            {},
        ),
        (
            {
                'order_id': 'test_id',
                'macro_ids': [123, 456],
                'tags': ['proactivity'],
            },
            200,
            ['test_id', [123, 456], ['proactivity']],
            {},
        ),
        (
            {
                'order_id': 'test_id',
                'macro_ids': [123, 456],
                'tags': ['proactivity'],
                'status': 'closed_with_csat',
            },
            200,
            ['test_id', [123, 456], ['proactivity']],
            {'status': 'closed_with_csat'},
        ),
    ],
)
async def test_driver_care_request(
        cbox, stq, data, expected_code, expected_args, expected_kwargs,
):
    await cbox.post('/v1/tasks/init/driver_care/', data=data)
    assert cbox.status == expected_code
    if expected_code == 200:
        call = stq.chatterbox_driver_care_init_task.next_call()
        assert call['args'] == expected_args
        assert 'request_id' in call['kwargs']
        assert isinstance(call['kwargs']['request_id'], str)
        call['kwargs'].pop('request_id')
        call['kwargs'].pop('log_extra')
        assert call['kwargs'] == expected_kwargs
    else:
        assert not stq.chatterbox_driver_care_init_task.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_ENABLE_CUSTOMER_CARE=True,
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    CHATTERBOX_POST_UPDATE_ROUTING=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
    },
)
@pytest.mark.parametrize(
    'order_id, macro_ids, tags, status, order_proc, user_phone_doc, '
    'task_created, expected_status, expected_meta, expected_history_actions,'
    'expected_create_chat, expected_add_update, expected_stat, expected_tags,'
    'expected_chat_id',
    [
        (
            'order_id',
            [456],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            False,
            None,
            None,
            None,
            None,
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_fail_unknown_template': 1,
            },
            None,
            None,
        ),
        (
            'order_id',
            [123],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_client_support',
                'user_phone_id': 'phone_id',
                'order_id': 'order_id',
                'user_phone': '+79001231234',
                'user_phone_pd_id': 'personal_phone_id',
                'phone_type': 'yandex',
                'car_number': '123XYZ',
                'city': 'moscow',
                'antifraud_rules': ['taxi_free_trips'],
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'user_locale': 'ru',
                'recently_used_macro_ids': ['1', '2'],
            },
            ['hidden_comment', 'ensure_predispatched'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'customer_care_order_id_123_client_support',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'update_metadata': {'ticket_status': 'pending'},
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
                'customer_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
            'created_chat_id',
        ),
        (
            'order_id',
            [123],
            ['proactivity'],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_client_support',
                'user_phone_id': 'phone_id',
                'order_id': 'order_id',
                'user_phone': '+79001231234',
                'user_phone_pd_id': 'personal_phone_id',
                'phone_type': 'yandex',
                'car_number': '123XYZ',
                'antifraud_rules': ['taxi_free_trips'],
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'user_locale': 'ru',
                'recently_used_macro_ids': ['1', '2'],
            },
            ['hidden_comment', 'ensure_predispatched'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'customer_care_order_id_123_client_support',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'update_metadata': {'ticket_status': 'pending'},
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
                'customer_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'proactivity',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
            'created_chat_id',
        ),
        (
            'order_id',
            [123, 456],
            None,
            None,
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'uber_iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'uber',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_client_support',
                'user_phone_id': 'phone_id',
                'order_id': 'order_id',
                'user_phone': '+79001231234',
                'user_phone_pd_id': 'personal_phone_id',
                'phone_type': 'uber',
                'car_number': '123XYZ',
                'antifraud_rules': ['taxi_free_trips'],
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'currently_used_macro_ids': ['456'],
                'macro_id': 456,
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'uber_iphone',
                'user_locale': 'ru',
                'recently_used_macro_ids': ['1', '2'],
            },
            ['hidden_comment', 'ensure_predispatched', 'communicate'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'customer_care_order_id_123_client_support',
                'platform': 'uber',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'uber_iphone',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'log_extra': None,
                        'update_metadata': {'ticket_status': 'pending'},
                    },
                },
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'comment +79001231234',
                        'message_id': (
                            'customer_care_order_id_456_client_support'
                        ),
                        'update_metadata': {'ticket_status': 'pending'},
                        'message_metadata': None,
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
                'customer_care_success_comment_added': 1,
                'customer_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'lang_none',
                'more',
                'some',
                'support_init',
                'tags',
            ],
            'created_chat_id',
        ),
        (
            'order_id',
            [123, 679],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_client_support',
                'user_phone_id': 'phone_id',
                'order_id': 'order_id',
                'user_phone': '+79001231234',
                'user_phone_pd_id': 'personal_phone_id',
                'phone_type': 'yandex',
                'car_number': '123XYZ',
                'antifraud_rules': ['taxi_free_trips'],
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'user_locale': 'ru',
                'recently_used_macro_ids': ['1', '2'],
            },
            ['hidden_comment', 'ensure_predispatched'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'customer_care_order_id_123_client_support',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'update_metadata': {'ticket_status': 'pending'},
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
                'customer_care_fail_no_macro': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
            'created_chat_id',
        ),
        (
            'order_id',
            [123, 901],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_client_support',
                'user_phone_id': 'phone_id',
                'order_id': 'order_id',
                'user_phone': '+79001231234',
                'user_phone_pd_id': 'personal_phone_id',
                'phone_type': 'yandex',
                'car_number': '123XYZ',
                'antifraud_rules': ['taxi_free_trips'],
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'user_locale': 'ru',
                'recently_used_macro_ids': ['1', '2'],
            },
            [
                'hidden_comment',
                'ensure_predispatched',
                'macro_processing_fail',
            ],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'customer_care_order_id_123_client_support',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'log_extra': None,
                        'update_metadata': {'ticket_status': 'pending'},
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
                'customer_care_fail_comment': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
            'created_chat_id',
        ),
        (
            'order_id',
            [123],
            [],
            'closed',
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': '5de7afc6779fb31d18b9762e',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'personal_phone_id',
                'phone': '+79001231234',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            True,
            'closed',
            {
                'request_id': 'customer_care_order_id_123_client_support',
                'user_phone_id': 'phone_id',
                'order_id': 'order_id',
                'user_phone': '+79001231234',
                'user_phone_pd_id': 'personal_phone_id',
                'phone_type': 'yandex',
                'car_number': '123XYZ',
                'antifraud_rules': ['taxi_free_trips'],
                'city': 'moscow',
                'country': 'rus',
                'clid': 'some_clid',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_park_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'iphone',
                'user_locale': 'ru',
                'recently_used_macro_ids': ['1', '2'],
            },
            ['hidden_comment', 'dismiss', 'ensure_predispatched'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'phone_id',
                'owner_role': 'client',
                'request_id': 'customer_care_order_id_123_client_support',
                'platform': 'yandex',
                'metadata': {
                    'user_id': 'some_user_id',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'message_id': None,
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': None,
                        'update_metadata': {
                            'ask_csat': False,
                            'retry_csat_request': False,
                            'ticket_status': 'solved',
                        },
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
                'customer_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_closed_status',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
            'created_chat_id',
        ),
        (
            'order_id',
            [123],
            [],
            'closed',
            {
                '_id': 'order_id',
                'order': {
                    'user_phone_id': 'race_task',
                    'application': 'iphone',
                },
            },
            {
                'id': '5de7afc6779fb31d18b9762e',
                'personal_phone_id': 'phone_pd_id_20',
                'phone': 'user_phone_race_task',
                'type': 'yandex',
                'stat': None,
                'is_loyal': None,
                'is_yandex_staff': None,
                'is_taxi_staff': None,
            },
            False,
            None,
            None,
            None,
            None,
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'customer_care_init': 1,
                'customer_care_first_step_success': 1,
            },
            None,
            'race_task_chat_id',
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_customer_care_stq_task(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_tags_v1,
        order_archive_mock,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_personal,
        order_id,
        macro_ids,
        tags,
        status,
        order_proc,
        user_phone_doc,
        task_created,
        expected_status,
        expected_meta,
        expected_history_actions,
        expected_create_chat,
        expected_add_update,
        expected_stat,
        expected_tags,
        expected_chat_id,
        patch_aiohttp_session,
        response_mock,
        mockserver,
):
    mock_get_tags_v1('empty', 'passenger-tags')

    order_archive_mock.set_order_proc(order_proc)

    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_user_phones_get(request):
        assert request.json == {
            'id': order_proc['order']['user_phone_id'],
            'primary_replica': False,
        }
        return user_phone_doc

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _mock_user_phones_retrieve(request):
        assert request.json == {
            'phone': user_phone_doc['phone'],
            'type': user_phone_doc['type'],
            'primary_replica': False,
        }
        return user_phone_doc

    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }

    mock_chat_get_history({'messages': []})
    mock_get_chat('client_support')

    task_id = await stq_task.customer_care_init(
        app=cbox.app,
        order_id=order_id,
        macro_ids=macro_ids,
        tags=tags,
        status=status,
    )

    if task_created:
        task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
        assert task['status'] == expected_status
        assert task['support_admin'] == 'superuser'
        assert task['tags'] == expected_tags

        assert 'ml_request_id' in task['meta_info']
        task['meta_info'].pop('ml_request_id')
        assert task['meta_info'] == expected_meta
        create_chat_call = mock_chat_create.calls[0]['kwargs']
        create_chat_call.pop('log_extra')
        assert create_chat_call == expected_create_chat
        add_update_calls = mock_chat_add_update.calls
        assert add_update_calls[1:] == expected_add_update
        for index, action in enumerate(expected_history_actions):
            task_action = task['history'][
                index - len(expected_history_actions)
            ]
            assert task_action['action'] == action
            if action == 'hidden_comment':
                assert (
                    task_action['hidden_comment']
                    == 'Trying add %s macros to task' % macro_ids
                )

        order_proc_call = order_archive_mock.order_proc_retrieve.next_call()
        assert order_proc_call['request'].json == {
            'id': order_id,
            'lookup_yt': True,
        }
    else:
        assert not task_id

    if expected_chat_id:
        task = await cbox.app.db.support_chatterbox.find_one(
            {'external_id': expected_chat_id},
        )
        assert task['status'] != 'routing'

    stats = await cbox.app.db.event_stats.find_one({}, {'_id': False})
    assert stats == expected_stat


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(CHATTERBOX_ENABLE_DRIVER_CARE=True)
@pytest.mark.parametrize(
    'order_id, macro_ids, tags, status, order_proc, task_created,'
    'expected_status, expected_meta, expected_history_actions,'
    'expected_create_chat, expected_add_update, expected_stat, expected_tags',
    [
        (
            'order_id',
            [456],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'performer': {'uuid': 'some_driver_uuid'},
                    'application': 'iphone',
                },
            },
            False,
            None,
            None,
            None,
            None,
            None,
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_care_init': 1,
                'driver_care_fail_unknown_template': 1,
            },
            None,
        ),
        (
            'order_id',
            [123],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'performer': {'uuid': 'some_driver_uuid'},
                    'application': 'iphone',
                },
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_driver_support',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'user_locale': 'ru',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'antifraud_rules': ['taxi_free_trips'],
            },
            ['hidden_comment', 'ensure_predispatched'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'customer_care_order_id_123_driver_support',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'update_metadata': {'ticket_status': 'pending'},
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_care_init': 1,
                'driver_care_first_step_success': 1,
                'driver_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
        ),
        (
            'order_id',
            [123, 789],
            [],
            None,
            {
                '_id': 'order_id',
                'order': {
                    'performer': {'uuid': 'some_driver_uuid'},
                    'application': 'iphone',
                },
            },
            True,
            'waiting',
            {
                'request_id': 'customer_care_order_id_123_driver_support',
                'driver_uuid': 'some_driver_uuid',
                'currently_used_macro_ids': ['789'],
                'macro_id': 789,
                'order_id': 'order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'user_locale': 'ru',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'antifraud_rules': ['taxi_free_trips'],
            },
            ['hidden_comment', 'ensure_predispatched', 'communicate'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'customer_care_order_id_123_driver_support',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'update_metadata': {'ticket_status': 'pending'},
                        'log_extra': None,
                    },
                },
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'comment some_driver_license',
                        'message_id': (
                            'customer_care_order_id_789_driver_support'
                        ),
                        'update_metadata': {'ticket_status': 'pending'},
                        'message_metadata': None,
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_care_init': 1,
                'driver_care_first_step_success': 1,
                'driver_care_success_comment_added': 1,
                'driver_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_waiting_status',
                'lang_none',
                'more',
                'some',
                'support_init',
                'tags',
            ],
        ),
        (
            'order_id',
            [123],
            [],
            'closed_with_csat',
            {
                '_id': 'order_id',
                'order': {
                    'performer': {'uuid': 'some_driver_uuid'},
                    'application': 'iphone',
                },
            },
            True,
            'closed',
            {
                'request_id': 'customer_care_order_id_123_driver_support',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'user_locale': 'ru',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'antifraud_rules': ['taxi_free_trips'],
            },
            ['hidden_comment', 'dismiss', 'ensure_predispatched'],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'customer_care_order_id_123_driver_support',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'message_id': None,
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': None,
                        'update_metadata': {
                            'ask_csat': True,
                            'retry_csat_request': False,
                            'ticket_status': 'solved',
                        },
                        'log_extra': None,
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_care_init': 1,
                'driver_care_first_step_success': 1,
                'driver_care_success': 1,
            },
            [
                'init_customer_care',
                'init_in_closed_status',
                'some',
                'support_init',
                'tags',
                'lang_none',
            ],
        ),
        (
            'order_id',
            [123, 789],
            [],
            'closed_with_csat',
            {
                '_id': 'order_id',
                'order': {
                    'performer': {'uuid': 'some_driver_uuid'},
                    'application': 'iphone',
                },
            },
            True,
            'closed',
            {
                'currently_used_macro_ids': ['789'],
                'macro_id': 789,
                'request_id': 'customer_care_order_id_123_driver_support',
                'driver_uuid': 'some_driver_uuid',
                'order_id': 'order_id',
                'city': 'moscow',
                'country': 'rus',
                'coupon': False,
                'coupon_used': False,
                'driver_id': 'some_driver_id',
                'order_alias_id': 'some_alias_id',
                'payment_type': 'cash',
                'precomment': 'ahaha',
                'tariff': 'econom',
                'customer_user_id': 'some_user_id',
                'user_platform': 'android',
                'user_locale': 'ru',
                'park_db_id': 'some_park_id',
                'driver_license': 'some_driver_license',
                'driver_name': 'Швабрэ Старая Пристарая',
                'driver_phone': '+70000000000',
                'driver_locale': 'ru',
                'taximeter_version': '0.1.2',
                'clid': 'some_clid',
                'park_name': 'Лещ',
                'park_city': 'moscow',
                'park_country': 'rus',
                'car_number': '123XYZ',
                'unique_driver_id': 'some_unique_driver_id',
                'antifraud_rules': ['taxi_free_trips'],
            },
            [
                'hidden_comment',
                'dismiss',
                'ensure_predispatched',
                'communicate',
            ],
            {
                'message_metadata': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'Test comment',
                'owner_id': 'some_unique_driver_id',
                'owner_role': 'driver',
                'request_id': 'customer_care_order_id_123_driver_support',
                'platform': 'taximeter',
                'metadata': {
                    'db': 'some_park_id',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                    'user_application': 'taximeter',
                },
            },
            [
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'message_id': None,
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': None,
                        'update_metadata': {
                            'ask_csat': True,
                            'retry_csat_request': False,
                            'ticket_status': 'solved',
                        },
                        'log_extra': None,
                    },
                },
                {
                    'args': ('created_chat_id',),
                    'kwargs': {
                        'log_extra': None,
                        'message_id': (
                            'customer_care_order_id_789_driver_support'
                        ),
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'comment some_driver_license',
                        'update_metadata': {'ticket_status': 'solved'},
                    },
                },
            ],
            {
                'name': 'user_support_chat_stats',
                'created': NOW,
                'driver_care_init': 1,
                'driver_care_first_step_success': 1,
                'driver_care_success': 1,
                'driver_care_success_comment_added': 1,
            },
            [
                'init_customer_care',
                'init_in_closed_status',
                'lang_none',
                'more',
                'some',
                'support_init',
                'tags',
            ],
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_driver_care_stq_task(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_tags_v1,
        order_archive_mock,
        order_id,
        macro_ids,
        tags,
        status,
        order_proc,
        task_created,
        expected_status,
        expected_meta,
        expected_history_actions,
        expected_create_chat,
        expected_add_update,
        expected_stat,
        expected_tags,
        patch_aiohttp_session,
        response_mock,
):
    mock_get_tags_v1('empty')

    order_archive_mock.set_order_proc(order_proc)

    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }

    mock_chat_get_history({'messages': []})
    mock_get_chat('client_support')

    task_id = await stq_task.driver_care_init(
        app=cbox.app,
        order_id=order_id,
        macro_ids=macro_ids,
        tags=tags,
        status=status,
    )

    if task_created:
        task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
        assert task['status'] == expected_status
        assert task['support_admin'] == 'superuser'
        assert task['tags'] == expected_tags

        assert 'ml_request_id' in task['meta_info']
        task['meta_info'].pop('ml_request_id')
        assert task['meta_info'] == expected_meta
        create_chat_call = mock_chat_create.calls[0]['kwargs']
        create_chat_call.pop('log_extra')
        assert create_chat_call == expected_create_chat
        add_update_calls = mock_chat_add_update.calls
        assert add_update_calls[1:] == expected_add_update
        for index, action in enumerate(expected_history_actions):
            task_action = task['history'][
                index - len(expected_history_actions)
            ]
            assert task_action['action'] == action
            if action == 'hidden_comment':
                assert (
                    task_action['hidden_comment']
                    == 'Trying add %s macros to task' % macro_ids
                )
        order_proc_call = order_archive_mock.order_proc_retrieve.next_call()
        assert order_proc_call['request'].json == {
            'id': order_id,
            'lookup_yt': True,
        }
    else:
        assert not task_id

    stats = await cbox.app.db.event_stats.find_one({}, {'_id': False})
    assert stats == expected_stat


async def test_driver_care_disabled(cbox):
    assert not await stq_task.driver_care_init(
        cbox.app, 'order_id', [123, 456],
    )


@pytest.fixture
def mock_antifraud_refund_bad(mockserver):
    @mockserver.json_handler(
        '/antifraud_refund-api/taxi/support', prefix=False,
    )
    def _rules(request):
        return None

    return mockserver.make_response('bad request', status=400)


@pytest.mark.config(
    CHATTERBOX_PREDISPATCH=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
    },
)
@pytest.mark.parametrize(
    ['url', 'data', 'expected_meta_antifraud_rules'],
    [
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
            },
            {'antifraud_rules': []},
        ),
        (
            '/v2/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'platform': 'yandex',
            },
            {'antifraud_rules': []},
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_client_task_with_bad_antifraud_refund(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_user_phone,
        mock_antifraud_refund_bad,
        mock_get_chat_order_meta,
        url,
        data,
        expected_meta_antifraud_rules,
        mock_uuid_uuid4,
        mock_personal,
):
    mock_chat_get_history({'messages': []})
    mock_get_chat('client_support')
    await cbox.post(url, data=data)

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(cbox.body_data['id'])},
    )
    assert (
        task['meta_info']['antifraud_rules']
        == expected_meta_antifraud_rules['antifraud_rules']
    )


@pytest.mark.config(
    CHATTERBOX_PREDISPATCH=True,
    CHATTERBOX_ANTIFRAUD_RULES_FOR_META=[],
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'user_phone': 'phones'},
    },
)
@pytest.mark.parametrize(
    ['url', 'data', 'expected_meta_antifraud_rules'],
    [
        (
            '/v1/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'phone_type': 'yandex',
            },
            {'antifraud_rules': []},
        ),
        (
            '/v2/tasks/init/client/',
            {
                'request_id': 'some_request_id',
                'message': 'Hello!',
                'user_phone': '+79999999999',
                'platform': 'yandex',
            },
            {'antifraud_rules': []},
        ),
    ],
)
@pytest.mark.translations(chatterbox=TRANSLATE)
async def test_init_client_task_with_empty_names_in_config(
        cbox,
        mock_chat_create,
        mock_chat_search,
        mock_get_chat,
        mock_chat_add_update,
        mock_get_additional_meta,
        mock_chat_get_history,
        mock_get_user_phone,
        mock_antifraud_refund,
        url,
        data,
        expected_meta_antifraud_rules,
        mock_uuid_uuid4,
        mock_personal,
):
    mock_chat_get_history({'messages': []})
    mock_get_chat('client_support')
    await cbox.post(url, data=data)

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(cbox.body_data['id'])},
    )
    assert (
        task['meta_info']['antifraud_rules']
        == expected_meta_antifraud_rules['antifraud_rules']
    )
