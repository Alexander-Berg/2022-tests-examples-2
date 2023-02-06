import json
import random
import string

import pytest


@pytest.fixture(name='fcm_service_tokens')
def _fcm_service_tokens(mockserver, fcm_service):
    @mockserver.json_handler('/fcm/send')
    def _send_by_tokens(request):
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
async def test_send_tokens(taxi_device_notify, fcm_service_tokens):
    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {
        'priority': 10,
        'ttl': 30,
        'event': 'test_send_tokens',
        'service': k_service_name1,
    }
    data = {
        'uids': ['driver:1', 'driver:2', 'driver:x'],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }

    # Normal send to token
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}

    # Long payload but fit in limits
    params['event'] = 'test_send_tokens_long'
    data['payload']['notification']['body'] = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(3000)
    )
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}

    # Unknown uid in a single push
    data['uids'] = ['driver:x']
    params['event'] = 'test_send_unknown_uid'
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json()['error'] == 'Unknown uid'
    assert response.json()['message'] == 'driver:x'

    # Unknown uid in a single async push
    data['uids'] = ['driver:x']
    params['event'] = 'test_send_unknown_uid'
    params['use_queue'] = True
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json()['error'] == 'Unknown uid'
    assert response.json()['message'] == 'driver:x'
