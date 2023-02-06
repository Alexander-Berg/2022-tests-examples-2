# pylint: disable=redefined-outer-name,no-member,expression-not-assigned
# pylint: disable=too-many-lines
import datetime
import http
import json

import bson
import pytest

from taxi_support_chat.internal import const


def _check_stq_call(stq, data, chat_id, chat_type, service_notifies=None):
    if chat_type == 'facebook_support':
        queue = 'taxi_sm_monitor_facebook'
        delay = 30
        kwargs = {}
    elif chat_type == 'sms_support':
        queue = 'taxi_support_chat_sms_notify'
        delay = 5
        kwargs = {}
    elif chat_type == 'eats_support':
        queue = 'taxi_support_chat_client_notify'
        delay = 30
        kwargs = {}
    elif chat_type == 'safety_center_support':
        queue = 'taxi_support_chat_client_notify'
        delay = 30
        kwargs = {}
    elif chat_type == 'opteum_support':
        queue = 'taxi_support_chat_opteum_notify'
        delay = 30
        kwargs = {'update_type': 'reply'}
    elif chat_type == 'lavka_storages_support':
        queue = 'taxi_support_chat_lavka_wms_notify'
        delay = 30
        kwargs = {'messages_count': 1}
    elif chat_type == 'market_support':
        queue = 'taxi_support_chat_market_notify'
        delay = 30
        kwargs = {}
    else:
        queue = 'driver_support_push'
        delay = 5
        kwargs = {}
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)

    if 'message' in data:
        if data['message']['sender']['role'] == 'support' and chat_type in [
                'facebook_support',
                'driver_support',
                'sms_support',
                'eats_support',
                'safety_center_support',
                'opteum_support',
                'lavka_storages_support',
                'market_support',
        ]:
            call_args = getattr(stq, queue).next_call()

            if chat_type == 'lavka_storages_support':
                assert call_args['kwargs'].pop('token')

            assert call_args == {
                'queue': queue,
                'eta': eta,
                'id': data['request_id'],
                'args': [{'$oid': chat_id}, data['request_id']],
                'kwargs': kwargs,
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
                        const.EVENT_NEW_MESSAGE,
                    ],
                    'kwargs': {},
                    'eta': datetime.datetime(2018, 7, 18, 11, 20, 5),
                }


async def test_invalid_id(web_app_client, mock_tvm_keys):
    response = await web_app_client.post(
        '/v1/chat/not_found_id/add_update/',
        data=json.dumps(
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '123',
                'message': {'sender': {'id': 'support', 'role': 'support'}},
            },
        ),
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


async def test_not_found(web_app_client, mock_tvm_keys):
    response = await web_app_client.post(
        '/v1/chat/5b436c16779fb3302cc784b9/add_update',
        data=json.dumps(
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '123',
                'message': {'sender': {'id': 'support', 'role': 'support'}},
            },
        ),
    )
    assert response.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'service_ticket,chat_id,expected_status',
    [
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.CREATED,
        ),
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.CREATED,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.CREATED,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_chat_type_access(
        web_app_client,
        mock_tvm_keys,
        service_ticket,
        chat_id,
        expected_status,
):
    response = await web_app_client.post(
        '/v1/chat/{}/add_update'.format(chat_id),
        data=json.dumps(
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '123',
                'message': {'sender': {'id': 'support', 'role': 'support'}},
            },
        ),
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_status


