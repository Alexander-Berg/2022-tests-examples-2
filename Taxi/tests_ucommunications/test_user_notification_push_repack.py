import pytest


@pytest.mark.skip('fix after: https://st.yandex-team.ru/TAXIINFRA-1737')
@pytest.mark.now('2010-01-01T00:00:00Z')
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
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

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            f'{{"id": "{user_id}", "application": "{application}"}}', 200,
        )

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': f'{user_id}',
            'data': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
            'intent': 'taxi_arrived',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.skip('fix after: https://st.yandex-team.ru/TAXIINFRA-1737')
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'intents': ['taxi_arrived']},
                'payload_repack': {
                    'apns': {'id': '$id', 'x': '$a/b', 'y': '$b', 'z': 50},
                },
            },
        ],
    },
)
async def test_repack_any_application(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json == {
            'apns': {'id': 'xxx', 'x': 'value', 'y': 10, 'z': 50},
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user_1',
            'data': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
            'intent': 'taxi_arrived',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.skip('fix after: https://st.yandex-team.ru/TAXIINFRA-1737')
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'application': ['taxi']},
                'payload_repack': {
                    'apns': {'id': '$id', 'x': '$a/b', 'y': '$b', 'z': 50},
                },
            },
        ],
    },
)
async def test_repack_any_intent(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json == {
            'apns': {'id': 'xxx', 'x': 'value', 'y': 10, 'z': 50},
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user_1',
            'data': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
            'intent': 'doesnt_matter',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': False,
                'conditions': {
                    'applications': ['taxi'],
                    'intents': ['taxi_arrived'],
                },
                'payload_repack': {
                    'apns': {'id': '$id', 'x': '$a/b', 'y': '$b', 'z': 50},
                },
            },
        ],
    },
)
@pytest.mark.parametrize(
    'data,status_code,expected_response',
    [
        (
            {
                'user': 'user_1',
                'data': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
                'confirm': True,
                'intent': 'taxi_arrived',
            },
            200,
            {},
        ),
    ],
)
async def test_repack_disabled(
        taxi_ucommunications, data, status_code, expected_response, mockserver,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        # 'enabled': False,
        assert request.json == {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10}
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/notification/push', json=data,
    )
    assert response.status_code == 200
    assert response.json() == {}


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
)
async def test_return_payload(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(_request):
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user_1',
            'data': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
            'intent': 'doesnt_matter',
            'return_payload': True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'payload': {'id': 'xxx', 'a': {'b': 'value'}, 'b': 10},
    }
