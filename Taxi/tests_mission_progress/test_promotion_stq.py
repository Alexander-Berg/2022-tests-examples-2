import asyncio

# pylint: disable=import-error
from mission_pb2 import MissionStatus
from mission_pb2 import ProgressStatus
from mission_progress_notification_pb2 import NotificationStatus
import pytest

NOTIFICATION_STATUS_UPDATED = NotificationStatus.NOTIFICATION_STATUS_UPDATED


@pytest.mark.pgsql(
    'cashback_levels', files=['segments_tasks.sql', 'users_segments.sql'],
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.parametrize(
    'yandex_uid,stage_id,users_setup_params,progress_setup_params,'
    'expected_db_content,expect_fail',
    [
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 2, 2, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 1, \'stage1\')',
                '(\'111\', \'task2_level1\', 20, \'stage1\')',
                '(\'111\', \'task1_level2\', 7, \'stage1\')',
                '(\'111\', \'task2_level2\', 7, \'stage1\')',
                '(\'111\', \'task1_level3\', 8, \'stage1\')',
                '(\'111\', \'task2_level3\', 8, \'stage1\')',
            ],
            (('111', 2, 2, 14, 'stage1'),),
            False,
            id='not_promoted_not_enough_of_current_level_but_enough_of_others',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 3, 2, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 1, \'stage1\')',
                '(\'111\', \'task2_level1\', 20, \'stage1\')',
                '(\'111\', \'task1_level2\', 7, \'stage1\')',
                '(\'111\', \'task2_level2\', 7, \'stage1\')',
                '(\'111\', \'task1_level3\', 8, \'stage1\')',
                '(\'111\', \'task2_level3\', 8, \'stage1\')',
            ],
            (('111', 3, 2, 14, 'stage1'),),
            False,
            id='not_promoted_not_enough_of_current_level_different_levels',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 2, 2, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 1, \'stage1\')',
                '(\'111\', \'task2_level1\', 1, \'stage1\')',
                '(\'111\', \'task1_level2\', 8, \'stage1\')',
                '(\'111\', \'task2_level2\', 7, \'stage1\')',
                '(\'111\', \'task1_level3\', 1, \'stage1\')',
                '(\'111\', \'task2_level3\', 1, \'stage1\')',
            ],
            (('111', 3, 3, 0, 'stage1'),),
            False,
            id='promoted_when_exactly_enough_current_level_and_used_is_same',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 4, 2, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 1, \'stage1\')',
                '(\'111\', \'task2_level1\', 1, \'stage1\')',
                '(\'111\', \'task1_level2\', 8, \'stage1\')',
                '(\'111\', \'task2_level2\', 7, \'stage1\')',
                '(\'111\', \'task1_level3\', 1, \'stage1\')',
                '(\'111\', \'task2_level3\', 1, \'stage1\')',
            ],
            (('111', 4, 3, 0, 'stage1'),),
            False,
            id='promoted_when_exactly_enough_of_current_level_and_used_higher',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 4, 1, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 8, \'stage1\')',
                '(\'111\', \'task2_level1\', 10, \'stage1\')',
            ],
            (('111', 4, 2, 0, 'stage1'),),
            False,
            id='promoted_when_more_than_enough_of_current_level',
        ),
        pytest.param(
            '111',
            'stage1',
            [],
            [
                '(\'111\', \'task1_level1\', 8, \'stage1\')',
                '(\'111\', \'task2_level1\', 10, \'stage1\')',
            ],
            (),
            True,
            id='level_was_not_set_yet',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 4, 2, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 8, \'stage1\')',
                '(\'111\', \'task2_level1\', 10, \'stage1\')',
            ],
            (('111', 4, 2, 0, 'stage1'),),
            True,
            id='no_progress_for_current_level',
        ),
    ],
)
async def test_promotion_stq_call(
        stq_runner,
        pgsql,
        yandex_uid,
        stage_id,
        users_setup_params,
        progress_setup_params,
        expected_db_content,
        expect_fail,
):
    cursor = pgsql['cashback_levels'].cursor()
    for params in users_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.users(
                yandex_uid, current_used_level, current_earned_level, stage_id
            )
            VALUES {params};
        """,
        )
    for params in progress_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.missions_completed(
                yandex_uid, task_description_id, completions, stage_id
            )
            VALUES {params};
        """,
        )

    await stq_runner.cashback_levels_promotion.call(
        task_id=yandex_uid + stage_id,
        kwargs=dict(yandex_uid=yandex_uid, stage_id=stage_id),
        expect_fail=expect_fail,
    )

    cursor.execute(
        'SELECT yandex_uid, current_used_level,'
        '       current_earned_level, progress, stage_id '
        'from cashback_levels.users',
    )
    assert not set(expected_db_content) ^ set(cursor)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.pgsql(
    'cashback_levels', files=['segments_tasks.sql', 'users_segments.sql'],
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.parametrize(
    (
        'notification_params',
        'users_setup_params',
        'progress_setup_params',
        'stq_times_called',
        'expected_db_content',
    ),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task2_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=15,
                    cyclic_progress_current_completed_iteration=14,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task2_level3',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=9,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task2_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
                    version=1,
                ),
            ],
            [
                '(\'111\', 1, 1, 14, \'stage1\')',
                '(\'222\', 1, 1, 13, \'stage1\')',
                '(\'333\', 4, 3, 9, \'stage1\')',
                '(\'444\', 4, 1, 9, \'stage1\')',
            ],
            [
                '(\'111\', \'task1_level1\', 14, \'stage1\')',
                '(\'222\', \'task1_level1\', 13, \'stage1\')',
                '(\'333\', \'task1_level3\', 8, \'stage1\')',
                '(\'333\', \'task2_level3\', 1, \'stage1\')',
                '(\'444\', \'task1_level1\', 5, \'stage1\')',
                '(\'444\', \'task2_level1\', 4, \'stage1\')',
            ],
            4,
            (
                ('111', 2, 2, 0, 'stage1'),
                ('222', 1, 1, 14, 'stage1'),
                ('333', 4, 4, 0, 'stage1'),
                ('444', 4, 2, 0, 'stage1'),
            ),
            id='several_users_progress_some_promoted_others_not',
        ),
    ],
)
async def test_mission_progress_stq_integration(
        notification_params,
        users_setup_params,
        progress_setup_params,
        stq_times_called,
        expected_db_content,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        stq,
        stq_runner,
        pgsql,
        testpoint,
        get_notification,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    cursor = pgsql['cashback_levels'].cursor()
    for params in users_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.users(
                yandex_uid, current_used_level, current_earned_level, progress,
                 stage_id
            )
            VALUES {params};
        """,
        )
    for params in progress_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.missions_completed(
                yandex_uid, task_description_id, completions, stage_id
            )
            VALUES {params};
        """,
        )

    notifications = [
        get_notification(**params) for params in notification_params
    ]
    response = await send_message_to_logbroker(
        consumer='cashback-levels-mission-progress-lb-consumer',
        data_b64=messages_to_b64_protoseq(*notifications),
    )

    await commit.wait_call()
    assert response.status_code == 200

    assert stq.cashback_levels_promotion.times_called == stq_times_called

    # Testsuite doesn't actually call the tasks by itself, just remembers the
    # arguments. We have to call them explicitly.
    tasks = []
    for _ in range(stq_times_called):
        task = stq.cashback_levels_promotion.next_call()
        tasks.append(
            stq_runner.cashback_levels_promotion.call(
                task_id=task['id'], kwargs=task['kwargs'],
            ),
        )
    await asyncio.gather(*tasks)

    cursor.execute(
        'SELECT yandex_uid, current_used_level,'
        '       current_earned_level, progress, stage_id '
        'from cashback_levels.users',
    )
    assert not set(expected_db_content) ^ set(cursor)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.parametrize(
    (
        'users_setup_params',
        'progress_setup_params',
        'expected_db_content',
        'is_rescheduled',
    ),
    [
        pytest.param(
            ['(\'111\', 1, 1, 0, \'stage1\')'],
            ['(\'111\', \'task1_level1\', 3, \'stage1\', 5)'],
            [('111', 1, 1, 0, 'stage1')],
            True,
            id='db_has_smaller_version_than_expected',
        ),
        pytest.param(
            ['(\'111\', 1, 1, 0, \'stage1\')'],
            ['(\'111\', \'task1_level1\', 3, \'stage1\', 10)'],
            [('111', 1, 1, 3, 'stage1')],
            False,
            id='db_has_equal_version_with_expected',
        ),
        pytest.param(
            ['(\'111\', 1, 1, 0, \'stage1\')'],
            ['(\'111\', \'task1_level1\', 3, \'stage1\', 12)'],
            [('111', 1, 1, 3, 'stage1')],
            False,
            id='db_has_bigger_version_than_expected',
        ),
    ],
)
async def test_promotion_stq_version(
        users_setup_params,
        progress_setup_params,
        expected_db_content,
        stq_runner,
        pgsql,
        stq,
        is_rescheduled,
):
    cursor = pgsql['cashback_levels'].cursor()
    for params in users_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.users(
                yandex_uid, current_used_level, current_earned_level, progress,
                 stage_id
            )
            VALUES {params};
        """,
        )
    for params in progress_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.missions_completed(
                yandex_uid, task_description_id, completions, stage_id, version
            )
            VALUES {params};
        """,
        )

    await stq_runner.cashback_levels_promotion.call(
        task_id='some_id',
        kwargs=dict(
            yandex_uid='111',
            task_description_id='task1_level1',
            stage_id='stage1',
            version=10,
        ),
    )
    assert stq.is_empty == (not is_rescheduled)

    cursor.execute(
        'SELECT yandex_uid, current_used_level,'
        '       current_earned_level, progress, stage_id '
        'from cashback_levels.users',
    )
    values = [*cursor]
    assert expected_db_content == values