@pytest.mark.now('2018-07-18T11:20:00')
async def test_double_request(web_app_client, stq, mock_tvm_keys):
    data = {
        'created_date': '2018-07-16T13:44:25.979000',
        'request_id': '123',
        'message': {'sender': {'id': 'support', 'role': 'support'}},
    }
    response = await web_app_client.post(
        '/v1/chat/5b436ca8779fb3302cc784ba/add_update', data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED
    _check_stq_call(stq, data, '5b436ca8779fb3302cc784ba', 'client_support')

    response = await web_app_client.post(
        '/v1/chat/5b436ca8779fb3302cc784ba/add_update', data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED
    _check_stq_call(stq, data, '5b436ca8779fb3302cc784ba', 'client_support')


async def test_post_existing_message(
        web_app_client, web_context, mock_tvm_keys,
):
    response = await web_app_client.post(
        '/v1/chat/5b436ca8779fb3302cc784ba/add_update',
        data=json.dumps(
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'message_12',
                'message': {
                    'text': 'text_2',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'include_chat': True,
            },
        ),
    )
    assert response.status == http.HTTPStatus.CREATED
    assert await response.json() == {
        'message_id': 'message_12',
        'chat': {
            'actions': [],
            'view': {'show_message_input': True},
            'id': '5b436ca8779fb3302cc784ba',
            'metadata': {
                'ask_csat': False,
                'chatterbox_id': 'chatterbox_id',
                'created': '2018-07-10T10:09:50+0000',
                'csat_reasons': ['fast answer', 'thank you'],
                'csat_value': 'good',
                'last_message_from_user': False,
                'new_messages': 2,
                'updated': '2018-07-11T12:15:50+0000',
                'user_locale': 'ru',
                'metadata_field_1': 'value_1',
            },
            'newest_message_id': 'message_12',
            'participants': [
                {
                    'avatar_url': 4,
                    'id': 'support',
                    'nickname': 'Иван',
                    'role': 'support',
                },
                {
                    'id': '5b4f5059779fb332fcc26152',
                    'role': 'client',
                    'is_owner': True,
                },
            ],
            'status': {'is_open': True, 'is_visible': True},
            'type': 'client_support',
            'messages': [
                {
                    'id': 'message_11',
                    'metadata': {
                        'attachments': [
                            {'id': 'attachment_id', 'name': 'filename.txt'},
                            {
                                'id': 'message_11_1',
                                'link': 'test_url_2',
                                'link_preview': 'link_preview',
                                'mimetype': 'image/png',
                                'name': 'file_1',
                                'preview_height': 200,
                                'preview_width': 150,
                                'size': 20000,
                            },
                        ],
                        'created': '2018-07-01T02:03:50+0000',
                    },
                    'sender': {
                        'id': 'some_user_id',
                        'role': 'client',
                        'sender_type': 'client',
                    },
                    'text': 'text_1',
                },
                {
                    'id': 'message_12',
                    'metadata': {'created': '2018-07-04T05:06:50+0000'},
                    'sender': {
                        'id': 'support',
                        'role': 'support',
                        'sender_type': 'support',
                    },
                    'text': 'text_2',
                },
            ],
        },
    }

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId('5b436ca8779fb3302cc784ba')},
    )
    assert chat_doc['messages'][-1] == {
        'id': 'message_12',
        'message': 'text_2',
        'timestamp': datetime.datetime(2018, 7, 4, 5, 6, 50),
        'author': 'support',
    }


async def test_post_closed_chat(web_app_client, web_context, mock_tvm_keys):
    response = await web_app_client.post(
        '/v1/chat/5b436ece779fb3302cc784bb/add_update',
        data=json.dumps(
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'message_25',
                'message': {
                    'text': 'text_5',
                    'sender': {'id': 'client', 'role': 'client'},
                },
            },
        ),
    )
    assert response.status == http.HTTPStatus.CREATED
    assert await response.json() == {'message_id': 'message_25'}

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId('5b436ece779fb3302cc784bb')},
    )
    assert chat_doc['messages'][-1] == {
        'id': 'message_25',
        'message': 'text_5',
        'timestamp': datetime.datetime(2018, 7, 19, 20, 21, 50),
        'author': 'user',
    }


