import json

import pytest


@pytest.mark.parametrize(
    'data,status_code,expected_response',
    [
        ({'user': 'user_1', 'ttl': 30, 'data': {}}, 200, {}),
        ({'user': 'user_1', 'data': {}}, 200, {}),
        (
            {'user': 'user_1', 'data': {}, 'confirm': True, 'intent': 'test'},
            200,
            {},
        ),
    ],
)
async def test_smoke(
        taxi_ucommunications, data, status_code, expected_response,
):
    response = await taxi_ucommunications.post(
        'user/notification/push', json=data,
    )
    assert response.status_code == status_code
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'data,status_code',
    [({}, 400), ({'user': 'user_1'}, 400), ({'user': '', 'data': {}}, 400)],
)
async def test_params_errors(taxi_ucommunications, data, status_code):
    response = await taxi_ucommunications.post(
        'user/notification/push', json=data,
    )
    assert response.status_code == status_code
    assert response.json()['code'] == '400'


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
@pytest.mark.parametrize(
    'user_id,status_code,expected_response',
    [('user_taxi', 200, {}), ('user_uber', 200, {}), ('user_yango', 200, {})],
)
# pylint: disable=redefined-outer-name
async def test_autodetect_service(
        taxi_ucommunications,
        user_id,
        status_code,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        if user_id == 'user_taxi':
            assert request.args['service'] == 'taxi'
        elif user_id == 'user_uber':
            assert request.args['service'] == 'yauber'
        elif user_id == 'user_yango':
            assert request.args['service'] == 'yango'
        else:
            assert False
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        if user_id == 'user_taxi':
            return mockserver.make_response(
                '{"id": "user_taxi", "gcm_token": "1234567"}', 200,
            )

        if user_id == 'user_uber':
            return mockserver.make_response(
                '{"id": "user_uber", "application": "uber_iphone"}', 200,
            )

        # user_id == 'user_yango':
        return mockserver.make_response(
            '{"id": "user_yango", "application": "yango_android"}', 200,
        )

    body = {'data': {}, 'confirm': True, 'intent': 'test'}
    body['user'] = user_id
    response = await taxi_ucommunications.post(
        'user/notification/push', json=body,
    )
    assert response.status_code == status_code
    assert response.json() == expected_response


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
@pytest.mark.parametrize(
    'response,code,expected_code,expected_response',
    [
        (
            {'code': '500', 'message': 'Internal server error'},
            500,
            502,
            {
                'code': '502',
                'message': (
                    'failed to request user user1: Unexpected HTTP '
                    'response code \'500\' for \'POST /users/get\''
                ),
            },
        ),
        (
            {'code': '404', 'message': 'Not found error'},
            404,
            404,
            {
                'code': '404',
                'message': (
                    'user user1 not found: POST /users/get, status code 404'
                ),
            },
        ),
    ],
)
# pylint: disable=redefined-outer-name
async def test_autodetect_service_errors(
        taxi_ucommunications,
        mockserver,
        response,
        code,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(json.dumps(response), code)

    body = {'data': {}, 'confirm': True, 'intent': 'test', 'user': 'user1'}
    response = await taxi_ucommunications.post(
        'user/notification/push', json=body,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_response


async def test_bad_xiva_response(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response('InternalServerError', 500)

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            '{"id": "user", "gcm_token": "1234567"}', 200,
        )

    await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user', 'data': {}, 'confirm': True, 'intent': 'test'},
    )


@pytest.mark.parametrize(
    'xiva_response,expected_code',
    [
        ('OK', 200),
        (
            '{"code":200,"body":{"apns_message_id":"629F43D"},"id":"mob:7d"}',
            200,
        ),
        ('{"code":205, "body": {"error":"MismatchSenderId"}}', 502),
        ('{"code":204, "body": {"error":"no subscriptions"}}', 400),
    ],
)
async def test_parse_xiva_body(
        taxi_ucommunications, mockserver, xiva_response, expected_code,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response(
            xiva_response, 200, headers={'TransitID': 'id'},
        )

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            '{"id": "user", "gcm_token": "1234567"}', 200,
        )

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user', 'data': {}, 'confirm': True, 'intent': 'test'},
    )
    assert response.status_code == expected_code


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_APPLICATIONS_BLACKLIST={
        'rules': [
            {'source_intent': 'test', 'applications_blacklist': ['mbro']},
        ],
    },
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_blacklist(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert False

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            '{"id": "user", "gcm_token": "1234567", "application": "mbro"}',
            200,
        )

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user_1', 'data': {}, 'confirm': True, 'intent': 'test'},
    )
    assert response.status_code == 400


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_WRITE_USER_ID_ENABLE=True,
    COMMUNICATIONS_USER_NOTIFICATION_INTENTS={
        'taxi_crm': {'tags': ['marketing', 'news']},
    },
)
@pytest.mark.parametrize(
    'data,xiva_body',
    [
        (
            {'payload': {}, 'repack': {}},
            {
                'tags': ['marketing', 'news'],
                'payload': {
                    'marketing_tags': ['marketing', 'news'],
                    'user_id': 'user_1',
                },
                'repack': {},
            },
        ),
        ({}, {'tags': ['marketing', 'news']}),
        (
            {'payload': {}, 'repack': {}, 'tags': ['existing_tags']},
            {
                'tags': ['marketing', 'news'],
                'payload': {
                    'marketing_tags': ['marketing', 'news'],
                    'user_id': 'user_1',
                },
                'repack': {},
            },
        ),
        (
            {
                'payload': {'id': '123', 'foo': 'bar'},
                'repack': {
                    'fcm': {
                        'notification': {},
                        'repack_payload': ['id', 'foo'],
                    },
                    'apns': {'aps': {}, 'repack_payload': ['id']},
                },
            },
            {
                'payload': {
                    'foo': 'bar',
                    'marketing_tags': ['marketing', 'news'],
                    'user_id': 'user_1',
                },
                'repack': {
                    'fcm': {
                        'notification': {},
                        'repack_payload': [
                            'id',
                            'foo',
                            'marketing_tags',
                            'user_id',
                        ],
                    },
                    'apns': {
                        'aps': {},
                        'repack_payload': ['id', 'marketing_tags', 'user_id'],
                    },
                },
                'tags': ['marketing', 'news'],
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

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            '{"id": "user", "gcm_token": "1234567", "application": "mbro"}',
            200,
        )

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user_1',
            'data': data,
            'confirm': True,
            'intent': 'taxi_crm',
        },
    )
    assert response.status_code == 200


@pytest.mark.config(COMMUNICATIONS_USER_NOTIFICATION_WRITE_USER_ID_ENABLE=True)
async def test_add_id_in_repack(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        _id = request.json['payload']['id']
        assert request.json == {
            'repack': {
                'fcm': {'text': 'Hello', 'repack_payload': ['*']},
                'apns': {'repack_payload': ['*'], 'aps': {'alert': 'Hello'}},
            },
            'payload': {'id': _id, 'user_id': 'user'},
        }
        return mockserver.make_response('Ok', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            '{"id": "user", "gcm_token": "1234567"}', 200,
        )

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user',
            'intent': 'test',
            'data': {
                'repack': {
                    'fcm': {'text': 'Hello'},
                    'apns': {'aps': {'alert': 'Hello'}},
                },
                'payload': {},
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_INTENTS={
        'test': {'write_user_id': False},
    },
)
async def test_write_user_id_disabled(taxi_ucommunications, mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        _id = request.json['payload']['id']
        assert request.json == {
            'repack': {
                'fcm': {'text': 'Hello', 'repack_payload': ['*']},
                'apns': {'repack_payload': ['*'], 'aps': {'alert': 'Hello'}},
            },
            'payload': {'id': _id},
        }
        return mockserver.make_response('Ok', 200, headers={'TransitID': 'id'})

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return mockserver.make_response(
            '{"id": "user", "gcm_token": "1234567"}', 200,
        )

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user',
            'intent': 'test',
            'data': {
                'repack': {
                    'fcm': {'text': 'Hello'},
                    'apns': {'aps': {'alert': 'Hello'}},
                },
                'payload': {},
            },
        },
    )
    assert response.status_code == 200
