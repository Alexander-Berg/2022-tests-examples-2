import datetime

import pytest

OPERATORS_SAVE_STATUS_URL = 'operators/save_status'

NOW = '2020-07-07T14:00:00.00Z'
NOW_DATETIME = datetime.datetime(2020, 7, 7, 14, tzinfo=datetime.timezone.utc)
DB_LAST_HISTORY_AT = datetime.datetime(
    2020, 7, 7, 12, 30, tzinfo=datetime.timezone.utc,
)
DB_STATUS_UPDATED_AT = datetime.datetime(
    2020, 7, 7, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
DB_SUB_STATUS_UPDATED_AT = datetime.datetime(
    2020, 7, 7, 13, 0, 0, tzinfo=datetime.timezone.utc,
)


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['agents', 'expected_status', 'expected_history'],
    (
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': None,
                },
            ],
            (
                '123456',
                'disconnect',
                [],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='insert_none',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': 'asd',
                },
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'connect',
                    'queues': ['q1', 'q2'],
                    'sub_status': None,
                },
            ],
            (
                '123456',
                'connect',
                ['q1', 'q2'],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'connect',
                    ['q1', 'q2'],
                    'test_login',
                    None,
                    'disconnect',
                    [],
                    'asd',
                    NOW_DATETIME,
                ),
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    'asd',
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='update_none',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': None,
                },
                {
                    'agent_id': '123456789',
                    'login': 'test_login',
                    'status': 'connect',
                    'queues': ['q1', 'q2'],
                    'sub_status': 'asd',
                },
            ],
            (
                '123456',
                'disconnect',
                [],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='no_change_none',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': 'qwe',
                },
            ],
            (
                '123456',
                'disconnect',
                [],
                'test_login',
                'qwe',
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    'qwe',
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='insert_qwe',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': None,
                },
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'connect',
                    'queues': ['q1', 'q2'],
                    'sub_status': 'qwe',
                },
            ],
            (
                '123456',
                'connect',
                ['q1', 'q2'],
                'test_login',
                'qwe',
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'connect',
                    ['q1', 'q2'],
                    'test_login',
                    'qwe',
                    'disconnect',
                    [],
                    None,
                    NOW_DATETIME,
                ),
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='update_qwe',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': 'qwe',
                },
                {
                    'agent_id': '123456789',
                    'login': 'test_login',
                    'status': 'connect',
                    'queues': ['q1', 'q2'],
                    'sub_status': 'asd',
                },
            ],
            (
                '123456',
                'disconnect',
                [],
                'test_login',
                'qwe',
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    'qwe',
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='no_change_qwe',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': None,
                },
            ],
            (
                '123456',
                'disconnect',
                [],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    None,
                    'paused',
                    ['q1', 'q2'],
                    'break',
                    DB_STATUS_UPDATED_AT,
                ),
            ],
            id='update_disconnect',
            marks=pytest.mark.pgsql(
                'callcenter_stats', files=['operator_status.sql'],
            ),
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnect',
                    'queues': [],
                    'sub_status': None,
                },
            ],
            (
                '123456',
                'disconnect',
                [],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnect',
                    [],
                    'test_login',
                    None,
                    'paused',
                    ['q1', 'q2'],
                    'break',
                    DB_LAST_HISTORY_AT,
                ),
                (
                    DB_LAST_HISTORY_AT,
                    '123456',
                    'paused',
                    ['q1', 'q2'],
                    'test_login',
                    'break',
                    None,
                    None,
                    None,
                    None,
                ),
            ],
            id='update_disconnect_with_history',
            marks=pytest.mark.pgsql(
                'callcenter_stats', files=['operator_status_with_history.sql'],
            ),
        ),
    ),
)
async def test_save_operator_status(
        taxi_callcenter_stats,
        pgsql,
        agents,
        expected_status,
        expected_history,
):
    for agent in agents:
        response = await taxi_callcenter_stats.post(
            OPERATORS_SAVE_STATUS_URL, agent,
        )
        assert response.status_code == 200

    cursor = pgsql['callcenter_stats'].cursor()

    cursor.execute(
        'SELECT agent_id, status, queues, login, sub_status,'
        ' updated_at, last_history_at'
        ' FROM callcenter_stats.operator_status'
        ' WHERE agent_id = \'123456\'',
    )
    status_result = cursor.fetchall()[0]
    assert status_result == expected_status

    cursor.execute(
        'SELECT created_at, agent_id, status, queues, login, sub_status,'
        ' prev_status, prev_queues, prev_sub_status, prev_created_at'
        ' FROM callcenter_stats.operator_history'
        ' WHERE agent_id = \'123456\''
        ' ORDER BY status',
    )
    history_result = cursor.fetchall()

    assert history_result == expected_history

    cursor.close()


