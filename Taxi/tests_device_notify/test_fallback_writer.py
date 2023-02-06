import json

import pytest

from testsuite.utils import callinfo


@pytest.fixture(name='fcm_service_500')
def _fcm_service_500(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/fcm/send')
        def handler(request):
            return mockserver.make_response(
                '{"error": "service is down"}',
                status=500,
                headers={'Retry-After': '360'},
            )

        @staticmethod
        @mockserver.json_handler('/iid/v1:batchAdd')
        def _iid_batch_add(request):
            return {'results': [{}]}

    return Context()


@pytest.mark.pgsql(
    'devicenotify',
    queries=[
        # driver:1
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES(1,\'driver:1\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES(1,\'fcm\',\'SOME-FCM-TOKEN-1\')',
        # driver:1030
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES(2,\'driver:1030\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES(2,\'fcm\',\'SOME-FCM-TOKEN-1030\')',
    ],
)
@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1, DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=True,
)
async def test_queue_write_enabled(taxi_device_notify, pgsql, fcm_service_500):
    def get_counters():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT (SELECT COUNT(1) FROM devicenotify.fallback_queue), '
            '(SELECT COUNT(1) FROM devicenotify.fallback_queue_users)',
        )
        result = []
        for row in cursor:
            result = [row[0], row[1]]
            break
        cursor.close()
        return result

    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {'priority': 10, 'ttl': 30, 'service': k_service_name1}
    data = {
        'topics': [],
        'uids': [],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }

    assert fcm_service_500.handler.times_called == 0
    assert get_counters() == [0, 0]

    # fallback queue due to: use_queue=1
    params['event'] = 'test_send_fallback_async'
    params['use_queue'] = 1
    data['topics'] = ['moscow.offline', 'russia.offline']
    assert fcm_service_500.handler.times_called == 0
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['code'] == '200'
    assert json_response['message'] == 'Pending'
    assert len(json_response['queue']) == 1
    await fcm_service_500.handler.wait_call()
    assert get_counters() == [1, 0]

    # fallback queue due to: 500 from fcm server
    params['event'] = 'test_send_fallback_due_500'
    params['use_queue'] = 0
    data['topics'] = []
    data['uids'] = []
    for i in range(1050):
        data['uids'].append('driver:' + str(i))
    assert fcm_service_500.handler.times_called == 0
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    json_response = response.json()
    assert json_response['code'] == '200'
    assert json_response['message'] == 'Pending'
    assert len(json_response['queue']) == 2
    await fcm_service_500.handler.wait_call()
    assert get_counters() == [3, 2]
    # only two calls are expected (one per /v1/send)
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await fcm_service_500.handler.wait_call(timeout=1)


@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1, DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=False,
)
async def test_queue_disabled(taxi_device_notify, pgsql, fcm_service_500):
    def get_counters():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT (SELECT COUNT(1) FROM devicenotify.fallback_queue), '
            '(SELECT COUNT(1) FROM devicenotify.fallback_queue_users)',
        )
        result = []
        for row in cursor:
            result = [row[0], row[1]]
            break
        cursor.close()
        return result

    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {
        'priority': 10,
        'ttl': 30,
        'service': k_service_name1,
        'event': 'test_send_fallback_async',
        'use_queue': 1,
    }
    data = {
        'topics': ['moscow.offline', 'russia.offline'],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }

    assert get_counters() == [0, 0]

    # fallback queue disabled, use_queue=1 should be ignored
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 502
    assert get_counters() == [0, 0]
