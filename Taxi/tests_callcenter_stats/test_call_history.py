import datetime
import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_POSTCALL_PROCESSING_TIME_MAP={'__default__': 10},
    CALLCENTER_STATS_QAPP_MESSAGE_PROCESSING_SETTINGS={
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
            'CALLINFO',
        ],
        'hanged_events_settings': {'cutoff': 86400, 'enabled': False},
        'retrying_policy': {
            'min_retry_delay': 10,
            'delay_multiplier': 1.2,
            'max_random_delay': 10,
            'max_possible_delay': 1000,
        },
    },
)
@pytest.mark.parametrize(
    ['events_data', 'expected_call_history'],
    (
        pytest.param('not_completed_call.txt', [], id='not_completed_call'),
        pytest.param(
            'completed_by_caller_call.txt',
            [
                (
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                    'krasnodar_disp_cc',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_caller',
                    None,
                    None,
                    # has called_number from META
                    '+73812955555',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
            ],
            id='completed_call',
        ),
        pytest.param(
            'completed_by_agent_call.txt',
            [
                (
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                    'krasnodar_disp_cc',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_agent',
                    None,
                    None,
                    # has called_number from META
                    '+73812955555',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
            ],
            id='completed_call',
        ),
        pytest.param(
            'completed_call_no_meta.txt',
            [
                (
                    # has NO call_guid from META
                    None,
                    'taxi-mar-qproc1.yndx.net-1588774115.600904',
                    'krasnodar_disp_cc',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_caller',
                    None,
                    None,
                    # has NO called_number from META
                    None,
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
            ],
            id='completed_call_no_meta',
        ),
        pytest.param(
            'completed_call_no_pre_events.txt',
            [
                (
                    # has NO call_guid from META
                    None,
                    'taxi-mar-qproc1.yndx.net-1588774115.600905',
                    'krasnodar_disp_cc',
                    # has NO abonent_phone_guid from ENTERQUEUE
                    None,
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_caller',
                    None,
                    None,
                    # has NO called_number from META
                    None,
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
            ],
            id='completed_call_no_pre_events',
        ),
        pytest.param(
            'abandoned_call.txt',
            [
                (
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600901',
                    'krasnodar_disp_cc',
                    '+79991111111_id',
                    # has NO agent_id
                    None,
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 36, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 28, tzinfo=datetime.timezone.utc,
                    ),
                    'abandoned',
                    None,
                    None,
                    '+73812955555',
                    None,
                    'in',
                ),
            ],
            id='abandoned_call',
        ),
        pytest.param(
            'transfered_call.txt',
            [
                (
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600907',
                    'krasnodar_disp_cc',
                    '+79991111111_id',
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    'transfered',
                    # has transfer information
                    None,
                    '8008',
                    '+73812955555',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
                (
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600907',
                    'cargo_disp_cc',
                    '+79991111111_id',
                    None,
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                    datetime.datetime(
                        2020, 5, 6, 14, 10, tzinfo=datetime.timezone.utc,
                    ),
                    'abandoned',
                    None,
                    None,
                    '+73812955555',
                    None,
                    'in',
                ),
            ],
            id='transfered_call',
        ),
        pytest.param(
            'completed_call_duplicate.txt',
            [
                # only one call in history
                (
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600903',
                    'krasnodar_disp_cc',
                    '+79991111111_id',
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_caller',
                    None,
                    None,
                    '+73812955555',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 18, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
            ],
            id='completed_call_duplicate',
        ),
        pytest.param(
            'reserve_node_call.txt',
            [
                # only last call in history
                (
                    '0002030101-0000065536-1588774110-0002446012',
                    'taxi-mar-qproc1.yndx.net-1588774115.600903',
                    'krasnodar_disp_cc',
                    '+79991111111_id',
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 10, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 30, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 43, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_caller',
                    None,
                    None,
                    '+73812955555',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 53, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
            ],
            id='reserve_node_call',
        ),
        pytest.param(
            'out_calls.txt',
            [
                # in call
                (
                    '0000013103-9942805704-1654508458-0000374639',
                    'taxi-std-qproc15.yndx.net-1654508468.2012082',
                    'ru_eda_support_clients_on_15',
                    '+79991111111_id',
                    '1000028771',
                    datetime.datetime(
                        2022, 6, 6, 9, 41, 8, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2022, 6, 6, 9, 41, 9, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2022, 6, 6, 9, 45, 30, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_agent',
                    None,
                    None,
                    '+73812955555',
                    datetime.datetime(
                        2022, 6, 6, 9, 45, 40, tzinfo=datetime.timezone.utc,
                    ),
                    'in',
                ),
                # out no connect abandoned
                (
                    '0000013103-9942805704-1654508458-0000374639',
                    'taxi-std-qproc15.yndx.net-1654508544.2012120',
                    'ru_eda_support_clients_on_15',
                    '+79992222222_id',
                    '1000028771',
                    datetime.datetime(
                        2022, 6, 6, 9, 42, 24, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                    datetime.datetime(
                        2022, 6, 6, 9, 42, 34, tzinfo=datetime.timezone.utc,
                    ),
                    'abandoned',
                    None,
                    None,
                    '+73812955555',
                    None,
                    'out',
                ),
                # out not answered abandoned
                (
                    '0000013103-9942805704-1654508458-0000374639',
                    'taxi-std-qproc15.yndx.net-1654508556.2012120',
                    'ru_eda_support_clients_on_15',
                    '+79992222222_id',
                    '1000028771',
                    datetime.datetime(
                        2022, 6, 6, 9, 42, 36, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                    datetime.datetime(
                        2022, 6, 6, 9, 42, 40, tzinfo=datetime.timezone.utc,
                    ),
                    'abandoned',
                    None,
                    None,
                    '+73812955555',
                    None,
                    'out',
                ),
                # out completed by caller
                (
                    '0000013103-9942805704-1654508458-0000374639',
                    'taxi-std-qproc15.yndx.net-1654508562.2012130',
                    'ru_eda_support_clients_on_15',
                    '+79993333333_id',
                    '1000028771',
                    datetime.datetime(
                        2022, 6, 6, 9, 42, 42, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2022, 6, 6, 9, 43, 1, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2022, 6, 6, 9, 43, 30, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_caller',
                    None,
                    None,
                    '+73812955555',
                    None,
                    'out',
                ),
                # out completed by agent
                (
                    '0000013103-9942805704-1654508458-0000374639',
                    'taxi-std-qproc15.yndx.net-1654508630.2012130',
                    'ru_eda_support_clients_on_15',
                    '+79993333333_id',
                    '1000028771',
                    datetime.datetime(
                        2022, 6, 6, 9, 43, 50, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2022, 6, 6, 9, 44, 9, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2022, 6, 6, 9, 45, 20, tzinfo=datetime.timezone.utc,
                    ),
                    'completed_by_agent',
                    None,
                    None,
                    '+73812955555',
                    None,
                    'out',
                ),
            ],
            id='out_calls',
        ),
    ),
)
async def test_scenarios(
        taxi_callcenter_stats,
        testpoint,
        events_data,
        load,
        pgsql,
        expected_call_history,
        mock_personal,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT '
        'id, created_at, call_guid, call_id, queue, abonent_phone_id, agent_id'
        ', queued_at, answered_at, completed_at, endreason'
        ', transfered_to, transfered_to_number, called_number, postcall_until'
        ', direction'
        ' FROM callcenter_stats.call_history',
    )
    call_history_result = cursor.fetchall()
    cursor.close()

    for i, call in enumerate(call_history_result):
        # will not check created_at and id fields
        tmp = list(call)
        tmp.pop(1)
        tmp.pop(0)
        call_history_result[i] = tuple(tmp)
    print(set(call_history_result))
    assert set(call_history_result) == set(expected_call_history)


@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_POSTCALL_PROCESSING_TIME_MAP={'__default__': 10},
)
async def test_commutation_id(
        taxi_callcenter_stats,
        testpoint,
        load,
        pgsql,
        mock_personal,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send('completed_with_commutation_id.txt')

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT id'
        ' FROM callcenter_stats.call_history',
    )
    result = cursor.fetchall()[0][0]
    cursor.close()

    assert result == 'commutation_id'


@pytest.mark.parametrize(
    ['events_data', 'call_id', 'expected_transfer'],
    (
        pytest.param(
            'transfered_call.txt',  # call transfered to 8008
            'taxi-mar-qproc1.yndx.net-1588774115.600907',
            None,
            id='default config',
            marks=pytest.mark.config(CALLCENTER_TRANSFER_NUMBER_MAP={}),
        ),
        pytest.param(
            'transfered_call.txt',  # call transfered to 8008
            'taxi-mar-qproc1.yndx.net-1588774115.600907',
            'help',
            id='help',
            marks=pytest.mark.config(
                CALLCENTER_TRANSFER_NUMBER_MAP={
                    '__default__': 'default',
                    '8008': 'help',
                    '8009': 'cargo',
                },
            ),
        ),
        pytest.param(
            'transfered_call.txt',  # call transfered to 8008
            'taxi-mar-qproc1.yndx.net-1588774115.600907',
            'default',
            id='__default__',
            marks=pytest.mark.config(
                CALLCENTER_TRANSFER_NUMBER_MAP={
                    '__default__': 'default',
                    '8000': 'help',
                    '8001': 'help',
                    '8002': 'cargo',
                },
            ),
        ),
        pytest.param(
            'transfered_call.txt',  # call transfered to 8008
            'taxi-mar-qproc1.yndx.net-1588774115.600907',
            None,
            id='null',
            marks=pytest.mark.config(
                CALLCENTER_TRANSFER_NUMBER_MAP={
                    '8000': 'help',
                    '8001': 'help',
                    '8002': 'cargo',
                },
            ),
        ),
    ),
)
async def test_transfer_to(
        taxi_callcenter_stats,
        testpoint,
        events_data,
        load,
        pgsql,
        call_id,
        expected_transfer,
        mock_personal,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        f'SELECT transfered_to FROM callcenter_stats.call_history'
        f' WHERE call_id = \'{call_id}\'',
    )
    transfer_results = list()
    for row in cursor.fetchall():
        transfer_results.append(row[0])
    cursor.close()

    if expected_transfer:
        assert expected_transfer in transfer_results
    else:
        for transfer_result in transfer_results:
            assert not transfer_result
