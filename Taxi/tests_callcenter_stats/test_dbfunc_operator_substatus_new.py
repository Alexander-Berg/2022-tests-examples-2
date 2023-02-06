# pylint: disable=C5521
from datetime import datetime
from datetime import timezone

import pytest

OPERATORS = [
    # agent_id                VARCHAR,
    # substatus               VARCHAR,
    # substatus_updated_at    TIMESTAMPTZ,
    # current_queue           VARCHAR
    (
        # disconnected
        'agent01',
        None,
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # disconnected
        'agent02',
        'register_error',
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # connected
        'agent03',
        'talking',
        datetime(2020, 6, 22, 10, 0, 0, tzinfo=timezone.utc),
        'queue1_on_1',
    ),
    (
        # connected
        'agent04',
        'talking',
        datetime(2020, 6, 22, 10, 0, 0, tzinfo=timezone.utc),
        'queue2_on_1',
    ),
    (
        # connected
        'agent05',
        'postcall',
        datetime(2020, 6, 22, 9, 59, 50, tzinfo=timezone.utc),
        'queue1_on_1',
    ),
    (
        # connected
        'agent06',
        'talking',
        datetime(2020, 6, 22, 10, 0, 0, tzinfo=timezone.utc),
        'queue1_on_1',
    ),
    (
        # connected
        'agent07',
        'waiting',
        datetime(2020, 6, 22, 10, 0, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # paused
        'agent08',
        None,
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # connected
        'agent09',
        'waiting',
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # paused
        'agent10',
        None,
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # paused
        'agent11',
        'p1',
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # paused
        'agent12',
        'p2',
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # paused
        'agent13',
        'p2',
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # paused
        'agent14',
        'break',
        datetime(2020, 6, 22, 9, 50, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # connected
        'agent15',
        'waiting',
        datetime(2020, 6, 22, 9, 59, 0, tzinfo=timezone.utc),
        None,
    ),
    (
        # connected
        'agent21',
        'waiting',
        datetime(2020, 6, 22, 9, 59, 50, tzinfo=timezone.utc),
        None,
    ),
    (
        # connected
        'agent22',
        'postcall',
        datetime(2020, 6, 22, 9, 59, 50, tzinfo=timezone.utc),
        'queue4_on_1',
    ),
    (
        # connected
        'agent23',
        'postcall',
        datetime(2020, 6, 22, 9, 59, 50, tzinfo=timezone.utc),
        None,
    ),
    (
        # connected
        'agent24',
        'postcall',
        datetime(2020, 6, 22, 9, 59, 50, tzinfo=timezone.utc),
        'queue4_on_1',
    ),
    (
        # connected
        'agent25',
        'waiting',
        datetime(2020, 6, 22, 9, 59, 55, tzinfo=timezone.utc),
        None,
    ),
]


@pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=True)
@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_status.sql'])
async def test_values(pgsql):
    cursor = pgsql['callcenter_stats'].cursor()
    query = (
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT * FROM callcenter_stats.user_substatus('
        f'\'2020-06-22T10:00:01.00Z\',TRUE,NULL)'
        ' ORDER BY sip_username'
    )

    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    assert result == OPERATORS


ALL_OPERATORS = [op[0] for op in OPERATORS]
NO_DISCONNECTED = [
    # agent_id only
    OPERATORS[2][0],
    OPERATORS[3][0],
    OPERATORS[4][0],
    OPERATORS[5][0],
    OPERATORS[6][0],
    OPERATORS[7][0],
    OPERATORS[8][0],
    OPERATORS[9][0],
    OPERATORS[10][0],
    OPERATORS[11][0],
    OPERATORS[12][0],
    OPERATORS[13][0],
    OPERATORS[14][0],
    OPERATORS[15][0],
    OPERATORS[16][0],
    OPERATORS[17][0],
    OPERATORS[18][0],
    OPERATORS[19][0],
]


@pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=True)
@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_status.sql'])
@pytest.mark.parametrize(
    ['show_disconnected', 'disconnected_time_depth', 'expected_result'],
    [
        pytest.param(False, 'NULL', NO_DISCONNECTED),
        pytest.param(True, 'NULL', ALL_OPERATORS),
        pytest.param(True, '\'2020-06-22T09:50:00.00Z\'', NO_DISCONNECTED),
        pytest.param(True, '\'2020-06-22T09:30:00.00Z\'', ALL_OPERATORS),
    ],
)
async def test_filtering(
        pgsql, show_disconnected, disconnected_time_depth, expected_result,
):
    cursor = pgsql['callcenter_stats'].cursor()
    query = (
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT sip_username FROM callcenter_stats.user_substatus('
        '\'2020-06-22T10:00:01.00Z\','
        f'{show_disconnected},'
        f'{disconnected_time_depth})'
        ' ORDER BY sip_username'
    )

    cursor.execute(query)
    result = [row[0] for row in cursor.fetchall()]
    cursor.close()
    assert result == expected_result
