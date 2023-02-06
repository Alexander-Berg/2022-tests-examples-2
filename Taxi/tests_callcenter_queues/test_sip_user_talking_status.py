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


@pytest.mark.config(CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_')
@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.parametrize(
    ['events_data', 'expected_talking_status'],
    (
        pytest.param(
            'completed_call_no_pre_events.txt',
            [
                (
                    '1000001304',
                    False,
                    'disp',
                    '1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                ),
            ],
            id='completed_call_no_pre_events',
        ),
        pytest.param(
            'completed_caller_call.txt',
            [
                (
                    '1000001304',
                    False,
                    'disp',
                    '1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                ),
            ],
            id='completed_caller_call',
        ),
        pytest.param(
            'completed_agent_call.txt',
            [
                (
                    '1000001304',
                    False,
                    'disp',
                    '1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                ),
            ],
            id='completed_agent_call',
        ),
        pytest.param(
            'in_process_call.txt',
            [
                (
                    '1000001304',
                    True,
                    'disp',
                    '1',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                ),
            ],
            id='in_process_call',
        ),
        pytest.param(
            'transfered_call.txt',
            [
                (
                    '1000001304',
                    False,
                    'disp',
                    '1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 13, tzinfo=datetime.timezone.utc,
                    ),
                    None,
                ),
            ],
            id='transfered_call',
        ),
        pytest.param(
            'completed_caller_call.txt',
            [
                (
                    '1000001304',
                    False,
                    'disp',
                    '1',
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 8, tzinfo=datetime.timezone.utc,
                    ),
                    datetime.datetime(
                        2020, 5, 6, 14, 9, 28, tzinfo=datetime.timezone.utc,
                    ),
                    None,
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
    ),
)
async def test_db_state(
        taxi_callcenter_queues,
        testpoint,
        events_data,
        load,
        pgsql,
        expected_talking_status,
        mock_personal,
        lb_message_sender,
        mockserver,
):

    await taxi_callcenter_queues.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT'
        ' sip_username,'
        ' is_talking,'
        ' metaqueue,'
        ' subcluster,'
        ' updated_at,'
        ' tech_postcall_until,'
        ' asterisk_call_id'
        ' FROM callcenter_queues.talking_status;',
    )
    db_result = cursor.fetchall()
    cursor.close()

    assert db_result == expected_talking_status
