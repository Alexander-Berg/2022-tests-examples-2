# pylint: disable=too-many-lines, protected-access
# pylint: disable=redefined-outer-name,no-member,expression-not-assigned
import datetime
import http
import json

import bson
import pytest

from taxi_support_chat.internal import const
from taxi_support_chat.internal import support_chats

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

USER_CHAT_SUPPORTS = {
    'rus': {
        'yandex': [
            {'tanker_key': 'dmitry', 'url': '0'},
            {'tanker_key': 'andrew', 'url': '1'},
            {'tanker_key': 'pavel', 'url': '2'},
            {'tanker_key': 'artem', 'url': '3'},
        ],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
    'kaz': {
        'yandex': [
            {'tanker_key': 'dias', 'url': '5', 'tags': ['business_client']},
            {'tanker_key': 'miras', 'url': '5'},
            {
                'tanker_key': 'alihan',
                'url': '5',
                'tags': ['test_tag', 'vip_tag'],
            },
            {'tanker_key': 'ajzere', 'url': '5'},
        ],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
    'civ': {
        'yandex': [
            {'tanker_key': 'patrick', 'url': '5'},
            {'tanker_key': 'fernand', 'url': '5'},
            {'tanker_key': 'richard', 'url': '5'},
            {'tanker_key': 'cheik', 'url': '5'},
        ],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
    '__default__': {
        'yandex': [{'tanker_key': 'yandex_support', 'url': '5'}],
        'uber': [{'tanker_key': 'uber_support', 'url': '4'}],
        '__default__': [{'tanker_key': 'yandex_support', 'url': '5'}],
    },
}


def _check_stq_call(stq, data, chat_id, chat_type, service_notifies=None):
    if chat_type == 'facebook_support':
        queue = 'taxi_sm_monitor_facebook'
        delay = 30
    elif chat_type == 'sms_support':
        queue = 'taxi_support_chat_sms_notify'
        delay = 5
    elif chat_type == 'whatsapp_support':
        queue = 'taxi_support_chat_whatsapp_notify'
        delay = 30
    else:
        queue = 'driver_support_push'
        delay = 5

    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)

    if 'message' in data and data['message']['sender']['role'] == 'support':
        if chat_type in [
                'facebook_support',
                'driver_support',
                'whatsapp_support',
        ]:
            call_args = getattr(stq, queue).next_call()
            call_args.pop('kwargs')

            assert call_args == {
                'queue': queue,
                'eta': eta,
                'id': data['request_id'],
                'args': [{'$oid': chat_id}, data['request_id']],
            }

    if service_notifies:
        for queue in service_notifies:
            call_args = getattr(stq, queue).next_call()
            del call_args['kwargs']['log_extra']

            assert call_args == {
                'queue': queue,
                'id': data['request_id'],
                'args': [
                    {'$oid': chat_id},
                    data['request_id'],
                    const.EVENT_NEW_CHAT,
                ],
                'kwargs': {},
                'eta': datetime.datetime(2018, 7, 18, 11, 40, 5),
            }


@pytest.mark.parametrize(
    'data',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5059779fb332fcc26152'},
            }
        ),
        (
            {
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': 'bad_owner_id', 'role': 'client'},
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {
                        'order_id': 'some_order_id',
                        'attachments': [
                            {'id': 'attachment_id_0', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'link': 'test_link',
                                'name': 'test_name',
                            },
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'lv',
                },
                'owner': {
                    'id': '5b4f5092779fb332fcc26153',
                    'role': 'client',
                    'platform': None,
                },
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {
                        'order_id': 'some_order_id',
                        'attachments': [
                            {'id': 'attachment_id_0', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'link': 'test_link',
                                'name': 'test_name',
                            },
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'lv',
                },
                'owner': {
                    'id': '5b4f5092779fb332fcc26153',
                    'role': 'client',
                    'platform': 'vezet',
                },
            }
        ),
        (
            {
                'request_id': 'opteum_message',
                'message': {
                    'text': 'test opteum',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'opteum_client',
                        'platform': 'yandex',
                    },
                },
                'owner': {
                    'id': '5b4f5059779fb332fcc26152',
                    'role': 'opteum_client',
                    'platform': 'yandex',
                },
            }
        ),
        (
            {
                'request_id': 'corp_cabinet_message',
                'message': {
                    'text': 'test corp_cabinet',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'corp_cabinet_client',
                        'platform': 'yandex',
                    },
                },
                'owner': {
                    'id': '5b4f5059779fb332fcc26152',
                    'role': 'corp_cabinet_client',
                    'platform': 'yandex',
                },
            }
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bad_request(web_app_client, mock_tvm_keys, data):
    response = await web_app_client.post(
        '/v1/chat/',
        data=json.dumps(data),
        headers={'X-Ya-Service-Ticket': 'backend_service_ticket'},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    'service_ticket,data,expected_status',
    [
        (
            'backend_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            http.HTTPStatus.CREATED,
        ),
        (
            'backend_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'driver'},
            },
            http.HTTPStatus.CREATED,
        ),
        (
            'disp_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'disp_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'driver'},
            },
            http.HTTPStatus.CREATED,
        ),
        (
            'corp_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            http.HTTPStatus.FORBIDDEN,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_chat_type_access(
        web_app_client, mock_tvm_keys, service_ticket, data, expected_status,
):
    response = await web_app_client.post(
        '/v1/chat/',
        data=json.dumps(data),
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_status


@pytest.mark.config(TVM_DISABLE_CHECK=['support_chat'])
@pytest.mark.parametrize(
    'service_ticket,data,expected_status',
    [
        (
            'backend_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'driver'},
            },
            http.HTTPStatus.CREATED,
        ),
        (
            'disp_service_ticket',
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            http.HTTPStatus.CREATED,
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(TVM_ENABLED=False)
async def test_chat_type_access_no_tvm(
        web_app_client, mock_tvm_keys, service_ticket, data, expected_status,
):
    response = await web_app_client.post(
        '/v1/chat/',
        data=json.dumps(data),
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_status


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_GENDER_BY_COUNTRY_PLATFORM_CHAT_TYPE={
        '__default__': {
            '__default__': {
                'driver_support': ['female'],
                'client_support': ['male'],
                'eats_support': ['male'],
                'eats_app_support': ['male'],
                'safety_center_support': ['male'],
                'opteum_support': ['male'],
                'corp_cabinet_support': ['male'],
                'google_play_support': ['male'],
                'help_yandex_support': ['male'],
                'labs_admin_yandex_support': ['male'],
                'carsharing_support': ['male'],
                'scouts_support': ['male'],
                'lavka_storages_support': ['male'],
                'website_support': ['male'],
                'market_support': ['male'],
            },
        },
    },
    SUPPORT_CHAT_PLATFORM_MAPPING={
        'yandex': 'yandex',
        'android': 'yandex',
        'iphone': 'yandex',
        'uber': 'uber',
        'uber_android': 'uber',
        'uber_iphone': 'uber',
        'yango_android': 'yandex',
        'yango_iphone': 'yandex',
        'taximeter': 'taximeter',
        'uberdriver': 'uberdriver',
        'help_yandex': 'help_yandex',
        'labs_admin_yandex': 'labs_admin_yandex',
    },
)
@pytest.mark.parametrize(
    'data, lang, expected_result, expected_db_result',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test 1111222233334444',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
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
                    'last_message_from_user': False,
                    'new_messages': 1,
                    'user_locale': 'ru',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'author': 'support',
                        'author_id': 'support',
                        'message': 'test 111122******4444',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'client_support',
                'new_messages': 1,
                'send_push': True,
                'owner_id': '5b4f17bb779fb332fcc26151',
                'last_message_from_user': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'support_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
            },
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
                    'platform': 'uberdriver',
                },
            },
            'ru',
            {
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'actions': [],
                'view': {'show_message_input': True},
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
                        'platform': 'uberdriver',
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
                    'platform': 'uberdriver',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
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
                'platform': 'uberdriver',
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
                    'platform': 'taximeter',
                },
            },
            'ru',
            {
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'view': {'show_message_input': True},
                'actions': [],
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
                        'platform': 'taximeter',
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
                    'platform': 'taximeter',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
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
                'platform': 'taximeter',
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
                'request_id': 'eats_app_message',
                'message': {
                    'text': 'test eats app',
                    'sender': {'id': '14355465656', 'role': 'eats_app_client'},
                },
                'owner': {'id': '14355465656', 'role': 'eats_app_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'eats_app_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'eats_app_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '14355465656',
                        'role': 'eats_app_client',
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
                        'id': 'eats_app_message',
                        'author': 'eats_app_client',
                        'author_id': '14355465656',
                        'message': 'test eats app',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'eats_app_support',
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
                'request_id': 'help_yandex_message',
                'message': {
                    'text': 'test help',
                    'sender': {
                        'id': '14355465656',
                        'role': 'help_yandex_client',
                        'platform': 'help_yandex',
                    },
                },
                'owner': {
                    'id': '14355465656',
                    'role': 'help_yandex_client',
                    'platform': 'help_yandex',
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
                    'platform': 'help_yandex',
                    'ticket_status': 'open',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'help_yandex_message',
                'participants': [
                    {
                        'id': 'support',
                        'nickname': 'Саппорт яндекс',
                        'role': 'support',
                    },
                    {
                        'id': '14355465656',
                        'platform': 'help_yandex',
                        'role': 'help_yandex_client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'help_yandex_support',
            },
            {
                'ask_csat': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'help_yandex_client',
                        'author_id': '14355465656',
                        'id': 'help_yandex_message',
                        'message': 'test help',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': '14355465656',
                'platform': 'help_yandex',
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'type': 'help_yandex_support',
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'visible': True,
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'labs_admin_yandex_message',
                'message': {
                    'text': 'test help',
                    'sender': {
                        'id': '14355465656',
                        'role': 'labs_admin_yandex_client',
                        'platform': 'labs_admin_yandex',
                    },
                },
                'owner': {
                    'id': '14355465656',
                    'role': 'labs_admin_yandex_client',
                    'platform': 'labs_admin_yandex',
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
                    'platform': 'labs_admin_yandex',
                    'ticket_status': 'open',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'labs_admin_yandex_message',
                'participants': [
                    {
                        'id': 'support',
                        'nickname': 'Саппорт яндекс',
                        'role': 'support',
                    },
                    {
                        'id': '14355465656',
                        'platform': 'labs_admin_yandex',
                        'role': 'labs_admin_yandex_client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'labs_admin_yandex_support',
            },
            {
                'ask_csat': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'labs_admin_yandex_client',
                        'author_id': '14355465656',
                        'id': 'labs_admin_yandex_message',
                        'message': 'test help',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': '14355465656',
                'platform': 'labs_admin_yandex',
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'type': 'labs_admin_yandex_support',
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'visible': True,
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'opteum_message',
                'message': {
                    'text': 'test opteum',
                    'sender': {
                        'id': 'l33t_sp34k_t3st',
                        'role': 'opteum_client',
                        'platform': 'yandex',
                    },
                },
                'owner': {
                    'id': 'l33t_sp34k_t3st',
                    'role': 'opteum_client',
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
                'newest_message_id': 'opteum_message',
                'participants': [
                    {
                        'id': 'support',
                        'nickname': 'Саппорт яндекс',
                        'role': 'support',
                    },
                    {
                        'id': 'l33t_sp34k_t3st',
                        'platform': 'yandex',
                        'role': 'opteum_client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'opteum_support',
            },
            {
                'ask_csat': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'opteum_client',
                        'author_id': 'l33t_sp34k_t3st',
                        'id': 'opteum_message',
                        'message': 'test opteum',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': 'l33t_sp34k_t3st',
                'platform': 'yandex',
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'type': 'opteum_support',
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'visible': True,
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'corp_cabinet_message',
                'message': {
                    'text': 'test corp_cabinet',
                    'sender': {
                        'id': 'l33t_sp34k_3333',
                        'role': 'corp_cabinet_client',
                        'platform': 'yandex',
                    },
                },
                'owner': {
                    'id': 'l33t_sp34k_3333',
                    'role': 'corp_cabinet_client',
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
                'newest_message_id': 'corp_cabinet_message',
                'participants': [
                    {
                        'id': 'support',
                        'nickname': 'Саппорт яндекс',
                        'role': 'support',
                    },
                    {
                        'id': 'l33t_sp34k_3333',
                        'platform': 'yandex',
                        'role': 'corp_cabinet_client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'corp_cabinet_support',
            },
            {
                'ask_csat': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'corp_cabinet_client',
                        'author_id': 'l33t_sp34k_3333',
                        'id': 'corp_cabinet_message',
                        'message': 'test corp_cabinet',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': 'l33t_sp34k_3333',
                'platform': 'yandex',
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'type': 'corp_cabinet_support',
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
                'request_id': 'google_play_feedback',
                'message': {
                    'text': 'test google_play',
                    'sender': {
                        'id': 'review_id_1',
                        'role': 'google_play_review',
                    },
                },
                'owner': {'id': 'review_id_1', 'role': 'google_play_review'},
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
                    'ticket_status': 'open',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'google_play_feedback',
                'participants': [
                    {'id': 'support', 'nickname': '', 'role': 'support'},
                    {
                        'id': 'review_id_1',
                        'role': 'google_play_review',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'google_play_support',
            },
            {
                'ask_csat': False,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'google_play_review',
                        'author_id': 'review_id_1',
                        'id': 'google_play_feedback',
                        'message': 'test google_play',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'owner_id': 'review_id_1',
                'type': 'google_play_support',
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'visible': True,
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'carsharing_message',
                'message': {
                    'text': 'test carsharing',
                    'sender': {
                        'id': '14355465656',
                        'role': 'carsharing_client',
                    },
                },
                'owner': {'id': '14355465656', 'role': 'carsharing_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'carsharing_message',
                'status': {'is_open': True, 'is_visible': False},
                'type': 'carsharing_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '14355465656',
                        'role': 'carsharing_client',
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
                        'id': 'carsharing_message',
                        'author': 'carsharing_client',
                        'author_id': '14355465656',
                        'message': 'test carsharing',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'carsharing_support',
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
                'request_id': 'scouts_message',
                'message': {
                    'text': 'test scouts',
                    'sender': {'id': '143554465656', 'role': 'scouts_client'},
                },
                'owner': {'id': '143554465656', 'role': 'scouts_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'scouts_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'scouts_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '143554465656',
                        'role': 'scouts_client',
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
                        'id': 'scouts_message',
                        'author': 'scouts_client',
                        'author_id': '143554465656',
                        'message': 'test scouts',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'scouts_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '143554465656',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'lavka_storages_message',
                'message': {
                    'text': 'test lavka_storages',
                    'sender': {
                        'id': '143554465656',
                        'role': 'lavka_storages_client',
                    },
                },
                'owner': {
                    'id': '143554465656',
                    'role': 'lavka_storages_client',
                },
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'lavka_storages_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'lavka_storages_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '143554465656',
                        'role': 'lavka_storages_client',
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
                        'id': 'lavka_storages_message',
                        'author': 'lavka_storages_client',
                        'author_id': '143554465656',
                        'message': 'test lavka_storages',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'lavka_storages_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '143554465656',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'website_message',
                'message': {
                    'text': 'test website',
                    'sender': {'id': '143554465656', 'role': 'website_client'},
                },
                'owner': {'id': '143554465656', 'role': 'website_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'website_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'website_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '143554465656',
                        'role': 'website_client',
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
                        'id': 'website_message',
                        'author': 'website_client',
                        'author_id': '143554465656',
                        'message': 'test website',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'website_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '143554465656',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'market_message',
                'message': {
                    'text': 'test market',
                    'sender': {'id': '143554465656', 'role': 'market_client'},
                },
                'owner': {'id': '143554465656', 'role': 'market_client'},
            },
            'ru',
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'market_message',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'market_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '143554465656',
                        'role': 'market_client',
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
                        'id': 'market_message',
                        'author': 'market_client',
                        'author_id': '143554465656',
                        'message': 'test market',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'market_support',
                'last_message_from_user': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '143554465656',
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
        mock_tvm_keys,
        stq,
        data,
        lang,
        expected_result,
        expected_db_result,
):
    response = await web_app_client.post(
        '/v1/chat/', data=json.dumps(data), headers={'Accept-Language': lang},
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
    _check_stq_call(stq, data, old_chat_id, chat_doc['type'])

    response = await web_app_client.post(
        '/v1/chat/',
        data=json.dumps(data),
        headers={
            'Accept-Language': lang,
            'X-Ya-Service-Ticket': 'backend_service_ticket',
        },
    )
    assert response.status == http.HTTPStatus.OK
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
    _check_stq_call(stq, data, old_chat_id, chat_doc['type'])


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_PLATFORM_MAPPING={
        'yandex': 'yandex',
        'android': 'yandex',
        'iphone': 'yandex',
        'uber': 'uber',
        'uber_android': 'uber',
        'uber_iphone': 'uber',
        'yango_android': 'yandex',
        'yango_iphone': 'yandex',
        'taximeter': 'taximeter',
        'uberdriver': 'uberdriver',
    },
)
@pytest.mark.parametrize(
    'data, expected_result, expected_db_result',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            },
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': False,
                    'new_messages': 3,
                    'user_locale': 'ru',
                    'csat_value': 'good',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'chatterbox_id': 'chatterbox_id',
                    'metadata_field_1': 'value_1',
                },
            },
            {
                'messages': [
                    {
                        'author': 'user',
                        'author_id': 'some_user_id',
                        'id': 'message_11',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'name': 'filename.txt',
                                },
                                {
                                    'link': 'test_url_2',
                                    'link_preview': 'link_preview',
                                    'preview_width': 150,
                                    'preview_height': 200,
                                    'type': 'image',
                                    'mimetype': 'image/png',
                                    'size': 20000,
                                },
                            ],
                        },
                    },
                    {
                        'author': 'support',
                        'id': 'message_12',
                        'message': 'text_2',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'author': 'support',
                        'author_id': 'support',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'text_indexed': True,
                'ask_csat': True,
                'new_messages': 3,
                'send_push': True,
                'user_phone_id': bson.ObjectId('5b4f5059779fb332fcc26152'),
                'owner_id': '5b4f5059779fb332fcc26152',
                'type': 'client_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'support_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'user_id': 'user_id1',
                'support_avatar_url': 4,
                'support_name': 'Иван',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': False,
                'csat_value': 'good',
                'chatterbox_id': 'chatterbox_id',
                'csat_reasons': ['fast answer', 'thank you'],
                'metadata': {'metadata_field_1': 'value_1'},
            },
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5bbf8048779fb35d847fdb1e', 'role': 'driver'},
            },
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
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'driver',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': False,
                    'new_messages': 3,
                    'user_locale': 'ru',
                    'csat_value': 'good',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'chatterbox_id': 'chatterbox_id',
                },
            },
            {
                'messages': [
                    {
                        'author': 'driver',
                        'id': 'message_71',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                    },
                    {
                        'author': 'support',
                        'id': 'message_72',
                        'message': 'text_2',
                        'metadata': {'order_id': 'some_order_id'},
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'author': 'support',
                        'author_id': 'support',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'text_indexed': True,
                'new_messages': 3,
                'send_push': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'support_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'user_id': 'user_id1',
                'unique_driver_id': bson.ObjectId('5bbf8048779fb35d847fdb1e'),
                'owner_id': '5bbf8048779fb35d847fdb1e',
                'type': 'driver_support',
                'support_avatar_url': 4,
                'support_name': 'Иван',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ask_csat': False,
                'last_message_from_user': False,
                'csat_value': 'good',
                'chatterbox_id': 'chatterbox_id',
                'csat_reasons': ['fast answer', 'thank you'],
            },
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'driver',
                    },
                },
                'owner': {
                    'id': '5bbf8048779fb35d847fdb1e',
                    'role': 'driver',
                    'platform': 'taximeter',
                },
            },
            {
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'driver_support',
                'view': {'show_message_input': True},
                'actions': [],
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'driver',
                        'platform': 'taximeter',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:20:00+0000',
                    'updated': '2018-07-18T11:20:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'csat_value': 'good',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'chatterbox_id': 'chatterbox_id',
                    'platform': 'taximeter',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'author': 'driver',
                        'id': 'message_71',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                    },
                    {
                        'author': 'support',
                        'id': 'message_72',
                        'message': 'text_2',
                        'metadata': {'order_id': 'some_order_id'},
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'author': 'driver',
                        'author_id': '5bbf8048779fb35d847fdb1e',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'text_indexed': True,
                'new_messages': 2,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'user_id': 'user_id1',
                'unique_driver_id': bson.ObjectId('5bbf8048779fb35d847fdb1e'),
                'owner_id': '5bbf8048779fb35d847fdb1e',
                'type': 'driver_support',
                'platform': 'taximeter',
                'support_avatar_url': 4,
                'support_name': 'Иван',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ask_csat': False,
                'retry_csat_request': False,
                'last_message_from_user': True,
                'csat_value': 'good',
                'chatterbox_id': 'chatterbox_id',
                'csat_reasons': ['fast answer', 'thank you'],
                'ticket_status': 'open',
            },
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5df1fc13779fb3085850a6cd',
                        'role': 'driver',
                    },
                },
                'owner': {'id': '5df1fc13779fb3085850a6cd', 'role': 'driver'},
            },
            {
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'view': {'show_message_input': True},
                'actions': [],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'driver_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 2,
                        'nickname': '',
                    },
                    {
                        'id': '5df1fc13779fb3085850a6cd',
                        'role': 'driver',
                        'platform': 'taximeter',
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
                    'platform': 'taximeter',
                },
            },
            {
                'messages': [
                    {
                        'author': 'support',
                        'id': '539eb65127e5b1f53980dfa9_message_5',
                        'message': 'text_to_driver',
                        'timestamp': datetime.datetime(2018, 7, 5, 10, 59, 50),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'author': 'driver',
                        'author_id': '5df1fc13779fb3085850a6cd',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'user_id': 'driver',
                'owner_id': '5df1fc13779fb3085850a6cd',
                'type': 'driver_support',
                'platform': 'taximeter',
                'support_avatar_url': 2,
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'ask_csat': False,
                'retry_csat_request': False,
                'last_message_from_user': True,
                'car_number': 'AM777R999',
                'support_timestamp': datetime.datetime(2018, 7, 5, 10, 59, 50),
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
                    'chatterbox_id': 'chatterbox_id_fb',
                    'page': '563720454066049',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'message_81',
                        'author': 'facebook_user',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                    },
                    {
                        'id': (
                            'jwKugoO71XA3_UOIdtsyT_'
                            'Bm4aG27EeCyJz6PRBI31En8ugi2tT1TBlDzBcnZIzLi'
                            '-U1XMH1RBACz6ZXPqOapw'
                        ),
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
                'chatterbox_id': 'chatterbox_id_fb',
                'open': True,
                'visible': True,
                'text_indexed': True,
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
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': '',
                        'avatar_url': '2',
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
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'chatterbox_id': 'anime',
                    'page': '563720454066049',
                    'platform': 'uber',
                    'ticket_status': 'open',
                },
            },
            {
                'ask_csat': False,
                'retry_csat_request': False,
                'chatterbox_id': 'anime',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'support',
                        'id': '539eb65be7e5b1f53980dfa9_message_2',
                        'message': 'text_4',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc29999',
                        'id': (
                            'jwKugoO71XA3_UOIdtsyT_Bm4aG27EeCyJz6PRBI31En8ugi'
                            '2tT1TBlDzBcnZIzLi-U1XMH1RBACz6ZXPqOapw'
                        ),
                        'message': 'text_1',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 20),
                    },
                ],
                'ticket_processed': True,
                'new_messages': 2,
                'open': True,
                'owner_id': '5b4f5059779fb332fcc29999',
                'page': '563720454066049',
                'platform': 'uber',
                'support_avatar_url': '2',
                'support_name': '',
                'text_indexed': True,
                'type': 'client_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 20),
                'user_id': 'user_id1337',
                'user_phone_id': bson.ObjectId('5b4f5059779fb332fcc26159'),
                'visible': True,
                'ticket_status': 'open',
            },
        ),
    ],
)
async def test_double_existing_chat(
        web_app_client,
        web_context,
        mock_tvm_keys,
        stq,
        data,
        expected_result,
        expected_db_result,
):

    response = await web_app_client.post('/v1/chat/', data=json.dumps(data))
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    old_chat_id = result.pop('id')
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(old_chat_id)},
    )

    expected_db_result['_id'] = bson.ObjectId(old_chat_id)
    assert chat_doc == expected_db_result
    _check_stq_call(stq, data, old_chat_id, chat_doc['type'])

    response = await web_app_client.post(
        '/v1/chat/',
        data=json.dumps(data),
        headers={'X-Ya-Service-Ticket': 'backend_service_ticket'},
    )
    assert response.status == http.HTTPStatus.OK
    result = await response.json()
    new_chat_id = result.pop('id')
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(old_chat_id)},
    )

    expected_db_result['_id'] = bson.ObjectId(new_chat_id)
    assert chat_doc == expected_db_result

    assert old_chat_id == new_chat_id
    _check_stq_call(stq, data, old_chat_id, chat_doc['type'])


