import json

import pytest

from tests_client_notify import helpers

X_IDEMPOTENCY_TOKEN = 'token'

SERVICES = {
    'taximeter': {'description': 'yandex pro', 'xiva_service': 'taximeter'},
}

INTENTS = {'taximeter': {'intent': {'description': ''}}}

REPACK_RULES = {
    'repack_rules': [
        {
            'enabled': True,
            'conditions': {'services': ['taximeter'], 'intents': ['intent']},
            'payload_repack': {
                'payload#concat-objects': [
                    {
                        'value#xget': {
                            'default-value': {},
                            'path': '/root/data',
                        },
                    },
                    {
                        'value#xget': {
                            'default-value': {},
                            'path': '/root/notification',
                        },
                    },
                ],
            },
        },
    ],
}


NOTIFICATION = {
    'text': 'text',
    'title': 'title',
    'sound': 'sound',
    'link': 'link',
}

DATA = {'order_id': 1234, 'flags': ['silent', 'important'], 'meta': 'metadata'}


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES=SERVICES,
    CLIENT_NOTIFY_INTENTS=INTENTS,
    CLIENT_NOTIFY_PAYLOAD_REPACK=REPACK_RULES,
)
async def test_all_in_one_bulk(taxi_client_notify, mockserver):
    users = [f'user{i}' for i in range(1, 8)]

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        assert dict(request.args) == {
            'service': 'taximeter',
            'ttl': '60',
            'event': 'intent',
        }
        assert request.json == {
            'recipients': users,
            'payload': dict(NOTIFICATION, **DATA),
        }

        # All known response forms of xiva batch handler
        response = {
            'results': [
                {'code': 200, 'body': 'OK'},
                [{'code': 200, 'body': 'OK'}, {'code': 200, 'body': 'OK'}],
                {'code': 200, 'body': {'duplicate': 5}},
                {'id': '9a4f5b5810c9fc3bac078', 'code': 200, 'body': 'OK'},
                {'code': 202, 'body': 'filtered'},
                {'code': 400, 'body': 'bad request'},
                {'code': 500, 'body': 'gateway error'},
            ],
        }

        return mockserver.make_response(
            json.dumps(response), 200, headers={'TransitID': 'bulk'},
        )

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert False

    response = await taxi_client_notify.post(
        'v2/bulk-push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'message_id',
            'intent': 'intent',
            'ttl': 60,
            'notification': NOTIFICATION,
            'data': DATA,
            'recipients': [{'client_id': user} for user in users],
        },
    )
    assert response.status_code == 200

    items = response.json()['notifications']
    assert len(items) == len(users)
    assert len(set(item['notification_id'] for item in items)) == 1


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES=SERVICES,
    CLIENT_NOTIFY_INTENTS=INTENTS,
    CLIENT_NOTIFY_PAYLOAD_REPACK=REPACK_RULES,
)
async def test_one_by_one_bulk(taxi_client_notify, mockserver):
    expected_user_payload = {
        'user1': {'payload': dict(NOTIFICATION, **DATA)},
        'user2': {
            'payload': dict(NOTIFICATION, **DATA),
            'subscriptions': [{'device': ['did2']}],
        },
        'user3': {
            'payload': dict(NOTIFICATION, **DATA),
            'subscriptions': [{'uuid': ['aid3']}],
        },
        'user4': {
            'payload': {
                'text': 'user4 text',
                'title': 'title',
                'sound': 'sound',
                'link': 'link',
                'order_id': 888,
                'personal_data': ['hello'],
                'flags': ['silent', 'important'],
                'meta': 'metadata',
            },
        },
        'user5': {
            'payload': dict(
                {
                    'text': 'user5 text',
                    'title': 'user5 title',
                    'sound': 'user5 sound',
                    'link': 'user5 link',
                },
                **DATA,
            ),
        },
    }

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        assert False

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        user = request.args['user']
        assert request.json == expected_user_payload[user]

        return mockserver.make_response(
            'OK', 200, headers={'TransitID': 'transit_id'},
        )

    response = await taxi_client_notify.post(
        'v2/bulk-push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'message_id',
            'intent': 'intent',
            'ttl': 60,
            'notification': NOTIFICATION,
            'data': DATA,
            'recipients': [
                {'client_id': 'user1'},
                {'client_id': 'user2', 'device_id': 'did2'},
                {'client_id': 'user3', 'app_install_id': 'aid3'},
                {
                    'client_id': 'user4',
                    'notification': {'text': 'user4 text'},
                    'data': {'order_id': 888, 'personal_data': ['hello']},
                },
                {
                    'client_id': 'user5',
                    'notification': {
                        'text': 'user5 text',
                        'title': 'user5 title',
                        'sound': 'user5 sound',
                        'link': 'user5 link',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200

    items = response.json()['notifications']
    assert len(items) == 5
    assert len(set(item['notification_id'] for item in items)) == 3


@helpers.TRANSLATIONS
@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES=SERVICES,
    CLIENT_NOTIFY_INTENTS=INTENTS,
    CLIENT_NOTIFY_PAYLOAD_REPACK=REPACK_RULES,
)
async def test_localization(taxi_client_notify, mockserver):
    expected_user_payload = {
        'user1': {'payload': {'text': '100 dollars.'}},
        'user2': {'payload': {'text': '100 kzt.'}},
        'user3': {'payload': {'text': '500 руб.'}},
    }

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        assert False

    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        user = request.args['user']
        assert request.json == expected_user_payload[user]

        return mockserver.make_response(
            'OK', 200, headers={'TransitID': 'transit_id'},
        )

    response = await taxi_client_notify.post(
        'v2/bulk-push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'taximeter',
            'message_id': 'message_id',
            'intent': 'intent',
            'locale': 'en',
            'ttl': 60,
            'notification': {
                'text': {
                    'key': 'key1',
                    'keyset': 'notify',
                    'params': {'cost': 100},
                },
            },
            'recipients': [
                {'client_id': 'user1'},
                {'client_id': 'user2', 'locale': 'kk'},
                {
                    'client_id': 'user3',
                    'locale': 'ru',
                    'notification': {
                        'text': {
                            'key': 'key1',
                            'keyset': 'notify',
                            'params': {'cost': 500},
                        },
                    },
                },
            ],
        },
    )
    assert response.status_code == 200

    items = response.json()['notifications']
    assert len(items) == 3