@pytest.mark.pgsql(
    'cashback_levels', files=['segments_tasks.sql', 'users_segments.sql'],
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.parametrize(
    (
        'yandex_uid',
        'stage_id',
        'users_setup_params',
        'progress_setup_params',
        'expected_assign_stq_kwargs',
        'expect_fail',
        'assign_stq_times_called',
    ),
    [
        pytest.param(
            '666',
            'stage1',
            ['(\'666\', 1, 1, \'stage1\')'],
            ['(\'111\', \'task1_level1\', 15, \'stage1\')'],
            [],
            True,
            0,
            id='user_without_segment',
        ),
        pytest.param(
            '555',
            'stage1',
            ['(\'555\', 1, 1, \'stage1\')'],
            ['(\'111\', \'task1_level1\', 15, \'stage1\')'],
            [],
            True,
            0,
            id='no_tasks_for_segment_error',
        ),
        pytest.param(
            '999',
            'stage1',
            ['(\'999\', 1, 1, \'stage1\')'],
            ['(\'999\', \'task1_level1\', 15, \'stage1\')'],
            [],
            True,
            0,
            id='task_not_in_config_error',
        ),
        pytest.param(
            '333',
            'stage1',
            ['(\'333\', 2, 2, \'stage1\')'],
            ['(\'333\', \'task2_level2\', 15, \'stage1\')'],
            [],
            False,
            0,
            id='no_tasks_for_some_level_is_ok',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 1, 1, \'stage1\')'],
            ['(\'111\', \'task1_level1\', 15, \'stage1\')'],
            [
                {
                    'force': False,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level2',
                    'yandex_uid': '111',
                },
            ],
            False,
            1,
            id='levelup_to_2',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 2, 2, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 15, \'stage1\')',
                '(\'111\', \'task1_level2\', 15, \'stage1\')',
            ],
            [
                {
                    'force': False,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level3',
                    'yandex_uid': '111',
                },
                {
                    'force': False,
                    'stage_id': 'stage1',
                    'task_description_id': 'task2_level3',
                    'yandex_uid': '111',
                },
            ],
            False,
            2,
            id='levelup_to_3',
        ),
        pytest.param(
            '111',
            'stage1',
            ['(\'111\', 3, 3, \'stage1\')'],
            [
                '(\'111\', \'task1_level1\', 15, \'stage1\')',
                '(\'111\', \'task1_level2\', 15, \'stage1\')',
                '(\'111\', \'task1_level3\', 15, \'stage1\')',
            ],
            [],
            False,
            0,
            id='levelup_to_4_doesnt_happen',
        ),
        pytest.param(
            '888',
            'stage1',
            ['(\'888\', 1, 1, \'stage1\')'],
            ['(\'888\', \'task1_level1\', 15, \'stage1\')'],
            [
                {
                    'force': False,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level2',
                    'yandex_uid': '888',
                },
                {
                    'force': False,
                    'stage_id': 'stage1',
                    'task_description_id': 'task2_level2',
                    'yandex_uid': '888',
                },
            ],
            False,
            2,
            id='user_with_multiple_segments_levelup_to_2',
        ),
    ],
)
async def test_mission_assign_on_promotion(
        stq_runner,
        stq,
        pgsql,
        yandex_uid,
        stage_id,
        users_setup_params,
        progress_setup_params,
        expected_assign_stq_kwargs,
        expect_fail,
        assign_stq_times_called,
):
    cursor = pgsql['cashback_levels'].cursor()
    for params in users_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.users(
                yandex_uid, current_used_level, current_earned_level, stage_id
            )
            VALUES {params};
        """,
        )
    for params in progress_setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.missions_completed(
                yandex_uid, task_description_id, completions, stage_id
            )
            VALUES {params};
        """,
        )

    await stq_runner.cashback_levels_promotion.call(
        task_id=yandex_uid + stage_id,
        kwargs=dict(yandex_uid=yandex_uid, stage_id=stage_id),
        expect_fail=expect_fail,
    )

    assert (
        stq.cashback_levels_assign_mission_to_user.times_called
        == assign_stq_times_called
    )

    for i in range(assign_stq_times_called):
        task = stq.cashback_levels_assign_mission_to_user.next_call()
        task['kwargs'].pop('log_extra')
        assert task['kwargs'] == expected_assign_stq_kwargs[i]