@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'data',
    [
        (
            {
                'request_id': 'message_21',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            }
        ),
        (
            {
                'request_id': 'message_11',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            }
        ),
    ],
)
async def test_not_found(web_app_client, dummy_tvm_check, data):
    response = await web_app_client.post('/v1/chat/', data=json.dumps(data))
    assert response.status == http.HTTPStatus.CONFLICT


@pytest.mark.now('2018-07-18T11:40:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
    SUPPORT_CHAT_SERVICE_NOTIFY=True,
    SUPPORT_CHAT_SERVICE_NOTIFY_FILTERS={
        'support_gateway': {'type': ['client_support']},
    },
)
@pytest.mark.parametrize(
    (
        'data',
        'match_response',
        'lang',
        'status',
        'expected_result',
        'db_result',
        'services_notifies',
    ),
    [
        (
            {
                'request_id': 'c0af0b343ec647faa75fdcd44d82a738',
                'message': {
                    'text': 'text_template_whatsapp',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'support',
                    },
                    'metadata': {},
                },
                'metadata': {
                    'user_phone_pd_id': 'user_phone_pd_id',
                    'template_name': 'infobip_test_hsm_1',
                    'contact_point_id': 'taxi_test',
                    'user_locale': 'ru',
                },
                'owner': {
                    'id': '5b4f5092779fb332fcc26153',
                    'role': 'whatsapp_client',
                },
            },
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'сдох',
                            'items': [
                                {
                                    'type': 'call',
                                    'id': 'action_3',
                                    'view': {'title': 'Позвонить в 112'},
                                    'params': {'number': '79099575227'},
                                },
                                {
                                    'type': 'text',
                                    'id': 'action_2',
                                    'view': {'title': 'Написать 112'},
                                    'params': {'text': '112'},
                                },
                            ],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            'ru',
            http.HTTPStatus.CREATED,
            {
                'metadata': {
                    'ask_csat': False,
                    'created': '2018-07-18T11:40:00+0000',
                    'last_message_from_user': False,
                    'new_messages': 1,
                    'updated': '2018-07-18T11:40:00+0000',
                    'user_locale': 'ru',
                },
                'newest_message_id': 'c0af0b343ec647faa75fdcd44d82a738',
                'participants': [
                    {
                        'avatar_url': '5',
                        'id': '5b4f5059779fb332fcc26152',
                        'nickname': 'Саппорт яндекс',
                        'role': 'support',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'is_owner': True,
                        'role': 'whatsapp_client',
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'whatsapp_support',
                'view': {'show_message_input': True},
                'actions': [],
            },
            {
                'contact_point_id': 'taxi_test',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'last_message_from_user': False,
                'messages': [
                    {
                        'author': 'support',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'id': 'c0af0b343ec647faa75fdcd44d82a738',
                        'message': 'text_template_whatsapp',
                        'message_type': 'text',
                        'metadata': {},
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'new_messages': 1,
                'open': True,
                'owner_id': '5b4f5092779fb332fcc26153',
                'send_push': False,
                'support_avatar_url': '5',
                'support_name': 'Саппорт яндекс',
                'support_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'template_name': 'infobip_test_hsm_1',
                'ticket_processed': True,
                'type': 'whatsapp_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'user_locale': 'ru',
                'user_phone_pd_id': 'user_phone_pd_id',
                'visible': True,
            },
            None,
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {
                        'order_id': 'some_order_id',
                        'attachments': [
                            {'id': 'attachment_id_0', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'link': 'test_link',
                                'name': 'test_name',
                            },
                        ],
                    },
                    'scenario_context': {'last_action_id': 'action_1'},
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'lv',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'сдох',
                            'items': [
                                {
                                    'type': 'call',
                                    'id': 'action_3',
                                    'view': {'title': 'Позвонить в 112'},
                                    'params': {'number': '79099575227'},
                                },
                                {
                                    'type': 'text',
                                    'id': 'action_2',
                                    'view': {'title': 'Написать 112'},
                                    'params': {'text': '112'},
                                },
                            ],
                            'scenario_context': {'last_action_id': 'action_1'},
                        },
                    },
                ],
                'view': {'show_message_input': False},
            },
            'lv',
            http.HTTPStatus.CREATED,
            {
                'actions': [
                    {
                        'type': 'questionary',
                        'id': 'action_1',
                        'content': {
                            'text': 'сдох',
                            'items': [
                                {
                                    'type': 'call',
                                    'id': 'action_3',
                                    'view': {'title': 'Позвонить в 112'},
                                    'params': {'number': '79099575227'},
                                },
                                {
                                    'type': 'text',
                                    'id': 'action_2',
                                    'view': {'title': 'Написать 112'},
                                    'params': {'text': '112'},
                                },
                            ],
                        },
                    },
                ],
                'view': {'show_message_input': False},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'status': {'is_open': True, 'is_visible': False},
                'type': 'client_support',
                'participants': [
                    {'id': 'system', 'role': 'system_scenarios'},
                    {
                        'id': 'support',
                        'role': 'support',
                        'nickname': 'Jūratė',
                        'avatar_url': '0',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'lv',
                    'ticket_id': 123,
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'author': 'system_scenarios',
                        'author_id': 'system',
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82_question',
                        'message': 'anime',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(
                            2018, 7, 18, 11, 39, 59,
                        ),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'metadata': {
                            'order_id': 'some_order_id',
                            'attachments': [
                                {
                                    'id': 'attachment_id_0',
                                    'source': 'mds',
                                    'size': 1000,
                                    'mimetype': 'application/octet-stream',
                                    'name': 'test_file',
                                },
                                {
                                    'id': 'attachment_id_2',
                                    'link': 'test_link',
                                    'name': 'test_name',
                                },
                            ],
                        },
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                        'scenario_context': {'last_action_id': 'action_1'},
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'client_support',
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_application': 'iphone',
                'user_country': 'rus',
                'user_locale': 'lv',
                'support_name': 'Jūratė',
                'support_avatar_url': '0',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.dmitry',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'aze',
                    'user_application': 'android',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'ru',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '5',
                        'nickname': 'Самир',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_id': 123,
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id_1',
                                    'source': 'mds',
                                    'size': 1000,
                                    'name': 'test_file',
                                    'mimetype': 'application/octet-stream',
                                },
                            ],
                        },
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'type': 'client_support',
                'visible': False,
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_application': 'android',
                'user_country': 'aze',
                'support_name': 'Самир',
                'support_avatar_url': '5',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.samir',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {},
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'user_tz': 'Asia/Vladivostok',
                    'user_locale': 'be',
                    'user_country': 'aze',
                    'user_application': 'android',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'be',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '5',
                        'nickname': 'Самир',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
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
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                        'metadata': {},
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'type': 'client_support',
                'visible': False,
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_application': 'android',
                'user_country': 'aze',
                'user_locale': 'ru',
                'support_name': 'Самир',
                'support_avatar_url': '5',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.samir',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_locale': 'en',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'en',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '5',
                        'nickname': 'Yandex support',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'en',
                    'ticket_id': 123,
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'client_support',
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_locale': 'en',
                'support_name': 'Yandex support',
                'support_avatar_url': '5',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_locale': 'az',
                    'user_application': 'uber_android',
                    'user_country': 'civ',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'en',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '4',
                        'nickname': 'Uber support',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'az',
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'client_support',
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_locale': 'az',
                'user_application': 'uber_android',
                'user_country': 'civ',
                'support_name': 'Uber support',
                'support_avatar_url': '4',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.uber_support',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5bbf8167779fb35d847fdb20',
                        'role': 'driver',
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_locale': 'az',
                    'user_application': 'uber_android',
                    'user_country': 'civ',
                },
                'owner': {'id': '5bbf8167779fb35d847fdb20', 'role': 'driver'},
            },
            None,
            'en',
            http.HTTPStatus.CREATED,
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'driver_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': '4',
                        'nickname': 'Uber support',
                    },
                    {
                        'id': '5bbf8167779fb35d847fdb20',
                        'role': 'driver',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'az',
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'driver',
                        'author_id': '5bbf8167779fb35d847fdb20',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'type': 'driver_support',
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_locale': 'az',
                'user_application': 'uber_android',
                'user_country': 'civ',
                'support_name': 'Uber support',
                'support_avatar_url': '4',
                'owner_id': '5bbf8167779fb35d847fdb20',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.uber_support',
                'ticket_status': 'open',
            },
            None,
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_locale': 'ru',
                    'user_country': 'rus',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'ru',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '5',
                        'nickname': 'Саппорт яндекс',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_id': 123,
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'client_support',
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_locale': 'ru',
                'user_country': 'rus',
                'support_name': 'Саппорт яндекс',
                'support_avatar_url': '5',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.yandex_support',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            },
            None,
            'ru',
            http.HTTPStatus.OK,
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 2,
                    'user_locale': 'ru',
                    'csat_value': 'good',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'chatterbox_id': 'chatterbox_id',
                    'metadata_field_1': 'value_1',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'author': 'user',
                        'author_id': 'some_user_id',
                        'id': 'message_11',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'name': 'filename.txt',
                                },
                                {
                                    'link': 'test_url_2',
                                    'link_preview': 'link_preview',
                                    'preview_width': 150,
                                    'preview_height': 200,
                                    'type': 'image',
                                    'mimetype': 'image/png',
                                    'size': 20000,
                                },
                            ],
                        },
                    },
                    {
                        'author': 'support',
                        'id': 'message_12',
                        'message': 'text_2',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'text_indexed': True,
                'new_messages': 2,
                'last_message_from_user': True,
                'support_avatar_url': 4,
                'support_name': 'Иван',
                'user_phone_id': bson.ObjectId('5b4f5059779fb332fcc26152'),
                'owner_id': '5b4f5059779fb332fcc26152',
                'type': 'client_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'user_id': 'user_id1',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'ask_csat': False,
                'retry_csat_request': False,
                'csat_value': 'good',
                'chatterbox_id': 'chatterbox_id',
                'ticket_status': 'open',
                'csat_reasons': ['fast answer', 'thank you'],
                'metadata': {'metadata_field_1': 'value_1'},
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test_c',
                    'sender': {
                        'id': '5b4f5059779fb332fcc2615e',
                        'role': 'client',
                    },
                },
                'owner': {'id': '5b4f5059779fb332fcc2615e', 'role': 'client'},
            },
            None,
            'ru',
            http.HTTPStatus.OK,
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
                        'avatar_url': 4,
                        'nickname': 'Иван',
                    },
                    {
                        'id': '5b4f5059779fb332fcc2615e',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'chatterbox_id': 'chatterbox_id_1',
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
                        'author': 'user',
                        'id': 'message_51',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc2615e',
                        'message': 'test_c',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'text_indexed': False,
                'new_messages': 0,
                'last_message_from_user': True,
                'support_name': 'Иван',
                'support_avatar_url': 4,
                'user_phone_id': bson.ObjectId('5b4f5059779fb332fcc2615e'),
                'owner_id': '5b4f5059779fb332fcc2615e',
                'type': 'client_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'user_id': 'user_id5',
                'ask_csat': False,
                'retry_csat_request': False,
                'ticket_status': 'open',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'chatterbox_id': 'chatterbox_id_1',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test_c',
                    'sender': {
                        'id': '5b4f5092779fb332fcc26155',
                        'role': 'client',
                    },
                },
                'owner': {'id': '5b4f5092779fb332fcc26155', 'role': 'client'},
            },
            None,
            'ru',
            http.HTTPStatus.OK,
            {
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': 2,
                        'nickname': 'Петр',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26155',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'old_metadata_field': 'old',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'author': 'user',
                        'id': 'message_41',
                        'message': 'text_1',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'author': 'support',
                        'id': 'message_42',
                        'message': 'text_2',
                        'timestamp': datetime.datetime(
                            2018, 7, 10, 11, 12, 50,
                        ),
                    },
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5092779fb332fcc26155',
                        'message': 'test_c',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': True,
                'text_indexed': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'last_message_from_user': True,
                'support_name': 'Петр',
                'support_avatar_url': 2,
                'user_phone_id': bson.ObjectId('5b4f5092779fb332fcc26155'),
                'owner_id': '5b4f5092779fb332fcc26155',
                'type': 'client_support',
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'user_id': 'user_id4',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'metadata': {'old_metadata_field': 'old'},
                'user_application': 'application',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {
                        'order_id': 'some_order_id',
                        'attachments': [
                            {'id': 'attachment_id_0', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'link': 'test_link',
                                'name': 'test_name',
                            },
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'lv',
                },
                'owner': {
                    'id': '5b4f5092779fb332fcc26153',
                    'role': 'client',
                    'platform': 'yandex',
                },
            },
            None,
            'lv',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '0',
                        'nickname': 'Jūratė',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'platform': 'yandex',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'lv',
                    'ticket_id': 123,
                    'author_id': 456,
                    'platform': 'yandex',
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'metadata': {
                            'order_id': 'some_order_id',
                            'attachments': [
                                {
                                    'id': 'attachment_id_0',
                                    'source': 'mds',
                                    'size': 1000,
                                    'mimetype': 'application/octet-stream',
                                    'name': 'test_file',
                                },
                                {
                                    'id': 'attachment_id_2',
                                    'link': 'test_link',
                                    'name': 'test_name',
                                },
                            ],
                        },
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'visible': False,
                'type': 'client_support',
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_application': 'iphone',
                'user_country': 'rus',
                'user_locale': 'lv',
                'support_name': 'Jūratė',
                'support_avatar_url': '0',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'platform': 'yandex',
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.dmitry',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc26152',
                        'role': 'client',
                    },
                    'metadata': {
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'aze',
                    'user_application': 'android',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'ru',
            http.HTTPStatus.CREATED,
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
                        'avatar_url': '5',
                        'nickname': 'Самир',
                    },
                    {
                        'id': '5b4f5092779fb332fcc26153',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'metadata': {
                    'created': '2018-07-18T11:40:00+0000',
                    'updated': '2018-07-18T11:40:00+0000',
                    'ask_csat': False,
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'ru',
                    'ticket_id': 123,
                    'author_id': 456,
                    'ticket_status': 'open',
                },
            },
            {
                'messages': [
                    {
                        'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc26152',
                        'message': 'test',
                        'message_type': 'text',
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id_1',
                                    'source': 'mds',
                                    'size': 1000,
                                    'name': 'test_file',
                                    'mimetype': 'application/octet-stream',
                                },
                            ],
                        },
                    },
                ],
                'ticket_processed': True,
                'open': True,
                'type': 'client_support',
                'visible': False,
                'user_id': 'test_user_id',
                'last_message_from_user': True,
                'user_application': 'android',
                'user_country': 'aze',
                'support_name': 'Самир',
                'support_avatar_url': '5',
                'owner_id': '5b4f5092779fb332fcc26153',
                'ask_csat': False,
                'retry_csat_request': False,
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'ticket_id': 123,
                'author_id': 456,
                'user_tz': 'Asia/Vladivostok',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'tanker_key': 'user_support_chat.support_name.samir',
                'ticket_status': 'open',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            {
                'request_id': '5b4f5059779fb332fcc29999',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f5059779fb332fcc29999',
                        'role': 'client',
                        'platform': 'yango_android',
                    },
                    'metadata': {
                        'order_id': 'some_order_id',
                        'attachments': [
                            {'id': 'attachment_id_0', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'link': 'test_link',
                                'name': 'test_name',
                            },
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'lv',
                },
                'owner': {
                    'id': '5b4f5059779fb332fcc29999',
                    'role': 'client',
                    'platform': 'yango_android',
                },
            },
            None,
            'lv',
            http.HTTPStatus.OK,
            {
                'metadata': {
                    'ask_csat': False,
                    'author_id': 456,
                    'chatterbox_id': 'anime',
                    'created': '2018-07-18T11:40:00+0000',
                    'csat_reasons': ['fast answer', 'thank you'],
                    'csat_value': 'good',
                    'last_message_from_user': True,
                    'new_messages': 2,
                    'ticket_id': 123,
                    'updated': '2018-07-18T11:40:00+0000',
                    'user_locale': 'lv',
                    'ticket_status': 'open',
                    'platform': 'yango',
                },
                'actions': [],
                'view': {'show_message_input': True},
                'newest_message_id': '5b4f5059779fb332fcc29999',
                'participants': [
                    {
                        'avatar_url': 4,
                        'id': 'support',
                        'nickname': 'Иван',
                        'role': 'support',
                    },
                    {
                        'id': '5b4f5059779fb332fcc29999',
                        'platform': 'yango',
                        'role': 'client',
                        'is_owner': True,
                    },
                ],
                'status': {'is_open': True, 'is_visible': True},
                'type': 'client_support',
            },
            {
                '_id': bson.ObjectId('539eb65be7e5b1f53980dfa8'),
                'ticket_processed': True,
                'ask_csat': False,
                'retry_csat_request': False,
                'author_id': 456,
                'chatterbox_id': 'anime',
                'csat_reasons': ['fast answer', 'thank you'],
                'csat_value': 'good',
                'incident_timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                'last_message_from_user': True,
                'messages': [
                    {
                        'author': 'user',
                        'author_id': 'some_user_id',
                        'id': '539eb65be7e5b1f53980dfa8_message_1',
                        'message': 'text_1',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'name': 'filename.txt',
                                },
                                {
                                    'link': 'test_url_2',
                                    'link_preview': 'link_preview',
                                    'mimetype': 'image/png',
                                    'preview_height': 200,
                                    'preview_width': 150,
                                    'size': 20000,
                                    'type': 'image',
                                },
                            ],
                        },
                        'timestamp': datetime.datetime(2018, 7, 1, 2, 3, 50),
                    },
                    {
                        'author': 'support',
                        'id': '539eb65be7e5b1f53980dfa8_message_2',
                        'message': 'text_2',
                        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
                    },
                    {
                        'author': 'user',
                        'author_id': '5b4f5059779fb332fcc29999',
                        'id': '5b4f5059779fb332fcc29999',
                        'message': 'test',
                        'message_type': 'text',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id_0',
                                    'mimetype': 'application/octet-stream',
                                    'name': 'test_file',
                                    'size': 1000,
                                    'source': 'mds',
                                },
                                {
                                    'id': 'attachment_id_2',
                                    'link': 'test_link',
                                    'name': 'test_name',
                                },
                            ],
                            'order_id': 'some_order_id',
                        },
                        'timestamp': datetime.datetime(2018, 7, 18, 11, 40),
                    },
                ],
                'new_messages': 2,
                'open': True,
                'owner_id': '5b4f5059779fb332fcc29999',
                'platform': 'yango',
                'support_avatar_url': 4,
                'support_name': 'Иван',
                'text_indexed': True,
                'ticket_id': 123,
                'type': 'client_support',
                'ticket_status': 'open',
                'updated': datetime.datetime(2018, 7, 18, 11, 40),
                'user_application': 'iphone',
                'user_country': 'rus',
                'user_id': 'test_user_id',
                'user_locale': 'lv',
                'user_phone_id': bson.ObjectId('5b4f5059779fb332fcc26159'),
                'user_tz': 'Asia/Vladivostok',
                'visible': True,
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
    ],
)
async def test_chatcreate_simple(
        web_app_client,
        web_context,
        mock_tvm_keys,
        stq,
        patch_support_scenarios_matcher,
        patch_support_scenarios_display,
        data,
        match_response,
        lang,
        status,
        expected_result,
        db_result,
        services_notifies,
):
    patch_support_scenarios_matcher(response=match_response)
    patch_support_scenarios_display()
    response = await web_app_client.post(
        '/v1/chat/', data=json.dumps(data), headers={'Accept-Language': lang},
    )
    assert response.status == status
    result = await response.json()
    chat_id = result.pop('id')
    assert result == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )

    db_result['_id'] = bson.ObjectId(chat_id)
    assert chat_doc == db_result
    _check_stq_call(stq, data, chat_id, chat_doc['type'], services_notifies)


