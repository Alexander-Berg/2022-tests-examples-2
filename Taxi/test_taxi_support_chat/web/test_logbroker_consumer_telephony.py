# pylint: disable=W0212
import datetime

import pytest

from taxi import discovery

from taxi_support_chat.components import (
    background_logbroker_consumer as logbroker,
)


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
        'channels': ['TELEPHONY'],
    },
)
@pytest.mark.parametrize('legacy_mode', (True, False))
@pytest.mark.parametrize(
    (
        'messages',
        'owner_id',
        'expected_chat',
        'expected_create_chatterbox_task',
        'expected_hangup_process',
        'expected_connected_data',
        'expected_csat',
        'expected_handle_message_calls',
    ),
    [
        (['123jhgd'], None, False, None, None, False, False, None),
        (
            [
                """
                    {
                        "id": "msg-id-0001",
                        "contactPoint": {
                            "id": "88001000200",
                            "provider": "TAXI_CALL_CENTER",
                            "channel": "TELEPHONY"
                        },
                        "service": {
                            "type": "FORWARD",
                            "status": "SUCCESS"
                        }
                    }
                    """,
            ],
            None,
            False,
            None,
            None,
            False,
            False,
            [
                {
                    'args': [
                        {
                            'id': 'msg-id-0001',
                            'service': {
                                'status': 'SUCCESS',
                                'type': 'FORWARD',
                            },
                            'contactPoint': {
                                'id': '88001000200',
                                'provider': 'TAXI_CALL_CENTER',
                                'channel': 'TELEPHONY',
                            },
                        },
                    ],
                    'kwargs': {},
                },
            ],
        ),
        (
            [
                """
                {
                    "id": "msg-id-0001",
                    "timestamp": "2021-12-30T12:23:59+03:00",
                    "contactPoint": {
                        "id": "88001000200",
                        "provider": "TAXI_CALL_CENTER",
                        "channel": "TELEPHONY"
                    },
                    "from": {
                        "userId": "phone:+79001234567",
                        "userName": "Aleksandr"
                    },
                    "service": {
                        "type": "INCOMING"
                    }
                }
                """,
            ],
            None,
            False,
            None,
            None,
            None,
            False,
            [
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
            ],
        ),
        (
            [
                """
                {
                    "id": "msg-id-0001",
                    "timestamp": "2021-12-30T12:23:59+03:00",
                    "contactPoint": {
                        "id": "88001000200",
                        "provider": "TAXI_CALL_CENTER",
                        "channel": "TELEPHONY"
                    },
                    "from": {
                        "id": "call-session-id-0001",
                        "userId": "phone:+79001234567",
                        "userName": "Aleksandr"
                    },
                    "service": {
                        "type": "INCOMING"
                    }
                }
                """,
            ],
            'test_pd_id_call-session-id-0001',
            True,
            {
                'call_id': 'call-session-id-0001',
                'contact_point_id': '88001000200',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0001',
                'user_phone_pd_id': 'test_pd_id',
                'user_name': 'Aleksandr',
            },
            None,
            None,
            False,
            [
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
                            'id': 'msg-id-0001',
                            'service': {'type': 'INCOMING'},
                            'timestamp': '2021-12-30T12:23:59+03:00',
                        },
                    ],
                    'kwargs': {},
                },
            ],
        ),
        (
            [
                """
                {
                    "id": "msg-id-0001",
                    "timestamp": "2021-12-30T12:23:59+03:00",
                    "contactPoint": {
                        "id": "88001000200",
                        "provider": "TAXI_CALL_CENTER",
                        "channel": "TELEPHONY"
                    },
                    "from": {
                        "id": "call-session-id-0001",
                        "userId": "phone:+79001234567"
                    },
                    "service": {
                        "type": "INCOMING"
                    }
                }
                """,
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2021-12-30T12:23:59+03:00",
                        "contactPoint": {
                            "id": "telephony::taxi_call_center::88001000200",
                            "provider": "TAXI_CALL_CENTER",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0001",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "FORWARD",
                            "status": "FAIL"
                        }
                    }
                    """,
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2022-01-14T17:46:12.9468+03:00",
                        "contactPoint": {
                            "provider": "TAXI_CALL_CENTER",
                            "id": "+74950328686",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0001",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "CONNECTED"
                        }
                    }
                    """,
            ],
            'test_pd_id_call-session-id-0001',
            True,
            {
                'call_id': 'call-session-id-0001',
                'contact_point_id': '88001000200',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0001',
                'user_phone_pd_id': 'test_pd_id',
            },
            None,
            {
                'telephony_connect_established_at': datetime.datetime(
                    2018, 7, 18, 11, 20,
                ),
                'telephony_connect_established': True,
            },
            False,
            [
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
                            'service': {'type': 'INCOMING'},
                            'timestamp': '2021-12-30T12:23:59+03:00',
                        },
                    ],
                    'kwargs': {},
                },
                {
                    'args': [
                        {
                            'contactPoint': {
                                'channel': 'TELEPHONY',
                                'id': (
                                    'telephony::taxi_call_center::88001000200'
                                ),
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
            ],
        ),
        (
            [
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2021-12-30T12:23:59+03:00",
                        "contactPoint": {
                            "id": "88001000200",
                            "provider": "TAXI_CALL_CENTER",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0002",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "INCOMING"
                        }
                    }
                    """,
                """
                        {
                            "id": "msg-id-0001",
                            "timestamp": "2022-01-14T17:46:12.9468+03:00",
                            "contactPoint": {
                                "provider": "TAXI_CALL_CENTER",
                                "id": "+74950328686",
                                "channel": "TELEPHONY"
                            },
                            "from": {
                                "id": "call-session-id-0002",
                                "userId": "phone:+79001234567"
                            },
                            "service": {
                                "type": "CONNECTED"
                            }
                        }
                        """,
            ],
            'test_pd_id_call-session-id-0002',
            True,
            {
                'call_id': 'call-session-id-0002',
                'contact_point_id': '88001000200',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0001',
                'user_phone_pd_id': 'test_pd_id',
            },
            None,
            {
                'telephony_connect_established_at': datetime.datetime(
                    2018, 1, 1, 1, 1, 1,
                ),
                'telephony_connect_established': True,
            },
            False,
            [
                {
                    'args': [
                        {
                            'contactPoint': {
                                'channel': 'TELEPHONY',
                                'id': '88001000200',
                                'provider': 'TAXI_CALL_CENTER',
                            },
                            'from': {
                                'id': 'call-session-id-0002',
                                'userId': 'phone:+79001234567',
                            },
                            'id': 'msg-id-0001',
                            'service': {'type': 'INCOMING'},
                            'timestamp': '2021-12-30T12:23:59+03:00',
                        },
                    ],
                    'kwargs': {},
                },
                {
                    'args': [
                        {
                            'contactPoint': {
                                'channel': 'TELEPHONY',
                                'id': '+74950328686',
                                'provider': 'TAXI_CALL_CENTER',
                            },
                            'from': {
                                'id': 'call-session-id-0002',
                                'userId': 'phone:+79001234567',
                            },
                            'id': 'msg-id-0001',
                            'service': {'type': 'CONNECTED'},
                            'timestamp': '2022-01-14T17:46:12.9468+03:00',
                        },
                    ],
                    'kwargs': {},
                },
            ],
        ),
        (
            [
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2022-01-14T17:46:12.9468+03:00",
                        "contactPoint": {
                            "provider": "TAXI_CALL_CENTER",
                            "id": "+74950328686",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0001",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "CONNECTED"
                        }
                    }
                    """,
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2022-01-14T14:46:12+0000",
                        "contactPoint": {
                            "id": "telephony::taxi_call_center::88001000200",
                            "provider": "TAXI_CALL_CENTER",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0001",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "HANGUP",
                            "status": "ABONENT_HANGUP"
                        }
                    }
                    """,
            ],
            'test_pd_id_call-session-id-0001',
            False,
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
            None,
            False,
            [
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
                {
                    'args': [
                        {
                            'contactPoint': {
                                'channel': 'TELEPHONY',
                                'id': (
                                    'telephony::taxi_call_center::88001000200'
                                ),
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
            ],
        ),
        (
            [
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2022-01-14T17:46:12.9468+03:00",
                        "contactPoint": {
                            "provider": "TAXI_CALL_CENTER",
                            "id": "+74950328686",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0001",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "INCOMING"
                        }
                    }
                    """,
                """
                    {
                        "id": "msg-id-0001",
                        "timestamp": "2022-01-14T17:46:12.9468+03:00",
                        "contactPoint": {
                            "provider": "TAXI_CALL_CENTER",
                            "id": "+74950328686",
                            "channel": "TELEPHONY"
                        },
                        "from": {
                            "id": "call-session-id-0001",
                            "userId": "phone:+79001234567"
                        },
                        "service": {
                            "type": "HANGUP"
                        }
                    }
                    """,
            ],
            'test_pd_id_call-session-id-0001',
            True,
            {
                'call_id': 'call-session-id-0001',
                'contact_point_id': '+74950328686',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0001',
                'user_phone_pd_id': 'test_pd_id',
            },
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
            None,
            False,
            [
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
                            'service': {'type': 'INCOMING'},
                            'timestamp': '2022-01-14T17:46:12.9468+03:00',
                        },
                    ],
                    'kwargs': {},
                },
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
            ],
        ),
        (
            [
                """
                {
                    "id": "msg-id-0001",
                    "timestamp": "2021-12-30T12:23:59+03:00",
                    "contactPoint": {
                        "id": "88001000200",
                        "provider": "TAXI_CALL_CENTER",
                        "channel": "TELEPHONY"
                    },
                    "from": {
                        "id": "call-session-id-0001",
                        "userId": "phone:+79001234567",
                        "userName": "Aleksandr"
                    },
                    "service": {
                        "type": "INCOMING"
                    }
                }
                """,
                """
                {
                    "id": "msg-id-0001",
                    "timestamp": "2021-12-30T12:23:59+03:00",
                    "contactPoint": {
                        "id": "88001000200",
                        "provider": "TAXI_CALL_CENTER",
                        "channel": "TELEPHONY"
                    },
                    "from": {
                        "id": "call-session-id-0001",
                        "userId": "phone:+79001234567"
                    },
                    "service": {
                        "type": "CSAT",
                        "input": 3
                    }
                }
                """,
            ],
            'test_pd_id_call-session-id-0001',
            False,
            {
                'call_id': 'call-session-id-0001',
                'contact_point_id': '88001000200',
                'logbroker_telephony': True,
                'message_id': 'msg-id-0001',
                'user_phone_pd_id': 'test_pd_id',
                'user_name': 'Aleksandr',
            },
            None,
            None,
            True,
            [
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
                            'id': 'msg-id-0001',
                            'service': {'type': 'INCOMING'},
                            'timestamp': '2021-12-30T12:23:59+03:00',
                        },
                    ],
                    'kwargs': {},
                },
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
            ],
        ),
    ],
)
async def test_logbroker_consumer(
        web_app_client,
        web_context,
        mock_tvm_keys,
        stq,
        patch,
        legacy_mode,
        messages,
        owner_id,
        expected_chat,
        expected_create_chatterbox_task,
        expected_hangup_process,
        expected_connected_data,
        expected_csat,
        expected_handle_message_calls,
        mock_personal_custom,
        mock_chatterbox_tasks,
        patch_aiohttp_session,
        response_mock,
):
    if legacy_mode:
        web_context.config.SUPPORT_CHAT_LOGBROKER_TELEPHONY_SETTINGS[
            'use_legacy_mode_for_handle_msg'
        ] = True
    chatterbox_url = discovery.find_service('chatterbox').url

    @patch_aiohttp_session(
        chatterbox_url + '/v1/tasks/chatterbox_id/update_meta', 'POST',
    )
    def _dummy_v1_tasks_update_meta(*args, **kwargs):
        assert kwargs['json']['update_meta'] == [
            {'change_type': 'set', 'field_name': 'telephony_csat', 'value': 3},
        ]
        return response_mock()

    task = logbroker.BackgroundLogbrokerConsumerTask(web_context)
    await task._handle_messages(
        messages, web_context.config.SUPPORT_CHAT_LOGBROKER_TELEPHONY_SETTINGS,
    )

    if not legacy_mode:
        stq_calls = [
            {'args': call['args'], 'kwargs': call['kwargs']}
            for call in (
                stq.support_chat_telephony_message_handle.next_call()
                for _ in range(
                    stq.support_chat_telephony_message_handle.times_called,
                )
            )
        ]
        if stq_calls:
            assert stq_calls == expected_handle_message_calls
        else:
            assert not expected_handle_message_calls
    else:
        query = {'owner_id': owner_id}
        chat_doc = await web_context.mongo.user_chat_messages.find_one(query)

        if expected_chat:
            chat_doc = await web_context.mongo.user_chat_messages.find_one(
                query,
            )
            assert chat_doc['type'] == 'sms_support'
            assert chat_doc['ticket_processed'] is True

        if expected_connected_data:
            chat_doc = await web_context.mongo.user_chat_messages.find_one(
                query,
            )
            for field, value in expected_connected_data.items():
                assert chat_doc[field] == value

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
