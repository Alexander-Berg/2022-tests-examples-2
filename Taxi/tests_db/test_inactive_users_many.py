import asyncio

import pytest


# Loads 1m of records in db, for manual run only
@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1,
    DEVICENOTIFY_PGAAS_TIMEOUTS={
        '__default__': 250,
        'cleanup_inactive_users': 1000,
    },
)
async def test_drop_inactive_users_1m(taxi_device_notify, pgsql, mockserver):
    @mockserver.json_handler('/iid/v1:batchRemove')
    def _iid_batch_remove(request):
        return {'results': [{}]}

    def get_counters():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute('SELECT COUNT(1) FROM devicenotify.users')
        result = []
        for row in cursor:
            result = row[0]
            break
        cursor.close()
        return result

    def insert_users(count):
        print('### insert {} users (begin)'.format(count))
        series = 'generate_series(1000001, 1000000+' + str(count) + ')'
        cursor = pgsql['devicenotify'].cursor()
        commands = [
            # one million of 'dummy:xxx' users
            'BEGIN',
            # service:1
            'INSERT INTO devicenotify.services(service_id, name)'
            '  VALUES(1, \'service:1\')',
            # 1m of drivers
            'INSERT INTO devicenotify.users(uid, updated)'
            '  SELECT \'dummy:\' || ' + series + ','
            '  current_timestamp - make_interval(days => 100);',
            # 1m of tokens
            'INSERT INTO devicenotify.tokens'
            '(user_id, channel_type, token, updated)'
            '  SELECT user_id, \'fcm\', \'token:\' || uid, updated'
            '    FROM devicenotify.users',
            # don't insert topics - too many requests to mock-server
            'COMMIT',
        ]
        for sql in commands:
            cursor.execute(sql)
        print('### insert {} users (end)'.format(count))
        return count

    assert get_counters() == 0

    # insert into db a lot of expired users
    inserted = insert_users(1000000)
    prev_counters = get_counters()
    assert prev_counters > (inserted - 1000)

    await asyncio.sleep(10)

    after_counters = get_counters()
    assert after_counters < (prev_counters - 2000)

    print('### prev={} after={}'.format(prev_counters, after_counters))
