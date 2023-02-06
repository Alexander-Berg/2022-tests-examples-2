import asyncio
import json

import pytest


def _get_counter(pgsql):
    cursor = pgsql['devicenotify'].cursor()
    cursor.execute('SELECT COUNT(1) FROM devicenotify.tokens')
    result = 0
    for row in cursor:
        result = row[0]
        break
    cursor.close()
    return result


async def _send(taxi_device_notify):
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
        'uids': ['driver:1', 'driver:2'],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }
    return await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )


@pytest.mark.pgsql(
    'devicenotify',
    queries=[
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES (1,\'driver:1\'), (2,\'driver:2\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES (1,\'fcm\',\'SOME-FCM-TOKEN-1\'), '
        '(2,\'fcm\',\'SOME-FCM-TOKEN-2\')',
    ],
)
async def test_send_tokens_bad(taxi_device_notify, mockserver, pgsql):
    @mockserver.json_handler('/fcm/send')
    def _handler(request):
        json_body = {
            'success': 0,
            'failure': 2,
            'results': [{'error': 'NotRegistered'}, {'error': 'AnotherError'}],
        }
        return mockserver.make_response(json.dumps(json_body), status=200)

    assert _get_counter(pgsql) == 2
    response = await _send(taxi_device_notify)
    assert response.status_code == 200
    assert response.json()['error'] == 'FCM error'
    for _ in range(10):
        if _get_counter(pgsql) == 0:
            break
        await asyncio.sleep(1)
    assert _get_counter(pgsql) == 0


@pytest.mark.pgsql(
    'devicenotify',
    queries=[
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES (1,\'driver:1\'), (2,\'driver:2\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES (1,\'fcm\',\'SOME-FCM-TOKEN-1\'), '
        '(2,\'fcm\',\'SOME-FCM-TOKEN-2\')',
    ],
)
async def test_send_tokens_partitial(taxi_device_notify, mockserver, pgsql):
    @mockserver.json_handler('/fcm/send')
    def _handler(request):
        json_body = {
            'success': 1,
            'failure': 1,
            'results': [{'error': 'NotRegistered'}, {'status': 'OK'}],
        }
        return mockserver.make_response(json.dumps(json_body), status=200)

    assert _get_counter(pgsql) == 2
    response = await _send(taxi_device_notify)
    assert response.status_code == 200
    assert response.json()['error'] == 'FCM partial'
    for _ in range(10):
        if _get_counter(pgsql) == 1:
            break
        await asyncio.sleep(1)
    assert _get_counter(pgsql) == 1
