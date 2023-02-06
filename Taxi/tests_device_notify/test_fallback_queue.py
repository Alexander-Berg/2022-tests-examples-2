import pytest

from testsuite.utils import callinfo


@pytest.mark.config(
    DEVICENOTIFY_FCM_RETRIES=1,
    DEVICENOTIFY_FCM_TIMEOUT_MS=1500,
    DEVICENOTIFY_FALLBACK_QUEUE_ENABLED=False,
    DEVICENOTIFY_PGAAS_TIMEOUTS={
        '__default__': 250,
        'process_message_queue': 1500,
    },
)
async def test_send_from_queue(
        taxi_device_notify, pgsql, mockserver, fcm_service,
):
    message_count = 16  # note, on long queues timeout may occur in mock server
    token_message_index = 1
    topic_message_index = token_message_index + message_count
    total_message_count = 2 * message_count
    fcm_token = 'SOME-FCM-TOKEN-1'
    topic_1 = 'moscow.offline'
    topic_2 = 'russia.offline'

    @mockserver.json_handler('/fcm/send')
    def handler(request):
        return fcm_service.on_send(request)

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
        cursor = pgsql['devicenotify'].cursor()
        # service:1
        cursor.execute(
            'INSERT INTO devicenotify.services(service_id, name) '
            'VALUES(1, \'service:1\')',
        )
        # driver:1
        cursor.execute(
            'INSERT INTO devicenotify.users(user_id, uid) '
            'VALUES(1, \'driver:1\')',
        )
        cursor.execute(
            'INSERT INTO devicenotify.tokens(user_id, channel_type, token) '
            'VALUES(1, \'fcm\', \'' + fcm_token + '\')',
        )
        for i in range(message_count):
            # send via token
            idx = str(i + token_message_index)
            cursor.execute(
                'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
                ' ttl, created, attempted, service_id, payload)'
                'VALUES(' + idx + ', 5,'
                ' current_timestamp + make_interval(hours => 1),'
                ' current_timestamp,'
                ' current_timestamp + make_interval(mins => 10),'
                ' 1, \'{}\')',
            )
            cursor.execute(
                'INSERT INTO devicenotify.fallback_queue_users'
                ' (queue_id, user_id) VALUES(' + idx + ', 1)',
            )
            # send via topic
            idx = str(i + topic_message_index)
            cursor.execute(
                'INSERT INTO devicenotify.fallback_queue(queue_id, priority,'
                ' ttl, created, attempted, service_id, topics, payload)'
                'VALUES(' + idx + ', 5,'
                ' current_timestamp + make_interval(hours => 1),'
                ' current_timestamp,'
                ' current_timestamp + make_interval(mins => 10),'
                ' 1, \'{' + topic_1 + ', ' + topic_2 + '}\', \'{}\')',
            )

    def start_processing():
        cursor = pgsql['devicenotify'].cursor()
        cursor.execute(
            'UPDATE devicenotify.fallback_queue'
            ' SET attempted = current_timestamp - make_interval(mins => 1)',
        )

    results = {'to': 0, 'condition': 0}

    assert get_counters() == [0, 0]
    insert_messages()
    assert get_counters() == [total_message_count, message_count]

    start_processing()

    # total_message_count is larger than current kMaxRowsToReads value
    # messages will be processed by two iterations of FallbackQueue::

    for _i in range(total_message_count):
        call_args = (await handler.wait_call())['request'].json
        if 'to' in call_args:
            assert call_args['to'] == fcm_token
            results['to'] += 1
        elif 'condition' in call_args:
            assert call_args['condition'] == (
                '\''
                + topic_1
                + '\' in topics || \''
                + topic_2
                + '\' in topics'
            )
            results['condition'] += 1
        else:
            assert ('to' in call_args) or ('condition' in call_args)

    assert results['to'] == message_count
    assert results['condition'] == message_count

    # use testpoint after TAXICOMMON-67
    for _i in range(10):
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await handler.wait_call(timeout=1)
        if get_counters() == [0, 0]:
            break
        print('test_send_from_queue: wait for db update')
    assert get_counters() == [0, 0]
    # check that there were no more calls
    assert not handler.has_calls
