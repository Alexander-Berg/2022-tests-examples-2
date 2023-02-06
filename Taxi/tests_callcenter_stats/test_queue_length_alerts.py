import time
import urllib.parse

import pytest


@pytest.mark.skip('too many flaps')
@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_crit.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': True,  # Enable periodic checks
        'check_interval': 100,  # Reduce check interval
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': 'test {status} on {queue}: {length} test',
            'telegram_msg_parse_mode': 'markdown',
        },
    },
)
# Let's test that component will periodically check the state and
# send notifications.
# Plus 'chat_id' parameter
async def test_enabled(mockserver, taxi_callcenter_stats):
    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        q_s = urllib.parse.parse_qs(request.query_string.decode())
        assert q_s['chat_id'] == ['test_chat_id']
        assert q_s['parse_mode'] == ['markdown']
        return mockserver.make_response(json={}, status=200)

    # force reload config'a because there is no call to the service API
    await taxi_callcenter_stats.invalidate_caches()

    await telegram_api.wait_call(1)


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_crit.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,  # Disable periodic checks
        'check_interval': 330,  # Reduce check interval
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}: {length}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
# Let's test that config parameter 'enabled' can turn off
# periodical checks and notifications.
async def test_disabled(mockserver, taxi_callcenter_stats):
    # force reload config'a because there is no call to the service API
    await taxi_callcenter_stats.invalidate_caches()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        return mockserver.make_response(json={}, status=200)

    time.sleep(1)
    assert telegram_api.times_called == 0


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_levels.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}: {length}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
# Let's test right 'warn_threshold' and 'crit_threshold' interpretation
async def test_levels(mockserver, taxi_callcenter_stats):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        text = request.json['text']

        assert text.find('ok_cc') == -1
        assert text.find('WARN on warn_cc: 3') != -1
        assert text.find('CRIT on crit_cc: 6') != -1
        return mockserver.make_response(json={}, status=200)

    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.has_calls
    assert telegram_api.times_called == 1


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_levels.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}: {length}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
# Let's test that we will NOT notify if there is no changes
async def test_no_change(mockserver, taxi_callcenter_stats):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        text = request.json['text']

        if state == 0:
            # no alert in ok zone
            assert text.find('ok_cc') == -1
            assert text.find('WARN on warn_cc: 3') != -1
            assert text.find('CRIT on crit_cc: 6') != -1

        # nothing changed - no alert
        assert state != 1

        return mockserver.make_response(json={}, status=200)

    state = 0
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 1

    state = 1  # nothing changed - no alert
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 1


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_levels.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}: {length}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
# Let's test if some queue changes state internally in zone
# or from one zone to another.
async def test_state_change(mockserver, taxi_callcenter_stats, pgsql, load):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        text = request.json['text']

        if state == 0:
            # no alert in ok zone
            assert text.find('ok_cc') == -1
            assert text.find('WARN on warn_cc: 3') != -1
            assert text.find('CRIT on crit_cc: 6') != -1

        if state == 1:
            # no alert in ok zone
            assert text.find('ok_cc') == -1
            # warn_cc switched to CRIT zone
            assert text.find('CRIT on warn_cc: 5') != -1
            # no alert in CRIT zone
            assert text.find('crit_cc') == -1

        if state == 2:
            # no alert in ok zone
            assert text.find('ok_cc') == -1
            # warn_cc switched to OK zone
            assert text.find('OK on warn_cc: 0') != -1
            # crit_cc switched to OK zone
            assert text.find('OK on crit_cc: 0') != -1

        return mockserver.make_response(json={}, status=200)

    state = 0
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 1

    # All queues change their values
    state = 1
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(load('test_state_change.sql'))
    cursor.close()
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 2

    # Remove all
    state = 2
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('DELETE FROM callcenter_stats.call_status')
    cursor.close()
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 3


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_levels.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': True,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}: {length}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
# Let's test that 'notify_within_status' parameter will
# force to notify any changes
async def test_notify_within_status(
        mockserver, taxi_callcenter_stats, pgsql, load,
):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        text = request.json['text']

        if state == 0:
            # no alert in ok zone
            assert text.find('ok_cc') == -1
            assert text.find('WARN on warn_cc: 3') != -1
            assert text.find('CRIT on crit_cc: 6') != -1

        if state == 1:
            # no alert in ok zone
            assert text.find('ok_cc') == -1
            # warn_cc switched to CRIT zone
            assert text.find('CRIT on warn_cc: 5') != -1
            # notify_within_status force to alert changes in CRIT zone
            assert text.find('CRIT on crit_cc: 7') != -1

        return mockserver.make_response(json={}, status=200)

    state = 0
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 1

    state = 1
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(load('test_state_change.sql'))
    cursor.close()
    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 2


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_queue_state_delay.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 60000,  # 1 minute
        'warn_threshold': 1,
        'crit_threshold': 3,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}: {length}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