@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    ['data', 'status'],
    [
        (
            {
                'request_id': '5a436ca8779fb3302cc784bf',
                'message': {
                    'text': 't' * 2001,
                    'sender': {'id': 'support', 'role': 'support'},
                    'metadata': {
                        'order_id': 'some_order_id',
                        'attachments': [
                            {'id': 'attachment_id_0', 'source': 'mds'},
                            {
                                'id': 'attachment_id_2',
                                'link': 'test_link',
                                'name': 'test_name',
                            },
                        ],
                    },
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'lv',
                },
                'owner': {
                    'id': '5a436ca8779fb3302cc784bf',
                    'role': 'facebook_user',
                },
            },
            http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        ),
        (
            {
                'request_id': '5a436ca8779fb3302cc784bf',
                'message': {
                    'text': 't' * 2001,
                    'sender': {'id': 'facebook_user', 'role': 'facebook_user'},
                    'metadata': {},
                },
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'author_id': 456,
                    'user_tz': 'Asia/Vladivostok',
                    'user_country': 'aze',
                    'user_application': 'android',
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            http.HTTPStatus.CREATED,
        ),
    ],
)
async def test_chatcreate_too_large(
        web_app_client,
        mock_tvm_keys,
        patch_support_scenarios_matcher,
        data,
        status,
):
    patch_support_scenarios_matcher()
    response = await web_app_client.post(
        '/v1/chat/', data=json.dumps(data), headers={'Accept-Language': 'lv'},
    )
    assert response.status == status


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'data',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'metadata': {
                    'csat_value': 'amazing',
                    'csat_reasons': ['good', 'ok'],
                },
                'message': {
                    'text': 'test_c',
                    'sender': {
                        'id': '5b4f5059779fb332fcc2615e',
                        'role': 'client',
                    },
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'metadata': {'ticket_status': 'solved'},
                'message': {
                    'text': 'test_c',
                    'sender': {
                        'id': '5b4f5059779fb332fcc2615e',
                        'role': 'client',
                    },
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            }
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'metadata': {'csat_reasons': ['good', 'ok']},
                'message': {
                    'text': 'test_c',
                    'sender': {
                        'id': '5b4f5059779fb332fcc2615e',
                        'role': 'client',
                    },
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
            }
        ),
    ],
)
async def test_ticket_bad_metadata(web_app_client, mock_tvm_keys, data):
    response = await web_app_client.post('/v1/chat/', data=json.dumps(data))
    assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.config(APPLICATION_MAP_EXPERIMENTS={'my_beauty_iphone': 'iphone'})
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'data, expected_result, chat_type',
    [
        (
            {
                'metadata': {
                    'user_country': '',
                    'user_application': 'test_app',
                    'user_locale': 'ru',
                },
            },
            {
                'name': 'Саппорт яндекс',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'ru',
                },
            },
            {
                'name': 'Андрей',
                'url': '0',
                'tanker_key': 'user_support_chat.support_name.dmitry',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'rus',
                    'user_application': 'android',
                    'user_locale': 'en',
                },
            },
            {
                'name': 'andrew',
                'url': '0',
                'tanker_key': 'user_support_chat.support_name.dmitry',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'civ',
                    'user_application': 'uber_iphone',
                    'user_locale': 'ky',
                },
            },
            {
                'name': 'ub sup',
                'url': '4',
                'tanker_key': 'user_support_chat.support_name.uber_support',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'civ',
                    'user_application': 'uber_iphone',
                    'user_locale': 'ru',
                },
            },
            {
                'name': 'Саппорт uber',
                'url': '4',
                'tanker_key': 'user_support_chat.support_name.uber_support',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': '',
                    'user_application': 'yango',
                    'user_locale': 'az',
                },
            },
            {
                'name': 'test',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.yandex_support',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'rus',
                    'user_application': 'iphone',
                    'user_locale': 'en',
                },
            },
            {
                'name': 'andrew',
                'url': '0',
                'tanker_key': 'user_support_chat.support_name.dmitry',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'rus',
                    'user_application': 'my_beauty_iphone',
                    'user_locale': 'en',
                },
            },
            {
                'name': 'andrew',
                'url': '0',
                'tanker_key': 'user_support_chat.support_name.dmitry',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'rus',
                    'user_application': 'my_beauty_iphone',
                    'user_locale': 'en',
                    'tags': ['tag_new'],
                },
            },
            {
                'name': 'andrew',
                'url': '0',
                'tanker_key': 'user_support_chat.support_name.dmitry',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'kaz',
                    'user_application': 'android',
                    'user_locale': 'en',
                    'tags': ['business_client'],
                },
            },
            {
                'name': 'dias',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.dias',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'kaz',
                    'user_application': 'android',
                    'user_locale': 'en',
                    'tags': ['test_tag', 'vip_tag'],
                },
            },
            {
                'name': 'alihan',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.alihan',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'kaz',
                    'user_application': 'android',
                    'user_locale': 'en',
                    'tags': ['test_tag'],
                },
            },
            {
                'name': 'alihan',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.alihan',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'kaz',
                    'user_application': 'android',
                    'user_locale': 'en',
                    'tags': ['new_tag'],
                },
            },
            {
                'name': 'miras',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.miras',
            },
            'client_support',
        ),
        (
            {
                'metadata': {
                    'user_country': 'kaz',
                    'user_application': 'android',
                    'user_locale': 'en',
                },
            },
            {
                'name': 'miras',
                'url': '5',
                'tanker_key': 'user_support_chat.support_name.miras',
            },
            'client_support',
        ),
    ],
)
@pytest.mark.config(USER_CHAT_SUPPORTS_BY_COUNTRY_PLATFORM=USER_CHAT_SUPPORTS)
async def test_get_support(web_context, data, expected_result, chat_type):
    result = support_chats.get_support(
        web_context, data.get('metadata', {}), chat_type,
    )
    assert result == expected_result