async def test_reply_to_message(web_app_client, web_context, mock_tvm_keys):
    chat_id = '5b436ca8779fb3302cc784ba'
    await web_app_client.post(
        '/v1/chat/{}/add_update'.format(chat_id),
        data=json.dumps(
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'message_10000',
                'message': {
                    'text': 'text_5',
                    'metadata': {
                        'reply_to': ['message_11', 'non_existing_id'],
                    },
                    'sender': {'id': 'client', 'role': 'client'},
                },
            },
        ),
    )

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    assert chat_doc['messages'][-1]['metadata']['reply_to'] == [
        'message_11',
        'non_existing_id',
    ]


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.config(
    SUPPORT_CHAT_ALLOWED_CHAT_TYPES_FOR_SCENARIOS=['client_support'],
    SUPPORT_CHAT_SERVICE_NOTIFY=True,
    SUPPORT_CHAT_SERVICE_NOTIFY_FILTERS={
        'support_gateway': {
            'type': [
                'client_support',
                'eats_support',
                'market_support',
                'safety_center_support',
            ],
        },
    },
)
@pytest.mark.parametrize(
    [
        'chat_id',
        'data',
        'match_response',
        'expected_result',
        'expected_db_message',
        'service_notifies',
    ],
    [
        (
            '5b436ca8889fb3302cc784ba',
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': '2a183a0d13a94593b91577c8703949f1',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
            },
            None,
            {'message_id': '2a183a0d13a94593b91577c8703949f1'},
            {
                'id': '2a183a0d13a94593b91577c8703949f1',
                'message': 'test',
                'message_type': 'text',
                'timestamp': datetime.datetime(
                    2018, 7, 16, 14, 46, 21, 333000,
                ),
                'author': 'support',
                'author_id': 'support',
            },
            None,
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
            },
            None,
            {'message_id': 'c5400585d9fa40b28e1c88a6c5a27c81'},
            {
                'id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': 'test',
                'message_type': 'text',
                'timestamp': datetime.datetime(
                    2018, 7, 16, 14, 46, 21, 333000,
                ),
                'author': 'support',
                'author_id': 'support',
            },
            None,
        ),
        (
            '5b436ece779fb3302cc784bc',
            {
                'created_date': '2018-06-16T14:06:21.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'client',
                    },
                },
                'update_metadata': {'test_field': 'test_value'},
            },
            {
                'id': 'action_1',
                'text': 'сдох',
                'show_message_input': False,
                'actions': [
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
            {'message_id': 'c5400585d9fa40b28e1c88a6c5a27c82'},
            {
                'id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': 'test',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 21, 333000),
                'author': 'user',
                'author_id': '5b4f17bb779fb332fcc26151',
            },
            None,
        ),
        (
            '5b436ece779fb3302cc784bc',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': {
                    'sender': {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'c5400585d9fa40b28e1c88a6c5a27c83'},
            {
                'id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': '',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': '5b4f17bb779fb332fcc26151',
            },
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': {
                    'sender': {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'c5400585d9fa40b28e1c88a6c5a27c83'},
            {
                'id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': '',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': '5b4f17bb779fb332fcc26151',
            },
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': {
                    'text': 'test_driver',
                    'sender': {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'driver',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'c5400585d9fa40b28e1c88a6c5a27c83'},
            {
                'id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': 'test_driver',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'driver',
                'author_id': '5bbf8048779fb35d847fdb1e',
            },
            None,
        ),
        (
            '5a436ca8779fb3302cc784bf',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': {
                    'text': 'test_support',
                    'sender': {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'c5400585d9fa40b28e1c88a6c5a27c83'},
            {
                'id': 'c5400585d9fa40b28e1c88a6c5a27c83',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': '5bbf8048779fb35d847fdb1e',
            },
            None,
        ),
        (
            '5a433ca8779fb3302cc784bf',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_sms',
                'message': {
                    'text': 'test_support',
                    'sender': {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_sms'},
            {
                'id': 'test_sms',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': '5bbf8048779fb35d847fdb1e',
            },
            None,
        ),
        (
            '5a436ca8779fb3302cc784ea',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_eats_support_response',
                'message': {
                    'text': 'test_support',
                    'sender': {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_eats_support_response'},
            {
                'id': 'test_eats_support_response',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': '5bbf8048779fb35d847fdb1e',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            '5a436ca8779fb3302cc784c8',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_eats_app_support_response',
                'message': {
                    'text': 'test_support',
                    'sender': {'id': 'eats_user_id_1', 'role': 'support'},
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_eats_app_support_response'},
            {
                'id': 'test_eats_app_support_response',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'eats_user_id_1',
            },
            None,
        ),
        (
            '5b56f0be8d64e6667db1440e',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_emergency_id',
                'message': {
                    'text': 'i am a support',
                    'sender': {
                        'id': '5bbf8048779fb35d847fdb1e',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_emergency_id'},
            {
                'id': 'test_emergency_id',
                'message': 'i am a support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': '5bbf8048779fb35d847fdb1e',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            '5e285103779fb3831c8b4ad2',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_opteum_id',
                'message': {
                    'text': 'i am a support',
                    'sender': {'id': 'support', 'role': 'support'},
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_opteum_id'},
            {
                'id': 'test_opteum_id',
                'message': 'i am a support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'support',
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4ad3',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_carsharing_support_response',
                'message': {
                    'text': 'test_support',
                    'sender': {
                        'id': 'carsharing_user_id_1',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_carsharing_support_response'},
            {
                'id': 'test_carsharing_support_response',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'carsharing_user_id_1',
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4ad4',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_scouts_support_response',
                'message': {
                    'text': 'test_support',
                    'sender': {'id': 'scouts_user_id_1', 'role': 'support'},
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_scouts_support_response'},
            {
                'id': 'test_scouts_support_response',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'scouts_user_id_1',
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4ad5',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_lavka_storages_support_response',
                'message': {
                    'text': 'test_support',
                    'sender': {
                        'id': 'lavka_storages_user_id_1',
                        'role': 'support',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_lavka_storages_support_response'},
            {
                'id': 'test_lavka_storages_support_response',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'lavka_storages_user_id_1',
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4a33',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_website_support_response',
                'message': {
                    'text': 'test_website',
                    'sender': {'id': 'website_user_id_1', 'role': 'support'},
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_website_support_response'},
            {
                'id': 'test_website_support_response',
                'message': 'test_website',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'website_user_id_1',
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4a34',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_restapp_support_response',
                'message': {
                    'text': 'test_restapp',
                    'sender': {'id': 'restapp_user_id_1', 'role': 'support'},
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_restapp_support_response'},
            {
                'id': 'test_restapp_support_response',
                'message': 'test_restapp',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'restapp_user_id_1',
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4ad6',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_market_support_response',
                'message': {
                    'text': 'test_support',
                    'sender': {'id': 'market_user_id_1', 'role': 'support'},
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_market_support_response'},
            {
                'id': 'test_market_support_response',
                'message': 'test_support',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'market_user_id_1',
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        (
            '5e285103779fb3831c8b4ad6',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_attach_support_response',
                'message': {
                    'text': 'test_attach',
                    'sender': {'id': 'support_user_id_1', 'role': 'support'},
                    'metadata': {
                        'attachments': [
                            {'id': 'attachment_id', 'source': 'mds'},
                        ],
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_attach_support_response'},
            {
                'id': 'test_attach_support_response',
                'message': 'test_attach',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'support_user_id_1',
                'metadata': {
                    'attachments': [
                        {
                            'id': 'attachment_id',
                            'source': 'mds',
                            'size': 1000,
                            'mimetype': 'application/octet-stream',
                            'name': 'test_file',
                        },
                    ],
                },
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
        pytest.param(
            '5e285103779fb3831c8b4ad6',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_attach_support_response',
                'message': {
                    'text': 'test_attach',
                    'sender': {'id': 'support_user_id_1', 'role': 'support'},
                    'metadata': {
                        'attachments': [
                            {'id': 'attachment_id', 'source': 'mds'},
                        ],
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_attach_support_response'},
            {
                'id': 'test_attach_support_response',
                'message': 'test_attach',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'support',
                'author_id': 'support_user_id_1',
                'metadata': {
                    'attachments': [{'id': 'attachment_id', 'source': 'mds'}],
                },
            },
            None,
            marks=[
                pytest.mark.config(
                    SUPPORT_CHAT_FORBIDDEN_EXTERNAL_REQUESTS={
                        'market_support': {
                            '__default__': False,
                            'check_attachments': True,
                            'support_gateway': True,
                        },
                    },
                ),
            ],
        ),
        (
            '5e285103779fb3831c8b4ad6',
            {
                'created_date': '2018-06-16T14:06:25.333000',
                'request_id': 'test_attach_user_response',
                'message': {
                    'text': 'test_attach_2',
                    'sender': {'id': 'user_id_1', 'role': 'client'},
                    'metadata': {
                        'attachments': [
                            {'id': 'attachment_id', 'source': 'mds'},
                        ],
                        'source': 'support_gateway',
                    },
                },
                'update_metadata': {},
            },
            None,
            {'message_id': 'test_attach_user_response'},
            {
                'id': 'test_attach_user_response',
                'message': 'test_attach_2',
                'message_type': 'text',
                'timestamp': datetime.datetime(2018, 6, 16, 14, 6, 25, 333000),
                'author': 'user',
                'author_id': 'user_id_1',
                'metadata': {
                    'attachments': [
                        {
                            'id': 'attachment_id',
                            'source': 'mds',
                            'size': 1000,
                            'mimetype': 'application/octet-stream',
                            'name': 'test_file',
                        },
                    ],
                    'source': 'support_gateway',
                },
            },
            ['taxi_support_chat_support_gateway_notify'],
        ),
    ],
)
async def test_add_update(
        web_app_client,
        stq,
        mock_tvm_keys,
        web_context,
        patch_support_scenarios_matcher,
        patch_support_scenarios_display,
        chat_id,
        data,
        match_response,
        expected_result,
        expected_db_message,
        service_notifies,
):
    patch_support_scenarios_matcher(response=match_response)
    patch_support_scenarios_display()
    old_chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    response = await web_app_client.post(
        '/v1/chat/%s/add_update' % chat_id, data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED
    assert await response.json() == expected_result

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    assert chat_doc['messages'][-1] == expected_db_message

    if data['message']['sender']['role'] != const.SUPPORT_ROLE:
        assert chat_doc['last_message_from_user']
        assert not chat_doc['ask_csat']
        assert not chat_doc['retry_csat_request']
        assert chat_doc['open']
        assert chat_doc['ticket_status'] == 'open'
    if data['message']['sender']['role'] == const.SUPPORT_ROLE:
        assert (
            old_chat_doc.get('new_messages', 0) + 1 == chat_doc['new_messages']
        )
        push_need = (
            'driver_support',
            'facebook_support',
            'sms_support',
            'eats_support',
            'eats_app_support',
            'safety_center_support',
            'opteum_support',
            'lavka_storages_support',
            'restapp_support',
            'market_support',
            'whatsapp_support',
        )
        if chat_doc['type'] in push_need:
            assert chat_doc['send_push'] is False
        else:
            assert chat_doc['send_push']
        assert (
            chat_doc['support_timestamp'] == expected_db_message['timestamp']
        )
        assert chat_doc['visible']
        assert not chat_doc['last_message_from_user']
    if data.get('update_metadata'):
        for key, value in data['update_metadata'].items():
            assert chat_doc[key] == value
    _check_stq_call(stq, data, chat_id, chat_doc['type'], service_notifies)


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.parametrize(
    ['chat_id', 'data', 'expected'],
    [
        (
            '5a433ca8779fb3302cc784bf',
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'a' * 671,
                    'sender': {'id': 'support', 'role': 'support'},
                },
            },
            {
                'error': 'Message length limit exceeded',
                'limit': 670,
                'reason': '671 > 670',
            },
        ),
        (
            '5a433ca8779fb3302cc784bf',
            {
                'created_date': '2018-06-16T14:06:21.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'a' * 671,
                    'sender': {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'client',
                    },
                },
                'update_metadata': {'test_field': 'test_value'},
            },
            {},
        ),
    ],
)
async def test_add_update_too_large(
        web_app_client, mock_tvm_keys, web_context, chat_id, data, expected,
):
    response = await web_app_client.post(
        '/v1/chat/%s/add_update' % chat_id, data=json.dumps(data),
    )
    if data['message']['sender']['role'] != 'support':
        assert response.status == http.HTTPStatus.CREATED
        return
    assert response.status == http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    assert expected == await response.json()


@pytest.mark.parametrize(
    'chat_id,data',
    [
        (
            '5b436ece779fb3302cc784bd',
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c81',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
            },
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'message_21',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
            },
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T14:46:21.333000',
                'request_id': 'message_21',
                'message': {
                    'text': 'test',
                    'sender': {'id': 'support', 'role': 'support'},
                },
            },
        ),
        (
            '5b436ece779fb3302cc784bb',
            {
                'created_date': '2018-06-16T14:06:21.333000',
                'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
                'message': {
                    'text': 'test',
                    'sender': {
                        'id': '5b4f17bb779fb332fcc26151',
                        'role': 'client',
                    },
                },
                'update_metadata': {},
            },
        ),
    ],
)
async def test_add_update_conflict(
        web_app_client, mock_tvm_keys, chat_id, data,
):
    response = await web_app_client.post(
        '/v1/chat/%s/add_update' % chat_id, data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    'chat_id,data,status,csat_value,csat_reasons',
    [
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {
                    'csat_value': 'good',
                    'csat_reasons': ['thank_you', 'helped_me'],
                },
            },
            http.HTTPStatus.CREATED,
            'good',
            ['thank_you', 'helped_me'],
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'csat_value': 'amazing'},
            },
            http.HTTPStatus.CREATED,
            'amazing',
            [],
        ),
        (
            '5b436ca8779fb3302cc7844f',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'csat_value': 'good'},
            },
            http.HTTPStatus.CREATED,
            'good',
            [],
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'csat_value': 'good'},
            },
            http.HTTPStatus.UNPROCESSABLE_ENTITY,
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc7844f',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {
                    'csat_values': {
                        'questions': [
                            {
                                'id': 'question_id_1',
                                'value': {
                                    'id': 'answer_id',
                                    'comment': 'user comment',
                                    'reasons': [
                                        {'id': 'reason_id_1'},
                                        {
                                            'id': 'reason_id_2',
                                            'reasons': [
                                                {'id': 'sub_reason_id'},
                                            ],
                                        },
                                    ],
                                },
                            },
                            {
                                'id': 'question_id_1',
                                'value': {'id': 'answer_id'},
                            },
                        ],
                    },
                },
            },
            http.HTTPStatus.CREATED,
            'answer_id',
            ['reason_id_1', 'reason_id_2'],
        ),
        (
            '5b436ca8779fb3302cc7844f',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {
                    'csat_values': {
                        'questions': [
                            {
                                'id': 'question_id',
                                'value': {'id': 'answer_id'},
                            },
                        ],
                    },
                },
            },
            http.HTTPStatus.CREATED,
            'answer_id',
            [],
        ),
        (
            '5b436ca8779fb3302cc7844f',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'csat_value': 'good', 'csat_values': {}},
            },
            http.HTTPStatus.CREATED,
            'good',
            [],
        ),
        (
            '5b436ca8779fb3302cc7844f',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {
                    'csat_value': 'good',
                    'csat_values': {'tmp': []},
                },
            },
            http.HTTPStatus.UNPROCESSABLE_ENTITY,
            None,
            None,
        ),
    ],
)
async def test_csat(
        web_app_client,
        mock_tvm_keys,
        web_context,
        chat_id,
        data,
        status,
        csat_value,
        csat_reasons,
):
    response = await web_app_client.post(
        '/v1/chat/%s/add_update' % chat_id, data=json.dumps(data),
    )
    assert response.status == status
    if status > 400:
        return
    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    assert chat_doc['csat_value'] == csat_value
    assert chat_doc['csat_reasons'] == csat_reasons

    if data['update_metadata'].get('csat_values'):
        assert (
            chat_doc['csat_values'] == data['update_metadata']['csat_values']
        )
    assert not chat_doc['ask_csat']
    assert not chat_doc['open']
    assert not chat_doc['visible']
    assert chat_doc['close_ticket']


@pytest.mark.parametrize(
    'chat_id,data,date',
    [
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'ticket_status': 'solved'},
            },
            datetime.datetime(2018, 7, 16, 13, 44, 25, 979000),
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'test_field': 'test_value'},
            },
            datetime.datetime.utcnow(),
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'ticket_status': 'open'},
            },
            datetime.datetime(2018, 7, 16, 13, 44, 25, 979000),
        ),
    ],
)
async def test_ticket_solved(
        web_app_client, mock_tvm_keys, web_context, chat_id, data, date,
):
    response = await web_app_client.post(
        '/v1/chat/%s/add_update' % chat_id, data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED
    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    ticket_status = data.get('update_metadata', {}).get('ticket_status')
    if ticket_status == 'solved':
        assert not chat_doc['last_message_from_user']
        assert chat_doc['support_timestamp'] == date


@pytest.mark.parametrize(
    'data, text_indexed',
    [
        (
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'chatterbox_id': '123'},
            },
            True,
        ),
        (
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'ticket_id': '123'},
            },
            False,
        ),
    ],
)
async def test_text_indexed(
        web_app_client, mock_tvm_keys, web_context, data, text_indexed,
):
    chat_id = '5b436ece779fb3302cc784bc'
    response = await web_app_client.post(
        '/v1/chat/{}/add_update'.format(chat_id), data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED
    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    assert chat_doc['text_indexed'] == text_indexed


@pytest.mark.parametrize(
    'chat_id,data,open_chat,visible_chat',
    [
        (
            '5b436ca8779fb3302cc784ba',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'ticket_id': '123'},
            },
            True,
            True,
        ),
        (
            '5c791c34779fb31eb470a580',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {
                    'ticket_id': '1234',
                    'ticket_status': 'open',
                },
            },
            False,
            False,
        ),
        (
            '5c791c34779fb31eb470a580',
            {
                'created_date': '2018-07-16T13:44:25.979000',
                'request_id': '1234',
                'update_metadata': {'test_field': '1234'},
            },
            True,
            True,
        ),
    ],
)
async def test_sms_close(
        web_app_client,
        mock_tvm_keys,
        web_context,
        chat_id,
        data,
        open_chat,
        visible_chat,
):
    for _ in range(2):
        response = await web_app_client.post(
            '/v1/chat/%s/add_update' % chat_id, data=json.dumps(data),
        )
        assert response.status == http.HTTPStatus.CREATED
        chat_doc = await web_context.mongo.user_chat_messages.find_one(
            {'_id': bson.ObjectId(chat_id)},
        )
        assert chat_doc['open'] == open_chat
        assert chat_doc['visible'] == visible_chat


