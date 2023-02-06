import asyncio
import datetime
import json

import pytest


# pylint: disable=too-many-statements
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
    def time_to_str(tme):
        if tme is None:
            return 'null'
        return tme.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def print_log(text):
        print(
            'test_send_retries.py:',
            time_to_str(datetime.datetime.now()),
            text,
        )

    def print_queue():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT queue_id, created, attempted, event '
            'FROM devicenotify.fallback_queue',
        )
        count = 0
        for row in cursor:
            print_log(
                'queue_id={} created={} attempted={} event={}'.format(
                    row[0], time_to_str(row[1]), time_to_str(row[2]), row[3],
                ),
            )
            count += 1
        cursor.close()
        return count

    @mockserver.json_handler('/fcm/send')
    def handler(request):
        nonlocal retry_after
        if retry_after is None:
            print_log('### handler >> 200')
            return {
                'multicast_id': 6212382472385364523,
                'success': 1,
                'failure': 0,
                'canonical_ids': 0,
                'results': [
                    {'message_id': '0:2547475151911802%%41bd5c9637bd1c96'},
                ],
            }
        print_log('### handler >> 500')
        return mockserver.make_response(
            'some error text',
            status=500,
            headers={'Retry-After': retry_after},
        )

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
    print_log('calling /v1/send')
    print_queue()
    retry_after = 3
    response = await taxi_device_notify.post(
        'v1/send', params=params, headers=headers, data=json.dumps(data),
    )
    assert handler.has_calls
    handler.flush()
    assert response.status_code == 200
    assert response.json()['message'] == 'Pending'
    print_queue()

    print_log('waiting before the first retry')
    for _i in range(10):
        await asyncio.sleep(10)
        print_queue()
        if handler.has_calls:
            print_log('call received, exit from first loop')
            break
    print_log('expect the first retry (erroneous)')
    await handler.wait_call()
    print_queue()

    print_log('waiting before the second retry (6s max)')
    for _i in range(6):
        await asyncio.sleep(1)
        print_queue()
        if handler.has_calls:
            print_log('call received, exit from second loop')
            break
    print_log('expect the second retry (erroneous)')
    await handler.wait_call()
    print_queue()

    print_log('waiting before the third retry (6s max)')
    handler.flush()
    retry_after = None
    for _i in range(6):
        await asyncio.sleep(1)
        print_queue()
        if handler.has_calls:
            print_log('call received, exit from third loop')
            break
    print_log('expect the third retry (successful)')
    await handler.wait_call()
    print_queue()

    print_log('no more calls are expected')
    for _i in range(10):
        await asyncio.sleep(10)
        if handler.has_calls:
            print_log('unexpected call, exit from fourth loop')
            break
    assert not handler.has_calls
