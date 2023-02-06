# pylint: disable=too-many-lines, protected-access
# pylint: disable=redefined-outer-name,no-member,expression-not-assigned
import datetime
import http
import json

import bson
import pytest

from taxi_support_chat.stq import stq_task

TRANSLATIONS = {
    'user_support_chat.support_name.dmitry': {
        'ru': 'Андрей',
        'en': 'andrew',
        'lv': 'Jūratė',
    },
    'user_support_chat.support_name.yandex_support': {
        'ru': 'Саппорт яндекс',
        'en': 'Yandex support',
        'lt': 'Jūratė',
        'az': 'test',
    },
    'user_support_chat.support_name.uber_support': {
        'ru': 'Саппорт uber',
        'en': 'Uber support',
        'az': 'Uber support',
        'ky': 'ub sup',
    },
    'user_support_chat.support_name.samir': {'ru': 'Самир', 'en': 'samir'},
    'user_support_chat.support_name.dias': {'ru': 'Самир', 'en': 'dias'},
    'user_support_chat.support_name.alihan': {'ru': 'Самир', 'en': 'alihan'},
    'user_support_chat.support_name.miras': {'ru': 'Самир', 'en': 'miras'},
}

CHAT_TYPES = [
    'driver_support',
    'selfreg_driver_support',
    'client_support',
    'facebook_support',
    'sms_support',
    'eats_support',
    'eats_app_support',
    'safety_center_support',
    'opteum_support',
    'corp_cabinet_support',
    'google_play_support',
    'help_yandex_support',
    'labs_admin_yandex_support',
    'carsharing_support',
    'scouts_support',
    'lavka_storages_support',
    'website_support',
    'restapp_support',
    'market_support',
]


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_GENDER_BY_COUNTRY_PLATFORM_CHAT_TYPE={
        '__default__': {
            '__default__': {
                'driver_support': ['female'],
                'client_support': ['male'],
                'eats_support': ['male'],
                'safety_center_support': ['male'],
            },
            'uber': {},
        },
    },
    SUPPORT_CHAT_CREATE_NEW_ALLOWED_CHAT_TYPES=list(CHAT_TYPES),
)
@pytest.mark.parametrize(
    'data, lang, expected_result, expected_db_result',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                    },
                },
                'owner': {'id': '5bbf8133779fb35d847fdb1f', 'role': 'driver'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'driver_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'processed_with_chatterbox': True,
                        'author': 'driver',
                        'author_id': '5bbf8133779fb35d847fdb1f',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'driver_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '5bbf8133779fb35d847fdb1f',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'eats_message',
                'message': {
                    'text': 'test eats',
                    'sender': {'id': '14355465656', 'role': 'eats_client'},
                },
                'owner': {'id': '14355465656', 'role': 'eats_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'eats_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'eats_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '14355465656',
                        'role': 'eats_client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'eats_message',
                        'processed_with_chatterbox': True,
                        'author': 'eats_client',
                        'author_id': '14355465656',
                        'message': 'test eats',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'eats_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '14355465656',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'emergency_message',
                'message': {
                    'text': 'test emergency',
                    'sender': {
                        'id': '14355465656',
                        'role': 'safety_center_client',
                        'platform': 'yandex',
                    },
                },
                'owner': {
                    'id': '14355465656',
                    'role': 'safety_center_client',
                    'platform': 'yandex',
                },
            },
            'ru',
            {
                'metadata': {
                    'ask_csat': False,
                    'created': '2018-07-18T11:20:00+0000',
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'updated': '2018-07-18T11:20:00+0000',
                    'user_locale': 'ru',
                    'platform': 'yandex',
                    'ticket_status': 'open',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'emergency_message',
                'participants': [
                    {
                        'id': 'support',
                        'nickname': 'Саппорт яндекс',
                        'role': 'support',
                    },
                    {
                        'id': '14355465656',
                        'platform': 'yandex',
                        'role': 'safety_center_client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'safety_center_support',
            },
            {
                'ask_csat': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'safety_center_client',
                        'processed_with_chatterbox': True,
                        'author_id': '14355465656',
                        'id': 'emergency_message',
                        'message': 'test emergency',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': '14355465656',
                'platform': 'yandex',
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'type': 'safety_center_support',
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'visible': True,
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'client',
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'user_application': 'uber_android',
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            'en',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'status': {'is_open': True, 'is_visible': False},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Uber support',
                    },
                    {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'en',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'processed_with_chatterbox': True,
                        'author': 'user',
                        'author_id': '5b4f17bb779fb332fcc26151',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'client_support',
                'user_id': 'test_user_id',
                'ask_csat': False,
                'retry_csat_request': False,
                'last_message_from_user': True,
                'owner_id': '5b4f17bb779fb332fcc26151',
                'support_name': 'Uber support',
                'support_avatar_url': '4',
                'user_locale': 'en',
                'user_country': 'rus',
                'user_application': 'uber_android',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.uber_support',
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'message': {
                    'text': 'test_fb',
                    'sender': {
                        'id': '1960892827353513',
                        'role': 'facebook_user',
                    },
                },
                'metadata': {'page': '563720454066049'},
                'owner': {'id': '1960892827353513', 'role': 'facebook_user'},
            },
            '',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'status': {'is_open': True, 'is_visible': True},
                'type': 'facebook_support',
                'participants': [
                    {'id': 'support', 'role': 'support', 'nickname': ''},
                    {
                        'id': '1960892827353513',
                        'role': 'facebook_user',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'page': '563720454066049',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': (
                            'jwKugoO71XA3_UOIdtsyT_'
                            'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                            '-U1XMH1RBACz6ZXPqOapw'
                        ),
                        'processed_with_chatterbox': True,
                        'author': 'facebook_user',
                        'author_id': '1960892827353513',
                        'message': 'test_fb',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'facebook_support',
                'ask_csat': False,
                'retry_csat_request': False,
                'page': '563720454066049',
                'last_message_from_user': True,
                'owner_id': '1960892827353513',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'sms_message',
                'message': {
                    'text': 'test_sms',
                    'sender': {'id': '+79001234568', 'role': 'sms_client'},
                },
                'owner': {'id': '+79001234568', 'role': 'sms_client'},
            },
            '',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'sms_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'sms_support',
                'participants': [
                    {'id': 'support', 'role': 'support', 'nickname': ''},
                    {
                        'id': '+79001234568',
                        'role': 'sms_client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'sms_message',
                        'processed_with_chatterbox': True,
                        'author': 'sms_client',
                        'author_id': '+79001234568',
                        'message': 'test_sms',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'sms_support',
                'ask_csat': False,
                'retry_csat_request': False,
                'last_message_from_user': True,
                'owner_id': '+79001234568',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'sms_message',
                'message': {
                    'text': 'test_sms',
                    'sender': {
                        'id': '+79001234568',
                        'role': 'sms_client',
                        'platform': 'android',
                    },
                },
                'owner': {
                    'id': '+79001234568',
                    'role': 'sms_client',
                    'platform': 'android',
                },
            },
            '',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'sms_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'sms_support',
                'participants': [
                    {'id': 'support', 'role': 'support', 'nickname': ''},
                    {
                        'id': '+79001234568',
                        'role': 'sms_client',
                        'platform': 'yandex',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'platform': 'yandex',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'sms_message',
                        'processed_with_chatterbox': True,
                        'author': 'sms_client',
                        'author_id': '+79001234568',
                        'message': 'test_sms',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'sms_support',
                'ask_csat': False,
                'retry_csat_request': False,
                'last_message_from_user': True,
                'owner_id': '+79001234568',
                'platform': 'yandex',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'support_message',
                'message': {
                    'text': 'test support',
                    'sender': {'id': 'some_support', 'role': 'support'},
                },
                'owner': {'id': '14355465656', 'role': 'eats_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'support_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'eats_support',
                'participants': [
                    {
                        'id': 'some_support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '14355465656',
                        'role': 'eats_client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'support_message',
                        'processed_with_chatterbox': True,
                        'author': 'support',
                        'author_id': 'some_support',
                        'message': 'test support',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'eats_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '14355465656',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
        ),
    ],
)
async def test_double_request_new_chat(
        web_app_client,
        web_context,
        data,
        lang,
        expected_result,
        expected_db_result,
):
    response = await web_app_client.post(
        '/v1/chat/new',
        data=json.dumps(data),
        headers={'Accept-Language': lang},
    )
    assert response.status == http.HTTPStatus.CREATED
    result = await response.json()
    old_chat_id = result.pop('id')
    avatar_url = result['participants'][0].pop('avatar_url')
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(old_chat_id)},
    )
    support_avatar_url = chat_doc.get('support_avatar_url')
    support_name = chat_doc.get('support_name')
    expected_db_result['_id'] = bson.ObjectId(old_chat_id)
    assert chat_doc == expected_db_result

    response = await web_app_client.post(
        '/v1/chat/new',
        data=json.dumps(data),
        headers={'Accept-Language': lang},
    )
    assert response.status == http.HTTPStatus.CREATED
    result = await response.json()
    new_chat_id = result.pop('id')
    expected_result['participants'][0]['avatar_url'] = avatar_url
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(old_chat_id)},
    )
    expected_db_result['_id'] = bson.ObjectId(new_chat_id)
    if support_avatar_url:
        expected_db_result['support_avatar_url'] = support_avatar_url
    if support_name:
        expected_db_result['support_name'] = support_name
    assert chat_doc == expected_db_result
    assert old_chat_id == new_chat_id


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_CREATE_NEW_ALLOWED_CHAT_TYPES=list(CHAT_TYPES),
)
@pytest.mark.parametrize(
    'data, expected_result, expected_db_result',
    [
        (
            {
                'request_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'message': {
                    'text': 'test_fb_ex',
                    'sender': {
                        'id': '1960892827353512',
                        'role': 'facebook_user',
                    },
                },
                'metadata': {'page': '563720454066049'},
                'owner': {'id': '1960892827353512', 'role': 'facebook_user'},
            },
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'status': {'is_open': True, 'is_visible': True},
                'type': 'facebook_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': '',
                        'avatar_url': None,
                    },
                    {
                        'id': '1960892827353512',
                        'role': 'facebook_user',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'page': '563720454066049',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': (
                            'jwKugoO71XA3_UOIdtsyT_'
                            'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                            '-U1XMH1RBACz6ZXPqOapw'
                        ),
                        'processed_with_chatterbox': True,
                        'author': 'facebook_user',
                        'author_id': '1960892827353512',
                        'message': 'test_fb_ex',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'open': True,
                'visible': True,
                'type': 'facebook_support',
                'page': '563720454066049',
                'last_message_from_user': True,
                'owner_id': '1960892827353512',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'message': {
                    'text': 'text_1',
                    'sender': {
                        'id': '5b4f5059779fb332fcc29999',
                        'role': 'client',
                        'platform': 'uber',
                    },
                },
                'metadata': {'page': '563720454066049'},
                'owner': {
                    'id': '5b4f5059779fb332fcc29999',
                    'role': 'client',
                    'platform': 'uber',
                },
            },
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'status': {'is_open': True, 'is_visible': False},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                        'avatar_url': '5',
                    },
                    {
                        'id': '5b4f5059779fb332fcc29999',
                        'role': 'client',
                        'platform': 'uber',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'page': '563720454066049',
                    'platform': 'uber',
                    'ticket_status': 'open',
                },
            },
            {
                'ask_csat': False,
                'retry_csat_request': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc29999',
                        'id': (
                            'jwKugoO71XA3_UOIdtsyT_Bm4aG27EeCyJz6PRBI31En8ugi'
                            '2tT1TBlDzBcnZIzLi-U1XMH1RBACz6ZXPqOapw'
                        ),
                        'processed_with_chatterbox': True,
                        'message': 'text_1',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': '5b4f5059779fb332fcc29999',
                'page': '563720454066049',
                'platform': 'uber',
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'type': 'client_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'visible': False,
                'ticket_status': 'open',
            },
        ),
    ],
)
async def test_create_new_with_existing_chat(
        web_app_client, web_context, data, expected_result, expected_db_result,
):

    response = await web_app_client.post('/v1/chat/new', data=json.dumps(data))
    assert response.status == http.HTTPStatus.CREATED
    result = await response.json()
    old_chat_id = result.pop('id')
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(old_chat_id)},
    )

    expected_db_result['_id'] = bson.ObjectId(old_chat_id)
    assert chat_doc == expected_db_result

    data['request_id'] = '{}_2'.format(data['request_id'])
    expected_result['newest_message_id'] = '{}_2'.format(
        expected_result['newest_message_id'],
    )

    response = await web_app_client.post('/v1/chat/new', data=json.dumps(data))
    assert response.status == http.HTTPStatus.CREATED
    result = await response.json()
    new_chat_id = result.pop('id')
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(old_chat_id)},
    )
    chat_doc.pop('_id', None)
    expected_db_result.pop('_id', None)

    assert chat_doc == expected_db_result
    assert old_chat_id != new_chat_id


