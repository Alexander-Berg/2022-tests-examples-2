# pylint: disable=too-many-lines
import datetime
import logging

import pytest


logger = logging.getLogger(__name__)


def actions_whitelist(extra):
    return [
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
    ] + extra


@pytest.mark.parametrize(
    ['failure', 'expected_call_count'],
    (
        # No failure - will work without retry
        pytest.param(
            '',
            1,
            id='no_failure_no_retry',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'hanged_events_settings': {
                        'cutoff': 86400,
                        'enabled': False,
                    },
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
            1,
            id='retry',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
async def test_message_retry(
        taxi_callcenter_stats,
        mock_personal,
        testpoint,
        pgsql,
        failure,
        expected_call_count,
        lb_message_sender,
):
    @testpoint('qapp-event-consumer-db-update')
    def mytp(data):
        if not hasattr(mytp, 'calls'):
            mytp.calls = 0
        mytp.calls += 1
        if mytp.calls < 4:
            return {'inject_failure': failure}
        return {'inject_failure': ''}

    # force cleanup internal state
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT count(*) from callcenter_stats.call_status')
    call_count = cursor.fetchall()[0][0]
    assert call_count == expected_call_count


@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_message_saving(
        taxi_callcenter_stats,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):

    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT * from callcenter_stats.qapp_events')
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
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
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
        taxi_callcenter_stats,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):

    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT * from callcenter_stats.qapp_events')
    messages = cursor.fetchall()
    assert not messages


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
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': True,
        'retring_delays': [0, 0, 0],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 1,
        'actions_whitelist': actions_whitelist([]),
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
        taxi_callcenter_stats,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
        is_hanged,
):

    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT * from callcenter_stats.qapp_events')
    messages = cursor.fetchall()
    if is_hanged:
        assert not messages
    else:
        assert messages


@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'skip_until': {'asd': 1000},
        'actions_whitelist': actions_whitelist([]),
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
        taxi_callcenter_stats,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):
    await lb_message_sender.send(['ENTERQUEUE.txt', 'ENTERQUEUE.txt'])

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT count(*) from callcenter_stats.qapp_events')
    messages_count = cursor.fetchall()[0][0]
    assert messages_count == 1


@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_glued_message(
        taxi_callcenter_stats,
        testpoint,
        load_json,
        pgsql,
        mock_personal,
        lb_message_sender,
):

    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('glued_message.txt')

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT count(*) from callcenter_stats.call_status')
    call_count = cursor.fetchall()[0][0]
    assert call_count == 3


