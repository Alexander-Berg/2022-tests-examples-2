import json
import logging

import pytest

logger = logging.getLogger(__name__)

EVENT_1 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600901","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446012","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_2 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600902","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446013","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_3 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600903","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446014","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_4 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600904","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446015","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_5 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600905","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446016","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_6 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600906","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446017","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_7 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600907","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446018","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_8 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600908","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446019","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa
EVENT_9 = '{"NODE":"YTC-TAXI-MAR-QPROC1","PARTITION":"TAXI1","DATE":1588774115,"CALLID":"taxi-mar-qproc1.yndx.net-1588774115.600909","QUEUENAME":"krasnodar_disp_cc","AGENT":null,"ACTION":"META","DATA1":"0","DATA2":"0002030101-0000065536-1588774110-0002446020","DATA3":"X-CC-OriginalDN","DATA4":"+73812955555","DATA5":null,"DATA6":null,"DATA7":null,"DATA8":null,"OTHER":null}'  # noqa

EVENTS = [EVENT_1, EVENT_2, EVENT_3, EVENT_4, EVENT_5, EVENT_6]
LONG_EVENTS = [
    EVENT_1,
    EVENT_2,
    EVENT_3,
    EVENT_4,
    EVENT_5,
    EVENT_6,
    EVENT_7,
    EVENT_8,
    EVENT_9,
]


@pytest.mark.parametrize(
    ('events', 'flushes', 'events_processed'),
    ((EVENTS, 2, 6), (LONG_EVENTS, 3, 9)),
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 4,  # important param
        'actions_whitelist': [
            'ADDMEMBER',
            'ABANDON',
            'ATTENDEDTRANSFER',
            'BLINDTRANSFER',
            'COMPLETEAGENT',
            'COMPLETECALLER',
            'CONNECT',
            'ENTERQUEUE',
            'META',
            'REMOVEMEMBER',
            'RINGCANCELED',
            'RINGNOANSWER',
        ],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.6,
            'max_random_delay': 20,
            'max_possible_delay': 1000,
        },
    },
)
async def test_short_buffer(
        taxi_callcenter_stats,
        testpoint,
        mock_personal,
        taxi_callcenter_stats_monitor,
        events,
        flushes,
        events_processed,
):
    @testpoint('qapp-event-consumer-bulk-processed')
    def bulk_processed(smth):
        pass

    for msg in events:
        response = await taxi_callcenter_stats.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'tel_qapp_messages_cc_consumer',
                    'data': msg,
                    'topic': '/taxi/callcenter/production/qapp-events',
                    'cookie': 'cookie1',
                },
            ),
        )
        assert response.status_code == 200

    async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
        for _ in range(flushes):
            await bulk_processed.wait_call()
        response = await taxi_callcenter_stats_monitor.get('/')
        assert response.status_code == 200
        metrics = response.json()['qapp-event-consumer']
        assert (
            metrics['postgres']['qapp_events']['inserts']['ok']['1min']
            == flushes
        )
        assert metrics['qapp_event']['ok']['1min'] == events_processed


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 10,
        'actions_whitelist': [
            'ADDMEMBER',
            'ABANDON',
            'ATTENDEDTRANSFER',
            'BLINDTRANSFER',
            'COMPLETEAGENT',
            'COMPLETECALLER',
            'CONNECT',
            'ENTERQUEUE',
            'META',
            'REMOVEMEMBER',
            'RINGCANCELED',
            'RINGNOANSWER',
        ],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.6,
            'max_random_delay': 20,
            'max_possible_delay': 1000,
        },
    },
)
async def test_long_buffer(
        taxi_callcenter_stats,
        testpoint,
        mock_personal,
        lb_message_sender,
        mocked_time,
        taxi_callcenter_stats_monitor,
):
    @testpoint('qapp-event-consumer-bulk-processed')
    def bulk_processed(smth):
        pass

    # it will be flushed because of no messages in lb
    for msg in EVENTS:
        response = await taxi_callcenter_stats.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'tel_qapp_messages_cc_consumer',
                    'data': msg,
                    'topic': '/taxi/callcenter/production/qapp-events',
                    'cookie': 'cookie1',
                },
            ),
        )
        assert response.status_code == 200

    async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
        await bulk_processed.wait_call()
        response = await taxi_callcenter_stats_monitor.get('/')
        assert response.status_code == 200
        metrics = response.json()['qapp-event-consumer']
        assert metrics['postgres']['qapp_events']['inserts']['ok']['1min'] == 1
        assert metrics['qapp_event']['ok']['1min'] == 6


