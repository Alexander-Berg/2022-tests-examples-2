import asyncio

import pytest


@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1, DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=False,
)
async def test_send_from_queue(
        taxi_device_notify, pgsql, mockserver, fcm_service,
):
    preload_count_ = 1  # for db tests

    @mockserver.json_handler('/fcm/send')
    def handler(request):
        return fcm_service.on_send(request)
        # it's better return 500, we should not get more than one call
        # return Response('{"error": "service is down"}', status=500)

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

    def insert_prepare():
        queries = [
            # service:1
            'INSERT INTO devicenotify.services(service_id, name) '
            'VALUES(1, \'service:1\')',
        ]
        cursor = pgsql['devicenotify'].cursor()
        for sql in queries:
            cursor.execute(sql)

    def insert_load(count):
        print('### insert {} users/messages (begin)'.format(count))
        series = 'generate_series(1000001, 1000000+' + str(count) + ')'
        next_hour = 'current_timestamp + make_interval(hours => 1)'
        queries = [
            'BEGIN',
            # 1m of drivers
            'INSERT INTO devicenotify.users(user_id, uid, updated)'
            '  SELECT id, \'dummy:\' || id, current_timestamp'
            '  FROM (SELECT ' + series + ' AS id) AS series',
            # 1m of messages
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            '  ttl, created, attempted, service_id, payload)'
            ' SELECT user_id, 5, '
            + next_hour
            + ','
            + next_hour
            + ','
            + next_hour
            + ', 1, \'{}\''
            ' FROM devicenotify.users',
            # and 1m recipients
            'INSERT INTO devicenotify.fallback_queue_users(queue_id, user_id) '
            ' SELECT user_id, user_id FROM devicenotify.users',
            'COMMIT',
        ]
        cursor = pgsql['devicenotify'].cursor()
        for sql in queries:
            cursor.execute(sql)
        print('### insert {} users/messages (end)'.format(count))
        return count

    def insert_messages():
        # only non-expired messages are processed where:
        # coalesce(attempted, created) <= current_timestamp
        next_hour = 'current_timestamp + make_interval(hours => 1)'
        queries = [
            # driver:1
            'INSERT INTO devicenotify.users(user_id, uid) '
            'VALUES(1,\'driver:1\')',
            'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
            'VALUES(1,\'fcm\',\'SOME-FCM-TOKEN-1\')',
            # message:1 - delayed, until update_created
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            ' ttl, created, service_id, payload)'
            'VALUES(1, 5, ' + next_hour + ',' + next_hour + ', 1, \'{}\')',
            'INSERT INTO devicenotify.fallback_queue_users(queue_id, user_id) '
            'VALUES(1, 1)',
            # message:2 - delayed, until update_created
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            ' ttl, created, service_id, payload) '
            'VALUES(2, 5, ' + next_hour + ',' + next_hour + ', 1, \'{}\')',
            'INSERT INTO devicenotify.fallback_queue_users(queue_id, user_id) '
            'VALUES(2, 1)',
            # message:3 - delayed, until update_created
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            ' ttl, created, service_id, topics, payload) '
            'VALUES(3, 5, ' + next_hour + ',' + next_hour + ', 1, '
            ' \'{moscow.offline, russia.offline}\', \'{}\')',
        ]
        cursor = pgsql['devicenotify'].cursor()
        for sql in queries:
            cursor.execute(sql)

    def update_created():
        queries = [
            # message:1 - send
            'UPDATE devicenotify.fallback_queue SET created = '
            ' current_timestamp - make_interval(mins => 2)'
            ' WHERE queue_id = 1',
            # message:2 - don't send due to attempted in the future
            'UPDATE devicenotify.fallback_queue SET attempted = '
            ' current_timestamp + make_interval(mins => 2)'
            ' WHERE queue_id = 2',
            # message:3 - send
            'UPDATE devicenotify.fallback_queue SET created = '
            ' current_timestamp - make_interval(mins => 2)'
            ' WHERE queue_id = 3',
        ]
        cursor = pgsql['devicenotify'].cursor()
        for sql in queries:
            cursor.execute(sql)

    results = {}

    # service
    insert_prepare()

    assert get_counters() == [0, 0]

    # insert a lot of messages to queue to ensure there are no problems with db
    # we don't expect the processor will send them due to created time
    preload_count = insert_load(preload_count_)
    preload = get_counters()
    assert preload == [preload_count, preload_count]

    # insert messages into fallback_queue to let background task
    # FallbackQueue read them and push to our mock 'handler'
    insert_messages()
    assert get_counters() == [preload[0] + 3, preload[1] + 2]

    # update created time in db to allow process these messages
    update_created()

    # expect two calls
    call_args = (await handler.wait_call())['request'].json
    send_type = 'to' if 'to' in call_args else 'condition'
    results.setdefault(send_type, call_args[send_type])

    call_args = (await handler.wait_call())['request'].json
    send_type = 'to' if 'to' in call_args else 'condition'
    results.setdefault(send_type, call_args[send_type])

    assert results['to'] == 'SOME-FCM-TOKEN-1'
    assert (
        results['condition']
        == '\'moscow.offline\' in topics || \'russia.offline\' in topics'
    )

    # use testpoint after TAXICOMMON-67
    for _i in range(10):
        await asyncio.sleep(1)
        if get_counters() == [preload[0] + 1, preload[1] + 1]:
            break
        print('test_send_from_queue: wait for db update')
    assert get_counters() == [preload[0] + 1, preload[1] + 1]
    # check that there were no more calls
    assert not handler.has_calls
