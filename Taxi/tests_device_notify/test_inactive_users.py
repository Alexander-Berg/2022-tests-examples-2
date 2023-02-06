import asyncio

import pytest


@pytest.mark.config(DEVICENOTIFY_FCM_RETRIES=1)
async def test_drop_inactive_users(
        taxi_device_notify, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/iid/v1:batchRemove')
    def iid_batch_remove(request):
        return {'results': [{}]}

    @testpoint('expired_users:done')
    def expired_users_done(data_json):  # pylint: disable=unused-variable
        pass

    def get_counters():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'SELECT (SELECT COUNT(1) FROM devicenotify.users), '
            '(SELECT COUNT(1) FROM devicenotify.tokens), '
            '(SELECT COUNT(1) FROM devicenotify.topics)',
        )
        result = []
        for row in cursor:
            result = [row[0], row[1], row[2]]
            break
        cursor.close()
        return result

    def insert_users():
        cursor = pgsql['devicenotify'].cursor()
        commands = [
            # service
            'INSERT INTO devicenotify.services(service_id, name) '
            'VALUES(1,\'taximeter\')',
            # driver:1
            'INSERT INTO devicenotify.users(user_id, uid, updated) '
            'VALUES(1,\'driver:1\', current_timestamp)',
            'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
            'VALUES(1,\'fcm\',\'SOME-FCM-TOKEN-1\')',
            'INSERT INTO devicenotify.topics(user_id, service_id, topics) '
            'VALUES(1,1,\'{"russia","moscow"}\')',
            # driver:2
            'INSERT INTO devicenotify.users(user_id, uid, updated) '
            'VALUES(2,\'driver:2\','
            ' current_timestamp - make_interval(days => 90))',
            'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
            'VALUES(2,\'fcm\',\'SOME-FCM-TOKEN-2\')',
            'INSERT INTO devicenotify.topics(user_id, service_id, topics) '
            'VALUES(2,1,\'{"russia","moscow"}\')',
            # driver:3
            'INSERT INTO devicenotify.users(user_id, uid, updated) '
            'VALUES(3,\'driver:3\','
            ' current_timestamp - make_interval(days => 100))',
            'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
            'VALUES(3,\'fcm\',\'SOME-FCM-TOKEN-3\')',
            'INSERT INTO devicenotify.topics(user_id, service_id, topics) '
            'VALUES(3,1,\'{"russia","moscow"}\')',
        ]
        for sql in commands:
            cursor.execute(sql)

    def expire_users():
        cursor = pgsql['devicenotify'].cursor()
        commands = [
            # driver:1
            'UPDATE devicenotify.users SET updated '
            ' = current_timestamp - make_interval(days => 30)'
            ' WHERE user_id = 1',
            # driver:2
            'UPDATE devicenotify.users SET updated '
            ' = current_timestamp - make_interval(days => 90)'
            ' WHERE user_id = 2',
            # driver:3
            'UPDATE devicenotify.users SET updated '
            ' = current_timestamp - make_interval(days => 180)'
            ' WHERE user_id = 3',
        ]
        for sql in commands:
            cursor.execute(sql)

    assert get_counters() == [0, 0, 0]

    # insert into db 3 users
    insert_users()
    assert get_counters() == [3, 3, 3]
    # make 2 users expired
    expire_users()

    # we expect two unsubscribe calls
    await iid_batch_remove.wait_call()
    await iid_batch_remove.wait_call()
    # we should wait wile async tasks finish their work and update db
    # use testpoint after TAXICOMMON-67
    # expired_users_done.wait_call()
    for _i in range(10):
        await asyncio.sleep(1)
        if get_counters() == [1, 1, 1]:
            break

    # and two users should gone from db
    assert get_counters() == [1, 1, 1]