@pytest.mark.pgsql(
    'cashback_levels', files=['segments_tasks.sql', 'users_segments.sql'],
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
async def test_parallel_promotion_with_mission_assign(
        stq_runner, stq, pgsql, compare_dct_lists,
):
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cashback_levels.users(
            yandex_uid, current_used_level, current_earned_level, stage_id
        )
        VALUES
        ('111', 2, 2, 'stage1'),
        ('111', 1, 1, 'stage2');
    """,
    )

    cursor.execute(
        f"""
        INSERT INTO cashback_levels.missions_completed(
            yandex_uid, task_description_id, completions, stage_id
        )
        VALUES
        ('111', 'task1_level2', 15, 'stage1'),
        ('111', 'stage2_task', 15, 'stage2');
    """,
    )

    tasks = [
        stq_runner.cashback_levels_promotion.call(
            task_id='111stage1',
            kwargs=dict(yandex_uid='111', stage_id='stage1'),
        ),
        stq_runner.cashback_levels_promotion.call(
            task_id='111stage2',
            kwargs=dict(yandex_uid='111', stage_id='stage2'),
        ),
    ]
    await asyncio.gather(*tasks)

    expected_stq_calls = 3
    assert (
        stq.cashback_levels_assign_mission_to_user.times_called
        == expected_stq_calls
    )

    expected_assign_stq_kwargs = [
        {
            'task_description_id': 'stage2_task_level2',
            'yandex_uid': '111',
            'stage_id': 'stage2',
            'force': False,
        },
        {
            'task_description_id': 'task1_level3',
            'yandex_uid': '111',
            'stage_id': 'stage1',
            'force': False,
        },
        {
            'task_description_id': 'task2_level3',
            'yandex_uid': '111',
            'stage_id': 'stage1',
            'force': False,
        },
    ]

    actual_stq_kwargs = []
    for _ in range(expected_stq_calls):
        task = stq.cashback_levels_assign_mission_to_user.next_call()
        task['kwargs'].pop('log_extra')
        actual_stq_kwargs.append(task['kwargs'])

    compare_dct_lists(expected_assign_stq_kwargs, actual_stq_kwargs)