@pytest.mark.config(
    APPLICATION_MAP_EXPERIMENTS={'uber_az_android': 'uber_android'},
)
@pytest.mark.parametrize(
    'app_name,expected_name',
    [
        ('uber_az_android', 'uber_android'),
        ('uber', 'uber'),
        ('', ''),
        (None, ''),
    ],
)
def test_get_app_by_experiment(web_context, app_name, expected_name):
    result = support_chats._get_user_application_by_experiment(
        web_context.config, app_name,
    )
    assert result == expected_name


@pytest.mark.parametrize(
    'data, lang, expected_lang, support_name',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            'ru',
            'ru',
            'Саппорт яндекс',
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            'en',
            'en',
            'Yandex support',
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            None,
            'ru',
            'Саппорт яндекс',
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'metadata': {'user_locale': 'hy'},
                'owner': {'id': '5b4f5092779fb332fcc26153', 'role': 'client'},
            },
            'en',
            'hy',
            'Yandex support',
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_chat_create_translations(
        web_app_client, data, lang, expected_lang, support_name,
):
    headers = {}
    if lang:
        headers['Accept-Language'] = lang
    response = await web_app_client.post(
        '/v1/chat/', data=json.dumps(data), headers=headers,
    )
    assert response.status == http.HTTPStatus.CREATED
    chat = await response.json()

    assert chat['participants'][0]['nickname'] == support_name, chat
    assert chat['metadata']['user_locale'] == expected_lang