@pytest.mark.config(SUPPORT_CHAT_ADD_CHAT_METADATA_FIELD=True)
@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.parametrize(
    'chat_id, update_metadata, expected_chat_metadata, '
    'expected_root_meta_fields',
    [
        (
            '5b436ece779fb3302cc784bc',
            {
                'unknown_field': 'test_value',
                'user_application': '10.1',
                'owner_phone': '+7999',
                'new_field': 5,
            },
            {'unknown_field': 'test_value', 'new_field': 5},
            {'user_application': '10.1', 'owner_phone': '+7999'},
        ),
        (
            '5b436ece779fb3302cc784bd',
            {
                'unknown_field': 'test_value',
                'user_application': '10.1',
                'owner_phone': '+7999',
                'new_field': 5,
            },
            {
                'unknown_field': 'test_value',
                'new_field': 5,
                'old_metadata_field': 'old',
            },
            {'user_application': '10.1', 'owner_phone': '+7999'},
        ),
    ],
)
async def test_update_meta(
        web_app_client,
        mock_tvm_keys,
        web_context,
        chat_id,
        update_metadata,
        expected_chat_metadata,
        expected_root_meta_fields,
):
    data = dict(
        {
            'created_date': '2018-06-16T14:06:21.333000',
            'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
            'message': {
                'text': 'test',
                'sender': {'id': '5b4f17bb779fb332fcc26151', 'role': 'client'},
            },
            'update_metadata': update_metadata,
        },
    )
    response = await web_app_client.post(
        '/v1/chat/{}/add_update'.format(chat_id), data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )

    if expected_chat_metadata:
        assert chat_doc['metadata'] == expected_chat_metadata

    for field, value in expected_root_meta_fields.items():
        assert chat_doc[field] == value


