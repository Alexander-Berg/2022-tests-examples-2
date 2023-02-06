# pylint: disable=no-member
import json

import bson
import pytest

from taxi_support_chat.internal import const


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
        'eats_app': 'eats_app',
    },
    SUPPORT_CHAT_SERVICE_NOTIFY=True,
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    (
        'chat_id',
        'owner',
        'service_ticket',
        'expected_code',
        'expected_db_result',
        'expected_notify',
        'service_notifies',
    ),
    [
        (
            '5b436ca8779fb3302cc784ba',
            {'role': 'client', 'id': '5b4f5059779fb332fcc26152'},
            'backend_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {'role': 'client', 'id': '5b4f5059779fb332fcc26152'},
            'disp_service_ticket',
            403,
            {'new_messages': 2},
            None,
            False,
        ),
        (
            '5b436ca8779fb3302cc784ba',
            {'role': 'client', 'id': '5b4f5059779fb332fcc26152'},
            'corp_service_ticket',
            403,
            {'new_messages': 2},
            None,
            False,
        ),
        (
            '539eb65be7e5b1f53980dfa8',
            {
                'role': 'client',
                'id': '5b4f5059779fb332fcc29999',
                'platform': 'android',
            },
            'backend_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            [
                {
                    'queue': 'taxi_support_chat_support_gateway_notify',
                    'args': [
                        {'$oid': '539eb65be7e5b1f53980dfa8'},
                        None,
                        const.EVENT_READ_MESSAGE,
                    ],
                },
            ],
        ),
        (
            '539eb65be7e5b1f53980dfa8',
            {
                'role': 'client',
                'id': '5b4f5059779fb332fcc29999',
                'platform': 'yango_android',
            },
            'backend_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            [
                {
                    'queue': 'taxi_support_chat_support_gateway_notify',
                    'args': [
                        {'$oid': '539eb65be7e5b1f53980dfa8'},
                        None,
                        const.EVENT_READ_MESSAGE,
                    ],
                },
            ],
        ),
        (
            '539eb65be7e5b1f53980dfa8',
            {
                'role': 'client',
                'id': '5b4f5059779fb332fcc29999',
                'platform': 'uber',
            },
            'backend_service_ticket',
            404,
            {'new_messages': 2},
            None,
            False,
        ),
        (
            '539eb65be7e5b1f53980dfa8',
            {'role': 'client', 'id': '5b4f5059779fb332fcc29999'},
            'backend_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            [
                {
                    'queue': 'taxi_support_chat_support_gateway_notify',
                    'args': [
                        {'$oid': '539eb65be7e5b1f53980dfa8'},
                        None,
                        const.EVENT_READ_MESSAGE,
                    ],
                },
            ],
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {'role': 'driver', 'id': '5bbf8048779fb35d847fdb1e'},
            'backend_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {'role': 'driver', 'id': '5bbf8048779fb35d847fdb1e'},
            'disp_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {
                'role': 'driver',
                'id': '5bbf8048779fb35d847fdb1e',
                'platform': 'taximeter',
            },
            'disp_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            None,
        ),
        (
            '5df208a0779fb3085850a6d0',
            {
                'role': 'driver',
                'id': '5b4f5092779fb332fcc26154',
                'platform': 'uberdriver',
            },
            'disp_service_ticket',
            200,
            {'send_push': False, 'new_messages': 0},
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {'role': 'driver', 'id': '5bbf8048779fb35d847fdb1e'},
            'corp_service_ticket',
            403,
            {'new_messages': 2},
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            {'role': 'client', 'id': '5bbf8048779fb35d847fdb1e'},
            'backend_service_ticket',
            404,
            {'new_messages': 2},
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784b0',
            {'role': 'client', 'id': '5bbf8048779fb35d847fdb1e'},
            'backend_service_ticket',
            404,
            None,
            None,
            None,
        ),
        (
            '5b436ca8779fb3302cc784b0',
            {'role': 'client', 'id': 'invalid object id'},
            'backend_service_ticket',
            404,
            None,
            None,
            None,
        ),
        (
            '5a436ca8779fb3302cc784c8',
            {'role': 'eats_app_client', 'id': 'eats_user_id_1'},
            'backend_service_ticket',
            200,
            {'new_messages': 0, 'send_push': False},
            {
                'queue': 'taxi_support_chat_eats_app_notify',
                'args': [{'$oid': '5a436ca8779fb3302cc784c8'}],
                'kwargs': {'log_extra': None, 'zero_messages': True},
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4ad5',
            {'role': 'lavka_storages_client', 'id': 'lavka_store_id'},
            'backend_service_ticket',
            200,
            {'new_messages': 0, 'send_push': False},
            {
                'queue': 'taxi_support_chat_lavka_wms_notify',
                'args': [{'$oid': '5e285103779fb3831c8b4ad5'}],
                'kwargs': {'messages_count': -2, 'log_extra': None},
                'token': True,
            },
            None,
        ),
        (
            '5e285103779fb3831c8b4ad7',
            {'role': 'market_client', 'id': 'market_yuid'},
            'backend_service_ticket',
            200,
            {'new_messages': 0, 'send_push': False},
            None,
            None,
        ),
        (
            '5e285103779fb3831c8b4bda',
            {'role': 'driver', 'id': '5b4f5092779fb332fcc26154'},
            'backend_service_ticket',
            200,
            {
                'csat_dialog': {'new_messages_count': 0},
                'send_push': False,
                'new_messages': 0,
            },
            None,
            None,
        ),
    ],
)
async def test_read(
        web_app_client,
        mock_tvm_keys,
        web_context,
        stq,
        chat_id,
        owner,
        service_ticket,
        expected_code,
        expected_db_result,
        expected_notify,
        service_notifies,
):
    response = await web_app_client.post(
        '/v1/chat/{}/read'.format(chat_id),
        data=json.dumps({'owner': owner}),
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_code
    chat_doc = await web_context.mongo.user_chat_messages.find_one(
        {'_id': bson.ObjectId(chat_id)},
        {
            '_id': False,
            'send_push': True,
            'new_messages': True,
            'csat_dialog.new_messages_count': True,
        },
    )
    if expected_notify:
        call = getattr(stq, expected_notify['queue']).next_call()
        assert call['queue'] == expected_notify['queue']
        assert call['args'] == expected_notify['args']
        if expected_notify.get('token'):
            assert call['kwargs'].pop('token')
        assert call['kwargs'] == expected_notify['kwargs']

    if service_notifies:
        stq_calls = []
        for notify in service_notifies:
            stq_call = getattr(stq, notify['queue']).next_call()
            stq_calls.append(stq_call)
        assert stq.is_empty
        for call, notify in zip(stq_calls, service_notifies):
            assert call['queue'] == notify['queue']
            assert call['args'] == notify['args']

    assert stq.is_empty
    assert chat_doc == expected_db_result