@pytest.mark.pgsql('callcenter_stats', files=['operator_status.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    [
        'agents',
        'expected_status',
        'is_new_status',
        'is_new_substatus',
        'expected_history',
    ],
    (
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'disconnected',
                    'queues': ['q1', 'q2'],
                    'sub_status': None,
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'disconnected',
                NOW_DATETIME,
                ['q1', 'q2'],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            True,
            True,
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'disconnected',
                    ['q1', 'q2'],
                    'test_login',
                    None,
                    'paused',
                    DB_STATUS_UPDATED_AT,
                    ['q1', 'q2'],
                    'break',
                ),
            ],
            id='update_status',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'paused',
                    'queues': [],
                    'sub_status': 'break',
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'paused',
                DB_STATUS_UPDATED_AT,
                [],
                'test_login',
                'break',
                DB_SUB_STATUS_UPDATED_AT,
                NOW_DATETIME,
            ),
            False,
            False,
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'paused',
                    [],
                    'test_login',
                    'break',
                    'paused',
                    DB_STATUS_UPDATED_AT,
                    ['q1', 'q2'],
                    'break',
                ),
            ],
            id='status_not_changed',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'paused',
                    'queues': [],
                    'sub_status': 'smoking',
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'paused',
                DB_STATUS_UPDATED_AT,
                [],
                'test_login',
                'smoking',
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            False,
            True,
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'paused',
                    [],
                    'test_login',
                    'smoking',
                    'paused',
                    DB_STATUS_UPDATED_AT,
                    ['q1', 'q2'],
                    'break',
                ),
            ],
            id='update_substatus_and_queues',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'paused',
                    'queues': ['q1', 'q2'],
                    'sub_status': 'smoking',
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'paused',
                DB_STATUS_UPDATED_AT,
                ['q1', 'q2'],
                'test_login',
                'smoking',
                NOW_DATETIME,
                None,
            ),
            False,
            True,
            [],
            id='update_substatus_only',
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'connected',
                    'queues': [],
                    'sub_status': 'break',
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'connected',
                NOW_DATETIME,
                [],
                'test_login',
                'break',
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            False,
            True,
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'connected',
                    [],
                    'test_login',
                    'break',
                    'paused',
                    DB_STATUS_UPDATED_AT,
                    ['q1', 'q2'],
                    'break',
                ),
            ],
            id='update_status_only',
        ),
    ),
)
async def test_update_operator_status(
        taxi_callcenter_stats,
        pgsql,
        agents,
        expected_status,
        is_new_status,
        is_new_substatus,
        expected_history,
):
    for agent in agents:
        response = await taxi_callcenter_stats.post(
            OPERATORS_SAVE_STATUS_URL, agent,
        )
        assert response.status_code == 200

    agent_id = agents[0]['agent_id']
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT agent_id, updated_at, status, status_updated_at,'
        ' queues, login, sub_status, sub_status_updated_at, last_history_at'
        ' FROM callcenter_stats.operator_status'
        f' WHERE agent_id = \'{agent_id}\'',
    )
    status_result = cursor.fetchall()[0]
    assert status_result == expected_status

    cursor.execute(
        'SELECT created_at, agent_id, status, queues, login, sub_status,'
        ' prev_status, prev_created_at, prev_queues, prev_sub_status'
        ' FROM callcenter_stats.operator_history'
        f' WHERE agent_id = \'{agent_id}\''
        ' ORDER BY status',
    )
    history_result = cursor.fetchall()

    assert history_result == expected_history

    cursor.close()