async def test_ticket_reopen(web_app_client, mock_tvm_keys, web_context):
    chat_id = '5b436ece779fb3302cc784bd'
    data = {
        'created_date': '2018-06-16T14:06:21.333000',
        'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
        'chat_id': chat_id,
        'update_metadata': {'ticket_status': 'open'},
    }
    response = await web_app_client.post(
        f'/v1/chat/{chat_id}/add_update', data=json.dumps(data),
    )
    assert response.status == http.HTTPStatus.CREATED

    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
    )
    assert chat_doc['open']
    assert chat_doc['visible']
    assert not chat_doc['ask_csat']


async def test_csat_after_reopen(web_app_client, mock_tvm_keys, web_context):
    chat_id = '5b436ece779fb3302cc784bd'
    reopen = {
        'created_date': '2018-06-16T14:06:21.333000',
        'request_id': 'c5400585d9fa40b28e1c88a6c5a27c82',
        'chat_id': chat_id,
        'update_metadata': {'ticket_status': 'open'},
    }
    response = await web_app_client.post(
        f'/v1/chat/{chat_id}/add_update', data=json.dumps(reopen),
    )
    assert response.status == http.HTTPStatus.CREATED

    csat = {
        'created_date': '2018-06-16T14:06:22.333000',
        'request_id': 'c5400585d9fa40b28e1c88a6c5a27c83',
        'chat_id': chat_id,
        'update_metadata': {'csat_value': 'good'},
    }
    response = await web_app_client.post(
        f'/v1/chat/{chat_id}/add_update', data=json.dumps(csat),
    )
    assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY
