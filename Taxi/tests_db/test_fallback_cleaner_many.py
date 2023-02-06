import asyncio

import pytest


# Loads 1m of records in db, for manual run only
@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1,
    DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=False,
    DEVICENOTIFY_PGAAS_TIMEOUTS={
        '__default__': 250,
        'cleanup_expired_messages': 1000,
    },
)
async def test_clean_queue_1m(taxi_device_notify, pgsql, mockserver):
    @mockserver.json_handler('/fcm/send')
    def handler(request):
        return mockserver.make_response(
            '{"error": "something-happened"}', status=500,
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

    def insert_messages(count):
        print('### insert {} messages (begin)'.format(count))
        series = 'generate_series(1000001, 1000000+' + str(count) + ')'
        queries = [
            'BEGIN',
            # service:1
            'INSERT INTO devicenotify.services(service_id, name) '
            'VALUES(1, \'service:1\')',
            # 1m of drivers
            'INSERT INTO devicenotify.users(uid, updated)'
            '  SELECT \'dummy:\' || ' + series + ','
            '   current_timestamp;',
            # 1m of messages
            'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
            '  ttl, created, attempted, service_id, payload)'
            ' SELECT user_id, 5, current_timestamp - make_interval(secs => 1),'
            '  current_timestamp - make_interval(mins => 10),'
            '  current_timestamp, 1, \'{}\' FROM devicenotify.users',
            # and 1m recipients
            'INSERT INTO devicenotify.fallback_queue_users(queue_id, user_id) '
            ' SELECT user_id, user_id FROM devicenotify.users',
            'COMMIT',
        ]
        cursor = pgsql['devicenotify'].cursor()
        for sql in queries:
            cursor.execute(sql)
        print('### insert {} messages (end)'.format(count))
        return count

    assert get_counters() == [0, 0]
    inserted = insert_messages(1000000)
    prev_counters = get_counters()
    assert prev_counters[0] > (inserted - 1000)
    assert prev_counters[1] > (inserted - 1000)

    await asyncio.sleep(10)

    after_counters = get_counters()
    assert (prev_counters[0] - after_counters[0]) > 1000
    assert (prev_counters[1] - after_counters[1]) > 1000
    # check that there were no calls
    assert not handler.has_calls

    print('### prev={} after={}'.format(prev_counters, after_counters))
