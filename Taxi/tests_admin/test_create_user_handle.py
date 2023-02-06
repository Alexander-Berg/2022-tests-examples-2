import pytest

STAGE_START_TIME_CONFIG_FORMAT = '2021-08-25T12:00:00+0000'
STAGE_START_TIME_PYTHON_ISOFORMAT = '2021-08-25T12:00:00+00:00'

STAGE_END_TIME_CONFIG_FORMAT = '2021-11-25T12:00:00+0000'
STAGE_END_TIME_PYTHON_ISOFORMAT = '2021-11-25T12:00:00+00:00'

SEGMENTS_SETUP_QUERY = f"""
    INSERT INTO cashback_levels.segments_tasks
    ( segment, task_description_id, stage_id )
    VALUES ('segment1', 'task1_level1', 'stage1'),
           ('segment2', 'task2_level1', 'stage1'),
           ('segment1', 'task1_level2', 'stage1'),
           ('segment2', 'task2_level2', 'stage2');
    """


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': STAGE_START_TIME_CONFIG_FORMAT,
            'end_time': STAGE_END_TIME_CONFIG_FORMAT,
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.parametrize(
    (
        'json_data',
        'user_setup_params',
        'get_user_params_query',
        'get_user_segments_query',
        'expected_user_params',
        'expected_user_segments',
        'expected_stq_calls',
        'expected_stq_data',
        'expected_status',
    ),
    [
        pytest.param(
            {
                'yandex_uid': '123',
                'current_used_level': 1,
                'current_earned_level': 1,
                'segments': ['segment1', 'segment2'],
                'stage_id': 'stage1',
            },
            """
            INSERT INTO cashback_levels.users
            ( yandex_uid, current_used_level, current_earned_level, stage_id)
            VALUES ('123', 1, 1, 'stage1');
            """,
            """
            SELECT
            yandex_uid, current_used_level, current_earned_level, stage_id
            FROM cashback_levels.users
            WHERE yandex_uid='123' AND stage_id='stage1';
            """,
            """
            SELECT
            segment
            FROM cashback_levels.users_segments
            WHERE yandex_uid='123' AND stage_id='stage1';
            """,
            [('123', 1, 1, 'stage1')],
            [('segment1',), ('segment2',)],
            2,
            [
                {
                    'yandex_uid': '123',
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level1',
                    'force': False,
                },
                {
                    'yandex_uid': '123',
                    'stage_id': 'stage1',
                    'task_description_id': 'task2_level1',
                    'force': False,
                },
            ],
            201,
            id='simple',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'current_used_level': 3,
                'current_earned_level': 2,
                'segments': ['segment1'],
                'stage_id': 'stage1',
            },
            """
            INSERT INTO cashback_levels.users
            ( yandex_uid, current_used_level, current_earned_level, stage_id)
            VALUES ('123', 1, 1, 'stage1');
            """,
            """
            SELECT
            yandex_uid, current_used_level, current_earned_level, stage_id
            FROM cashback_levels.users
            WHERE yandex_uid='123' AND stage_id='stage1';
            """,
            """
            SELECT
            segment
            FROM cashback_levels.users_segments
            WHERE yandex_uid='123' AND stage_id='stage1';
            """,
            [('123', 3, 2, 'stage1')],
            [('segment1',)],
            1,
            [
                {
                    'yandex_uid': '123',
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level2',
                    'force': False,
                },
            ],
            201,
            id='with-levels-change',
        ),
    ],
)
async def test_create_user_handle(
        pgsql,
        stq,
        json_data,
        user_setup_params,
        get_user_params_query,
        get_user_segments_query,
        expected_user_params,
        expected_user_segments,
        expected_stq_calls,
        expected_stq_data,
        taxi_cashback_levels,
        expected_status,
):
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(SEGMENTS_SETUP_QUERY)
    cursor.execute(user_setup_params)

    response = await taxi_cashback_levels.post(
        'admin/user/create', json=json_data,
    )
    assert response.status_code == expected_status
    if expected_status == 201:
        cursor.execute(get_user_params_query)
        values = [*cursor]
        assert expected_user_params == values

        cursor.execute(get_user_segments_query)
        values = [*cursor]
        assert expected_user_segments == values

        assert (
            stq.cashback_levels_assign_mission_to_user.times_called
            == expected_stq_calls
        )
        for expected_data in expected_stq_data:
            task = stq.cashback_levels_assign_mission_to_user.next_call()
            task['kwargs'].pop('log_extra')
            assert task['kwargs'] == expected_data
    else:
        assert stq.cashback_levels_assign_mission_to_user.times_called == 0
