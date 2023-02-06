# pylint: disable=W0212
import pytest

from chatterbox.components import background_logbroker_consumer as logbroker


@pytest.mark.now('2018-07-18T11:20:00')
@pytest.mark.config(
    CHATTERBOX_SETTINGS_LOGBROKER={
        'test_client_first': {
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
        'test_operator_first': {
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
            'dial_operator_first': True,
        },
    },
)
@pytest.mark.parametrize(
    ('messages', 'expected_handle_message_calls', 'settings_name'),
    [
        (['123jhgd'], None, 'test_client_first'),
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "OUTGOING",
                            "status": "FAIL"
                        }
                    }
                    """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'status_completed': 'not_answered',
                        },
                    ],
                    'kwargs': {'completed': False},
                },
            ],
            'test_client_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "FORWARD",
                            "status": "FAIL"
                        }
                    }
                    """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'status_completed': 'failed',
                        },
                    ],
                    'kwargs': {'completed': False},
                },
            ],
            'test_client_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "CONNECTED"
                        }
                    }
                    """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'answered_at': '2021-12-30T09:23:59+0000',
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'status_completed': 'bridged',
                        },
                    ],
                    'kwargs': {'completed': False},
                },
            ],
            'test_client_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "HANGUP"
                        }
                    }
                    """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'call_record_id': None,
                            'completed_at': '2021-12-30T09:23:59+0000',
                            'hangup_disposition': 'caller_bye',
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                        },
                    ],
                    'kwargs': {'completed': True},
                },
            ],
            'test_client_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "HANGUP",
                            "status": "ABONENT_HANGUP",
                            "callRecordId": "1234"
                        }
                    }
                    """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'call_record_id': '1234',
                            'completed_at': '2021-12-30T09:23:59+0000',
                            'hangup_disposition': 'callee_bye',
                        },
                    ],
                    'kwargs': {'completed': True},
                },
            ],
            'test_client_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "HANGUP",
                            "status": "ABONENT_HANGUP",
                            "callRecordId": "1234"
                        }
                    }
                """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'call_record_id': '1234',
                            'completed_at': '2021-12-30T09:23:59+0000',
                            'hangup_disposition': 'caller_bye',
                        },
                    ],
                    'kwargs': {'completed': True},
                },
            ],
            'test_operator_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "HANGUP",
                            "callRecordId": "1234"
                        }
                    }
                    """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'call_record_id': '1234',
                            'completed_at': '2021-12-30T09:23:59+0000',
                            'hangup_disposition': 'callee_bye',
                        },
                    ],
                    'kwargs': {'completed': True},
                },
            ],
            'test_operator_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "OUTGOING",
                            "status": "FAIL"
                        }
                    }
                """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'status_completed': 'failed',
                        },
                    ],
                    'kwargs': {'completed': False},
                },
            ],
            'test_operator_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "FORWARD",
                            "status": "FAIL"
                        }
                    }
                """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'status_completed': 'not_answered',
                        },
                    ],
                    'kwargs': {'completed': False},
                },
            ],
            'test_operator_first',
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
                            "id": "outgoing_5b2cae5cb2682a976914c2a5_123",
                            "userId": "phone:+79001234567",
                            "userName": "Aleksandr"
                        },
                        "service": {
                            "type": "CSAT",
                            "input": 5
                        }
                    }
                """,
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {
                            'id': 'outgoing_5b2cae5cb2682a976914c2a5_123',
                            'csat_value': 5,
                        },
                    ],
                    'kwargs': {'completed': False},
                },
            ],
            'test_operator_first',
        ),
    ],
)
async def test_logbroker_consumer(
        web_app_client,
        web_context,
        stq,
        patch,
        messages,
        expected_handle_message_calls,
        settings_name,
        patch_aiohttp_session,
        response_mock,
):
    task = logbroker.BackgroundLogbrokerConsumerTask(web_context)
    await task._handle_messages(
        messages,
        web_context.config.CHATTERBOX_SETTINGS_LOGBROKER[settings_name],
    )

    stq_calls = [
        {'args': call['args'], 'kwargs': call['kwargs']}
        for call in (
            stq.chatterbox_handle_outgoing_call.next_call()
            for _ in range(stq.chatterbox_handle_outgoing_call.times_called)
        )
    ]
    if expected_handle_message_calls:
        assert stq_calls == expected_handle_message_calls
    else:
        assert not stq_calls
