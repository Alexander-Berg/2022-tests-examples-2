import pytest


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_UNAUTHORIZED_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
)
async def test_acks(taxi_ucommunications, mockserver, testpoint, mongodb):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response('{}', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/unauthorized/notification/push',
        json={
            'user': 'user_1',
            'data': {'payload': {'text': 'Hello'}},
            'intent': 'taxi_crm',
            'application': 'lavka_iphone',
        },
    )
    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()
    assert mongodb.user_notification_ack_queue.count() == 1


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_INTENTS={
        'taxi_crm': {'tags': ['marketing', 'news']},
    },
    COMMUNICATIONS_USER_NOTIFICATION_WRITE_USER_ID_ENABLE=True,
)
@pytest.mark.parametrize(
    'data,xiva_body',
    [
        (
            {'payload': {'text': 'Hello'}},
            {
                'tags': ['marketing', 'news'],
                'payload': {
                    'marketing_tags': ['marketing', 'news'],
                    'text': 'Hello',
                    'user_id': 'user_1',
                },
            },
        ),
    ],
)
async def test_tags(taxi_ucommunications, mockserver, data, xiva_body):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        request_data = request.json
        payload = request_data.get('payload', {})
        if 'id' in payload:
            payload.pop('id')

        assert request_data == xiva_body
        return mockserver.make_response('{}', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/unauthorized/notification/push',
        json={
            'user': 'user_1',
            'data': data,
            'intent': 'taxi_crm',
            'application': 'lavka_iphone',
        },
    )
    assert response.status_code == 200


@pytest.mark.now('2010-01-01T00:00:00Z')
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {
                    'applications': ['yango_iphone', 'yango_android'],
                    'intents': ['taxi_arrived'],
                },
                'payload_repack': {
                    'apns': {
                        'id': '$id',
                        'x': '$a/b',
                        'y': '$b',
                        'z': 50,
                        'w': {'#stringify': {'test': 'me'}},
                        'ts': '#timestamp',
                    },
                },
            },
        ],
    },
    XIVA_APPLICATION_TO_XIVA_SERVICE={
        '__default__': 'taxi',
        'yango_android': 'yango',
        'yango_iphone': 'yauber',
    },
)
@pytest.mark.parametrize(
    'user_id,application,sending_token',
    [
        ('user_android', 'yango_android', 'yango_sending_token'),
        ('user_iphone', 'yango_iphone', 'yauber_sending_token'),
    ],
)
async def test_repack(
        taxi_ucommunications, mockserver, user_id, application, sending_token,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json == {
            'apns': {
                'id': 'xxx',
                'x': 'value',
                'y': 10,
                'z': 50,
                'w': '{"test":"me"}',
                'ts': 1262304000000,
            },
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/unauthorized/notification/push',
        json={
            'user': f'{user_id}',
            'application': application,
            'data': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
            'intent': 'taxi_arrived',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}