# Let's test that calls which in 'queued' state are less then
# 'queue_state_delay' time will not be counted
async def test_queue_state_delay(mockserver, taxi_callcenter_stats):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        text = request.json['text']
        # Only two calls will be counted -> only WARN status is expected
        assert text.find('WARN on delay_cc: 2') != -1
        return mockserver.make_response(json={}, status=200)

    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.has_calls
    assert telegram_api.times_called == 1


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_crit.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1,
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': 'test {status} on {queue}: {length} test',
            'telegram_msg_parse_mode': 'markdown',
        },
    },
)
async def test_metrics(
        taxi_callcenter_stats,
        taxi_callcenter_stats_monitor,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        return mockserver.make_response(json={}, status=200)

    await taxi_callcenter_stats.invalidate_caches()
    await taxi_callcenter_stats.enable_testpoints()

    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.times_called == 1

    response = await taxi_callcenter_stats_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['queue-length-alerts']
    assert metrics == load_json('expected_metrics.json')


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': (
                '{status} on {queue}: '
                'l={length} '
                'p={paused} '
                'c={connected} '
                't={talking} '
                'po={postcall} '
                'w={waiting} '
                'b={busy}'
            ),
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_',
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
)
@pytest.mark.parametrize(
    'use_new_data',
    [
        pytest.param(
            True,
            marks=[pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=True)],
        ),
        pytest.param(
            False,
            marks=[pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=False)],
        ),
    ],
)
@pytest.mark.parametrize(
    ['expected_text'],
    (
        pytest.param(
            'CRIT on crit_cc: l=6 p=1 c=5 t=1 po=0 w=2 b=2\n'
            'WARN on warn_cc: l=3 p=0 c=4 t=1 po=0 w=2 b=1',
            id='no postcall',
            marks=pytest.mark.pgsql(
                'callcenter_stats', files=['test_agent_stats.sql'],
            ),
        ),
        pytest.param(
            'CRIT on crit_cc: l=6 p=1 c=5 t=1 po=0 w=2 b=2\n'
            'WARN on warn_cc: l=3 p=0 c=4 t=1 po=1 w=1 b=1',
            id='with postcall',
            marks=pytest.mark.pgsql(
                'callcenter_stats', files=['test_agent_stats_postcall.sql'],
            ),
        ),
    ),
)
# Let's test agent stats
async def test_agent_stats(
        mockserver, taxi_callcenter_stats, expected_text, use_new_data,
):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    text = ''

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        nonlocal text
        text = request.json['text']
        return mockserver.make_response(json={}, status=200)

    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.has_calls
    assert telegram_api.times_called == 1
    assert text == expected_text


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_levels.sql'])
@pytest.mark.parametrize(
    ['expected_text'],
    (
        pytest.param(
            'CRIT on crit_cc: l=6 mt=5.5\nWARN on warn_cc: l=3 mt=1.0',
            id='wait times',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
                    'enabled': False,
                    'check_interval': 1000,
                    'queued_state_delay': 0,
                    'warn_threshold': 3,
                    'crit_threshold': 5,
                    'notify_within_status': False,
                },
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
                    '__default__': {
                        'telegram_chat_id': 'test_chat_id',
                        'telegram_msg_template': (
                            '{status} on {queue}: '
                            'l={length} '
                            'mt={queue_max_time:.1f}'
                        ),
                        'telegram_msg_parse_mode': 'plaintext',
                    },
                },
            ),
        ),
    ),
)
# Let's test agent stats
async def test_queue_max_time(
        mockserver, taxi_callcenter_stats, expected_text,
):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    text = ''

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        nonlocal text
        text = request.json['text']
        return mockserver.make_response(json={}, status=200)

    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.has_calls
    assert telegram_api.times_called == 1
    assert text == expected_text