@pytest.fixture(name='mock_personal_503')
def _mock_personal_503(mockserver):
    phones_store_calls = 0
    phones_bulk_store_calls = 0

    class MockPersonal:
        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/store')
        def phones_store(request):
            nonlocal phones_store_calls
            phones_store_calls += 1
            if phones_store_calls <= 2:
                return mockserver.make_response(
                    '503 Service Unavailable ', 503,
                )
            return {'id': '557f191e810c19729de860ea', 'value': '+70001112233'}

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
    ['times_called'],
    (
        pytest.param(
            3,  # because of retrying in loop
            id='no_retries',
            marks=pytest.mark.config(
                PERSONAL_CLIENT_QOS={
                    '__default__': {'attempts': 1, 'timeout-ms': 1000},
                },
            ),
        ),
        pytest.param(
            3,  # because of retrying in client
            id='3_retries',
            marks=pytest.mark.config(
                PERSONAL_CLIENT_QOS={
                    '__default__': {'attempts': 3, 'timeout-ms': 1000},
                },
            ),
        ),
    ),
)
async def test_personal_client_retry(
        taxi_callcenter_stats,
        testpoint,
        pgsql,
        mock_personal_503,
        times_called,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')
    assert mock_personal_503.phones_bulk_store.times_called == times_called
    mock_personal_503.phones_bulk_store_calls = 0
    mock_personal_503.phones_store_calls = 0


@pytest.fixture(name='mock_personal_400')
def _mock_personal_400(mockserver):
    phones_store_calls = 0
    phones_bulk_store_calls = 0

    class MockPersonal:
        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/store')
        def phones_store(request):
            nonlocal phones_store_calls
            phones_store_calls += 1
            if phones_store_calls <= 2:
                return mockserver.make_response(
                    json={'code': '400', 'message': 'Invalid phone number'},
                    status=400,
                )
            return {'id': '557f191e810c19729de860ea', 'value': '+70001112233'}

        @staticmethod
        @mockserver.json_handler('/personal/v2/phones/bulk_store')
        def phones_bulk_store(request):
            nonlocal phones_bulk_store_calls
            phones_bulk_store_calls += 1
            if phones_bulk_store_calls <= 2:
                return mockserver.make_response(
                    json={'code': '400', 'message': 'Invalid phone number'},
                    status=400,
                )
            return {
                'items': [
                    {'id': x['value'], 'value': x['value']}
                    for x in request.json['items']
                ],
            }

    return MockPersonal()


async def test_personal_client_fail(
        taxi_callcenter_stats,
        testpoint,
        pgsql,
        mock_personal_400,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')


@pytest.mark.parametrize(
    ['failure', 'message_skipped'],
    (
        # No failure - will work without retry
        pytest.param(
            '',
            0,
            id='no_failure_no_retry',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': True,
                    'retring_delays': [0, 0, 0],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
        taxi_callcenter_stats,
        taxi_callcenter_stats_monitor,
        testpoint,
        pgsql,
        failure,
        message_skipped,
        lb_message_sender,
        mock_personal,
):
    @testpoint('qapp-event-consumer-saving-qapp-messages')
    def mytp(data):
        if not hasattr(mytp, 'calls'):
            mytp.calls = 0
        mytp.calls += 1
        if mytp.calls < 4:
            return {'inject_failure': failure}
        return {'inject_failure': ''}

    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('ENTERQUEUE.txt')

    response = await taxi_callcenter_stats_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['qapp-event-consumer']
    if message_skipped:
        assert not metrics['qapp_event']['ok']['1min']
    else:
        assert metrics['qapp_event']['ok']['1min']


@pytest.mark.parametrize(
    ['source_id', 'seq_no', 'expected_call_count'],
    (
        # No skip
        pytest.param(
            'asd',
            10,
            1,
            id='no-config - process',
            marks=pytest.mark.config(
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'qwe': 1000},
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'qwe': -1},
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': 8},
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': 10},
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': 1000},
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
                CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
                    'retring_enabled': False,
                    'retring_delays': [],
                    'pg-execute-timeout': 500,
                    'pg-statement-timeout': 500,
                    'skip_until': {'asd': -1},
                    'message_buffer_max_size': 1,
                    'actions_whitelist': actions_whitelist([]),
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
        taxi_callcenter_stats,
        mock_personal,
        testpoint,
        pgsql,
        source_id,
        seq_no,
        expected_call_count,
        lb_message_sender,
):

    # Send main msg
    await taxi_callcenter_stats.invalidate_caches()
    extra_kwargs = {'source_id': source_id, 'seq_no': seq_no}
    await lb_message_sender.send('ENTERQUEUE.txt', **extra_kwargs)

    # Check main msg process result
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute('SELECT count(*) from callcenter_stats.call_status')
    call_count = cursor.fetchall()[0][0]
    assert call_count == expected_call_count


@pytest.mark.config(
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
        'retring_enabled': False,
        'retring_delays': [],
        'pg-execute-timeout': 500,
        'pg-statement-timeout': 500,
        'message_buffer_max_size': 1,
        'actions_whitelist': actions_whitelist(['CALLINFO']),
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.2,
            'max_random_delay': 10,
            'max_possible_delay': 1000,
        },
    },
)
@pytest.mark.now('2022-03-22T17:42:00.00Z')
@pytest.mark.parametrize(
    ['message_file', 'expected_result_file'],
    (pytest.param('CALLINFO.txt', 'callinfo_result.json', id='answered out'),),
)
async def test_callinfo_messages(
        taxi_callcenter_stats,
        mock_personal,
        pgsql,
        lb_message_sender,
        load_json,
        message_file,
        expected_result_file,
):
    # Send main msg
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send(message_file)

    # Check main msg process result
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SELECT id '
        ',created_at::varchar'
        ',queued_at::varchar'
        ',answered_at::varchar'
        ',completed_at::varchar'
        ',postcall_until::varchar'
        ',call_guid'
        ',call_id'
        ',queue'
        ',abonent_phone_id'
        ',agent_id'
        ',endreason'
        ',transfered_to'
        ',transfered_to_number'
        ',called_number'
        ',direction'
        ' FROM callcenter_stats.call_history'
        ' ORDER BY completed_at',
    )
    call_history = [list(i) for i in cursor.fetchall()]
    result = load_json(expected_result_file)
    assert call_history == result['rows']