@pytest.mark.config(SUPPORT_CHAT_ADD_CHAT_METADATA_FIELD=True)
@pytest.mark.parametrize(
    'data, expected_chat_metadata, expected_root_meta_fields, status',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
            },
            {'unknown_field': 'unknown'},
            {'user_id': 'test_user_id', 'ask_csat': False, 'ticket_id': 123},
            201,
        ),
        (
            {
                'request_id': 'new_message',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
                'metadata': {
                    'user_id': 'test_user_id',
                    'ask_csat': False,
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
            },
            {'unknown_field': 'unknown', 'metadata_field_1': 'value_1'},
            {'user_id': 'test_user_id', 'ask_csat': False, 'ticket_id': 123},
            200,
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_chat_metadata(
        web_app_client,
        web_context,
        data,
        expected_chat_metadata,
        expected_root_meta_fields,
        status,
):
    response = await web_app_client.post('/v1/chat/', data=json.dumps(data))
    assert response.status == status
    chat_resp = await response.json()

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_resp['id'])},
    )

    assert chat_doc

    if expected_chat_metadata:
        assert chat_doc['metadata'] == expected_chat_metadata

    for field, value in expected_root_meta_fields.items():
        assert chat_doc[field] == value


@pytest.mark.parametrize(
    'data, status, expected_stq_put_calls',
    [
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                    'metadata': {'driver_on_order': True},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
                'metadata': {
                    'driver_uuid': 'some_driver_uuid',
                    'db': 'some_park_db_id',
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
            },
            201,
            [],
        ),
        (
            {
                'request_id': 'new_message',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                    'metadata': {'driver_on_order': True},
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
                'metadata': {
                    'driver_uuid': 'some_driver_uuid',
                    'db': 'some_park_db_id',
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
            },
            200,
            [],
        ),
        (
            {
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                    'metadata': {'driver_on_order': True},
                },
                'owner': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
                'metadata': {
                    'driver_uuid': 'some_driver_uuid',
                    'db': 'some_park_db_id',
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
                'create_chatterbox_task': True,
            },
            201,
            [
                {
                    'queue': 'support_chat_prepare_chatterbox_meta',
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'args': ['some_chat_id'],
                    'kwargs': {
                        'chat_request_data': {
                            'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                            'message': {
                                'text': 'test',
                                'sender': {'id': 'support', 'role': 'support'},
                                'metadata': {'driver_on_order': True},
                            },
                            'owner': {
                                'id': '5b4f17bb779fb332fcc26151',
                                'role': 'client',
                            },
                            'metadata': {
                                'driver_uuid': 'some_driver_uuid',
                                'db': 'some_park_db_id',
                                'ticket_id': 123,
                                'unknown_field': 'unknown',
                            },
                            'create_chatterbox_task': True,
                        },
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_chatterbox_update(
        web_app_client, stq, data, status, expected_stq_put_calls,
):
    response = await web_app_client.post('/v1/chat/', data=json.dumps(data))
    assert response.status == status
    chat_resp = await response.json()

    calls = []
    while not stq.is_empty:
        calls.append(stq.support_chat_prepare_chatterbox_meta.next_call())
    for call in calls:
        del call['kwargs']['log_extra']
        assert call['args'][0] == chat_resp['id']
        call['args'] = ['some_chat_id'] + call['args'][1:]
        assert call['id'] == chat_resp['id']
        del call['id']
    assert calls == expected_stq_put_calls


@pytest.mark.parametrize(
    'data, status, expected_stq_put_calls',
    [
        (
            {
                'request_id': 'new_message',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                    'metadata': {'driver_on_order': True},
                },
                'owner': {'id': '5b4f5059779fb332fcc26152', 'role': 'client'},
                'metadata': {
                    'driver_uuid': 'some_driver_uuid',
                    'db': 'some_park_db_id',
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
                'create_chatterbox_task': True,
            },
            200,
            [
                {
                    'args': ['some_chat_id', {}],
                    'kwargs': {},
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'queue': 'support_chat_create_chatterbox_task',
                },
            ],
        ),
    ],
)
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_chatterbox_create_task(
        web_app_client, stq, data, status, expected_stq_put_calls,
):
    response = await web_app_client.post('/v1/chat/', data=json.dumps(data))
    assert response.status == status
    chat_resp = await response.json()

    calls = []
    while not stq.is_empty:
        calls.append(stq.support_chat_create_chatterbox_task.next_call())
    for call in calls:
        del call['kwargs']['log_extra']
        assert call['args'][0] == chat_resp['id']
        call['args'] = ['some_chat_id'] + call['args'][1:]
        assert call['id'] == chat_resp['id']
        del call['id']
    assert calls == expected_stq_put_calls


@pytest.mark.now('2018-07-16T14:46:00')
@pytest.mark.translations(client_messages=TRANSLATIONS)
async def test_post_waiting_complete_dialog_csat(
        web_app_client, web_context, mock_tvm_keys,
):
    chat_id = '5e285103779fb3831c8b4bdd'
    response = await web_app_client.post(
        '/v1/chat',
        data=json.dumps(
            {
                'request_id': 'message_26',
                'message': {
                    'text': 'text_5',
                    'sender': {
                        'id': '5b4f5092779fb332fcc26152',
                        'platform': 'taximeter',
                        'role': 'driver',
                    },
                    'metadata': {
                        'driver_uuid': 'some_driver_uuid',
                        'source': 'chat',
                    },
                },
                'owner': {'id': '5b4f5092779fb332fcc26152', 'role': 'driver'},
                'metadata': {
                    'driver_uuid': 'some_driver_uuid',
                    'db': 'some_park_db_id',
                    'ticket_id': 123,
                    'unknown_field': 'unknown',
                },
            },
        ),
    )
    assert response.status == http.HTTPStatus.OK

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    assert chat_doc['messages'][-1] == {
        'id': 'message_26',
        'message': 'text_5',
        'timestamp': datetime.datetime(2018, 7, 16, 14, 46),
        'author': 'driver',
        'author_id': '5b4f5092779fb332fcc26152',
        'message_type': 'text',
        'metadata': {'driver_uuid': 'some_driver_uuid', 'source': 'chat'},
    }
    assert chat_doc['ticket_status'] == 'open'
    assert chat_doc['previous_csat_dialogs'] == [
        {
            'answers': [
                {
                    'actions': [
                        {
                            'answered': datetime.datetime(
                                2018, 7, 6, 13, 44, 50,
                            ),
                            'id': 'set_rating_amazing',
                            'text': 'Восхитительно',
                            'type': 'rating',
                        },
                    ],
                    'created': datetime.datetime(2018, 7, 6, 13, 44, 50),
                    'id': 'initial_answer_id',
                    'question': 'Оцените качество поддержки',
                    'state': 'waiting_qa_rating',
                },
                {
                    'actions': [
                        {
                            'answered': datetime.datetime(
                                2018, 7, 6, 13, 44, 50,
                            ),
                            'id': 'set_reason_thank_you',
                            'text': 'Спасибо',
                            'type': 'reason',
                        },
                    ],
                    'created': datetime.datetime(2018, 7, 6, 13, 44, 50),
                    'id': 'amazing_reason_answer_id',
                    'question': 'Почему так клёво?',
                    'state': 'waiting_qa_amazing_reason',
                },
            ],
            'last_action_id': 'set_reason_thank_you',
            'last_request_id': 'last_request_id',
            'new_messages_count': 0,
            'state': 'qa_amazing_waiting_finish',
        },
    ]
    assert chat_doc.get('csat_dialog') is None
