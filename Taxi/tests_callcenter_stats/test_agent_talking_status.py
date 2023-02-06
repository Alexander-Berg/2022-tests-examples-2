import datetime
import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.parametrize(
    ['events_data', 'expected_talking_status'],
    (
        pytest.param(
            'completed_call_no_pre_events.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    False,
                    'disp_on_1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                ),
            ],
            id='completed_call_no_pre_events',
        ),
        pytest.param(
            'completed_caller_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    False,
                    'disp_on_1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                ),
            ],
            id='completed_caller_call',
        ),
        pytest.param(
            'completed_agent_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    False,
                    'disp_on_1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                ),
            ],
            id='completed_agent_call',
        ),
        pytest.param(
            'in_process_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    True,
                    'disp_on_1',
                    None,
                ),
            ],
            id='in_process_call',
        ),
        pytest.param(
            'transfered_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    False,
                    'disp_on_1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                ),
            ],
            id='transfered_call',
        ),
        pytest.param(
            'completed_caller_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    False,
                    'disp_on_1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 28, tzinfo=datetime.timezone.utc,
                    ),
                ),
            ],
            id='test_custom_postcall_time',
            marks=pytest.mark.config(
                CALLCENTER_POSTCALL_PROCESSING_TIME_MAP={
                    '__default__': 10,
                    'disp': 20,
                },
            ),
        ),
        pytest.param(
            'dbl_in_process_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    True,
                    'disp_on_1',
                    None,
                ),
            ],
            id='dbl_in_process_call',
        ),
        pytest.param(
            'dbl_completed_agent_call.txt',
            [
                (
                    '1000001304',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    False,
                    'disp_on_1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                ),
            ],
            id='dbl_completed_agent_call',
        ),
    ),
)
async def test_db_state(
        taxi_callcenter_stats,
        testpoint,
        events_data,
        load,
        pgsql,
        expected_talking_status,
        mock_personal,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT * FROM callcenter_stats.operator_talking_status',
    )
    db_result = cursor.fetchall()
    cursor.close()

    assert db_result == expected_talking_status
