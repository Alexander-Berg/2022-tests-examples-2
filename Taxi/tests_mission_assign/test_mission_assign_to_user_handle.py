import pytest

STAGE_START_TIME_CONFIG_FORMAT = '2021-08-25T12:00:00+0000'
STAGE_START_TIME_PYTHON_ISOFORMAT = '2021-08-25T12:00:00+00:00'

STAGE_END_TIME_CONFIG_FORMAT = '2021-11-25T12:00:00+0000'
STAGE_END_TIME_PYTHON_ISOFORMAT = '2021-11-25T12:00:00+00:00'


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
    ('json_data', 'expected_stq_data', 'expected_status'),
    [
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
            },
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': False,
            },
            200,
            id='simple',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            200,
            id='force',
        ),
        pytest.param(
            {
                'yandex_uid': '1111',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            {},
            400,
            id='bad_uid',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage2',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            {},
            400,
            id='bad_stage',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage2',
                'task_description_id': 'some-task',
                'force': True,
            },
            {},
            400,
            id='bad_task',
        ),
    ],
)
async def test_assign_mission_to_user_handle(
        pgsql,
        stq,
        json_data,
        expected_stq_data,
        taxi_cashback_levels,
        expected_status,
):
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cashback_levels.users
        ( yandex_uid, current_used_level, current_earned_level, stage_id)
        VALUES ('123', 1, 1, 'stage1');
        """,
    )

    response = await taxi_cashback_levels.post(
        'admin/mission/assign', json=json_data,
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert stq.cashback_levels_assign_mission_to_user.times_called == 1
        task = stq.cashback_levels_assign_mission_to_user.next_call()
        task['kwargs'].pop('log_extra')
        assert task['kwargs'] == expected_stq_data
    else:
        assert stq.cashback_levels_assign_mission_to_user.times_called == 0
