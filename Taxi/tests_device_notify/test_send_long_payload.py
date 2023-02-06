import json
import random
import string

import pytest


@pytest.mark.pgsql(
    'devicenotify',
    queries=[
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES (1,\'driver:1\'), (2,\'driver:2\'),'
        '       (3,\'driver:3\'), (4,\'driver:4\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES (1,\'fcm\',\'SOME-LOOOOOOOOOOOOOOOOOOOOOOOONG-FCM-TOKEN-1\'),'
        '       (2,\'fcm\',\'SOME-LOOOOOOOOOOOOOOOOOOOOO00ONG-FCM-TOKEN-2\'),'
        '       (3,\'fcm\',\'SOME-LOOOOOOOOOOOOOOOOOOOOOOOONG-FCM-TOKEN-3\'),'
        '       (4,\'fcm\',\'SOME-LOOOOOOOOOOOOOOOOOOOOO00ONG-FCM-TOKEN-4\')',
    ],
)
async def test_send_long_payload(taxi_device_notify, mockserver):
    @mockserver.json_handler('/fcm/send')
    def fcm_send(request):
        data = request.get_data()
        assert len(data) <= 4096
        data = json.loads(data)
        field = 'registration_ids'
        success = len(data[field]) if field in data else 1
        return {'success': success, 'failure': 0, 'message_id': 218}

    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {
        'priority': 10,
        'ttl': 30,
        'event': 'test_long_payload',
        'use_queue': 0,
        'service': k_service_name1,
    }
    data = {
        'uids': ['driver:1', 'driver:2', 'driver:3', 'driver:4'],
        'payload': {
            'priority': 'high',
            'notification': {'title': 'Test title'},
        },
    }
    # +1(4), +2(3,1), +2(2,2), +4(1,1,1,1)
    for size, called in [(3800, 1), (3850, 3), (3900, 5), (3950, 9)]:
        data['payload']['notification']['body'] = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(size)
        )

        # Long payload with tokens
        response = await taxi_device_notify.post(
            'v1/send', params=params, headers=headers, data=json.dumps(data),
        )
        assert response.status_code == 200
        assert response.json() == {'code': '200', 'message': 'OK'}
        assert fcm_send.times_called == called

    # Too large payload
    data['payload']['notification']['body'] = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(4020)
    )
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 400

    # Topics
    data['uids'] = []
    data['topics'] = [
        'looooooooooooooooooooooooong_topic1',
        'looooooooooooooooooooooooong_topic2',
        'looooooooooooooooooooooooong_topic3',
        'looooooooooooooooooooooooong_topic4',
    ]

    # +1(4), +2(3,1), +2(2,2), +4(1,1,1,1)
    for size, called in [(3800, 10), (3850, 12), (3900, 14), (3950, 18)]:
        data['payload']['notification']['body'] = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(size)
        )

        # Long payload with topics
        response = await taxi_device_notify.post(
            'v1/send', params=params, headers=headers, data=json.dumps(data),
        )
        assert response.status_code == 200
        assert response.json() == {'code': '200', 'message': 'OK'}
        assert fcm_send.times_called == called

    # Too large payload
    data['payload']['notification']['body'] = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(4020)
    )
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 400
