import datetime

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import common_pb2
from google.protobuf import timestamp_pb2
import mission_pb2
import pytest

STAGE_START_TIME_CONFIG_FORMAT = '2021-08-25T12:00:00+0000'
STAGE_START_TIME_PYTHON_ISOFORMAT = '2021-08-25T12:00:00+00:00'

STAGE_END_TIME_CONFIG_FORMAT = '2021-11-25T12:00:00+0000'
STAGE_END_TIME_PYTHON_ISOFORMAT = '2021-11-25T12:00:00+00:00'

STAGE_START_SECONDS = int(
    datetime.datetime.fromisoformat(
        STAGE_START_TIME_PYTHON_ISOFORMAT,
    ).timestamp(),
)
STAGE_END_SECONDS = int(
    datetime.datetime.fromisoformat(
        STAGE_END_TIME_PYTHON_ISOFORMAT,
    ).timestamp(),
)


def get_notifications_from_db(cursor):
    cursor.execute(
        f"""
        SELECT yandex_uid, task_description_id, stage_id, version
        FROM cashback_levels.missions_notifications;
        """,
    )
    return [*cursor]


def get_progress_from_db(cursor):
    cursor.execute(
        f"""
        SELECT yandex_uid, task_description_id, stage_id, version, completions
        FROM cashback_levels.missions_completed;
        """,
    )
    return [*cursor]


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
@pytest.mark.pgsql('cashback_levels', files=['mission_assign_test.sql'])
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.parametrize(
    (
        'stq_data',
        'assign_mission_called',
        'delete_mission_called',
        'expected_requests',
        'expected_responses',
        'expected_notifications_db',
        'expected_progress_db',
        'expect_fail',
    ),
    [
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
            },
            1,
            0,
            [
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                ),
            ],
            [dict(status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS)],
            None,
            None,
            False,
            id='simple_assign',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            1,
            1,
            [
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                ),
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    deleted_amount=1,
                ),
                dict(status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS),
            ],
            None,
            None,
            False,
            id='simple_assign_force',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            1,
            1,
            [
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                ),
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    deleted_amount=1,
                ),
                dict(status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS),
            ],
            [
                ('123', 'task1_level1', 'stage2', 0),
                ('123', 'task2_level1', 'stage1', 0),
                ('789', 'task1_level1', 'stage1', 0),
            ],
            [
                ('123', 'task1_level1', 'stage2', 0, 2),
                ('123', 'task2_level1', 'stage1', 0, 3),
                ('789', 'task1_level1', 'stage1', 0, 4),
            ],
            False,
            id='force_assign_removes_progress_and_notifications',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'stage1',
                'task_description_id': 'some-nonexistent-task',
                'force': True,
            },
            0,
            0,
            [],
            [],
            None,
            None,
            True,
            id='assign_task_doesnt_exist',
        ),
        pytest.param(
            {
                'yandex_uid': '123',
                'stage_id': 'some-nonexistent-stage',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            0,
            0,
            [],
            [],
            None,
            None,
            True,
            id='assign_stage_doesnt_exist',
        ),
        pytest.param(
            {
                'yandex_uid': '1111111111',
                'stage_id': 'stage1',
                'task_description_id': 'task1_level1',
                'force': True,
            },
            0,
            0,
            [],
            [],
            None,
            None,
            True,
            id='assign_no_level_for_user_on_stage',
        ),
    ],
)
async def test_assign_mission_to_user_stq(
        pgsql,
        stq_runner,
        stq_data,
        assign_mission_called,
        delete_mission_called,
        expected_requests,
        expected_responses,
        expect_fail,
        mock_mc_user_mission_service,
        expected_notifications_db,
        expected_progress_db,
):
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cashback_levels.users
        ( yandex_uid, current_used_level, current_earned_level, stage_id)
        VALUES ('123', 1, 1, 'stage1');
        """,
    )

    async with mock_mc_user_mission_service(
            expected_requests, expected_responses,
    ) as service:
        await stq_runner.cashback_levels_assign_mission_to_user.call(
            task_id='kek', kwargs=stq_data, expect_fail=expect_fail,
        )
        assert service.servicer.assign_mission_called == assign_mission_called
        assert service.servicer.delete_mission_called == delete_mission_called

        if expected_notifications_db:
            actual_notifications_db = get_notifications_from_db(cursor)
            assert not (
                set(expected_notifications_db) ^ set(actual_notifications_db)
            )

        if expected_progress_db:
            actual_progress_db = get_progress_from_db(cursor)
            assert not set(expected_progress_db) ^ set(actual_progress_db)