@pytest.mark.parametrize(
    'data',
    [
        (
            {
                'request_id': (
                    'jwKugoO71XA3_UOIdtsyT_'
                    'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                    '-U1XMH1RBACz6ZXPqOapw'
                ),
                'message': {
                    'text': 'test_fb_ex',
                    'sender': {
                        'id': '1960892827353512',
                        'role': 'facebook_user',
                    },
                },
                'metadata': {'page': '563720454066049'},
                'owner': {'id': '1960892827353512', 'role': 'facebook_user'},
            }
        ),
    ],
)
async def test_create_not_allowed_chat_type(web_app_client, web_context, data):

    response = await web_app_client.post('/v1/chat/new', data=json.dumps(data))
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.config(
    SUPPORT_CHAT_CREATE_NEW_ALLOWED_CHAT_TYPES=list(CHAT_TYPES),
    SUPPORT_CHAT_ADD_CHAT_METADATA_FIELD=True,
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'send_metadata, chat_metadata, root_meta_fields',
    [
        (
            {
                'user_id': 'test_user_id',
                'user_application': 'uber_android',
                'unknown_field': 'unknown',
            },
            {'unknown_field': 'unknown'},
            {'user_id': 'test_user_id', 'user_application': 'uber_android'},
        ),
    ],
)
async def test_chat_metadata(
        web_app_client,
        web_context,
        send_metadata,
        chat_metadata,
        root_meta_fields,
):
    data = dict(
        {
            'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
            'message': {
                'text': 'test',
                'sender': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
        },
    )
    data['metadata'] = send_metadata
    response = await web_app_client.post('/v1/chat/new', data=json.dumps(data))
    assert response.status == http.HTTPStatus.CREATED

    result = await response.json()
    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(result['id'])},
    )

    if chat_metadata:
        assert chat_doc['metadata'] == chat_metadata

    for field, value in root_meta_fields.items():
        assert chat_doc[field] == value