@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_stats', files=['test_levels.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_SETTINGS={
        'enabled': False,
        'check_interval': 1000,
        'queued_state_delay': 0,
        'warn_threshold': 3,
        'crit_threshold': 5,
        'notify_within_status': False,
    },
    CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_SETTINGS={
        '__default__': {
            'telegram_chat_id': 'default_chat_id',
            'telegram_msg_template': '{status} on {queue}',
            'telegram_msg_parse_mode': 'plaintext',
        },
        'test_chat': {
            'telegram_chat_id': 'test_chat_id',
            'telegram_msg_template': '{status} on {queue}',
            'telegram_msg_parse_mode': 'plaintext',
        },
        'crit_chat': {
            'telegram_chat_id': 'crit_chat_id',
            'telegram_msg_template': '{status} on {queue}',
            'telegram_msg_parse_mode': 'plaintext',
        },
        'warn_chat': {
            'telegram_chat_id': 'warn_chat_id',
            'telegram_msg_template': '{status} on {queue}',
            'telegram_msg_parse_mode': 'plaintext',
        },
        '400_chat': {
            'telegram_chat_id': '400_chat_id',
            'telegram_msg_template': '{status} on {queue}',
            'telegram_msg_parse_mode': 'plaintext',
        },
    },
)
@pytest.mark.parametrize(
    ['expected_texts'],
    (
        pytest.param(
            ['default_chat_id = CRIT on crit_cc\nWARN on warn_cc'],
            id='default channel',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': '__default__',
                },
            ),
        ),
        pytest.param(
            ['test_chat_id = CRIT on crit_cc\nWARN on warn_cc'],
            id='custom channel',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': 'test_chat',
                },
            ),
        ),
        pytest.param(
            ['default_chat_id = CRIT on crit_cc\nWARN on warn_cc'],
            id='incorrect channel',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': 'incorrect_chat',
                },
            ),
        ),
        pytest.param(
            ['crit_chat_id = CRIT on crit_cc\nWARN on warn_cc'],
            id='one channel',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': 'test_chat',
                    'crit': 'crit_chat',
                    'wa': 'crit_chat',
                },
            ),
        ),
        pytest.param(
            [
                'crit_chat_id = CRIT on crit_cc',
                'test_chat_id = WARN on warn_cc',
            ],
            id='different channels',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': 'test_chat',
                    'crit': 'crit_chat',
                },
            ),
        ),
        pytest.param(
            [
                'crit_chat_id = CRIT on crit_cc',
                'default_chat_id = WARN on warn_cc',
            ],
            id='different channels',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': 'default_chat',
                    'cr': 'warn_chat',
                    'crit': 'crit_chat',
                    'c': 'test_chat',
                },
            ),
        ),
        pytest.param(
            ['crit_chat_id = CRIT on crit_cc'],
            id='error on channel',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QUEUE_LENGTH_ALERT_CHANNELS_MAP={
                    '__default__': '400_chat',
                    'crit': 'crit_chat',
                },
            ),
        ),
    ),
)
async def test_multi_channels(
        mockserver, taxi_callcenter_stats, expected_texts,
):

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()

    texts = set()

    @mockserver.json_handler('/telegram/bot123/sendMessage')
    def telegram_api(request):
        text = request.json['text']
        chat_id = request.json['chat_id']
        if chat_id == '400_chat_id':
            return mockserver.make_response(json={}, status=400)
        nonlocal texts
        texts.add(chat_id + ' = ' + text)
        return mockserver.make_response(json={}, status=200)

    response = await taxi_callcenter_stats.post(
        '/tests/queue_length_alerts/check_and_notify',
    )
    assert response.status_code == 200
    assert telegram_api.has_calls
    assert texts == set(expected_texts)
