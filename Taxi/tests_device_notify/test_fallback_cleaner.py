import asyncio

import pytest


@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1, DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=False,
)
async def test_clean_queue(taxi_device_notify, pgsql, mockserver, fcm_service):
    @mockserver.json_handler('/fcm/send')
    def handler(request):
        return mockserver.make_response(
            'some error text', status=500, headers={'Retry-After': 60},
        )

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

    def insert_messages():
        queries = [
            # service:1
            'INSERT INTO devicenotify.services(service_id, name) '
            'VALUES(1, \'service:1\')',
            # driver:1
            'INSERT INTO devicenotify.users(user_id, uid) '
            'VALUES(1,\'driver:1\')',
            'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
            'VALUES(1,\'fcm\',\'SOME-FCM-TOKEN-1\')',
            # message:1 - send
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            ' ttl, created, attempted, service_id, payload)'
            'VALUES(1, 5, current_timestamp + make_interval(hours => 1),'
            ' current_timestamp - make_interval(mins => 10),'
            ' current_timestamp, 1, \'{}\')',
            'INSERT INTO devicenotify.fallback_queue_users(queue_id, user_id) '
            'VALUES(1, 1)',
            # message:2 - don't send due to attempted+10m
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            ' ttl, created, attempted, service_id, payload) '
            'VALUES(2, 5, current_timestamp + make_interval(hours => 1),'
            ' current_timestamp - make_interval(mins => 10),'
            ' current_timestamp + make_interval(mins => 10), 1, \'{}\')',
            'INSERT INTO devicenotify.fallback_queue_users(queue_id, user_id) '
            'VALUES(2, 1)',
            # message:3 - send
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            ' ttl, created, attempted, service_id, topics, payload) '
            'VALUES(3, 5, current_timestamp + make_interval(hours => 1),'
            ' current_timestamp - make_interval(mins => 10),'
            ' current_timestamp, 1, '
            ' \'{moscow.offline, russia.offline}\', \'{}\')',
        ]
        cursor = pgsql['devicenotify'].cursor()
        for sql in queries:
            cursor.execute(sql)

    def deprecate_messages():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'UPDATE devicenotify.fallback_queue'
            ' SET ttl = current_timestamp - make_interval(secs => 1)'
            ' WHERE queue_id in (1, 3)',
        )

    assert get_counters() == [0, 0]
    insert_messages()
    assert get_counters() == [3, 2]

    deprecate_messages()

    # use testpoint after TAXICOMMON-67
    for _i in range(10):
        await asyncio.sleep(1)
        if get_counters() == [1, 1]:
            break
        print('test_send_from_queue: wait for db update')
    assert get_counters() == [1, 1]
    # check that there were no calls
    assert not handler.has_calls
