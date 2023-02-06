import json
import random
import string

import pytest


@pytest.fixture(name='fcm_service_topics')
def _fcm_service_topics(mockserver, fcm_service):
    @mockserver.json_handler('/fcm/send')
    def _fcm_send(request):
        return fcm_service.on_send(request)


@pytest.mark.pgsql(
    'devicenotify',
    queries=[
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES(1,\'driver:1\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES(1,\'fcm\',\'SOME-FCM-TOKEN-1\')',
    ],
)
async def test_send_topics_rejects(taxi_device_notify, fcm_service_topics):
    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {
        'priority': 10,
        'ttl': 30,
        'event': '',
        'service': k_service_name1,
    }
    data = {
        'uids': [],
        'topics': [],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }

    # Long payload, reject is expected
    data['payload']['notification']['body'] = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(5000)
    )

    # by topics
    data['topics'] = [
        'moscow.online',
        'russia.online',
        'debug',
        'topic1',
        'topic2',
        'topic3',
    ]
    params['event'] = 'test_send_topics_reject'
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 400

    # by tokens
    data['topics'] = []
    data['uids'] = ['driver:1', 'driver:2', 'driver:x']
    params['event'] = 'test_send_tokens_reject'
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 400
