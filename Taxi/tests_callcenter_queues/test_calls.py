import datetime
import logging

import pytest


logger = logging.getLogger(__name__)

_NOW_DATE = datetime.date(year=2007, month=1, day=1)

MOCK_OPERATORS = [
    {
        'id': 1,
        'login': 'operator_1',
        'yandex_uid': '1001',
        'agent_id': '1000001304',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'roles': ['ru_disp_operator', 'ru_support_operator'],
        'name_in_telephony': 'operator_1',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
]


@pytest.mark.config(CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_disp_')
@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.parametrize(
    ['events_data', 'expected_call'],
    (
        pytest.param(
            '1_meta.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600901',
                    'commutation_id',
                    'krasnodar',
                    'cc',
                    'queued',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has NO abonent_phone_guid from ENTERQUEUE
                    None,
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO completed_at
                    None,
                    # has NO endreason
                    None,
                    # has NO transfered_to_number
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,  # updated_seq
                ),
            ],
            id='1_meta.txt',
        ),
        pytest.param(
            '2_queued.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                    'commutation_id',
                    'krasnodar',
                    'cc',
                    'queued',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO completed_at
                    None,
                    # has NO endreason
                    None,
                    # has NO transfered_to_number
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,  # updated_seq
                ),
            ],
            id='2_queued.txt',
        ),
        pytest.param(
            '3_queued_no_meta.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600903',
                    None,
                    'krasnodar',
                    'cc',
                    'queued',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO call_guid from META
                    None,
                    # has NO called_number from META
                    None,
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO completed_at
                    None,
                    # has NO endreason
                    None,
                    # has NO transfered_to_number
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,  # updated_seq
                ),
            ],
            id='3_queued_no_meta.txt',
        ),
        pytest.param(
            '4_talking.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600904',
                    'commutation_id',
                    'krasnodar',
                    'cc',
                    'talking',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has answered_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO completed_at
                    None,
                    # has NO endreason
                    None,
                    # has NO transfered_to_number
                    None,
                    # has agent_id from CONNECT
                    '1000001304',
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,  # updated_seq
                ),
            ],
            id='4_talking.txt',
        ),
        pytest.param(
            '5_talking_no_pre_events.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600905',
                    None,
                    'krasnodar',
                    'cc',
                    'talking',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO call_guid from META
                    None,
                    # has NO called_number from META
                    None,
                    # has abonent_phone_guid from ENTERQUEUE
                    None,
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has answered_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO completed_at
                    None,
                    # has NO endreason
                    None,
                    # has NO transfered_to_number
                    None,
                    # has agent_id from CONNECT
                    '1000001304',
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,  # updated_seq
                ),
            ],
            id='5_talking_no_pre_events.txt',
        ),
        pytest.param(
            '6_abandoned.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600906',
                    'commutation_id',
                    'krasnodar',
                    'cc',
                    'completed',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 28, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 36, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has completed at
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 28, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO endreason
                    'abandoned',
                    # has NO transfered_to_number
                    None,
                    # has agent_id from CONNECT
                    None,
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,  # updated_seq
                ),
            ],
            id='6_abandoned.txt',
        ),
        pytest.param(
            '7_completed_by_agent.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600907',
                    'commutation_id',
                    'krasnodar',
                    'cc',
                    'completed',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    '+73812955555',
                    '+79991111111_id',
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
                    '1000001304',
                    datetime.datetime(
                        2019, 9, 3, 11, 0, tzinfo=datetime.timezone.utc,
                    ),
                    1,
                ),
            ],
            id='7_completed_by_agent.txt',
        ),
    ),
)
async def test_call_status(
        taxi_callcenter_queues,
        testpoint,
        events_data,
        load,
        pgsql,
        expected_call,
        mock_personal,
        lb_message_sender,
        mockserver,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';' 'SELECT * from callcenter_queues.calls',
    )
    call_status_result = cursor.fetchall()
    cursor.close()

    assert call_status_result == expected_call


@pytest.mark.config(CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_disp_')
@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.pgsql('callcenter_queues', files=['routed_calls.sql'])
@pytest.mark.parametrize(
    ['events_data', 'expected_routed_call'],
    (
        pytest.param(
            '1_meta.txt',
            [
                (
                    'commutation_id',
                    'taxi-mar-qproc1.yndx.net-1588774115.600901',
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='1_meta.txt',
        ),
        pytest.param(
            '2_queued.txt',
            [
                (
                    'commutation_id',
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='2_queued.txt',
        ),
        pytest.param(
            '3_queued_no_meta.txt',
            [
                (
                    'commutation_id',
                    None,
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='3_queued_no_meta.txt',
        ),
        pytest.param(
            '4_talking.txt',
            [
                (
                    'commutation_id',
                    'taxi-mar-qproc1.yndx.net-1588774115.600904',
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='4_talking.txt',
        ),
        pytest.param(
            '5_talking_no_pre_events.txt',
            [
                (
                    'commutation_id',
                    None,
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='5_talking_no_pre_events.txt',
        ),
        pytest.param(
            '6_abandoned.txt',
            [
                (
                    'commutation_id',
                    'taxi-mar-qproc1.yndx.net-1588774115.600906',
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='6_abandoned.txt',
        ),
        pytest.param(
            '7_completed_by_agent.txt',
            [
                (
                    'commutation_id',
                    'taxi-mar-qproc1.yndx.net-1588774115.600907',
                    datetime.datetime(
                        2021, 10, 13, 11, 39, 1, tzinfo=datetime.timezone.utc,
                    ),
                    '0002030101-0000065536-1588774110-0002446012',
                    'krasnodar_disp_cc',
                    'QPROC1',
                ),
            ],
            id='7_completed_by_agent.txt',
        ),
    ),
)
async def test_routed_call_status(
        taxi_callcenter_queues,
        testpoint,
        events_data,
        load,
        pgsql,
        expected_routed_call,
        mock_personal,
        lb_message_sender,
        mockserver,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT * from callcenter_queues.routed_calls',
    )
    routed_call_status_result = cursor.fetchall()
    cursor.close()

    assert routed_call_status_result == expected_routed_call