@pytest.mark.pgsql(
    'callcenter_stats', files=['operator_status_with_postcall.sql'],
)
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['agents', 'expected_status', 'expected_history'],
    (
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'connected',
                    'queues': ['q1', 'q2'],
                    'sub_status': None,
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'connected',
                DB_STATUS_UPDATED_AT,
                ['q1', 'q2'],
                'test_login',
                None,
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456',
                    'connected',
                    ['q1', 'q2'],
                    'test_login',
                    None,
                    'connected',
                    DB_LAST_HISTORY_AT,
                    ['q1', 'q2'],
                    'postcall',
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456789',
                    'login': 'test_login',
                    'status': 'connected',
                    'queues': ['q1', 'q2'],
                    'sub_status': 'postcall',
                },
            ],
            (
                '123456789',
                NOW_DATETIME,
                'connected',
                DB_STATUS_UPDATED_AT,
                ['q1', 'q2'],
                'test_login',
                'postcall',
                NOW_DATETIME,
                NOW_DATETIME,
            ),
            [
                (
                    NOW_DATETIME,
                    '123456789',
                    'connected',
                    ['q1', 'q2'],
                    'test_login',
                    'postcall',
                    'connected',
                    DB_LAST_HISTORY_AT,
                    ['q1', 'q2'],
                    None,
                ),
            ],
        ),
        pytest.param(
            [
                {
                    'agent_id': '123456',
                    'login': 'test_login',
                    'status': 'connected',
                    'queues': ['q1', 'q2'],
                    'sub_status': 'postcall',
                },
            ],
            (
                '123456',
                NOW_DATETIME,
                'connected',
                DB_STATUS_UPDATED_AT,
                ['q1', 'q2'],
                'test_login',
                'postcall',
                DB_SUB_STATUS_UPDATED_AT,
                DB_LAST_HISTORY_AT,
            ),
            [],
        ),
    ),
)
async def test_postcall_case(
        taxi_callcenter_stats,
        pgsql,
        agents,
        expected_status,
        expected_history,
):
    for agent in agents:
        response = await taxi_callcenter_stats.post(
            OPERATORS_SAVE_STATUS_URL, agent,
        )
        assert response.status_code == 200

    agent_id = agents[0]['agent_id']
    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT agent_id, updated_at, status, status_updated_at,'
        ' queues, login, sub_status, sub_status_updated_at, last_history_at'
        ' FROM callcenter_stats.operator_status'
        f' WHERE agent_id = \'{agent_id}\'',
    )
    status_result = cursor.fetchall()[0]
    assert status_result == expected_status

    cursor.execute(
        'SELECT created_at, agent_id, status, queues, login, sub_status,'
        ' prev_status, prev_created_at, prev_queues, prev_sub_status'
        ' FROM callcenter_stats.operator_history'
        f' WHERE agent_id = \'{agent_id}\''
        ' ORDER BY status',
    )
    history_result = cursor.fetchall()

    assert history_result == expected_history

    cursor.close()


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    (
        'queues',
        'status',
        'sub_status',
        'expected_code',
        'expected_operator_status',
    ),
    [
        pytest.param(None, None, None, 400, {}, id='no status, no queues'),
        pytest.param(
            ['ru_taxi_disp_on_', 'ru_taxi_corp_on_'],
            None,
            'new_sub_status',
            400,
            {},
            id='sub_status wo status',
        ),
        pytest.param(
            ['ru_taxi_disp_on_', 'ru_taxi_corp_on_'],
            None,
            None,
            200,
            {
                'status': 'disconnected',
                'queues': ['ru_taxi_disp_on_', 'ru_taxi_corp_on_'],
                'sub_status': None,
            },
            id='queues',
        ),
        pytest.param(
            None,
            'connected',
            None,
            200,
            {'status': 'connected', 'queues': [], 'sub_status': None},
            id='status',
        ),
        pytest.param(
            None,
            'connected',
            'new_sub_status',
            200,
            {
                'status': 'connected',
                'queues': [],
                'sub_status': 'new_sub_status',
            },
            id='status_with_sub_status',
        ),
    ],
)
async def test_save_status_not_full_request(
        taxi_callcenter_stats,
        pgsql,
        queues,
        status,
        sub_status,
        expected_code,
        expected_operator_status,
):
    response = await taxi_callcenter_stats.post(
        OPERATORS_SAVE_STATUS_URL,
        {
            'agent_id': '123456',
            'login': 'test_login',
            'status': status,
            'queues': queues,
            'sub_status': sub_status,
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:

        cursor = pgsql['callcenter_stats'].cursor()

        cursor.execute(
            'SELECT status, queues, sub_status'
            ' FROM callcenter_stats.operator_status'
            ' WHERE agent_id = \'123456\'',
        )
        status_result = cursor.fetchall()[0]
        assert status_result[0] == expected_operator_status['status']
        assert status_result[1] == expected_operator_status['queues']
        assert status_result[2] == expected_operator_status['sub_status']
        cursor.close()