@pytest.mark.parametrize(
    'data, expected_stq_put_calls',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                    },
                },
                'owner': {'id': '5bbf8133779fb35d847fdb1f', 'role': 'driver'},
            },
            [],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                    },
                },
                'owner': {'id': '5bbf8133779fb35d847fdb1f', 'role': 'driver'},
                'create_chatterbox_task': True,
            },
            [
                {
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'chat_request_data': {
                            'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                            'message': {
                                'text': 'test',
                                'sender': {
                                    'id': '5bbf8133779fb35d847fdb1f',
                                    'role': 'driver',
                                },
                            },
                            'owner': {
                                'id': '5bbf8133779fb35d847fdb1f',
                                'role': 'driver',
                            },
                            'create_chatterbox_task': True,
                        },
                    },
                    'queue': 'support_chat_prepare_chatterbox_meta',
                },
            ],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                    },
                    'metadata': {
                        'driver_on_order': True,
                        'appeal_source': 'chat',
                    },
                },
                'metadata': {
                    'db': 'some_park_db_id',
                    'driver_uuid': 'some_uuid',
                },
                'owner': {'id': '5bbf8133779fb35d847fdb1f', 'role': 'driver'},
                'create_chatterbox_task': True,
            },
            [
                {
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'chat_request_data': {
                            'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                            'message': {
                                'text': 'test',
                                'sender': {
                                    'id': '5bbf8133779fb35d847fdb1f',
                                    'role': 'driver',
                                },
                                'metadata': {
                                    'driver_on_order': True,
                                    'appeal_source': 'chat',
                                },
                            },
                            'metadata': {
                                'db': 'some_park_db_id',
                                'driver_uuid': 'some_uuid',
                            },
                            'owner': {
                                'id': '5bbf8133779fb35d847fdb1f',
                                'role': 'driver',
                            },
                            'create_chatterbox_task': True,
                        },
                    },
                    'queue': 'support_chat_prepare_chatterbox_meta',
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    SUPPORT_CHAT_CREATE_NEW_ALLOWED_CHAT_TYPES=list(CHAT_TYPES),
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_chatterbox_task(
        web_app_client, web_context, stq, data, expected_stq_put_calls,
):
    response = await web_app_client.post('/v1/chat/new', data=json.dumps(data))
    assert response.status == http.HTTPStatus.CREATED

    response_json = await response.json()

    calls = []
    while not stq.is_empty:
        calls.append(stq.support_chat_prepare_chatterbox_meta.next_call())

    for call in calls:
        del call['kwargs']['log_extra']
        assert call['args'] == [response_json['id']]
        assert call['id'] == response_json['id']
        del call['args']
        del call['id']
    assert calls == expected_stq_put_calls


