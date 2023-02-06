# pylint: disable=W0212
import pytest

from taxi import discovery

from taxi_support_chat.stq import stq_task


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.config(
    SUPPORT_CHAT_LOGBROKER_TELEPHONY_SETTINGS={
        'consumer': 'test_consumer',
        'consumer_topic': 'test_consumer_topic',
        'enabled': False,
        'max_tries': {'create_consumer': 5},
        'producer_topic': 'test_producer_topic',
        'timeouts': {
            'create_consumer': 60,
            'forward_call': 5,
            'get_message': 3600,
        },
        'workers_count': 3,
    },
    SUPPORT_CHAT_SETTINGS_LOGBROKER={
        'telephony': {
            'consumer': 'test_consumer',
            'consumer_topic': 'test_consumer_topic',
            'enabled': False,
            'max_tries': {'create_consumer': 5},
            'producer_topic': 'test_producer_topic',
            'timeouts': {
                'create_consumer': 60,
                'forward_call': 5,
                'get_message': 3600,
            },
            'workers_count': 3,
            'channels': ['TELEPHONY'],
        },
    },
)
@pytest.mark.parametrize(
    (
        'call',
        'message_id',
        'expected_chat',
        'expected_create_chatterbox_task',
        'expected_hangup_process',
        'expected_connected',
        'expected_csat',
    ),
    [
        (
            {
                'args': [
                    {
                        'id': 'msg-id-0001',
                        'service': {'status': 'SUCCESS', 'type': 'FORWARD'},
                    },
                ],
                'kwargs': {},
            },
            None,
            False,
            None,
            None,
            False,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': '88001000200',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'userId': 'phone:+79001234567',
                            'userName': 'Aleksandr',
                        },
                        'id': 'msg-id-0001',
                        'service': {'type': 'INCOMING'},
                        'timestamp': '2021-12-30T12:23:59+03:00',
                    },
                ],
                'kwargs': {},
            },
            None,
            False,
            None,
            None,
            False,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': '88001000200',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'id': 'call-session-id-0001',
                            'userId': 'phone:+79001234567',
                            'userName': 'Aleksandr',
                        },
                        'id': 'msg-id-0002',
                        'service': {'type': 'INCOMING'},
                        'timestamp': '2021-12-30T12:23:59+03:00',
                    },
                ],
                'kwargs': {},
            },
            'msg-id-0002',
            False,
            {
                'call_id': 'call-session-id-0001',
                'contact_point_id': '88001000200',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0002',
                'user_phone_pd_id': 'test_pd_id',
                'user_name': 'Aleksandr',
            },
            None,
            False,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': 'telephony::taxi_call_center::88001000200',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'id': 'call-session-id-0001',
                            'userId': 'phone:+79001234567',
                        },
                        'id': 'msg-id-0001',
                        'service': {'status': 'FAIL', 'type': 'FORWARD'},
                        'timestamp': '2021-12-30T12:23:59+03:00',
                    },
                ],
                'kwargs': {},
            },
            'msg-id-0001',
            True,
            {
                'call_id': 'call-session-id-0001',
                'contact_point_id': '88001000200',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0001',
                'user_phone_pd_id': 'test_pd_id',
                'force_reoffer': True,
            },
            None,
            False,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': '+74950328686',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'id': 'call-session-id-0001',
                            'userId': 'phone:+79001234567',
                        },
                        'id': 'msg-id-0001',
                        'service': {'type': 'CONNECTED'},
                        'timestamp': '2022-01-14T17:46:12.9468+03:00',
                    },
                ],
                'kwargs': {},
            },
            'msg-id-0001',
            True,
            None,
            None,
            True,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': 'telephony::taxi_call_center::88001000200',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'id': 'call-session-id-0001',
                            'userId': 'phone:+79001234567',
                        },
                        'id': 'msg-id-0001',
                        'service': {
                            'status': 'ABONENT_HANGUP',
                            'type': 'HANGUP',
                        },
                        'timestamp': '2022-01-14T14:46:12+0000',
                    },
                ],
                'kwargs': {},
            },
            'msg-id-0001',
            True,
            None,
            [
                'test_pd_id_call-session-id-0001',
                {
                    'message_id': 'msg-id-0001',
                    'user_phone': '+79001234567',
                    'contact_point_id': '88001000200',
                    'call_id': 'call-session-id-0001',
                    'user_name': None,
                    'call_record_id': None,
                    'message_input': None,
                    'timestamp': '2022-01-14T14:46:12+0000',
                },
                'ABONENT_HANGUP',
            ],
            False,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': '+74950328686',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'id': 'call-session-id-0001',
                            'userId': 'phone:+79001234567',
                        },
                        'id': 'msg-id-0001',
                        'service': {'type': 'HANGUP'},
                        'timestamp': '2022-01-14T17:46:12.9468+03:00',
                    },
                ],
                'kwargs': {},
            },
            'msg-id-0001',
            True,
            None,
            [
                'test_pd_id_call-session-id-0001',
                {
                    'message_id': 'msg-id-0001',
                    'user_phone': '+79001234567',
                    'contact_point_id': '+74950328686',
                    'call_id': 'call-session-id-0001',
                    'user_name': None,
                    'call_record_id': None,
                    'message_input': None,
                    'timestamp': '2022-01-14T14:46:12+0000',
                },
                None,
            ],
            False,
            None,
        ),
        (
            {
                'args': [
                    {
                        'contactPoint': {
                            'channel': 'TELEPHONY',
                            'id': '88001000200',
                            'provider': 'TAXI_CALL_CENTER',
                        },
                        'from': {
                            'id': 'call-session-id-0001',
                            'userId': 'phone:+79001234567',
                        },
                        'id': 'msg-id-0001',
                        'service': {'input': 3, 'type': 'CSAT'},
                        'timestamp': '2021-12-30T12:23:59+03:00',
                    },
                ],
                'kwargs': {},
            },
            'msg-id-0001',
            True,
            None,
            None,
            False,
            [
                {
                    'update_meta': [
                        {
                            'change_type': 'set',
                            'field_name': 'telephony_csat',
                            'value': 3,
                        },
                    ],
                    'update_tags': [],
                },
            ],
        ),
    ],
)
async def test_stq_telephony_message_handle(
        stq3_context,
        mock_tvm_keys,
        stq,
        patch,
        call,
        message_id,
        expected_chat,
        expected_create_chatterbox_task,
        expected_hangup_process,
        expected_connected,
        expected_csat,
        mock_personal_custom,
        mock_chatterbox_tasks,
        patch_aiohttp_session,
        response_mock,
):
    chatterbox_url = discovery.find_service('chatterbox').url

    @patch_aiohttp_session(
        chatterbox_url + '/v1/tasks/chatterbox_id/update_meta', 'POST',
    )
    def _dummy_v1_tasks_update_meta(*args, **kwargs):
        assert kwargs['json']['update_meta'] == [
            {'change_type': 'set', 'field_name': 'telephony_csat', 'value': 3},
        ]
        return response_mock()

    await stq_task.telephony_message_handle(
        stq3_context, *call['args'], **call['kwargs'],
    )

    query = {'messages.id': message_id}
    chat_doc = await stq3_context.mongo.user_chat_messages.find_one(query)

    if expected_chat:
        chat_doc = await stq3_context.mongo.user_chat_messages.find_one(query)
        assert chat_doc['type'] == 'sms_support'

    if expected_connected:
        chat_doc = await stq3_context.mongo.user_chat_messages.find_one(query)
        assert chat_doc['telephony_connect_established']

    if expected_hangup_process:
        stq_call = stq.support_chat_handle_logbroker_hangup.next_call()
        assert stq_call['args'] == expected_hangup_process
    else:
        assert not stq.support_chat_handle_logbroker_hangup.times_called

    if expected_create_chatterbox_task:
        stq_call = getattr(
            stq, 'support_chat_create_chatterbox_task',
        ).next_call()
        assert stq_call['args'] == [
            str(chat_doc['_id']),
            expected_create_chatterbox_task,
        ]
    else:
        assert not getattr(
            stq, 'support_chat_create_chatterbox_task',
        ).times_called

    if expected_csat:
        chatterbox_calls = [
            call['kwargs']['json']
            for call in _dummy_v1_tasks_update_meta.calls
        ]
        assert chatterbox_calls == expected_csat
