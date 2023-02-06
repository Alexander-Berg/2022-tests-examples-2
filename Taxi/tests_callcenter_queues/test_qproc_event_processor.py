# pylint: disable=too-many-lines
import datetime
import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_message_saving(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT * from callcenter_queues.qproc_events')
    expected_message = cursor.fetchall()[0]
    assert expected_message == (
        datetime.datetime(
            2019, 9, 3, 11, 0, 0, 0, tzinfo=datetime.timezone.utc,
        ),
        'TAXI-MYT-QAPP1',
        'TAXIMYT1',
        datetime.timedelta(days=18129, seconds=49849),
        'taxi-myt-qapp1.yndx.net-1566395444.1632',
        'disp_cc',
        None,
        'ENTERQUEUE',
        '',
        '79872676410',
        '1',
        None,
        None,
        None,
        None,
        None,
        None,
        'jkLxrwgRVKwSeKqEAvY/RoLx/B4=',
        1,
    )


@pytest.mark.config(
    CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
        'retring_enabled': True,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 1,
        'actions_whitelist': [],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.2,
            'max_random_delay': 10,
            'max_possible_delay': 1000,
        },
    },
)
@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_event_not_suitable(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT * from callcenter_queues.qproc_events')
    qproc_events_parsed = cursor.fetchall()
    assert not qproc_events_parsed


@pytest.mark.parametrize(
    'is_hanged',
    (
        pytest.param(
            False, marks=[pytest.mark.now('2019-08-21T13:50:50.00Z')],
        ),
        pytest.param(True, marks=[pytest.mark.now('2019-08-21T13:50:51.00Z')]),
    ),
)
@pytest.mark.config(
    CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
        'retring_enabled': True,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 1,
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
        'hanged_events_settings': {'cutoff': 2, 'enabled': True},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.2,
            'max_random_delay': 10,
            'max_possible_delay': 1000,
        },
    },
)
async def test_event_hanged(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
        is_hanged,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT * from callcenter_queues.qproc_events')
    qproc_events_parsed = cursor.fetchall()
    if is_hanged:
        assert not qproc_events_parsed
    else:
        assert qproc_events_parsed


@pytest.mark.config(
    CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'skip_until': {'asd': 1000},
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
        'message_buffer_max_size': 2,  # to process 2 messages at once
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.2,
            'max_random_delay': 10,
            'max_possible_delay': 1000,
        },
    },
)
@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_message_deduplication(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):
    await lb_message_sender.send(['ENTERQUEUE.txt', 'ENTERQUEUE.txt'])

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT count(*) from callcenter_queues.qproc_events')
    qproc_events_parsed = cursor.fetchall()[0][0]
    assert qproc_events_parsed == 1


@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_glued_message(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send('glued_message.txt')

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT count(*) from callcenter_queues.qproc_events')
    qproc_events_parsed = cursor.fetchall()[0][0]
    assert qproc_events_parsed == 3


@pytest.fixture(name='mock_personal_503')
def _mock_personal_503(mockserver):
    phones_bulk_store_calls = 0

    class MockPersonal:
        @staticmethod
        @mockserver.json_handler('/personal/v2/phones/bulk_store')
        def phones_bulk_store(request):
            nonlocal phones_bulk_store_calls
            phones_bulk_store_calls += 1
            if phones_bulk_store_calls <= 2:
                return mockserver.make_response(
                    '503 Service Unavailable ', 503,
                )
            return {
                'items': [
                    {'id': x['value'], 'value': x['value']}
                    for x in request.json['items']
                ],
            }

    return MockPersonal()


@pytest.mark.parametrize(
    ['failure', 'message_skipped'],
    (
        # No failure - will work without retry
        pytest.param(
            '',
            0,
            id='no_failure_no_retry',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # std::exception - retry will not help
        pytest.param(
            'std_exception',
            1,
            id='std_exception_retry',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # storages::postgres::RuntimeError - no retry - no result
        pytest.param(
            'postgres_runtime_error',
            1,
            id='std_exception_no_retry',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # storages::postgres::RuntimeError - no enough retry - no result
        pytest.param(
            'postgres_runtime_error',
            1,
            id='no_enough_retry',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # storages::postgres::RuntimeError - enough retry - result
        pytest.param(
            'postgres_runtime_error',
            0,
            id='retry',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
    ),
)
async def test_counters(
        taxi_callcenter_queues,
        taxi_callcenter_queues_monitor,
        testpoint,
        pgsql,
        failure,
        message_skipped,
        lb_message_sender,
        mock_personal,
):
    @testpoint('qproc-event-processor-saving-qproc-events')
    def mytp(data):
        if not hasattr(mytp, 'calls'):
            mytp.calls = 0
        mytp.calls += 1
        if mytp.calls < 4:
            return {'inject_failure': failure}
        return {'inject_failure': ''}

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    response = await taxi_callcenter_queues_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['qproc-event-processor']
    if message_skipped:
        assert not metrics['qproc_event']['ok']['1min']
    else:
        assert metrics['qproc_event']['ok']['1min']


@pytest.mark.parametrize(
    ['source_id', 'seq_no', 'expected_count'],
    (
        # No skip
        pytest.param(
            'asd',
            10,
            1,
            id='no-config - process',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # No skip
        pytest.param(
            'asd',
            10,
            1,
            id='{qwe: 1000} - process',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'qwe': 1000},
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # No skip
        pytest.param(
            'asd',
            10,
            1,
            id='{qwe: -1} - process',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'qwe': -1},
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # No skip
        pytest.param(
            'asd',
            10,
            1,
            id='{asd: 8} - process',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': 8},
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # No skip
        pytest.param(
            'asd',
            10,
            1,
            id='{asd: 10} - process',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': 10},
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # Skip
        pytest.param(
            'asd',
            10,
            0,
            id='{asd: 1000} - skip',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': 1000},
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
        # Skip
        pytest.param(
            'asd',
            10,
            0,
            id='{asd: -1} - skip',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_QPROC_EVENTS_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': -1},
                    'message_buffer_max_size': 1,
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
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'retrying_policy': {
                        'min_retry_delay': 10,
                        'delay_multiplier': 1.2,
                        'max_random_delay': 10,
                        'max_possible_delay': 1000,
                    },
                },
            ),
        ),
    ),
)
async def test_message_skip(
        taxi_callcenter_queues,
        mock_personal,
        testpoint,
        pgsql,
        source_id,
        seq_no,
        expected_count,
        lb_message_sender,
):

    # Send main msg
    await taxi_callcenter_queues.invalidate_caches()
    extra_kwargs = {'source_id': source_id, 'seq_no': seq_no}
    await lb_message_sender.send('ENTERQUEUE.txt', **extra_kwargs)

    # Check main msg process result
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT count(*) from callcenter_queues.qproc_events')
    qproc_events_saved = cursor.fetchall()[0][0]
    assert qproc_events_saved == expected_count