@pytest.mark.parametrize(
    'chat_id, request_data, expected_additional_meta, expected_stq_put_calls',
    [
        (
            '5b436ece779fb3302cc784bf',
            {'message': {}},
            {'metadata': {}},
            [
                {
                    'args': ['5b436ece779fb3302cc784bf', {'some': 'metadata'}],
                    'kwargs': {},
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'queue': 'support_chat_create_chatterbox_task',
                    'id': '00000000000040008000000000000000',
                },
            ],
        ),
        (
            '5b436ece779fb3302cc784bf',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                    },
                    'metadata': {
                        'driver_on_order': True,
                        'appeal_source': 'chat',
                    },
                },
                'metadata': {
                    'db': 'some_park_db_id',
                    'driver_uuid': 'some_uuid',
                },
                'owner': {'id': '5bbf8133779fb35d847fdb1f', 'role': 'driver'},
                'create_chatterbox_task': True,
            },
            {
                'metadata': {
                    'driver_uuid': 'some_uuid',
                    'park_db_id': 'some_park_db_id',
                    'source': 'chat',
                },
            },
            [
                {
                    'args': ['5b436ece779fb3302cc784bf', {'some': 'metadata'}],
                    'kwargs': {'add_tags': ['driver_on_order']},
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'queue': 'support_chat_create_chatterbox_task',
                    'id': '00000000000040008000000000000000',
                },
            ],
        ),
        pytest.param(
            '5b436ece779fb3302cc784bf',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8133779fb35d847fdb1f',
                        'role': 'driver',
                    },
                    'metadata': {
                        'driver_on_order': True,
                        'appeal_source': 'chat',
                    },
                },
                'metadata': {
                    'db': 'some_park_db_id',
                    'driver_uuid': 'some_uuid',
                },
                'owner': {'id': '5bbf8133779fb35d847fdb1f', 'role': 'driver'},
                'create_chatterbox_task': True,
            },
            None,
            [
                {
                    'args': [
                        '5b436ece779fb3302cc784bf',
                        {
                            'driver_uuid': 'some_uuid',
                            'park_db_id': 'some_park_db_id',
                            'source': 'chat',
                        },
                    ],
                    'kwargs': {'add_tags': ['driver_on_order']},
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'queue': 'support_chat_create_chatterbox_task',
                    'id': '00000000000040008000000000000000',
                },
            ],
            marks=[
                pytest.mark.config(
                    SUPPORT_CHAT_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client_support': {
                            '__default__': False,
                            'chatterbox_meta': True,
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_prepare_chatterbox_meta(
        stq3_context,
        stq,
        mock_uuid4,
        mock_additional_meta,
        chat_id,
        request_data,
        expected_additional_meta,
        expected_stq_put_calls,
):
    mocked_additional_meta = mock_additional_meta(
        metadata={'some': 'metadata'},
    )
    await stq_task.prepare_chatterbox_meta(
        stq3_context, chat_id, chat_request_data=request_data,
    )
    if expected_additional_meta:
        assert (
            mocked_additional_meta.calls[0]['json'] == expected_additional_meta
        )
    else:
        assert not mocked_additional_meta.calls

    calls = []
    while not stq.is_empty:
        calls.append(stq.support_chat_create_chatterbox_task.next_call())

    for call in calls:
        del call['kwargs']['log_extra']
    assert calls == expected_stq_put_calls
