import asyncio
import json

import pytest


@pytest.mark.pgsql(
    'devicenotify',
    queries=[
        'INSERT INTO devicenotify.users(user_id, uid) '
        'VALUES(1,\'driver:1\')',
        'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
        'VALUES(1,\'fcm\',\'SOME-FCM-TOKEN-1\')',
    ],
)
@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1, DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=True,
)
async def test_send_with_retries(taxi_device_notify, mockserver, pgsql):
    @mockserver.json_handler('/fcm/send')
    def handler(request):
        nonlocal retry_after
        if retry_after is None:
            return {
                'multicast_id': 6212382472385364523,
                'success': 1,
                'failure': 0,
                'canonical_ids': 0,
                'results': [
                    {'message_id': '0:2547475151911802%%' '41bd5c9637bd1c96'},
                ],
            }
        return mockserver.make_response(
            'some error text',
            status=500,
            headers={'Retry-After': str(retry_after)},
        )

    def get_queue_len():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute('SELECT count(*) FROM devicenotify.fallback_queue')
        count = 0
        for row in cursor:
            count = row[0]
        cursor.close()
        return count

    k_api_key_header = 'X-YaTaxi-API-Key'
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'

    headers = {k_api_key_header: k_api_key1}
    params = {
        'priority': 10,
        'ttl': 300,
        'event': 'test_send_retries',
        'service': k_service_name1,
    }
    data = {
        'uids': ['driver:1'],
        'payload': {
            'priority': 'high',
            'notification': {
                'title': 'sample title',
                'body': 'sample notification',
            },
        },
    }

    # return "Retry-After"
    assert get_queue_len() == 0
    retry_after = 3
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert handler.has_calls
    handler.flush()
    assert response.status_code == 200
    assert response.json()['message'] == 'Pending'
    assert get_queue_len() == 1

    # expect the first retry (still erroneous)
    await handler.wait_call()
    assert get_queue_len() == 1

    # expect the second retry (still erroneous)
    await handler.wait_call()
    assert get_queue_len() == 1

    # expect the third retry (successful)
    handler.flush()
    retry_after = None
    await handler.wait_call()
    # row is deleted after our mock process a call
    # use testpoint after TAXICOMMON-67
    for _i in range(10):
        await asyncio.sleep(1)
        if get_queue_len() == 0:
            break
    assert get_queue_len() == 0

    # no more calls are expected
    assert not handler.has_calls
