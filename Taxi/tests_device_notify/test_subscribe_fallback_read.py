import asyncio
import json

# pylint: disable=R0915


async def test_subscribe_fallback_read(
        taxi_device_notify, pgsql, mockserver, fcm_service,
):
    fail_reg_request = True

    @mockserver.json_handler('/iid/v1:batchAdd')
    def _iid_batch_add(request):
        # print("### batchAdd", request)
        if fail_reg_request:
            return mockserver.make_response(
                '{"error": "something-happened"}', status=500,
            )
        return fcm_service.on_register(request)

    @mockserver.json_handler('/iid/v1:batchRemove')
    def _iid_batch_remove(request):
        # print("### batchRemove", request)
        if fail_reg_request:
            return mockserver.make_response(
                '{"error": "something-happened"}', status=500,
            )
        return fcm_service.on_register(request)

    # row counters for: users, tokens, topics, subscribe_queue
    def get_counters():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT '
            '(SELECT COUNT(1) FROM devicenotify.users), '
            '(SELECT COUNT(1) FROM devicenotify.tokens), '
            '(SELECT COUNT(1) FROM devicenotify.topics), '
            '(SELECT COUNT(1) FROM devicenotify.subscribe_queue) ',
        )
        result = 0
        for row in cursor:
            result = [row[0], row[1], row[2], row[3]]
            break
        cursor.close()
        return result

    def get_queue():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT action, token, topic '
            ' FROM devicenotify.subscribe_queue'
            ' ORDER BY id',
        )
        result = []
        for row in cursor:
            result.append(row[0] + '/' + row[1] + '/' + row[2])
        return result

    def move_to_past():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'UPDATE devicenotify.subscribe_queue'
            ' SET updated = current_timestamp - make_interval(mins => 10)',
        )

    k_api_key_header = 'X-YaTaxi-API-Key'
    # Keys, initialized by secdist_vars.yaml
    k_api_key1 = '2345'
    k_service_name1 = 'taximeter'
    # Few tokens
    k_fcm_token1 = 'fcm:token:1'
    # Dummy drivers
    k_user1 = 'driver:1'

    headers = {k_api_key_header: k_api_key1}
    params = {'uid': k_user1, 'service': k_service_name1, 'event': '_'}

    data = {'channels': [{'type': 'fcm', 'token': k_fcm_token1}]}

    assert get_counters() == [0, 0, 0, 0]
    assert get_queue() == []

    params['event'] = 'fallback-write-1'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'OK'}
    assert get_counters() == [1, 1, 0, 0]
    assert get_queue() == []

    data = {'topics': ['moscow.online', 'russia.online']}
    params['event'] = 'fallback-write-2'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    # FCM failed here, all requests go to the queue
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'Pending'}
    assert get_counters() == [1, 1, 1, 2]
    assert get_queue() == [
        'register/fcm:token:1/moscow.online',
        'register/fcm:token:1/russia.online',
    ]

    data = {'topics': ['moscow.offline', 'russia.online']}
    params['event'] = 'fallback-write-3'
    response = await taxi_device_notify.post(
        'v1/subscribe', params=params, headers=headers, data=json.dumps(data),
    )
    # FCM failed here, all requests go to the queue
    assert response.status_code == 200
    assert response.json() == {'code': '200', 'message': 'Pending'}
    assert get_counters() == [1, 1, 1, 4]
    assert get_queue() == [
        'register/fcm:token:1/russia.online',  # left from first call
        'revoke/fcm:token:1/moscow.online',  # revoked from first call
        'register/fcm:token:1/moscow.offline',  # new call
        'register/fcm:token:1/russia.online',
    ]  # new call

    # let FCM return "OK"
    fail_reg_request = False

    # let worker process messages
    # print("### move_to_past")
    move_to_past()

    # and wait for calls
    # use testpoint after TAXICOMMON-67
    for _i in range(10):
        await asyncio.sleep(1)
        if get_counters() == [1, 1, 1, 0]:
            break
        print('test_subscribe_fallback_read: wait for db update')
    assert get_counters() == [1, 1, 1, 0]