@pytest.mark.parametrize(
    ('failure', 'tries'),
    (
        ('', 0),  # no exc
        ('std_exception', 1),  # 1 fail, then throw
        ('postgres_runtime_error', 0),  # no fails, cause of retries cycle
    ),
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': True,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 10,
        'actions_whitelist': [
            'ADDMEMBER',
            'ABANDON',
            'ATTENDEDTRANSFER',
            'BLINDTRANSFER',
            'COMPLETEAGENT',
            'COMPLETECALLER',
            'CONNECT',
            'ENTERQUEUE',
            'META',
            'REMOVEMEMBER',
            'RINGCANCELED',
            'RINGNOANSWER',
        ],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.6,
            'max_random_delay': 20,
            'max_possible_delay': 1000,
        },
    },
)
async def test_flush(
        taxi_callcenter_stats,
        testpoint,
        mock_personal,
        lb_message_sender,
        mocked_time,
        taxi_callcenter_stats_monitor,
        failure,
        tries,
):
    @testpoint('qapp-event-consumer-saving-qapp-messages')
    def mytp(data):
        if not hasattr(mytp, 'calls'):
            mytp.calls = 0
        mytp.calls += 1
        if mytp.calls < 4:
            return {'inject_failure': failure}
        return {'inject_failure': ''}

    for msg in EVENTS:
        response = await taxi_callcenter_stats.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'tel_qapp_messages_cc_consumer',
                    'data': msg,
                    'topic': '/taxi/callcenter/production/qapp-events',
                    'cookie': 'cookie1',
                },
            ),
        )
        assert response.status_code == 200

    async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
        response = await taxi_callcenter_stats_monitor.get('/')
        assert response.status_code == 200
        metrics = response.json()['qapp-event-consumer']
        assert (
            metrics['postgres']['qapp_events']['inserts']['failed']['1min']
            == tries
        )


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 10,
        'actions_whitelist': [
            'ADDMEMBER',
            'ABANDON',
            'ATTENDEDTRANSFER',
            'BLINDTRANSFER',
            'COMPLETEAGENT',
            'COMPLETECALLER',
            'CONNECT',
            'ENTERQUEUE',
            'META',
            'REMOVEMEMBER',
            'RINGCANCELED',
            'RINGNOANSWER',
        ],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 100,
            'delay_multiplier': 2,
            'max_random_delay': 0,
            'max_possible_delay': 1000,
        },
    },
)
async def test_delay(taxi_callcenter_stats, testpoint, mock_personal):
    await taxi_callcenter_stats.invalidate_caches()
    sleep_delays = list()

    @testpoint('qapp-event-consumer-loop-sleep')
    def sleep(data):
        sleep_delays.append(data)

    async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()

    assert sleep_delays == [100, 200, 400, 800, 1000]


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 10,
        'actions_whitelist': [
            'ADDMEMBER',
            'ABANDON',
            'ATTENDEDTRANSFER',
            'BLINDTRANSFER',
            'COMPLETEAGENT',
            'COMPLETECALLER',
            'CONNECT',
            'ENTERQUEUE',
            'META',
            'REMOVEMEMBER',
            'RINGCANCELED',
            'RINGNOANSWER',
        ],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 100,
            'delay_multiplier': 1,
            'max_random_delay': 20,
            'max_possible_delay': 1000,
        },
    },
)
async def test_delay_jitter(taxi_callcenter_stats, testpoint, mock_personal):
    await taxi_callcenter_stats.invalidate_caches()
    sleep_delays = list()

    @testpoint('qapp-event-consumer-loop-sleep')
    def sleep(data):
        sleep_delays.append(data)

    async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()
        await sleep.wait_call()

    for i in range(1, len(sleep_delays)):
        assert sleep_delays[i] - sleep_delays[i - 1] <= 20  # max_random_delay
