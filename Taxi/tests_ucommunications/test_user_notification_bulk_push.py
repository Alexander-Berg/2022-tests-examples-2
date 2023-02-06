import json

import pytest


# pylint: disable=redefined-outer-name
async def test_wrong_method(taxi_ucommunications):
    response = await taxi_ucommunications.get(
        'user/notification/bulk-push', json={},
    )
    assert response.status_code == 405


@pytest.mark.parametrize('data,status_code', [({}, 400)])
async def test_params_errors(taxi_ucommunications, data, status_code):
    response = await taxi_ucommunications.post(
        'user/notification/bulk-push', json=data,
    )
    assert response.status_code == status_code
    assert response.json()['code'] == str(status_code)


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
)
# pylint: disable=redefined-outer-name
async def test_bulk_send(taxi_ucommunications, mockserver, load):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        users = json.loads(load('users.json'))
        return mockserver.make_response(
            json.dumps(users[request.json['id']]), 200,
        )

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        message = request.json
        user = request.args['user']

        assert message['payload'].get('id') is not None
        del message['payload']['id']

        if user == 'user_taxi0':
            assert message == {
                'payload': {'msg': '100 руб.', 'title': 'Title'},
                'repack': {
                    'gcm': {'title': 'Title', 'repack_payload': ['*']},
                    'apns': {'msg': 'ApnsUserTaxi', 'repack_payload': ['*']},
                },
            }
        elif user == 'user_uber':
            assert message == {'payload': {'msg': 'Message', 'title': 'Title'}}
        elif user == 'user_yango':
            assert message == {'payload': {'msg': 'Message', 'title': 'Title'}}
        else:
            assert False, f'Invalid user: f{user}'

        return mockserver.make_response(
            'OK', 200, headers={'TransitID': 'single'},
        )

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        message = request.json
        assert message['payload'].get('id') is not None
        del message['payload']['id']

        assert message == {
            'payload': {'msg': 'Message', 'title': 'Title'},
            'recipients': ['user_taxi1', 'user_taxi2'],
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'results': [
                        {'code': 200, 'body': 'OK'},
                        {'code': 200, 'body': {'text': 'OK'}},
                    ],
                },
            ),
            200,
            headers={'TransitID': 'bulk'},
        )

    text = {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}}
    data = {'payload': {'msg': 'Message', 'title': 'Title'}}
    users = [
        {
            'user_id': 'user_taxi0',
            'locale': 'ru',
            'data': {
                'payload': {'msg': text},
                'repack': {
                    'gcm': {'title': 'Title'},
                    'apns': {'msg': 'ApnsUserTaxi'},
                },
            },
        },
        {'user_id': 'user_taxi1', 'locale': 'ru'},
        {'user_id': 'user_taxi2', 'locale': 'ru'},
        {'user_id': 'user_uber', 'locale': 'en'},
        {'user_id': 'user_yango'},
    ]
    body = {
        'data': data,
        'confirm': True,
        'intent': 'test',
        'recipients': users,
    }
    response = await taxi_ucommunications.post(
        'user/notification/bulk-push', json=body,
    )
    assert response.status_code == 200


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_APPLICATIONS_BLACKLIST={
        'rules': [
            {
                'source_intent': 'test',
                'applications_blacklist': ['taxi_android'],
            },
        ],
    },
)
# pylint: disable=redefined-outer-name
async def test_bulk_blacklist(taxi_ucommunications, mockserver, load):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        users = json.loads(load('users.json'))
        return mockserver.make_response(
            json.dumps(users[request.json['id']]), 200,
        )

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response(
            'OK', 200, headers={'TransitID': 'single'},
        )

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        assert False

    text = {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}}
    data = {'payload': {'msg': 'Message', 'title': 'Title'}}
    users = [
        {
            'user_id': 'user_taxi0',
            'locale': 'ru',
            'data': {
                'payload': {'msg': text},
                'repack': {
                    'gcm': {'title': 'Title'},
                    'apns': {'msg': 'ApnsUserTaxi'},
                },
            },
        },
        {'user_id': 'user_taxi1', 'locale': 'ru'},
        {'user_id': 'user_taxi2', 'locale': 'ru'},
        {'user_id': 'user_uber', 'locale': 'en'},
        {'user_id': 'user_yango'},
    ]
    body = {
        'data': data,
        'confirm': True,
        'intent': 'test',
        'recipients': users,
    }
    response = await taxi_ucommunications.post(
        'user/notification/bulk-push', json=body,
    )
    assert response.status_code == 200


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key2': {'ru': 'сообщение1', 'en': 'message1'},
        'key3': {'ru': 'сообщение2', 'en': 'message2'},
    },
)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_INTENTS={'crm': {'tags': ['marketing']}},
)
async def test_bulk_tags(taxi_ucommunications, mockserver, load):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        users = json.loads(load('users.json'))
        return mockserver.make_response(
            json.dumps(users[request.json['id']]), 200,
        )

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        message = request.json
        user = request.args['user']

        assert message['payload'].get('id') is not None
        del message['payload']['id']

        if user == 'user_taxi0':
            assert message == {
                'tags': ['marketing'],
                'payload': {
                    'msg': '100 руб.',
                    'title': 'Title',
                    'marketing_tags': ['marketing'],
                },
                'repack': {
                    'gcm': {'title': 'Title', 'repack_payload': ['*']},
                    'apns': {'msg': 'ApnsUserTaxi', 'repack_payload': ['*']},
                },
            }
            assert request.args['service'] == 'taxi'
        elif user == 'user_uber':
            assert message == {
                'tags': ['marketing'],
                'payload': {
                    'msg': 'Message',
                    'title': 'Title',
                    'marketing_tags': ['marketing'],
                },
            }
            assert request.args['service'] == 'yauber'
        elif user == 'user_yango':
            assert message == {
                'tags': ['marketing'],
                'payload': {
                    'msg': 'Message',
                    'title': 'Title',
                    'marketing_tags': ['marketing'],
                },
            }
            assert request.args['service'] == 'yango'
        else:
            assert False, f'Invalid user: f{user}'

        return mockserver.make_response(
            'OK', 200, headers={'TransitID': 'single'},
        )

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        message = request.json
        assert message['payload'].get('id') is not None
        del message['payload']['id']

        assert message == {
            'payload': {
                'msg': 'Message',
                'title': 'Title',
                'marketing_tags': ['marketing'],
            },
            'tags': ['marketing'],
            'recipients': ['user_taxi1', 'user_taxi2'],
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'results': [
                        {'code': 200, 'body': 'OK'},
                        {'code': 200, 'body': {'text': 'OK'}},
                    ],
                },
            ),
            200,
            headers={'TransitID': 'bulk'},
        )

    text = {'key': 'key1', 'keyset': 'notify', 'params': {'cost': 100}}
    data = {'payload': {'msg': 'Message', 'title': 'Title'}}
    users = [
        {
            'user_id': 'user_taxi0',
            'locale': 'ru',
            'data': {
                'payload': {'msg': text},
                'repack': {
                    'gcm': {'title': 'Title'},
                    'apns': {'msg': 'ApnsUserTaxi'},
                },
            },
        },
        {'user_id': 'user_taxi1', 'locale': 'ru'},
        {'user_id': 'user_taxi2', 'locale': 'ru'},
        {'user_id': 'user_uber', 'locale': 'en'},
        {'user_id': 'user_yango'},
    ]
    body = {
        'data': data,
        'confirm': True,
        'intent': 'crm',
        'recipients': users,
    }
    response = await taxi_ucommunications.post(
        'user/notification/bulk-push', json=body,
    )
    assert response.status_code == 200
